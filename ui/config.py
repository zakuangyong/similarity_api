from __future__ import annotations

from similarity_pipeline import ROOT

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
