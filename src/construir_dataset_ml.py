
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"

CASOS = PROCESSED / "dataset_casos.csv"
CONSOLIDADO = PROCESSED / "dataset_consolidado.csv"
SALIDA = PROCESSED / "dataset_entrenamiento.csv"

ETIQUETAS = {
    "ADMISIBLE",
    "INADMISIBLE",
    "IMPROCEDENTE",
}

def main():
    for archivo in [CASOS, CONSOLIDADO]:
        if not archivo.exists():
            print(f"ERROR: Falta {archivo.name}")
            return

    casos = pd.read_csv(
        CASOS, dtype=str, keep_default_na=False
    )

    validacion = pd.read_csv(
        CONSOLIDADO,
        dtype=str,
        keep_default_na=False
    )

    if (
        casos["caso_id"].duplicated().any()
        or validacion["caso_id"].duplicated().any()
    ):
        print("ERROR: Hay identificadores duplicados.")
        return

    aptos = validacion[
        (validacion["estado_dataset"] == "APTO_PARA_DATASET")
        &
        (validacion["etiqueta_validada"].isin(ETIQUETAS))
    ][["caso_id", "etiqueta_validada"]]

    dataset = casos.merge(
        aptos,
        on="caso_id",
        how="inner",
        validate="one_to_one"
    )

    if len(dataset) != len(aptos):
        print(
            "ERROR: Hay casos validados sin "
            "correspondencia en dataset_casos.csv."
        )
        return

    # Se conserva la estructura documental existente.
    # No se incorporan columnas del auto judicial.
    columnas_excluidas = [
        c for c in dataset.columns
        if (
            "auto" in c.lower()
            or "resolucion" in c.lower()
        )
    ]

    dataset = dataset.drop(
        columns=columnas_excluidas
    )

    SALIDA.parent.mkdir(
        parents=True, exist_ok=True
    )

    dataset.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nDATASET DE ENTRENAMIENTO")
    print("=" * 55)
    print(f"Casos: {len(dataset)}")

    print("\nDistribucion:")
    print(
        dataset["etiqueta_validada"].value_counts()
    )

    print("\nColumnas:")
    for columna in dataset.columns:
        print("-", columna)

    print(f"\nArchivo generado: {SALIDA}")

if __name__ == "__main__":
    main()
