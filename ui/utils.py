from __future__ import annotations

import base64
import datetime as dt
from io import BytesIO
import json
from pathlib import Path
import textwrap
import unicodedata

import streamlit as st
from PIL import Image

from similarity_pipeline import IMAGE_EXTS, _safe_name
from tools.cdse_similarity import make_diff_highlight, preprocess_color, preprocess_gray

def _count_gallery(gallery_dir: Path) -> int:
    if not gallery_dir.exists():
        return 0
    total = 0
    for p in gallery_dir.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in IMAGE_EXTS:
            continue
        if "_uploads" in {x.lower() for x in p.relative_to(gallery_dir).parts[:-1]}:
            continue
        total += 1
    return total

def _gallery_image_paths(gallery_dir: Path, limit: int = 12) -> list[Path]:
    if not gallery_dir.exists():
        return []
    paths: list[Path] = []
    for p in sorted(gallery_dir.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in IMAGE_EXTS:
            continue
        if "_uploads" in {x.lower() for x in p.relative_to(gallery_dir).parts[:-1]}:
            continue
        paths.append(p)
        if len(paths) >= limit:
            break
    return paths

def _save_upload(file, upload_root: Path) -> Path:
    upload_dir = upload_root / "_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = Path(file.name).suffix.lower() or ".jpg"
    dest = upload_dir / f"query_{stamp}_{_safe_name(Path(file.name).stem)}{suffix}"
    dest.write_bytes(file.getbuffer())
    return dest

def _find_label(label_dir: Path, item_id: str) -> Path | None:
    if not label_dir.exists():
        return None
    for p in label_dir.glob(f"{item_id}.*"):
        if p.suffix.lower() in IMAGE_EXTS:
            return p
    return None

def _get_query_params() -> dict[str, str]:
    try:
        qp = st.query_params  # type: ignore[attr-defined]
        out: dict[str, str] = {}
        for k in qp.keys():
            v = qp.get_all(k)  # type: ignore[attr-defined]
            if not v:
                continue
            out[str(k)] = str(v[0])
        return out
    except Exception:
        raw = st.experimental_get_query_params()
        out2: dict[str, str] = {}
        for k, v in (raw or {}).items():
            if not v:
                continue
            if isinstance(v, list):
                out2[str(k)] = str(v[0])
            else:
                out2[str(k)] = str(v)
        return out2

def _set_query_params(**params: str) -> None:
    clean = {k: v for k, v in params.items() if v is not None and str(v) != ""}
    try:
        qp = st.query_params  # type: ignore[attr-defined]
        qp.clear()  # type: ignore[attr-defined]
        for k, v in clean.items():
            qp[k] = v  # type: ignore[index]
    except Exception:
        st.experimental_set_query_params(**clean)

def _clear_query_params() -> None:
    try:
        qp = st.query_params  # type: ignore[attr-defined]
        qp.clear()  # type: ignore[attr-defined]
    except Exception:
        st.experimental_set_query_params()

def _normalize_report_payload(payload: dict, output_dir: Path) -> dict:
    query_obj = payload.get("query") or {}
    run_id = str(payload.get("run_id", ""))
    reports_dir = output_dir / "reports"
    return {
        "run_id": run_id,
        "query_id": query_obj.get("id", ""),
        "query": query_obj.get("path", ""),
        "query_staged_path": query_obj.get("staged_path", ""),
        "gallery_count": payload.get("gallery_count", 0),
        "results": payload.get("results") or [],
        "outputs": payload.get("outputs") or {},
        "reports": payload.get("reports")
        or {
            "json": str(reports_dir / f"{run_id}.json"),
            "markdown": str(reports_dir / f"{run_id}.md"),
            "latest_json": str(output_dir / "latest_report.json"),
            "latest_markdown": str(output_dir / "latest_report.md"),
        },
    }

def _load_latest_result(output_dir: Path) -> dict | None:
    latest = output_dir / "latest_report.json"
    if not latest.is_file():
        return None
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except Exception:
        return None
    return _normalize_report_payload(payload, output_dir)

def _img_to_data_uri(
    img: Image.Image,
    *,
    max_size: tuple[int, int] = (520, 360),
    fmt: str = "PNG",
    quality: int = 85,
) -> str:
    out = img.copy()
    out.thumbnail(max_size, Image.LANCZOS)
    buffer = BytesIO()
    fmt_u = fmt.upper()
    if fmt_u in {"JPG", "JPEG"}:
        out = out.convert("RGB")
        out.save(buffer, format="JPEG", quality=int(quality))
        mime = "image/jpeg"
    else:
        out.save(buffer, format="PNG", optimize=True)
        mime = "image/png"
    b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def _thumb_uri_for_path(path_str: str, mtime: float, size: tuple[int, int] = (240, 180)) -> str | None:
    path = Path(path_str)
    if not path.is_file():
        return None
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            return _img_to_data_uri(img, max_size=size, fmt="JPEG", quality=85)
    except Exception:
        return None

def _fmt_score(value) -> str:
    if value is None:
        return "None"
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return str(value)

def _fmt_weight(value) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "0.00"

def _display_width(value: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in {"F", "W"} else 1 for ch in value)

def _pad_display(value: str, width: int, align: str = "left") -> str:
    text = str(value)
    pad = max(0, width - _display_width(text))
    if align == "right":
        return " " * pad + text
    return text + " " * pad

def _part_visuals(query_path: str, candidate_path: str, size: int = 148):
    color_a = preprocess_color(query_path, img_size=224).resize((size, size), Image.LANCZOS)
    color_b = preprocess_color(candidate_path, img_size=224).resize((size, size), Image.LANCZOS)
    gray_a = preprocess_gray(query_path, img_size=224).resize((size, size), Image.LANCZOS)
    gray_b = preprocess_gray(candidate_path, img_size=224).resize((size, size), Image.LANCZOS)
    diff = make_diff_highlight(gray_a, gray_b, img_size=size)
    return color_a, color_b, gray_a.convert("RGB"), gray_b.convert("RGB"), diff

def _html_block(s: str) -> str:
    return textwrap.dedent(s).strip()
