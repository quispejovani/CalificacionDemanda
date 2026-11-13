
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
SALIDA = PROCESSED / "propuesta_paginas_evidencia.csv"

PATRONES = {
    "ADMISIBLE": [
        r"\bADMITIR\s+(?:A\s+TRAMITE\s+)?"
        r"(?:EN\s+PROCESO\s+UNICO\s*,?\s*)?"
        r"(?:LA\s+)?DEMANDA\b",
        r"\bADMITASE\s+A\s+TRAMITE\s+"
        r"LA\s+PRESENTE\s+DEMANDA\b",
    ],
    "INADMISIBLE": [
        r"\bDECLARAR\s+INADMISIBLE\s+"
        r"LA\s+DEMANDA\b",
    ],
}

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto.upper()).strip()

def buscar_paginas(ruta, etiqueta):
    patrones = PATRONES.get(etiqueta, [])
    paginas = []

    with pymupdf.open(ruta) as pdf:
        for numero, pagina in enumerate(pdf, 1):
            texto = normalizar(pagina.get_text("text"))

            if any(
                re.search(patron, texto)
                for patron in patrones
            ):
                paginas.append(numero)

    return paginas

def main():
    validacion = PROCESSED / "validacion_juridica.csv"

    if not validacion.exists():
        print("Falta validacion_juridica.csv")
        return

    df = pd.read_csv(
        validacion,
        dtype=str,
        keep_default_na=False
    )

    registros = []

    for _, fila in df.iterrows():
        caso = fila["caso_id"].strip()
        etiqueta = fila["etiqueta_validada"].strip()

        if etiqueta not in PATRONES:
            continue

        numero = int(caso.split("_")[-1])
        nombre_auto = f"auto_{numero}.pdf"
        archivos = list(RAW.rglob(nombre_auto))

        if len(archivos) != 1:
            registros.append({
                "caso_id": caso,
                "auto": nombre_auto,
                "etiqueta": etiqueta,
                "paginas_candidatas": "",
                "estado": "REVISAR_ARCHIVO",
            })
            continue

        paginas = buscar_paginas(
            archivos[0], etiqueta
        )

        registros.append({
            "caso_id": caso,
            "auto": nombre_auto,
            "etiqueta": etiqueta,
            "paginas_candidatas": ";".join(
                map(str, paginas)
            ),
            "estado": (
                "PENDIENTE_CONFIRMACION"
                if paginas
                else "SIN_COINCIDENCIA"
            ),
        })

    resultado = pd.DataFrame(registros)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    resultado.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nPROPUESTA DE PAGINAS DE EVIDENCIA")
    print("=" * 65)

    if not resultado.empty:
        print(resultado.to_string(index=False))

    print(f"\nArchivo: {SALIDA}")
    print("No se modificaron las etiquetas validadas.")

if __name__ == "__main__":
    main()
