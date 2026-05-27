from __future__ import annotations

from pathlib import Path

import streamlit as st

from .utils import _gallery_image_paths

def _render_gallery_preview(gallery_dir: Path, gallery_count: int) -> None:
    preview_paths = _gallery_image_paths(gallery_dir, limit=12)
    head_l, head_r = st.columns([1.25, 0.75], gap="small")
    with head_l:
        st.markdown(
            f"""
            <div class="gallery-preview" style="margin: 0;">
                <div class="gallery-preview-head">
                    <div class="gallery-count">图库数量: {gallery_count}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with head_r:
        with st.popover("图库预览"):
            if not preview_paths:
                st.caption("暂无可预览图片")
            else:
                for start in range(0, len(preview_paths), 4):
                    batch = preview_paths[start : start + 4]
                    cols = st.columns(min(4, len(batch)), gap="small")
                    for col, path in zip(cols, batch):
                        with col:
                            st.image(str(path), caption=path.name, width=120)
    st.selectbox(
        "车型选择",
        ["SUV", "轿车", "轿跑", "越野", "MPV", "皮卡"],
        index=0,
        key="vehicle_type_demo",
    )
