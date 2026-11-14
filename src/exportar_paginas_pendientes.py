
from pathlib import Path, PureWindowsPath
import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parents[1]
RAW = (BASE / "data" / "raw").resolve()
PROCESSED = BASE / "data" / "processed"

ENTRADA = PROCESSED / "paginas_pendientes_ocr.csv"
DESTINO = PROCESSED / "revision_visual_ocr"


def main():
    df = pd.read_csv(ENTRADA, dtype=str)
    DESTINO.mkdir(parents=True, exist_ok=True)

    generadas = 0

    for _, fila in df.iterrows():
        caso = fila["caso_id"]
        documento = fila["documento"]
        pagina_numero = int(fila["pagina"])

        ruta = RAW.joinpath(
            *PureWindowsPath(documento).parts
        ).resolve()

        if not ruta.is_relative_to(RAW):
            raise ValueError("Ruta fuera de data/raw")

        if not ruta.is_file():
            print(f"No encontrado: {documento}")
            continue

        carpeta_caso = DESTINO / caso
        carpeta_caso.mkdir(parents=True, exist_ok=True)

        with pymupdf.open(ruta) as pdf:
            if not 1 <= pagina_numero <= len(pdf):
                print(f"Pagina invalida: {documento}")
                continue

            pagina = pdf[pagina_numero - 1]

            imagen = pagina.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            nombre = (
                f"{ruta.stem}_pagina_{pagina_numero:03d}.png"
            )

            salida = carpeta_caso / nombre

            imagen.save(str(salida))
            generadas += 1

            print(f"Generada: {salida}")

    print("\nEXPORTACION FINALIZADA")
    print(f"Imagenes generadas: {generadas}")
    print(f"Carpeta: {DESTINO}")


if __name__ == "__main__":
    main()
