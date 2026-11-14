
from pathlib import Path
from datetime import datetime
import hashlib

import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

registros = []

def sha256_archivo(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()

carpetas = sorted(
    p for p in RAW.iterdir() if p.is_dir()
)

for carpeta in carpetas:
    caso_id = carpeta.name
    archivos = sorted(carpeta.rglob("*.pdf"))

    print(f"Procesando {caso_id}: {len(archivos)} PDF")

    for ruta in archivos:
        registro = {
            "caso_id": caso_id,
            "documento": str(ruta.relative_to(RAW)),
            "tipo_documento": (
                "AUTO" if ruta.stem.lower().startswith("auto")
                else "DEMANDA" if ruta.stem.lower().startswith("demanda")
                else "OTRO"
            ),
            "paginas": 0,
            "paginas_con_texto": 0,
            "paginas_sin_texto": 0,
            "sha256": "",
            "estado": "OK",
        }

        try:
            registro["sha256"] = sha256_archivo(ruta)

            with pymupdf.open(ruta) as pdf:
                registro["paginas"] = len(pdf)

                for pagina in pdf:
                    texto = pagina.get_text("text").strip()

                    if texto:
                        registro["paginas_con_texto"] += 1
                    else:
                        registro["paginas_sin_texto"] += 1

        except Exception as e:
            registro["estado"] = f"ERROR: {e}"

        registros.append(registro)

df = pd.DataFrame(registros)

if df.empty:
    print("No se encontraron documentos PDF.")
else:
    df["duplicado_sha256"] = df.duplicated(
        "sha256", keep=False
    ) & df["sha256"].ne("")

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    salida = PROCESSED / f"inventario_ingesta_{fecha}.csv"

    df.to_csv(salida, index=False, encoding="utf-8-sig")

    print("\n========== RESUMEN ==========")
    print("Expedientes:", df["caso_id"].nunique())
    print("Documentos PDF:", len(df))
    print("Páginas:", df["paginas"].sum())
    print("Páginas sin texto:", df["paginas_sin_texto"].sum())
    print("PDF duplicados:", df["duplicado_sha256"].sum())
    print("\nTipos de documentos:")
    print(df["tipo_documento"].value_counts())
    print("\nInventario guardado en:", salida)
