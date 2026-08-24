from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(cmd,cwd):
 print(f"\n$ {' '.join(cmd)} [{cwd.name}]"); p=subprocess.run(cmd,cwd=cwd);
 if p.returncode: raise SystemExit(p.returncode)
def main():
 matrix=[('00_base_clean','smoke_base'),('01_dia1','smoke_dia1'),('02_dia2','smoke_dia2'),('03_dia3','smoke_dia3'),('complete','smoke_complete')]
 for name,smoke in matrix:
  cwd=ROOT/name; run([sys.executable,'-m','compileall','-q','.'],cwd); run([sys.executable,'-m','pytest','-q'],cwd); run([sys.executable,'-m',f'scripts.{smoke}'],cwd)
 print('\nOFFLINE COURSE VALIDATION: PASS')
 print('LIVE GATES NOT RUN IN THIS ENVIRONMENT: Docker/n8n, Prometheus container, Jaeger container, Ollama text, Ollama vision.')
if __name__=='__main__': main()
