
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"

REVISION = PROCESSED / "revision_autos_mejorada.csv"
VALIDACION = PROCESSED / "validacion_juridica.csv"
SALIDA = PROCESSED / "dataset_consolidado.csv"

ETIQUETAS = {
    "ADMISIBLE",
    "INADMISIBLE",
    "IMPROCEDENTE",
}

def main():
    if not REVISION.exists():
        print("ERROR: Falta revision_autos_mejorada.csv")
        return

    if not VALIDACION.exists():
        print("ERROR: Falta validacion_juridica.csv")
        return

    revision = pd.read_csv(
        REVISION,
        dtype=str,
        keep_default_na=False
    )

    validacion = pd.read_csv(
        VALIDACION,
        dtype=str,
        keep_default_na=False
    )

    if (
        revision["caso_id"].duplicated().any()
        or validacion["caso_id"].duplicated().any()
    ):
        print("ERROR: Existen caso_id duplicados.")
        return

    columnas_revision = [
        "caso_id",
        "etiqueta_sugerida",
        "requiere_subsanacion",
        "alertas",
    ]

    columnas_validacion = [
        "caso_id",
        "materia_validada",
        "tipo_procedimiento",
        "objeto_decision",
        "decision_principal",
        "etiqueta_validada",
        "pagina_evidencia",
        "revisor",
        "estado_revision",
        "decision_asignacion_anticipada",
    ]

    # Compatibilidad con archivos anteriores.
    if (
        "decision_asignacion_anticipada"
        not in validacion.columns
    ):
        validacion[
            "decision_asignacion_anticipada"
        ] = "PENDIENTE"

    faltantes = (
        [c for c in columnas_revision
         if c not in revision.columns]
        +
        [c for c in columnas_validacion
         if c not in validacion.columns]
    )

    if faltantes:
        print("ERROR: Columnas faltantes:", faltantes)
        return

    df = revision[columnas_revision].merge(
        validacion[columnas_validacion],
        on="caso_id",
        how="outer",
        validate="one_to_one",
        indicator=True
    )

    def evaluar(fila):
        if fila["_merge"] != "both":
            return "REVISAR_VINCULACION"

        if (
            fila["tipo_procedimiento"]
            == "CONCILIACION_ALIMENTOS"
            or fila["etiqueta_validada"]
            == "FUERA_ALCANCE"
        ):
            return "FUERA_ALCANCE"

        if fila["tipo_procedimiento"] != "DEMANDA_ALIMENTOS":
            return "REVISAR_PROCEDIMIENTO"

        if fila["materia_validada"] != "ALIMENTOS":
            return "PENDIENTE_MATERIA"

        if fila["estado_revision"] != "VALIDADO":
            return "PENDIENTE_VALIDACION"

        if fila["etiqueta_validada"] not in ETIQUETAS:
            return "PENDIENTE_ETIQUETA"

        if not fila["pagina_evidencia"].strip():
            return "PENDIENTE_EVIDENCIA"

        if not fila["revisor"].strip():
            return "PENDIENTE_REVISOR"

        if fila["objeto_decision"] != "DEMANDA_ALIMENTOS":
            return "REVISAR_OBJETO_DECISION"

        return "APTO_PARA_DATASET"

    df["estado_dataset"] = df.apply(
        evaluar, axis=1
    )

    df = df.drop(columns=["_merge"])

    SALIDA.parent.mkdir(
        parents=True, exist_ok=True
    )

    df.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nDATASET CONSOLIDADO")
    print("=" * 65)

    print(
        df[
            [
                "caso_id",
                "etiqueta_sugerida",
                "etiqueta_validada",
                "decision_asignacion_anticipada",
                "estado_dataset",
            ]
        ].to_string(index=False)
    )

    print("\nRESUMEN")
    print("=" * 65)

    print(
        df["estado_dataset"].value_counts()
    )

    print(f"\nArchivo: {SALIDA}")

if __name__ == "__main__":
    main()
