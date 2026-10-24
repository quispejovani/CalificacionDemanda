
from pathlib import Path
from collections import defaultdict
import re
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

PATRON = re.compile(
    r"^(demanda|auto)_(\d+)(?:\.(\d+))?\.pdf$",
    re.IGNORECASE
)


def construir_dataset():
    casos = defaultdict(
        lambda: {"demanda": None, "anexos": [], "auto": None}
    )

    for archivo in RAW_DIR.rglob("*"):
        if not archivo.is_file():
            continue

        coincidencia = PATRON.fullmatch(archivo.name)

        if not coincidencia:
            continue

        tipo, numero, complemento = coincidencia.groups()
        caso = casos[int(numero)]

        ruta = str(archivo.relative_to(RAW_DIR))

        if tipo.lower() == "auto":
            if caso["auto"] is not None:
                raise ValueError(
                    f"Auto duplicado para caso {numero}"
                )
            caso["auto"] = ruta

        elif complemento is None:
            if caso["demanda"] is not None:
                raise ValueError(
                    f"Demanda principal duplicada: {numero}"
                )
            caso["demanda"] = ruta

        else:
            caso["anexos"].append(ruta)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    salida = OUTPUT_DIR / "dataset_casos.csv"

    columnas = [
        "caso_id",
        "demanda_principal",
        "documentos_complementarios",
        "auto_judicial",
        "estado"
    ]

    with salida.open(
        "w", newline="", encoding="utf-8-sig"
    ) as archivo_csv:

        escritor = csv.DictWriter(
            archivo_csv, fieldnames=columnas
        )
        escritor.writeheader()

        for numero, datos in sorted(casos.items()):
            completo = bool(
                datos["demanda"] and datos["auto"]
            )

            escritor.writerow({
                "caso_id": f"CASO_{numero:03d}",
                "demanda_principal": datos["demanda"] or "",
                "documentos_complementarios": ";".join(
                    sorted(datos["anexos"])
                ),
                "auto_judicial": datos["auto"] or "",
                "estado": (
                    "pendiente_verificacion"
                    if completo else "incompleto"
                )
            })

    print(f"Casos identificados: {len(casos)}")
    print(f"Dataset generado: {salida}")


if __name__ == "__main__":
    construir_dataset()
