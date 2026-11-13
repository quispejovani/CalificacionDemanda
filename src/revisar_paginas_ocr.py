
from pathlib import Path, PureWindowsPath
import io

import pandas as pd
import pymupdf
import pytesseract
from PIL import Image
import os

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

TESSERACT = BASE / "tools" / "tesseract"

pytesseract.pytesseract.tesseract_cmd = str(
    TESSERACT / "tesseract.exe"
)

os.environ["TESSDATA_PREFIX"] = str(
    TESSERACT / "tessdata"
)

ENTRADA = PROCESSED / "dataset_entrenamiento.csv"
SALIDA = PROCESSED / "paginas_pendientes_ocr.csv"


def main():
    df = pd.read_csv(
        ENTRADA,
        dtype=str,
        keep_default_na=False
    )

    pendientes = []

    for _, fila in df.iterrows():
        caso = fila["caso_id"]

        documentos = [fila["demanda_principal"]]
        documentos += [
            x.strip()
            for x in fila["documentos_complementarios"].split(";")
            if x.strip()
        ]

        for nombre in documentos:
            ruta = RAW.joinpath(
                *PureWindowsPath(nombre).parts
            )

            with pymupdf.open(ruta) as pdf:
                for numero, pagina in enumerate(pdf, 1):
                    texto = pagina.get_text("text").strip()

                    if texto:
                        continue

                    pix = pagina.get_pixmap(
                        matrix=pymupdf.Matrix(2, 2),
                        alpha=False
                    )

                    imagen = Image.open(
                        io.BytesIO(pix.tobytes("png"))
                    )

                    texto_ocr = pytesseract.image_to_string(
                        imagen,
                        lang="spa",
                        config="--psm 3"
                    ).strip()

                    if not texto_ocr:
                        pendientes.append({
                            "caso_id": caso,
                            "documento": nombre,
                            "pagina": numero,
                            "ancho": pix.width,
                            "alto": pix.height,
                            "estado": "SIN_TEXTO_OCR",
                            "revision_manual": "PENDIENTE"
                        })

    resultado = pd.DataFrame(
        pendientes,
        columns=[
            "caso_id",
            "documento",
            "pagina",
            "ancho",
            "alto",
            "estado",
            "revision_manual"
        ]
    )

    resultado.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nPAGINAS PENDIENTES DE OCR")
    print("=" * 75)

    if resultado.empty:
        print("No hay paginas pendientes.")
    else:
        print(resultado.to_string(index=False))

    print(f"\nTotal pendientes: {len(resultado)}")
    print(f"Archivo: {SALIDA}")


if __name__ == "__main__":
    main()
