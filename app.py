from __future__ import annotations

import base64
import datetime as dt
from html import escape
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from similarity_pipeline import IMAGE_EXTS, ROOT, _safe_name, run_pipeline
from tools.cdse_similarity import make_diff_highlight, preprocess_color, preprocess_gray


PART_LABELS = {
    "right_mirror": "右后视镜",
    "front_right_light": "右前灯",
    "front_bumper": "前保险杠",
    "grille": "格栅",
    "hood": "机盖",
    "front_glass": "前挡风",
}
DEFAULT_PARTS = ["right_mirror", "front_right_light"]
DEFAULT_FEATURES = ["dino", "ssim", "edge", "clip"]
DEFAULT_GALLERY_DIR = ROOT / "img" / "front"
DEFAULT_UPLOAD_ROOT = ROOT / "img"
DEFAULT_OUTPUT_DIR = ROOT / "result"
DEFAULT_TOPK = 10

CDSE_METHOD_ROWS = [
    ("CLIP ViT-L/14", "语义理解，整体感知", "跨风格（渲染图vs实车）；整体风格是否相似"),
    ("DINOv2 ViT-B/14", "外形轮廓，结构细节", "部件形状是否接近"),
    ("SSIM", "局部结构/纹理相似性", "补充 DINOv2 的局部细节，对格栅纹理、大灯内部结构敏感"),
    ("边缘图余弦", "线条形状和走向", "完全排除颜色干扰，只看轮廓线条"),
]

APP_CSS = """
<style>
    :root {
        --app-bg: #07090c;
        --panel: #15191f;
        --panel-2: #1f252e;
        --line: #303946;
        --line-soft: #252c36;
        --text: #edf4ff;
        --muted: #9aa8b8;
        --accent: #1479b8;
        --accent-2: #2ea8e5;
        --score: #ff7a2f;
    }
    body,
    .stApp,
    .main,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background: var(--app-bg) !important;
        color: var(--text) !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background: rgba(7, 9, 12, 0.92) !important;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background: #1f232a !important;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] [data-testid="stHeading"] *,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #f4f8ff !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
    [data-testid="stSidebar"] p,
    .field-label {
        color: #e8f1ff !important;
        opacity: 1 !important;
        font-weight: 700 !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: var(--text);
    }
    div[data-testid="stCaptionContainer"], .muted {
        color: var(--muted) !important;
    }
    .stTextInput input, .stNumberInput input,
    div[data-testid="stTextInputRootElement"] input,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    input[data-testid="stNumberInputField"] {
        background: #0c1117 !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInputRootElement"],
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-testid="stNumberInputContainer"] {
        background: #0c1117 !important;
        color: var(--text) !important;
        border: 1px solid #465160 !important;
        border-radius: 7px !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-baseweb="select"]:focus-within > div,
    div[data-testid="stNumberInputContainer"]:focus-within {
        border-color: var(--accent-2) !important;
        box-shadow: 0 0 0 1px rgba(46, 168, 229, 0.22) !important;
    }
    div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 42px !important;
        background: #0c1117 !important;
        color: var(--text) !important;
        border: 1px solid #465160 !important;
        border-radius: 7px !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] > div > div,
    div[data-baseweb="select"] [role="combobox"],
    div[data-baseweb="select"] [data-baseweb="select-value"],
    div[data-baseweb="select"] input {
        background: transparent !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }
    div[data-baseweb="select"] svg,
    div[data-testid="stMultiSelect"] svg,
    div[data-testid="stSelectbox"] svg {
        color: #c8d6e6 !important;
        fill: #c8d6e6 !important;
    }
    div[data-baseweb="select"] [aria-disabled="true"],
    div[data-baseweb="select"] [disabled] {
        color: #7f8c9b !important;
        -webkit-text-fill-color: #7f8c9b !important;
    }
    span[data-baseweb="tag"],
    div[data-baseweb="tag"] {
        background: #126fa9 !important;
        border: 1px solid #2ea8e5 !important;
        color: #f5fbff !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    span[data-baseweb="tag"] span,
    div[data-baseweb="tag"] span,
    span[data-baseweb="tag"] svg,
    div[data-baseweb="tag"] svg {
        color: #f5fbff !important;
        fill: #f5fbff !important;
    }
    div[data-testid="portal"] div[data-baseweb="popover"],
    div[data-baseweb="popover"],
    ul[role="listbox"],
    div[role="listbox"] {
        background: #131922 !important;
        color: var(--text) !important;
        border: 1px solid #3a4656 !important;
        border-radius: 8px !important;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.45) !important;
    }
    li[role="option"],
    div[role="option"] {
        background: #131922 !important;
        color: #dce8f7 !important;
    }
    li[role="option"]:hover,
    div[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    div[role="option"][aria-selected="true"] {
        background: #123a55 !important;
        color: #ffffff !important;
    }
    div[data-testid="stNumberInputContainer"] button,
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        background: #151c25 !important;
        color: #dce8f7 !important;
        border: 0 !important;
        border-left: 1px solid #465160 !important;
        box-shadow: none !important;
    }
    div[data-testid="stNumberInputContainer"] button:hover,
    button[data-testid="stNumberInputStepDown"]:hover,
    button[data-testid="stNumberInputStepUp"]:hover {
        background: #1f2b38 !important;
        color: #ffffff !important;
    }
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"] {
        background: #111720 !important;
        border: 1px dashed #465160 !important;
        border-radius: 8px !important;
        color: var(--text) !important;
    }
    section[data-testid="stFileUploaderDropzone"]:hover,
    div[data-testid="stFileUploaderDropzone"]:hover {
        background: #131c27 !important;
        border-color: var(--accent-2) !important;
    }
    div[data-testid="stFileUploaderDropzoneInstructions"],
    div[data-testid="stFileUploaderDropzoneInstructions"] *,
    section[data-testid="stFileUploaderDropzone"] small {
        color: var(--muted) !important;
    }
    section[data-testid="stFileUploaderDropzone"] [data-testid^="stFileUploaderFile"],
    div[data-testid="stFileUploaderDropzone"] [data-testid^="stFileUploaderFile"],
    div[data-testid="stFileUploaderFile"] {
        background: #17202a !important;
        border: 1px solid #3a4656 !important;
        border-radius: 7px !important;
        color: var(--text) !important;
        box-shadow: none !important;
    }
    section[data-testid="stFileUploaderDropzone"] [data-testid^="stFileUploaderFile"] *,
    div[data-testid="stFileUploaderDropzone"] [data-testid^="stFileUploaderFile"] *,
    div[data-testid="stFileUploaderFile"] * {
        color: #e8f1ff !important;
        fill: #e8f1ff !important;
    }
    div[data-testid="stFileUploaderFileSize"] {
        color: #9fb0c4 !important;
    }
    button[data-testid="stBaseButton-secondary"],
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"],
    button[kind="secondaryFormSubmit"] {
        background: #151c25 !important;
        color: #dce8f7 !important;
        border: 1px solid #465160 !important;
        border-radius: 7px !important;
        box-shadow: none !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover,
    button[kind="secondaryFormSubmit"]:hover {
        background: #1f2b38 !important;
        border-color: var(--accent-2) !important;
        color: #ffffff !important;
    }
    button[data-testid="stBaseButton-secondary"][disabled],
    button[data-testid="baseButton-secondary"][disabled],
    button[kind="secondary"][disabled],
    button[kind="secondaryFormSubmit"][disabled],
    button[disabled] {
        background: #111720 !important;
        color: #728093 !important;
        border-color: #303946 !important;
        opacity: 1 !important;
    }
    button[data-testid="stBaseButton-primary"],
    button[data-testid="baseButton-primary"],
    button[kind="primary"] {
        background: var(--accent) !important;
        color: #f5fbff !important;
        border: 1px solid #1f8fd2 !important;
        border-radius: 7px !important;
        font-weight: 800 !important;
    }
    button[data-testid="stBaseButton-primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background: var(--accent-2) !important;
        color: #ffffff !important;
        border-color: var(--accent-2) !important;
    }
    label[data-baseweb="checkbox"] > div:first-child {
        background: #0c1117 !important;
        border-color: #465160 !important;
    }
    label[data-baseweb="checkbox"] > span:first-of-type {
        background: #0c1117 !important;
        border: 1px solid #465160 !important;
        border-radius: 4px !important;
        box-shadow: none !important;
    }
    label[data-baseweb="checkbox"]:hover > span:first-of-type {
        border-color: var(--accent-2) !important;
    }
    label[data-baseweb="checkbox"]:has(input:checked) > span:first-of-type {
        background: var(--accent) !important;
        border-color: var(--accent-2) !important;
    }
    label[data-baseweb="checkbox"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    div[data-testid="stAlert"] > div,
    div[data-baseweb="notification"] {
        background: #081a2a !important;
        border: 1px solid #173d5d !important;
        color: #dce8f7 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line-soft);
        border-radius: 8px;
        padding: 12px 14px;
    }
    div[data-testid="stExpander"] {
        background: #0e1116;
        border: 1px solid var(--line);
        border-radius: 8px;
    }
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] details[open],
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] details[open] summary {
        background: #0e1116 !important;
        color: var(--text) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] details[open] summary:hover {
        background: #151c25 !important;
        color: #ffffff !important;
    }
    div[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] details[open] summary *,
    div[data-testid="stExpander"] svg {
        color: var(--text) !important;
        fill: var(--text) !important;
        opacity: 1 !important;
    }
    div[data-testid="StyledFullScreenButton"],
    button[data-testid="StyledFullScreenButton"],
    button[title="View fullscreen"],
    button[aria-label="View fullscreen"] {
        display: none !important;
    }
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrame"] *,
    div[data-testid="stTable"],
    div[data-testid="stTable"] * {
        color: #dce8f7 !important;
    }
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrameResizable"],
    div[data-testid="stDataFrameGlideDataEditor"] {
        background: #0c1117 !important;
        border: 1px solid #303946 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    div[data-testid="stDataFrame"] canvas,
    div[data-testid="stDataFrameResizable"] canvas,
    div[data-testid="stDataFrameGlideDataEditor"] canvas {
        filter: invert(0.92) hue-rotate(180deg) saturate(0.72) brightness(0.78) contrast(1.08);
        border-radius: 6px !important;
    }
    div[data-testid="stDataFrame"] [data-testid="StyledFullScreenButton"],
    div[data-testid="stDataFrame"] button,
    div[data-testid="stDataFrameResizable"] button {
        background: #151c25 !important;
        color: #dce8f7 !important;
        border: 1px solid #465160 !important;
        border-radius: 7px !important;
        box-shadow: none !important;
    }
    div[data-testid="stDataFrame"] [role="toolbar"],
    div[data-testid="stDataFrameResizable"] [role="toolbar"] {
        background: #0c1117 !important;
        border-color: #303946 !important;
    }
    .stButton > button {
        background: var(--accent);
        color: #f5fbff;
        border: 1px solid #1f8fd2;
        border-radius: 6px;
        font-weight: 700;
    }
    .stButton > button:hover {
        background: var(--accent-2);
        color: #fff;
        border-color: var(--accent-2);
    }
    .report-row {
        background: #101419;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 10px 12px 12px;
        margin: 10px 0 14px;
    }
    .part-title {
        color: var(--text);
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .img-caption {
        color: var(--muted);
        font-size: 12px;
        text-align: center;
        margin-top: 4px;
    }
    .score-card {
        height: 148px;
        background: #151515;
        border: 2px solid var(--score);
        border-radius: 8px;
        padding: 10px;
        color: #ff8a3d;
        font-size: 13px;
        line-height: 1.45;
        overflow: hidden;
    }
    .score-card b {
        color: #ffb178;
    }
    .cdse-table {
        width: 100%;
        border-collapse: collapse;
        color: #d8dee8;
        font-size: 14px;
        background: #171a1f;
    }
    .cdse-table th,
    .cdse-table td {
        border: 1px solid #98a2ad;
        padding: 8px 12px;
        text-align: left;
    }
    .cdse-table th {
        color: #f3f7ff;
        background: #15191f;
    }
    .rank-table-wrap {
        background: #0c1117;
        border: 1px solid #303946;
        border-radius: 8px;
        overflow: hidden;
        margin: 8px 0 12px;
    }
    .rank-table {
        width: 100%;
        border-collapse: collapse;
        color: #dce8f7;
        font-size: 13px;
    }
    .rank-table th {
        background: #151c25;
        color: #f4f8ff;
        font-weight: 800;
        padding: 9px 10px;
        border-bottom: 1px solid #303946;
        text-align: left;
        white-space: nowrap;
    }
    .rank-table td {
        background: #0c1117;
        color: #dce8f7;
        padding: 8px 10px;
        border-bottom: 1px solid #202832;
        vertical-align: middle;
    }
    .rank-table tr:nth-child(even) td {
        background: #101720;
    }
    .rank-table tr:hover td {
        background: #123047;
    }
    .rank-table tr:last-child td {
        border-bottom: 0;
    }
    .rank-num,
    .rank-score {
        color: #7fd0ff !important;
        font-weight: 800;
    }
    .gallery-preview {
        background: #081a2a;
        border: 1px solid #173d5d;
        border-radius: 8px;
        padding: 9px 12px;
        margin: 8px 0 8px;
    }
    .gallery-preview-head {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }
    .gallery-count {
        color: #e8f1ff;
        font-size: 14px;
        font-weight: 800;
    }
    .gallery-title {
        color: #7fd0ff;
        font-size: 14px;
        font-weight: 800;
    }
    .gallery-grid {
        display: grid;
        gap: 10px;
        grid-template-columns: repeat(auto-fill, minmax(118px, 1fr));
    }
    .gallery-thumb {
        background: #0c1117;
        border: 1px solid #303946;
        border-radius: 8px;
        overflow: hidden;
        min-height: 112px;
    }
    .gallery-thumb img {
        background: #ffffff;
        display: block;
        height: 92px;
        object-fit: contain;
        width: 100%;
    }
    .gallery-thumb-name {
        color: #c8d6e6;
        font-size: 12px;
        overflow: hidden;
        padding: 6px 8px;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .run-summary {
        align-items: center;
        background: #081a2a;
        border: 1px solid #173d5d;
        border-radius: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin: 10px 0 12px;
        padding: 10px 12px;
    }
    .run-summary-item {
        align-items: baseline;
        display: inline-flex;
        gap: 6px;
        min-width: 0;
    }
    .run-summary-label {
        color: #9fb0c4;
        font-size: 12px;
        font-weight: 700;
        white-space: nowrap;
    }
    .run-summary-value {
        color: #f4f8ff;
        font-size: 14px;
        font-weight: 800;
        white-space: nowrap;
    }
    .rank-list-header {
        display: grid;
        grid-template-columns: 54px minmax(220px, 1fr) 88px 88px 88px minmax(180px, 0.9fr);
        gap: 8px;
        padding: 8px 12px;
        margin-top: 6px;
        background: #151c25;
        border: 1px solid #303946;
        border-radius: 8px;
        color: #f4f8ff;
        font-size: 12px;
        font-weight: 800;
    }
    .rank-row-summary {
        display: grid;
        grid-template-columns: 54px minmax(220px, 1fr) 88px 88px 88px minmax(180px, 0.9fr);
        gap: 8px;
        width: 100%;
        align-items: center;
    }
    .rank-row-summary span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .part-support-note {
        color: #9aa8b8;
        font-size: 13px;
        text-align: left;
        margin: 2px 0 4px;
    }
</style>
"""


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


@st.cache_data(show_spinner=False)
def _gallery_preview_items(gallery_dir: str, limit: int = 12) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for path in _gallery_image_paths(Path(gallery_dir), limit=limit):
        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                img.thumbnail((180, 120), Image.LANCZOS)
                canvas = Image.new("RGB", (180, 120), "white")
                x = (180 - img.width) // 2
                y = (120 - img.height) // 2
                canvas.paste(img, (x, y))
                buffer = BytesIO()
                canvas.save(buffer, format="JPEG", quality=85)
            uri = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
            items.append((path.name, uri))
        except Exception:
            continue
    return items


def _render_gallery_preview(gallery_dir: Path, gallery_count: int) -> None:
    preview_items = _gallery_preview_items(str(gallery_dir), limit=12)
    thumbs = "".join(
        f"""
        <div class="gallery-thumb">
            <img src="{uri}" alt="{escape(name)}">
            <div class="gallery-thumb-name" title="{escape(name)}">{escape(name)}</div>
        </div>
        """
        for name, uri in preview_items
    )
    empty = '<div class="muted">暂无可预览图片</div>' if not preview_items else ""
    with st.expander(f"当前图库图片数量: {gallery_count}    图库预览", expanded=False):
        st.markdown(f'<div class="gallery-grid">{thumbs}{empty}</div>', unsafe_allow_html=True)


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


@st.cache_data(show_spinner=False)
def _part_visuals(query_path: str, candidate_path: str, size: int = 148):
    color_a = preprocess_color(query_path, img_size=224).resize((size, size), Image.LANCZOS)
    color_b = preprocess_color(candidate_path, img_size=224).resize((size, size), Image.LANCZOS)
    gray_a = preprocess_gray(query_path, img_size=224).resize((size, size), Image.LANCZOS)
    gray_b = preprocess_gray(candidate_path, img_size=224).resize((size, size), Image.LANCZOS)
    diff = make_diff_highlight(gray_a, gray_b, img_size=size)
    return color_a, color_b, gray_a.convert("RGB"), gray_b.convert("RGB"), diff


def _render_cdse_info() -> None:
    rows = "\n".join(
        f"<tr><td>{method}</td><td>{strength}</td><td>{solves}</td></tr>"
        for method, strength, solves in CDSE_METHOD_ROWS
    )
    st.markdown(
        f"""
        <table class="cdse-table">
            <thead>
                <tr><th>方法</th><th>擅长</th><th>解决什么问题</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def _score_card_html(part: str, detail: dict) -> str:
    weights = detail.get("weights_used") or {}
    return f"""
    <div class="score-card">
        <b>part={part}</b><br>
        Fused: {_fmt_score(detail.get("fused"))}<br>
        CLIP: {_fmt_score(detail.get("clip"))}<br>
        DINO: {_fmt_score(detail.get("dino"))}<br>
        SSIM: {_fmt_score(detail.get("ssim"))}<br>
        EDGE: {_fmt_score(detail.get("edge"))}<br>
        W: C{_fmt_weight(weights.get("clip"))}
        D{_fmt_weight(weights.get("dino"))}
        S{_fmt_weight(weights.get("ssim"))}
        E{_fmt_weight(weights.get("edge"))}
    </div>
    """


def _render_part_report_row(part: str, detail: dict) -> None:
    label = PART_LABELS.get(part, part)
    st.markdown('<div class="report-row">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="part-title">{label} <span class="muted">({part})</span>&nbsp;&nbsp;相似度评分：{_fmt_score(detail.get("fused"))}</div>',
        unsafe_allow_html=True,
    )
    try:
        color_a, color_b, gray_a, gray_b, diff = _part_visuals(detail["query_path"], detail["candidate_path"])
        cols = st.columns([1, 1, 1, 1, 1, 1.15], gap="small")
        captions = ["A color", "图库 color", "A gray", "图库 gray", "diff"]
        for col, img, caption in zip(cols[:5], [color_a, color_b, gray_a, gray_b, diff], captions):
            with col:
                st.image(img, width=148)
                st.markdown(f'<div class="img-caption">{caption}</div>', unsafe_allow_html=True)
        with cols[5]:
            st.markdown(_score_card_html(part, detail), unsafe_allow_html=True)
    except Exception as exc:
        st.warning(f"{label} 可视化生成失败: {exc}")
    st.markdown("</div>", unsafe_allow_html=True)


def _render_rank_table(rows: list[dict]) -> None:
    if not rows:
        st.info("暂无排名结果。")
        return
    headers = list(rows[0].keys())
    header_html = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = []
        for header in headers:
            value = row.get(header, "")
            klass = ""
            if header == "排名":
                klass = ' class="rank-num"'
            elif header in {"最终分", "轮廓分", "部件分"}:
                klass = ' class="rank-score"'
            cells.append(f"<td{klass}>{escape(str(value))}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    st.markdown(
        f"""
        <div class="rank-table-wrap">
            <table class="rank-table">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{''.join(body_rows)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_run_summary(result: dict, rows: list[dict]) -> None:
    best = rows[0]["final_score"] if rows else 0
    st.markdown(
        f"""
        <div class="run-summary">
            <div class="run-summary-item">
                <span class="run-summary-label">分析状态</span>
                <span class="run-summary-value">完成</span>
            </div>
            <div class="run-summary-item">
                <span class="run-summary-label">运行编号</span>
                <span class="run-summary-value">{escape(str(result.get("run_id", "")))}</span>
            </div>
            <div class="run-summary-item">
                <span class="run-summary-label">最高相似度</span>
                <span class="run-summary-value">{_fmt_score(best)}</span>
            </div>
            <div class="run-summary-item">
                <span class="run-summary-label">图库数量</span>
                <span class="run-summary-value">{escape(str(result.get("gallery_count", 0)))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_result_detail(row: dict, label_dir: Path, query_label: Path | None) -> None:
    header_col, info_col = st.columns([5, 1])
    with header_col:
        st.markdown("**本版比对结果**")
    with info_col:
        with st.popover("ⓘ CDSE"):
            _render_cdse_info()

    c1, c2, c3 = st.columns(3)
    with c1:
        if query_label:
            st.image(str(query_label), caption="待比对图片部件标注", use_container_width=True)
    with c2:
        cand_label = _find_label(label_dir, row["candidate_id"])
        if cand_label:
            st.image(str(cand_label), caption="图库图片部件标注", use_container_width=True)
    with c3:
        diff = row.get("contour_diff_image")
        if diff:
            st.image(diff, caption="整车轮廓差异图", use_container_width=True)

    st.markdown("**评判分析**")
    for point in row.get("analysis") or []:
        st.write(f"- {point}")

    part_scores = row.get("part_scores") or {}
    if part_scores:
        st.markdown("**部件横向对比**")
        for part, detail in part_scores.items():
            _render_part_report_row(part, detail)
        st.markdown('<div class="part-support-note">暂时不支持出其他部件</div>', unsafe_allow_html=True)


def _rank_expander_label(idx: int, row: dict) -> str:
    valid_parts = ", ".join((row.get("part_scores") or {}).keys()) or "-"
    return (
        f"{idx}  |  {row['candidate_id']}  |  最终分 {_fmt_score(row.get('final_score'))}"
        f"  |  轮廓分 {_fmt_score(row.get('contour_score'))}"
        f"  |  部件分 {_fmt_score(row.get('part_score'))}"
        f"  |  有效部件 {valid_parts}  |  详情"
    )


st.set_page_config(page_title="汽车图片相似度比对", layout="wide", initial_sidebar_state="collapsed")
st.markdown(APP_CSS, unsafe_allow_html=True)
st.title("汽车图片相似度比对")
st.caption("上传单张待比对图片，系统会依次与图片库中的每张图片完成相似度比对。")

gallery_dir = DEFAULT_GALLERY_DIR
upload_root = DEFAULT_UPLOAD_ROOT
output_dir = DEFAULT_OUTPUT_DIR
features = DEFAULT_FEATURES
device_choice = "auto"
topk = DEFAULT_TOPK
skip_cutout = False

gallery_count = _count_gallery(gallery_dir)
_render_gallery_preview(gallery_dir, gallery_count)

selected_parts = DEFAULT_PARTS
left, right = st.columns([1.45, 1], gap="large")
with left:
    uploaded = st.file_uploader("上传待比对图片", type=["jpg", "jpeg", "png", "webp", "bmp"])
    if uploaded is not None:
        st.image(uploaded, caption="待比对图片", use_container_width=True)

with right:
    start = st.button(
        "开始比对",
        type="primary",
        use_container_width=True,
        disabled=uploaded is None or gallery_count <= 0,
    )

if start and uploaded is not None:
    query_path = _save_upload(uploaded, upload_root)
    with st.spinner("正在执行相似度计算，请稍候..."):
        result = run_pipeline(
            input_dir=gallery_dir,
            query_image=query_path,
            output_dir=output_dir,
            parts=selected_parts,
            ignore_parts=[],
            features=",".join(features),
            topk=int(topk),
            device=None if device_choice == "auto" else device_choice,
            skip_cutout=bool(skip_cutout),
        )
    st.session_state["last_result"] = result

result = st.session_state.get("last_result")
if result:
    rows = result.get("results") or []
    reports = result.get("reports") or {}
    outputs = result.get("outputs") or {}

    _render_run_summary(result, rows)

    st.subheader("排名结果")
    label_dir = Path(outputs.get("front_label", ""))
    query_label = _find_label(label_dir, result.get("query_id", ""))

    st.markdown(
        """
        <div class="rank-list-header">
            <span>排名</span>
            <span>图库图片</span>
            <span>最终分</span>
            <span>轮廓分</span>
            <span>部件分</span>
            <span>详情</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for idx, row in enumerate(rows[: int(topk)], start=1):
        with st.expander(_rank_expander_label(idx, row), expanded=idx == 1):
            _render_result_detail(row, label_dir, query_label)

    st.caption(f"JSON 报告: {reports.get('json')} | Markdown 报告: {reports.get('markdown')}")
