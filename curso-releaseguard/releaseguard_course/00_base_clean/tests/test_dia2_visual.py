from pathlib import Path
from PIL import Image, ImageDraw
from visual.compare import compare

def test_compare_detects_local_change(tmp_path):
    a=Image.new('RGB',(200,100),'white'); b=a.copy(); ImageDraw.Draw(b).rectangle((150,60,190,90),fill='black')
    pa=tmp_path/'a.png'; pb=tmp_path/'b.png'; pd=tmp_path/'d.png'; a.save(pa); b.save(pb)
    m=compare(pa,pb,pd)
    assert 0 < m['pixel_change_ratio'] < 0.2
    assert m['ssim'] < 1
    assert m['bbox'] is not None and pd.exists()
