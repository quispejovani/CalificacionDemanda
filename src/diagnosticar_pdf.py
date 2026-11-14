
from pathlib import Path, PureWindowsPath
import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

ENTRADA = PROCESSED / "dataset_entrenamiento.csv"
SALIDA = PROCESSED / "diagnostico_pdf.csv"


def main():
    df = pd.read_csv(
        ENTRADA,
        dtype=str,
        keep_default_na=False
    )

    registros = []

    for _, fila in df.iterrows():
        caso = fila["caso_id"]

        documentos = [
            fila["demanda_principal"]
        ]

        documentos += [
            x.strip()
            for x in fila["documentos_complementarios"].split(";")
            if x.strip()
        ]

        for nombre in documentos:
            partes = PureWindowsPath(nombre).parts
            ruta = RAW.joinpath(*partes)

            if not ruta.is_file():
                registros.append({
                    "caso_id": caso,
                    "documento": nombre,
                    "paginas": 0,
                    "paginas_sin_texto": "",
                    "estado": "NO_ENCONTRADO",
                })
                continue

            try:
                with pymupdf.open(ruta) as pdf:
                    sin_texto = [
                        numero
                        for numero, pagina in enumerate(pdf, 1)
                        if not pagina.get_text("text").strip()
                    ]

                    registros.append({
                        "caso_id": caso,
                        "documento": nombre,
                        "paginas": len(pdf),
                        "paginas_sin_texto": ";".join(
                            map(str, sin_texto)
                        ),
                        "estado": (
                            "REQUIERE_REVISION"
                            if sin_texto else "OK"
                        ),
                    })

            except Exception as error:
                registros.append({
                    "caso_id": caso,
                    "documento": nombre,
                    "paginas": 0,
                    "paginas_sin_texto": "",
                    "estado": f"ERROR_{type(error).__name__}",
                })

    resultado = pd.DataFrame(registros)

    resultado.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nDIAGNOSTICO DE PDF")
    print("=" * 75)
    print(resultado.to_string(index=False))
    print(f"\nArchivo: {SALIDA}")


if __name__ == "__main__":
    main()
