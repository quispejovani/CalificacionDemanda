
from pathlib import Path
import csv

BASE = Path(__file__).resolve().parent.parent
CARPETA = BASE / "data" / "processed"

ENTRADA = CARPETA / "revision_autos.csv"
SALIDA = CARPETA / "validacion_juridica.csv"

CAMPOS = [
    "caso_id",
    "auto",
    "palabras_clave",
    "materia_validada",
    "tipo_procedimiento",
    "objeto_decision",
    "decision_principal",
    "etiqueta_validada",
    "pagina_evidencia",
    "observaciones",
    "revisor",
    "estado_revision",
]

def ejecutar():
    if SALIDA.exists():
        raise FileExistsError(
            f"El archivo ya existe: {SALIDA}. "
            "No se sobrescribira una revision anterior."
        )

    with ENTRADA.open(
        newline="", encoding="utf-8-sig"
    ) as archivo:
        registros = list(csv.DictReader(archivo))

    with SALIDA.open(
        "w", newline="", encoding="utf-8-sig"
    ) as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=CAMPOS
        )
        escritor.writeheader()

        for registro in registros:
            escritor.writerow({
                "caso_id": registro["caso_id"],
                "auto": registro["auto"],
                "palabras_clave": registro["palabras_clave"],
                "materia_validada": "",
                "tipo_procedimiento": "",
                "objeto_decision": "",
                "decision_principal": "",
                "etiqueta_validada": "",
                "pagina_evidencia": "",
                "observaciones": "",
                "revisor": "",
                "estado_revision": "PENDIENTE"
            })

    print(f"Casos preparados: {len(registros)}")
    print(f"Archivo generado: {SALIDA}")

if __name__ == "__main__":
    ejecutar()
