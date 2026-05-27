from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

from .config import CDSE_METHOD_ROWS, PART_LABELS
from .utils import (
    _display_width,
    _find_label,
    _fmt_score,
    _fmt_weight,
    _html_block,
    _img_to_data_uri,
    _pad_display,
    _part_visuals,
    _set_query_params,
    _thumb_uri_for_path,
)

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

def _ensure_drag_scroll_js() -> None:
    if st.session_state.get("_drag_scroll_js_loaded"):
        return
    components.html(
        """
        <script>
        (function () {
          function bind(el) {
            var isDown = false;
            var startX = 0;
            var startLeft = 0;
            el.addEventListener("pointerdown", function (e) {
              isDown = true;
              startX = e.clientX;
              startLeft = el.scrollLeft;
              try { el.setPointerCapture(e.pointerId); } catch (err) {}
            });
            el.addEventListener("pointermove", function (e) {
              if (!isDown) return;
              var dx = e.clientX - startX;
              el.scrollLeft = startLeft - dx;
            });
            function end(e) {
              isDown = false;
              try { el.releasePointerCapture(e.pointerId); } catch (err) {}
            }
            el.addEventListener("pointerup", end);
            el.addEventListener("pointercancel", end);
            el.addEventListener("mouseleave", function () { isDown = false; });
          }
          function init() {
            document.querySelectorAll("[data-drag-scroll]").forEach(bind);
          }
          if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", init);
          } else {
            init();
          }
        })();
        </script>
        """,
        height=0,
        width=0,
    )
    st.session_state["_drag_scroll_js_loaded"] = True

def _render_top5_pentagon(rows: list[dict], query_image_path: Path, selected_candidate_id: str | None) -> None:
    query_uri = _thumb_uri_for_path(str(query_image_path), float(query_image_path.stat().st_mtime), size=(640, 440))
    if not query_uri:
        st.info("未找到待比对图片，无法展示 Top5 概览。")
        return

    slots = ["pentagon-p1", "pentagon-p2", "pentagon-p3", "pentagon-p4", "pentagon-p5"]
    nodes_html: list[str] = []
    for idx, row in enumerate(rows[:5], start=1):
        candidate_id = str(row.get("candidate_id", ""))
        candidate_path = str(row.get("candidate_path", ""))
        mtime = 0.0
        try:
            mtime = float(Path(candidate_path).stat().st_mtime)
        except Exception:
            mtime = 0.0
        cand_uri = _thumb_uri_for_path(candidate_path, mtime, size=(360, 260)) if candidate_path else None
        if not cand_uri:
            continue
        klass = f"pentagon-card pentagon-node {slots[idx-1]}"
        if selected_candidate_id and candidate_id == selected_candidate_id:
            klass += " pentagon-selected"
        href = f"?view=detail&cid={quote(candidate_id)}"
        nodes_html.append(
            _html_block(
                f"""
<a class="{klass}" href="{href}" target="_self" title="点击展开 Top{idx} 详情">
  <span class="pentagon-badge pentagon-rank">Top{idx}</span>
  <span class="pentagon-badge pentagon-score">{escape(_fmt_score(row.get("final_score")))}</span>
  <img class="pentagon-img" src="{cand_uri}" alt="{escape(candidate_id)}" />
  <div class="pentagon-name">{escape(candidate_id)}</div>
</a>
"""
            )
        )

    if not nodes_html:
        st.info("暂无可展示的 Top5 缩略图。")
        return

    st.markdown(
        _html_block(
            f"""
        <div class="pentagon-stage">
          <div class="pentagon-arena">
            <div class="pentagon-card pentagon-center">
              <img class="pentagon-img" src="{query_uri}" alt="query" />
              <div class="pentagon-name">上传比对图片</div>
            </div>
            {''.join(nodes_html)}
          </div>
        </div>
        """,
        ),
        unsafe_allow_html=True,
    )

def _render_part_row_compact_scroll(part: str, detail: dict) -> None:
    label = PART_LABELS.get(part, part)
    fused = _fmt_score(detail.get("fused"))
    weights = detail.get("weights_used") or {}
    try:
        color_a, color_b, gray_a, gray_b, diff = _part_visuals(detail["query_path"], detail["candidate_path"], size=140)
        tiles = [
            ("A color", _img_to_data_uri(color_a, max_size=(92, 92), fmt="JPEG")),
            ("B color", _img_to_data_uri(color_b, max_size=(92, 92), fmt="JPEG")),
            ("A gray", _img_to_data_uri(gray_a, max_size=(92, 92), fmt="JPEG")),
            ("B gray", _img_to_data_uri(gray_b, max_size=(92, 92), fmt="JPEG")),
            ("diff", _img_to_data_uri(diff, max_size=(92, 92), fmt="JPEG")),
        ]
    except Exception as exc:
        st.warning(f"{label} 可视化生成失败: {exc}")
        return

    tiles_html = "".join(
        _html_block(
            f"""
<div class="part-tile">
  <img src="{uri}" alt="{escape(cap)}" />
  <div class="part-cap">{escape(cap)}</div>
</div>
"""
        )
        for cap, uri in tiles
    )
    score_html = _html_block(
        f"""
<div class="part-scorebox">
  <div class="part-score-top">
    <div class="part-score-big">{escape(fused)}</div>
    <div class="part-score-id">{escape(f"part={part}")}</div>
  </div>
  <div class="part-score-grid">
    <div><span>CLIP</span>{escape(_fmt_score(detail.get("clip")))}</div>
    <div><span>DINO</span>{escape(_fmt_score(detail.get("dino")))}</div>
    <div><span>SSIM</span>{escape(_fmt_score(detail.get("ssim")))}</div>
    <div><span>EDGE</span>{escape(_fmt_score(detail.get("edge")))}</div>
    <div><span>W</span>{escape(f"C{_fmt_weight(weights.get('clip'))} D{_fmt_weight(weights.get('dino'))}")}</div>
    <div><span>&nbsp;</span>{escape(f"S{_fmt_weight(weights.get('ssim'))} E{_fmt_weight(weights.get('edge'))}")}</div>
  </div>
</div>
"""
    )

    st.markdown('<div class="report-row">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="part-title">{escape(label)} <span class="muted">({escape(part)})</span>&nbsp;&nbsp;相似度评分：{escape(fused)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        _html_block(
            f"""
<div class="part-scroll" data-drag-scroll>
  <div class="part-grid">
    {tiles_html}
    {score_html}
  </div>
</div>
        """
        ),
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

def _render_detail_view(row: dict, label_dir: Path, query_label: Path | None) -> None:
    _ensure_drag_scroll_js()
    candidate_id = str(row.get("candidate_id", ""))
    fused = _fmt_score(row.get("final_score"))

    actions_l, actions_r = st.columns([1, 1], gap="small")
    with actions_l:
        if st.button("返回 Top5", type="secondary"):
            st.session_state.pop("selected_candidate_id", None)
            _set_query_params(view="top5")
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()
    with actions_r:
        st.markdown(
            f'<div class="detail-pill">Top · {escape(candidate_id)} <span class="detail-pill-score">总分 {escape(fused)}</span></div>',
            unsafe_allow_html=True,
        )

    parts_shell, _ = st.columns([0.92, 0.08], gap="small")
    with parts_shell:
        st.markdown("**部件横向对比**")
        part_scores = row.get("part_scores") or {}
        for part, detail in part_scores.items():
            _render_part_row_compact_scroll(part, detail)
        if not part_scores:
            st.caption("无可用部件明细。")

    detail_shell, _ = st.columns([0.92, 0.08], gap="small")
    with detail_shell:
        st.markdown("**轮廓对比分析**")
        c1, c2, c3 = st.columns(3, gap="small")
        with c1:
            if query_label:
                st.image(str(query_label), caption="待比对图片部件标注", use_container_width=True)
        with c2:
            cand_label = _find_label(label_dir, candidate_id)
            if cand_label:
                st.image(str(cand_label), caption="图库图片部件标注", use_container_width=True)
        with c3:
            diff = row.get("contour_diff_image")
            if diff:
                st.image(diff, caption="整车轮廓差异图", use_container_width=True)

        m1, m2, m3 = st.columns(3, gap="small")
        with m1:
            st.metric("总相似度", fused)
        with m2:
            st.metric("轮廓分（40%）", _fmt_score(row.get("contour_score")))
        with m3:
            st.metric("部件分（60%）", _fmt_score(row.get("part_score")))

        st.markdown("**评判分析**")
        for point in row.get("analysis") or []:
            st.write(f"- {point}")

def _render_result_detail(row: dict, label_dir: Path, query_label: Path | None) -> None:
    st.markdown("**本版比对结果**")

    c1, c2, c3 = st.columns(3)
    with c1:
        if query_label:
            st.image(str(query_label), caption="待比对图片部件标注", width=260)
    with c2:
        cand_label = _find_label(label_dir, row["candidate_id"])
        if cand_label:
            st.image(str(cand_label), caption="图库图片部件标注", width=260)
    with c3:
        diff = row.get("contour_diff_image")
        if diff:
            st.image(diff, caption="整车轮廓差异图", width=260)

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
    image_name = str(row["candidate_id"])
    while _display_width(image_name) > 46:
        image_name = image_name[:-2] + "..."
    return (
        f"{_pad_display(str(idx), 4)}"
        f"{_pad_display(image_name, 48)}"
        f"{_pad_display(_fmt_score(row.get('final_score')), 8, 'right')}"
        f"{_pad_display(_fmt_score(row.get('contour_score')), 8, 'right')}"
        f"{_pad_display(_fmt_score(row.get('part_score')), 8, 'right')}"
        f"{_pad_display('详情', 10, 'right')}"
    )

def _rank_header_label() -> str:
    return (
        f"{_pad_display('排名', 4)}"
        f"{_pad_display('图库图片', 48)}"
        f"{_pad_display('最终分', 8, 'right')}"
        f"{_pad_display('轮廓分', 8, 'right')}"
        f"{_pad_display('部件分', 8, 'right')}"
        f"{_pad_display('详情', 10, 'right')}"
    )
