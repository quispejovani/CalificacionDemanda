
from pathlib import Path
import csv
import pymupdf

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def extraer_pdf(ruta_pdf):
    paginas = []

    with pymupdf.open(ruta_pdf) as documento:
        for numero, pagina in enumerate(documento, start=1):
            texto = pagina.get_text("text")

            paginas.append({
                "pagina": numero,
                "texto": texto,
                "caracteres": len(texto),
                "palabras": len(texto.split())
            })

    return paginas


def procesar_pdfs():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    archivos = sorted(
        p for p in RAW_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() == ".pdf"
    )

    registros = []

    for archivo in archivos:
        try:
            paginas = extraer_pdf(archivo)

            registros.append({
                "archivo": str(archivo.relative_to(RAW_DIR)),
                "paginas": len(paginas),
                "caracteres": sum(p["caracteres"] for p in paginas),
                "palabras": sum(p["palabras"] for p in paginas),
                "paginas_sin_texto": sum(
                    not p["texto"].strip() for p in paginas
                ),
                "estado": "procesado"
            })

            print(f"OK: {archivo.name}")

        except Exception as error:
            registros.append({
                "archivo": str(archivo.relative_to(RAW_DIR)),
                "paginas": 0,
                "caracteres": 0,
                "palabras": 0,
                "paginas_sin_texto": 0,
                "estado": f"error: {type(error).__name__}"
            })

            print(f"ERROR: {archivo.name}: {type(error).__name__}")

    salida = PROCESSED_DIR / "inventario_documentos.csv"

    columnas = [
        "archivo", "paginas", "caracteres",
        "palabras", "paginas_sin_texto", "estado"
    ]

    with salida.open("w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(registros)

    print(f"\nPDF encontrados: {len(archivos)}")
    print(f"Inventario generado: {salida}")


if __name__ == "__main__":
    procesar_pdfs()
