
from pathlib import Path, PureWindowsPath
import re
import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parents[1]
RAW = (BASE / "data" / "raw").resolve()
PROCESSED = BASE / "data" / "processed"

ENTRADA = PROCESSED / "dataset_entrenamiento.csv"
SALIDA = PROCESSED / "dataset_textos_demandas.csv"
REPORTE = PROCESSED / "reporte_extraccion_demandas.csv"

ETIQUETAS = {"ADMISIBLE", "INADMISIBLE", "IMPROCEDENTE"}

def resolver_ruta(valor, caso):
    partes = PureWindowsPath(valor.strip()).parts

    if not partes or any(p in ("", ".", "..") for p in partes):
        raise ValueError("Ruta vacia o no permitida")

    if PureWindowsPath(valor).is_absolute():
        raise ValueError("No se permiten rutas absolutas")

    ruta = (RAW.joinpath(*partes)).resolve()

    if not ruta.is_relative_to(RAW):
        raise ValueError("Ruta fuera de data/raw")

    if not ruta.is_relative_to(RAW / caso.lower()):
        raise ValueError("Documento fuera de la carpeta del caso")

    if ruta.suffix.lower() != ".pdf":
        raise ValueError("Solo se admiten archivos PDF")

    if not re.fullmatch(r"demanda_\d+(?:\.\d+)?\.pdf",
                        ruta.name, re.IGNORECASE):
        raise ValueError("Nombre de documento no permitido")

    if not ruta.is_file():
        raise FileNotFoundError("PDF no encontrado")

    return ruta

def extraer_pdf(ruta):
    partes = []
    paginas_vacias = 0

    with pymupdf.open(ruta) as documento:
        total_paginas = len(documento)

        for pagina in documento:
            texto = pagina.get_text("text").strip()

            if texto:
                partes.append(texto)
            else:
                paginas_vacias += 1

    return "\n\n".join(partes), total_paginas, paginas_vacias

def main():
    if not ENTRADA.exists():
        print("ERROR: No existe dataset_entrenamiento.csv")
        return

    df = pd.read_csv(
        ENTRADA, dtype=str, keep_default_na=False
    )

    requeridas = {
        "caso_id", "demanda_principal",
        "documentos_complementarios", "etiqueta_validada"
    }

    if not requeridas.issubset(df.columns):
        print("ERROR: Faltan columnas requeridas")
        return

    if df["caso_id"].duplicated().any():
        print("ERROR: Hay casos duplicados")
        return

    textos = []
    reporte = []

    for _, fila in df.iterrows():
        caso = fila["caso_id"].strip()
        etiqueta = fila["etiqueta_validada"].strip()

        if etiqueta not in ETIQUETAS:
            continue

        principal = fila["demanda_principal"].strip()
        complementarios = [
            x.strip()
            for x in fila["documentos_complementarios"].split(";")
            if x.strip()
        ]

        documentos = [principal] + complementarios
        fragmentos = []
        paginas = 0
        paginas_vacias = 0
        errores = []

        for indice, nombre in enumerate(documentos):
            try:
                ruta = resolver_ruta(nombre, caso)
                texto, n_paginas, n_vacias = extraer_pdf(ruta)

                paginas += n_paginas
                paginas_vacias += n_vacias

                if not texto.strip():
                    raise ValueError("PDF sin texto extraible")

                tipo = (
                    "DEMANDA_PRINCIPAL"
                    if indice == 0 else "COMPLEMENTARIO"
                )

                fragmentos.append(
                    f"\n[{tipo}]\n{texto}"
                )

            except Exception as error:
                errores.append(
                    f"{nombre}: {type(error).__name__}: {error}"
                )

        estado = "OK" if not errores and not paginas_vacias else (
            "REVISAR"
        )

        reporte.append({
            "caso_id": caso,
            "documentos_esperados": len(documentos),
            "documentos_extraidos": len(fragmentos),
            "paginas": paginas,
            "paginas_sin_texto": paginas_vacias,
            "estado": estado,
            "errores": " | ".join(errores),
        })

        # No crear registros parciales para entrenamiento.
        if estado != "OK":
            continue

        textos.append({
            "caso_id": caso,
            "texto_demanda": "\n\n".join(fragmentos),
            "etiqueta_validada": etiqueta,
        })

    PROCESSED.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        textos,
        columns=["caso_id", "texto_demanda", "etiqueta_validada"]
    ).to_csv(
        SALIDA, index=False, encoding="utf-8-sig"
    )

    pd.DataFrame(reporte).to_csv(
        REPORTE, index=False, encoding="utf-8-sig"
    )

    print("\nEXTRACCION DE DEMANDAS")
    print("=" * 55)
    print(f"Casos esperados: {len(df)}")
    print(f"Casos extraidos completos: {len(textos)}")

    print("\nREPORTE")
    print(
        pd.DataFrame(reporte)[
            ["caso_id", "documentos_extraidos",
             "paginas", "paginas_sin_texto", "estado"]
        ].to_string(index=False)
    )

    print(f"\nDataset: {SALIDA}")
    print(f"Reporte: {REPORTE}")
    print(
        "\nADVERTENCIA: El dataset contiene texto judicial "
        "potencialmente identificable. Mantenerlo local."
    )

if __name__ == "__main__":
    main()
