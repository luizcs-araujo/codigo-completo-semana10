from __future__ import annotations
from pathlib import Path
import json, numpy as np
from PIL import Image, ImageChops, ImageEnhance
from skimage.metrics import structural_similarity

def compare(baseline:Path,current:Path,diff_path:Path)->dict:
    a=Image.open(baseline).convert('RGB'); b=Image.open(current).convert('RGB')
    if a.size!=b.size: raise ValueError('images must have the same dimensions')
    aa=np.asarray(a); bb=np.asarray(b)
    changed=np.any(aa!=bb,axis=2)
    pixel_ratio=float(changed.mean())
    gray_a=np.asarray(a.convert('L')); gray_b=np.asarray(b.convert('L'))
    score, ssim_map=structural_similarity(gray_a,gray_b,data_range=255,full=True)
    diff=ImageChops.difference(a,b)
    bbox=diff.getbbox()
    diff_path.parent.mkdir(parents=True,exist_ok=True)
    ImageEnhance.Contrast(diff).enhance(4).save(diff_path)
    return {'pixel_change_ratio':pixel_ratio,'ssim':float(score),'bbox':list(bbox) if bbox else None,'width':a.width,'height':a.height}

def save_metrics(metrics:dict,path:Path): path.write_text(json.dumps(metrics,indent=2))
