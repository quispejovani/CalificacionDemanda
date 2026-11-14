
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"

CONSOLIDADO = PROCESSED / "dataset_consolidado.csv"
SALIDA = PROCESSED / "pendientes_revision_juridica.csv"

COLUMNAS = [
    "caso_id",
    "etiqueta_sugerida",
    "materia_validada",
    "tipo_procedimiento",
    "objeto_decision",
    "decision_principal",
    "etiqueta_validada",
    "pagina_evidencia",
    "decision_asignacion_anticipada",
    "revisor",
    "estado_revision",
]

def main():
    if not CONSOLIDADO.exists():
        print("ERROR: Falta dataset_consolidado.csv")
        return

    df = pd.read_csv(
        CONSOLIDADO,
        dtype=str,
        keep_default_na=False
    )

    pendientes = df[
        df["estado_dataset"] == "PENDIENTE_VALIDACION"
    ].copy()

    faltantes = [
        columna for columna in COLUMNAS
        if columna not in pendientes.columns
    ]

    if faltantes:
        print("Columnas faltantes:", faltantes)
        return

    pendientes = pendientes[COLUMNAS]

    # La plantilla es independiente del archivo maestro.
    # No se reemplazan las validaciones existentes.
    if SALIDA.exists():
        print(
            "La plantilla ya existe. "
            "No se sobrescribió."
        )
        return

    pendientes.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nPLANTILLA DE REVISION JURIDICA")
    print("=" * 55)

    print(
        pendientes[
            [
                "caso_id",
                "etiqueta_sugerida",
                "estado_revision",
            ]
        ].to_string(index=False)
    )

    print(f"\nCasos pendientes: {len(pendientes)}")
    print(f"Archivo: {SALIDA}")

if __name__ == "__main__":
    main()
