
from pathlib import Path
import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

registros = []

for carpeta in sorted(RAW.iterdir()):
    if not carpeta.is_dir():
        continue

    caso_id = carpeta.name

    for ruta in sorted(carpeta.rglob("*.pdf")):
        if not ruta.stem.lower().startswith("demanda"):
            continue

        textos = []
        paginas_sin_texto = 0

        try:
            with pymupdf.open(ruta) as doc:
                total_paginas = len(doc)

                for pagina in doc:
                    texto = pagina.get_text("text").strip()

                    if len(texto) < 30:
                        paginas_sin_texto += 1

                    textos.append(texto)

            texto_completo = "\n".join(textos)

            registros.append({
                "caso_id": caso_id,
                "documento": str(ruta.relative_to(RAW)),
                "paginas": total_paginas,
                "paginas_sin_texto": paginas_sin_texto,
                "caracteres": len(texto_completo),
                "requiere_ocr": paginas_sin_texto > 0,
                "texto": texto_completo,
                "estado": "OK"
            })

            print(
                f"{caso_id} | {ruta.name} | "
                f"caracteres={len(texto_completo)} | "
                f"paginas_ocr={paginas_sin_texto}"
            )

        except Exception as exc:
            registros.append({
                "caso_id": caso_id,
                "documento": str(ruta.relative_to(RAW)),
                "paginas": 0,
                "paginas_sin_texto": 0,
                "caracteres": 0,
                "requiere_ocr": True,
                "texto": "",
                "estado": f"ERROR: {exc}"
            })

df = pd.DataFrame(registros)

salida = OUT / "textos_demandas_101.csv"
df.to_csv(salida, index=False, encoding="utf-8-sig")

print("\n========== RESUMEN ==========")
print("Documentos:", len(df))
print("Expedientes:", df["caso_id"].nunique())
print("Documentos con OCR pendiente:", df["requiere_ocr"].sum())
print("Documentos sin texto:", (df["caracteres"] == 0).sum())
print("Errores:", (df["estado"] != "OK").sum())
print("Archivo:", salida)