from __future__ import annotations

import base64
import datetime as dt
from html import escape
from io import BytesIO
from pathlib import Path
import unicodedata
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components
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
    [data-testid="stMainBlockContainer"] {
        max-width: 1280px !important;
        padding-top: 18px !important;
        padding-bottom: 36px !important;
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
    .field-label {
        margin: 0 0 6px;
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
        display: block;
        padding: 8px 12px;
        margin-top: 6px;
        background: #151c25;
        border: 1px solid #303946;
        border-radius: 8px;
        color: #f4f8ff;
        font-family: Consolas, "Courier New", monospace;
        font-size: 13px;
        font-weight: 800;
        white-space: pre;
    }
    .rank-row-summary {
        display: grid;
        grid-template-columns: 48px minmax(260px, 1fr) 86px 86px 86px 96px;
        gap: 8px;
        width: 100%;
        align-items: center;
        color: #e8f1ff;
        font-size: 13px;
        font-weight: 700;
    }
    .rank-row-summary span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .rank-row-summary .rank-score-cell {
        color: #7fd0ff !important;
        font-weight: 800;
    }
    div[data-testid="stExpander"] summary p {
        font-family: Consolas, "Courier New", monospace !important;
        font-size: 13px !important;
        line-height: 1.25 !important;
        white-space: pre !important;
    }
    .result-image-grid {
        display: grid;
        gap: 14px;
        grid-template-columns: repeat(3, minmax(180px, 260px));
        justify-content: start;
        margin: 10px 0 14px;
    }
    .result-image-grid img {
        background: #ffffff;
        border-radius: 6px;
        display: block;
        max-height: 190px;
        object-fit: contain;
        width: 100%;
    }
    .part-support-note {
        color: #9aa8b8;
        font-size: 13px;
        text-align: left;
        margin: 2px 0 4px;
    }
    .upload-placeholder {
        align-items: center;
        background: #0c1117;
        border: 1px dashed #303946;
        border-radius: 8px;
        color: #9aa8b8;
        display: flex;
        font-size: 14px;
        font-weight: 700;
        justify-content: center;
        min-height: 260px;
        margin-top: 10px;
    }
    .pentagon-stage {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: linear-gradient(180deg, rgba(21, 28, 37, 0.9), rgba(12, 17, 23, 0.96));
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
        padding: 18px;
        margin-top: 12px;
    }
    .pentagon-arena {
        position: relative;
        max-width: 980px;
        margin: 0 auto;
        height: 700px;
        border-radius: 18px;
        background: radial-gradient(560px 420px at 50% 48%, rgba(46, 168, 229, 0.14), transparent 60%);
    }
    .pentagon-card {
        background: #0b0f15;
        border: 1px solid rgba(42, 52, 66, 0.85);
        border-radius: 14px;
        position: absolute;
        overflow: hidden;
        transition: transform 140ms ease, border-color 140ms ease;
        text-decoration: none;
        color: inherit;
    }
    .pentagon-selected {
        border-color: rgba(255, 59, 48, 0.85) !important;
        box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.18);
    }
    .pentagon-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(46, 168, 229, 0.65);
    }
    .pentagon-center {
        width: 460px;
        left: 50%;
        top: 52%;
        transform: translate(-50%, -50%);
        z-index: 10;
        cursor: default;
        box-shadow: 0 26px 70px rgba(0, 0, 0, 0.35);
    }
    .pentagon-node {
        width: 216px;
        z-index: 3;
        cursor: pointer;
    }
    .pentagon-p1 {
        left: 50%;
        top: 8%;
        transform: translate(-50%, -50%);
    }
    .pentagon-p2 {
        left: 12%;
        top: 34%;
        transform: translate(-50%, -50%);
    }
    .pentagon-p3 {
        left: 88%;
        top: 34%;
        transform: translate(-50%, -50%);
    }
    .pentagon-p4 {
        left: 30%;
        top: 97%;
        transform: translate(-50%, -50%);
    }
    .pentagon-p5 {
        left: 70%;
        top: 97%;
        transform: translate(-50%, -50%);
    }
    .pentagon-img {
        display: block;
        width: 100%;
        background: #ffffff;
        object-fit: contain;
    }
    .pentagon-center .pentagon-img {
        aspect-ratio: 16 / 11;
        max-height: 360px;
    }
    .pentagon-node .pentagon-img {
        aspect-ratio: 4 / 3;
        max-height: 200px;
    }
    .pentagon-name {
        padding: 8px 10px 9px;
        border-top: 1px solid rgba(42, 52, 66, 0.6);
        color: rgba(200, 214, 230, 0.92);
        font-size: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .pentagon-badge {
        position: absolute;
        top: 8px;
        padding: 4px 7px;
        border-radius: 10px;
        backdrop-filter: blur(6px);
        font-weight: 900;
        font-size: 12px;
        line-height: 1;
        background: rgba(0, 0, 0, 0.55);
    }
    .pentagon-rank {
        left: 8px;
        border: 1px solid rgba(46, 168, 229, 0.42);
        color: rgba(237, 244, 255, 0.95);
        background: rgba(8, 26, 42, 0.5);
    }
    .pentagon-score {
        right: 8px;
        border: 1px solid rgba(255, 59, 48, 0.78);
        color: #ffd8d6;
    }
    .detail-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin: 12px 0 10px;
    }
    .detail-title {
        font-size: 16px;
        font-weight: 900;
        margin: 0;
    }
    .detail-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(46, 168, 229, 0.35);
        background: rgba(8, 26, 42, 0.35);
        font-weight: 900;
        font-size: 12px;
        white-space: nowrap;
    }
    .detail-pill-score {
        background: rgba(0, 0, 0, 0.55);
        border: 1px solid rgba(255, 59, 48, 0.8);
        color: #ffd8d6;
        border-radius: 999px;
        padding: 4px 8px;
    }
    .part-scroll {
        border-radius: 12px;
        overflow-x: auto;
        overflow-y: hidden;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 6px;
        cursor: grab;
        user-select: none;
    }
    .part-scroll:active {
        cursor: grabbing;
    }
    .part-scroll::-webkit-scrollbar {
        height: 10px;
    }
    .part-scroll::-webkit-scrollbar-track {
        background: rgba(12, 17, 23, 0.35);
        border-radius: 999px;
    }
    .part-scroll::-webkit-scrollbar-thumb {
        background: rgba(46, 168, 229, 0.35);
        border: 1px solid rgba(46, 168, 229, 0.25);
        border-radius: 999px;
    }
    .part-grid {
        display: grid;
        grid-auto-flow: column;
        grid-auto-columns: 92px;
        gap: 10px;
        align-items: start;
        width: max-content;
        padding-right: 4px;
    }
    .part-tile {
        width: 92px;
        border: 1px solid rgba(48, 57, 70, 0.85);
        background: rgba(12, 17, 23, 0.5);
        border-radius: 12px;
        overflow: hidden;
    }
    .part-tile img {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        display: block;
        background: #ffffff;
    }
    .part-cap {
        padding: 7px 8px;
        border-top: 1px solid rgba(48, 57, 70, 0.55);
        color: rgba(154, 168, 184, 0.95);
        font-size: 11px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .part-scorebox {
        width: 220px;
        border: 1px solid rgba(255, 59, 48, 0.5);
        background: rgba(21, 28, 37, 0.52);
        border-radius: 12px;
        padding: 9px 10px;
        display: grid;
        gap: 8px;
        min-height: 92px;
    }
    .part-score-top {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 10px;
    }
    .part-score-big {
        font-weight: 1000;
        color: rgba(255, 216, 214, 0.95);
        font-size: 18px;
        letter-spacing: 0.2px;
    }
    .part-score-id {
        color: rgba(154, 168, 184, 0.95);
        font-weight: 900;
        font-size: 11px;
        white-space: nowrap;
    }
    .part-score-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 4px 10px;
        color: rgba(255, 216, 214, 0.92);
        font-weight: 900;
        font-size: 11px;
    }
    .part-score-grid span {
        color: rgba(154, 168, 184, 0.95);
        font-weight: 900;
        margin-right: 6px;
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


@st.cache_data(show_spinner=False)
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
            f"""
            <a class="{klass}" href="{href}">
              <span class="pentagon-badge pentagon-rank">Top{idx}</span>
              <span class="pentagon-badge pentagon-score">{escape(_fmt_score(row.get("final_score")))}</span>
              <img class="pentagon-img" src="{cand_uri}" alt="{escape(candidate_id)}" />
              <div class="pentagon-name">{escape(candidate_id)}</div>
            </a>
            """
        )

    if not nodes_html:
        st.info("暂无可展示的 Top5 缩略图。")
        return

    st.markdown(
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
        f"""
        <div class="part-tile">
          <img src="{uri}" alt="{escape(cap)}" />
          <div class="part-cap">{escape(cap)}</div>
        </div>
        """
        for cap, uri in tiles
    )
    score_html = f"""
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

    st.markdown('<div class="report-row">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="part-title">{escape(label)} <span class="muted">({escape(part)})</span>&nbsp;&nbsp;相似度评分：{escape(fused)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="part-scroll" data-drag-scroll>
          <div class="part-grid">
            {tiles_html}
            {score_html}
          </div>
        </div>
        """,
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
            _clear_query_params()
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()
    with actions_r:
        st.markdown(
            f'<div class="detail-pill">Top · {escape(candidate_id)} <span class="detail-pill-score">总分 {escape(fused)}</span></div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
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
            st.metric("轮廓分", _fmt_score(row.get("contour_score")))
        with m3:
            st.metric("部件分", _fmt_score(row.get("part_score")))

        st.markdown("**评判分析**")
        for point in row.get("analysis") or []:
            st.write(f"- {point}")

    with right:
        st.markdown("**部件横向对比**")
        part_scores = row.get("part_scores") or {}
        for part, detail in part_scores.items():
            _render_part_row_compact_scroll(part, detail)
        if not part_scores:
            st.caption("无可用部件明细。")


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

selected_parts = DEFAULT_PARTS
gallery_count = _count_gallery(gallery_dir)

label_col, tools_col = st.columns([1.35, 1], gap="large")
with label_col:
    st.markdown('<div class="field-label">上传待比对图片</div>', unsafe_allow_html=True)
with tools_col:
    st.markdown('<div class="field-label">&nbsp;</div>', unsafe_allow_html=True)

upload_col, gallery_col = st.columns([1.35, 1], gap="large")
with upload_col:
    uploaded = st.file_uploader(
        "上传待比对图片",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        label_visibility="collapsed",
    )
with gallery_col:
    _render_gallery_preview(gallery_dir, gallery_count)

preview_col, spacer_col = st.columns([1.35, 1], gap="large")
with preview_col:
    if uploaded is not None:
        st.image(uploaded, caption="待比对图片", use_container_width=True)
    else:
        st.markdown('<div class="upload-placeholder">待比对图片信息</div>', unsafe_allow_html=True)
    start = st.button(
        "开始比对",
        type="primary",
        use_container_width=True,
        disabled=uploaded is None or gallery_count <= 0,
    )
with spacer_col:
    st.empty()

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
    label_dir = Path(outputs.get("front_label", ""))
    query_label = _find_label(label_dir, result.get("query_id", ""))

    qp = _get_query_params()
    selected_cid = qp.get("cid")
    rows_by_id = {str(x.get("candidate_id")): x for x in rows}

    if selected_cid and selected_cid in rows_by_id:
        _render_detail_view(rows_by_id[selected_cid], label_dir, query_label)
    else:
        query_path = Path(str(result.get("query", "")))
        if query_path.is_file():
            _render_top5_pentagon(rows, query_path, selected_cid)
        else:
            st.info("未找到待比对图片，无法展示 Top5 概览。")

    st.caption(f"JSON 报告: {reports.get('json')} | Markdown 报告: {reports.get('markdown')}")
