from __future__ import annotations

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
        min-height: 220px;
        margin-top: -24px;
    }
    .upload-preview-tight {
        margin-top: -8px;
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
        height: 860px;
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
    .pentagon-node {
        transform: var(--pentagon-pos);
        transform-origin: center center;
    }
    .pentagon-selected {
        border-color: rgba(255, 59, 48, 0.85) !important;
        box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.18);
    }
    .pentagon-node:hover {
        transform: var(--pentagon-pos) scale(1.06);
        border-color: rgba(46, 168, 229, 0.65);
        box-shadow: 0 18px 42px rgba(46, 168, 229, 0.18);
        z-index: 12;
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
        top: 15%;
        --pentagon-pos: translate(-50%, -50%);
    }
    .pentagon-p2 {
        left: 12%;
        top: 34%;
        --pentagon-pos: translate(-50%, -50%);
    }
    .pentagon-p3 {
        left: 88%;
        top: 34%;
        --pentagon-pos: translate(-50%, -50%);
    }
    .pentagon-p4 {
        left: 30%;
        top: 88%;
        --pentagon-pos: translate(-50%, -50%);
    }
    .pentagon-p5 {
        left: 70%;
        top: 88%;
        --pentagon-pos: translate(-50%, -50%);
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
