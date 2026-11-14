
from pathlib import Path
import io
import time

import pandas as pd
import pymupdf
import pytesseract
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"

TESSERACT = BASE / "tools" / "tesseract" / "tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = str(TESSERACT)

if not TESSERACT.is_file():
    raise FileNotFoundError(f"No existe: {TESSERACT}")

registros = []
inicio = time.time()

for carpeta in sorted(RAW.iterdir()):
    if not carpeta.is_dir():
        continue

    for ruta in sorted(carpeta.rglob("*.pdf")):
        if not ruta.stem.lower().startswith("demanda"):
            continue

        textos = []
        paginas_ocr = 0
        errores_ocr = 0

        try:
            with pymupdf.open(ruta) as doc:
                for numero, pagina in enumerate(doc, start=1):
                    texto = pagina.get_text("text").strip()

                    # OCR solamente si hay poco texto extraíble.
                    if len(texto) < 30:
                        try:
                            pix = pagina.get_pixmap(
                                dpi=200,
                                colorspace=pymupdf.csRGB,
                                alpha=False
                            )

                            imagen = Image.open(
                                io.BytesIO(pix.tobytes("png"))
                            )

                            texto_ocr = pytesseract.image_to_string(
                                imagen,
                                lang="spa",
                                config="--psm 3",
                                timeout=90
                            ).strip()

                            if len(texto_ocr) > len(texto):
                                texto = texto_ocr

                            paginas_ocr += 1

                        except Exception as exc:
                            errores_ocr += 1
                            print(
                                f"ERROR OCR {ruta.name} "
                                f"página {numero}: {exc}"
                            )

                    textos.append(texto)

            registros.append({
                "caso_id": carpeta.name,
                "documento": str(ruta.relative_to(RAW)),
                "texto": "\n".join(textos),
                "caracteres": sum(len(t) for t in textos),
                "paginas_ocr": paginas_ocr,
                "errores_ocr": errores_ocr,
                "estado": "OK" if errores_ocr == 0 else "OCR_PARCIAL"
            })

            print(
                f"{carpeta.name} | {ruta.name} | "
                f"OCR={paginas_ocr} | errores={errores_ocr}",
                flush=True
            )

        except Exception as exc:
            print(f"ERROR PDF {ruta}: {exc}", flush=True)
            registros.append({
                "caso_id": carpeta.name,
                "documento": str(ruta.relative_to(RAW)),
                "texto": "",
                "caracteres": 0,
                "paginas_ocr": 0,
                "errores_ocr": 1,
                "estado": "ERROR_PDF"
            })

OUT.mkdir(parents=True, exist_ok=True)
salida = OUT / "textos_demandas_ocr.csv"

df = pd.DataFrame(registros)
df.to_csv(salida, index=False, encoding="utf-8-sig")

print("\n========== RESUMEN OCR ==========")
print("Documentos:", len(df))
print("Expedientes:", df["caso_id"].nunique())
print("Páginas procesadas con OCR:", df["paginas_ocr"].sum())
print("Errores OCR:", df["errores_ocr"].sum())
print("Tiempo (min):", round((time.time() - inicio) / 60, 2))
print("Archivo:", salida)
