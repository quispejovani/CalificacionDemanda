"""Inventario LOCAL de metadatos PDF. No lee ni publica contenido de expedientes."""
from pathlib import Path
import csv, sys
try:
 import fitz
except ImportError:
 raise SystemExit("Instale dependencias: pip install -r requirements.txt")
folder = Path(sys.argv[1]) if len(sys.argv)>1 else Path('data/raw')
rows=[]
for p in sorted(folder.rglob('*.pdf')):
 try:
  with fitz.open(p) as doc:
   paginas=len(doc)
   texto=sum(len(page.get_text().strip()) for page in doc)
  rows.append([p.name,paginas, 'SI' if texto>100 else 'NO','SI' if texto<=100 else 'NO'])
 except Exception as e:
  rows.append([p.name,'ERROR','NO_DETERMINADO','NO_DETERMINADO'])
out=Path('data/processed/inventario_local.csv');out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['archivo_local','paginas','texto_extraible_estimado','ocr_probable']);w.writerows(rows)
print(f'Inventario local generado: {out} ({len(rows)} PDFs). No subir este archivo sin revisión de privacidad.')
