from pathlib import Path
import json, numpy as np
from PIL import Image, ImageChops, ImageEnhance
from skimage.metrics import structural_similarity # SSIM

def compare(baseline:Path, current:Path, diff_path:Path):
    baseline_image=Image.open(baseline).convert("RGB")
    current_image =Image.open(current).convert("RGB")
    if baseline_image.size!=current_image.size: raise ValueError("Images must have the same dimensions")

    a_baseline_image = np.asarray(baseline_image)
    a_current_image = np.asarray(current_image)
    changed=np.any(a_baseline_image!=a_current_image, axis=2)
    pixel_ratio=float(changed.mean())
    gray_baseline=np.asarray(baseline_image.convert("L"))
    gray_current=np.asarray(current_image.convert("L"))

    score, ssim_map=structural_similarity(gray_baseline, gray_current, data_range=255, full=True)
    diff = ImageChops.difference(baseline_image, current_image)
    bbox = diff.getbbox()
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    ImageEnhance.Contrast(diff).enhance(4).save(diff_path)
    return {
        'pixel_change_ratio':pixel_ratio,
        'ssim':float(score),
        'bbox': list(bbox) if bbox else None,
        'width': baseline_image.width, 'height':baseline_image.height
    }

def save_metrics(metrics, path):
    path.write_text(json.dumps(metrics, indent=2))