
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SALIDA = BASE / "data" / "processed" / "estructura_autos.csv"

MARCADORES = re.compile(
    r"\b(?:"
    r"SE\s+RESUELVE|"
    r"RESUELVE|"
    r"RESUELVO|"
    r"RESUELVEN|"
    r"FALLO"
    r")\s*:?",
    re.IGNORECASE
)

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto.upper())

def analizar(ruta):
    paginas_con_marcador = []
    total_marcadores = 0

    with pymupdf.open(ruta) as pdf:
        total_paginas = len(pdf)

        for numero, pagina in enumerate(pdf, 1):
            texto = normalizar(pagina.get_text("text"))
            coincidencias = list(PATRON.finditer(texto))

            if coincidencias:
                paginas_con_marcador.append(numero)
                total_marcadores += len(coincidencias)

    if total_marcadores == 0:
        alerta = "SIN_MARCADOR"
    elif total_marcadores > 1:
        alerta = "MULTIPLES_MARCADORES"
    else:
        alerta = "MARCADOR_UNICO"

    return {
        "auto": ruta.name,
        "total_paginas": total_paginas,
        "total_marcadores": total_marcadores,
        "paginas_marcadores": ";".join(
            map(str, paginas_con_marcador)
        ),
        "alerta_estructura": alerta,
    }

def main():
    registros = []

    for ruta in sorted(RAW.rglob("auto_*.pdf")):
        try:
            registros.append(analizar(ruta))
        except Exception as error:
            print(
                f"Error en {ruta.name}: "
                f"{type(error).__name__}"
            )

    df = pd.DataFrame(registros)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False, encoding="utf-8-sig")

    print("\nESTRUCTURA DE AUTOS")
    print("=" * 65)

    if not df.empty:
        print(df.to_string(index=False))

    print(f"\nReporte: {SALIDA}")

if __name__ == "__main__":
    main()
