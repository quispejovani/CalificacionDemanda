
from pathlib import Path, PureWindowsPath
import re
import io

import pandas as pd
import pymupdf
import pytesseract
import os

from dotenv import load_dotenv
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
RAW = (BASE / "data" / "raw").resolve()
PROCESSED = BASE / "data" / "processed"

ENTRADA = PROCESSED / "dataset_entrenamiento.csv"
SALIDA = PROCESSED / "dataset_textos_ocr.csv"
REPORTE = PROCESSED / "reporte_ocr.csv"

load_dotenv(BASE / ".env")

TESSERACT = Path(
    os.environ["TESSERACT_CMD"]
)

if not TESSERACT.is_file():
    raise FileNotFoundError(
        f"No se encontró Tesseract: {TESSERACT}"
    )

pytesseract.pytesseract.tesseract_cmd = str(TESSERACT)

TESSDATA = Path(os.environ["TESSDATA_PREFIX"])

if not TESSDATA.is_dir():
    raise FileNotFoundError(
        f"No se encontró tessdata: {TESSDATA}"
    )

os.environ["TESSDATA_PREFIX"] = str(TESSDATA)

OCR_LANG = os.getenv("OCR_LANG", "spa")


def resolver_ruta(valor, caso):
    partes = PureWindowsPath(valor.strip()).parts

    if (
        not partes
        or PureWindowsPath(valor).is_absolute()
        or any(p in ("", ".", "..") for p in partes)
    ):
        raise ValueError("Ruta no permitida")

    ruta = RAW.joinpath(*partes).resolve()

    if not ruta.is_relative_to(RAW / caso.lower()):
        raise ValueError("Documento fuera del caso")

    if not re.fullmatch(
        r"demanda_\d+(?:\.\d+)?\.pdf",
        ruta.name,
        re.IGNORECASE
    ):
        raise ValueError("Documento no permitido")

    if not ruta.is_file():
        raise FileNotFoundError("Archivo no encontrado")

    return ruta


def extraer_documento(ruta):
    fragmentos = []
    paginas_ocr = 0
    paginas_sin_resultado = 0

    with pymupdf.open(ruta) as pdf:
        total_paginas = len(pdf)

        for numero, pagina in enumerate(pdf, 1):
            texto = pagina.get_text("text").strip()
            metodo = "TEXTO"

            if not texto:
                pix = pagina.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                imagen = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )

                texto = pytesseract.image_to_string(
                    imagen,
                    lang=OCR_LANG,
                    config="--psm 3"
                ).strip()

                metodo = "OCR"
                paginas_ocr += 1

            if not texto:
                paginas_sin_resultado += 1

            fragmentos.append(
                f"[PAGINA {numero} | {metodo}]\n{texto}"
            )

    return (
        "\n\n".join(fragmentos),
        total_paginas,
        paginas_ocr,
        paginas_sin_resultado
    )


def main():
    if not ENTRADA.exists():
        print("ERROR: Falta dataset_entrenamiento.csv")
        return

    df = pd.read_csv(
        ENTRADA,
        dtype=str,
        keep_default_na=False
    )

    textos = []
    reportes = []

    for _, fila in df.iterrows():
        caso = fila["caso_id"].strip()

        documentos = [fila["demanda_principal"].strip()]
        documentos += [
            x.strip()
            for x in fila["documentos_complementarios"].split(";")
            if x.strip()
        ]

        fragmentos = []
        paginas = 0
        paginas_ocr = 0
        sin_resultado = 0
        errores = []

        for nombre in documentos:
            try:
                ruta = resolver_ruta(nombre, caso)

                texto, total, ocr, vacias = extraer_documento(
                    ruta
                )

                paginas += total
                paginas_ocr += ocr
                sin_resultado += vacias

                fragmentos.append(
                    f"[DOCUMENTO {ruta.name}]\n{texto}"
                )

            except Exception as error:
                errores.append(
                    f"{nombre}: {type(error).__name__}: {error}"
                )

        estado = (
            "OK"
            if not errores and sin_resultado == 0
            else "REVISAR"
        )

        reportes.append({
            "caso_id": caso,
            "documentos_esperados": len(documentos),
            "documentos_procesados": len(fragmentos),
            "paginas": paginas,
            "paginas_ocr": paginas_ocr,
            "paginas_sin_resultado": sin_resultado,
            "estado": estado,
            "errores": " | ".join(errores),
        })

        if estado == "OK":
            textos.append({
                "caso_id": caso,
                "texto_demanda": "\n\n".join(fragmentos),
                "etiqueta_validada": fila["etiqueta_validada"],
            })

        print(
            f"{caso}: {estado} | "
            f"paginas OCR: {paginas_ocr}"
        )

    PROCESSED.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        textos,
        columns=[
            "caso_id",
            "texto_demanda",
            "etiqueta_validada"
        ]
    ).to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    resultado = pd.DataFrame(reportes)
    resultado.to_csv(
        REPORTE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nREPORTE OCR")
    print("=" * 75)
    print(
        resultado[
            [
                "caso_id",
                "paginas",
                "paginas_ocr",
                "paginas_sin_resultado",
                "estado"
            ]
        ].to_string(index=False)
    )

    print(f"\nCasos completos: {len(textos)}")
    print(f"Dataset: {SALIDA}")
    print(f"Reporte: {REPORTE}")


if __name__ == "__main__":
    main()
