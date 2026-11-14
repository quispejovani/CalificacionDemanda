
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DIR = BASE / "data" / "processed"

OCR = DIR / "textos_demandas_ocr.csv"
SELECCION = DIR / "seleccion_documentos_demanda.csv"
ALCANCE = DIR / "validacion_alcance_101.csv"
ETIQUETAS = DIR / "etiquetas_validadas.csv"

SALIDA = DIR / "dataset_filtrado_101.csv"
REPORTE = DIR / "reporte_dataset_filtrado.csv"

def normalizar_caso(df):
    df["caso_id"] = df["caso_id"].str.upper().str.strip()
    return df

def main():
    ocr = normalizar_caso(
        pd.read_csv(OCR, dtype=str).fillna("")
    )
    seleccion = normalizar_caso(
        pd.read_csv(SELECCION, dtype=str).fillna("")
    )
    alcance = normalizar_caso(
        pd.read_csv(ALCANCE, dtype=str).fillna("")
    )
    etiquetas = normalizar_caso(
        pd.read_csv(ETIQUETAS, dtype=str).fillna("")
    )

    # Documentos seleccionados manualmente.
    principales = seleccion[
        seleccion["usar_texto_modelo"] == "SI"
    ][["caso_id", "documento"]].copy()

    if principales["caso_id"].duplicated().any():
        raise ValueError("Hay casos con más de una demanda principal.")

    # Para los casos sin selección manual, usar solo si
    # existe exactamente un documento de demanda.
    casos_seleccionados = set(principales["caso_id"])

    restantes = ocr[
        ~ocr["caso_id"].isin(casos_seleccionados)
    ]

    conteos = restantes.groupby("caso_id").size()
    casos_unicos = set(conteos[conteos == 1].index)

    automaticos = restantes[
        restantes["caso_id"].isin(casos_unicos)
    ][["caso_id", "documento"]].copy()

    documentos = pd.concat(
        [principales, automaticos],
        ignore_index=True
    )

    if documentos["caso_id"].duplicated().any():
        raise ValueError("Selección documental duplicada.")

    
    # Conservar todos los expedientes del inventario de alcance,
    # aunque no tengan demanda principal seleccionada.
    documentos = alcance[["caso_id"]].merge(
        documentos,
        on="caso_id",
        how="left",
        validate="one_to_one"
    )

    documentos["documento"] = documentos["documento"].fillna("")
    
    # Incorporar el texto de la demanda principal.
    dataset = documentos.merge(
        ocr,
        on=["caso_id", "documento"],
        how="left",
        validate="one_to_one"
    )

    # Incorporar validación del alcance.
    dataset = dataset.merge(
        alcance[
            ["caso_id", "dentro_alcance",
             "estado_alcance", "pretension_validada",
             "procedimiento_validado"]
        ],
        on="caso_id",
        how="left",
        validate="one_to_one"
    )

    # Incorporar etiquetas judiciales validadas.
    dataset = dataset.merge(
        etiquetas[
            ["caso_id", "etiqueta_inicial"]
        ],
        on="caso_id",
        how="left",
        validate="one_to_one"
    )

    dataset["etiqueta_inicial"] = (
        dataset["etiqueta_inicial"].fillna("")
    )

    dataset["dentro_alcance"] = (
        dataset["dentro_alcance"].fillna("PENDIENTE")
    )

    dataset["apto_entrenamiento"] = (
        (dataset["dentro_alcance"] == "SI")
        & dataset["etiqueta_inicial"].isin([
            "ADMISIBLE",
            "INADMISIBLE",
            "IMPROCEDENTE"
        ])
        & (dataset["documento"].str.strip() != "")
        & (dataset["texto"].str.strip() != "")
    )

    # Verificar que no haya documentos sin texto.
    dataset["caracteres_texto"] = (
        dataset["texto"].str.len()
    )

    # No sobrescribir resultados anteriores.
    for archivo in [SALIDA, REPORTE]:
        if archivo.exists():
            raise FileExistsError(
                f"Ya existe {archivo}. Haz una copia "
                "antes de volver a ejecutar."
            )

    dataset.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    reporte = dataset[
        ["caso_id", "documento", "dentro_alcance",
         "etiqueta_inicial", "caracteres_texto",
         "apto_entrenamiento"]
    ].copy()

    reporte.to_csv(
        REPORTE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n=== DATASET FILTRADO ===")
    print("Expedientes:", len(dataset))

    print("\n=== ALCANCE ===")
    print(dataset["dentro_alcance"].value_counts().to_string())

    print("\n=== APTOS PARA ENTRENAMIENTO ===")
    print(dataset["apto_entrenamiento"].value_counts().to_string())

    print("\n=== ETIQUETAS APTAS ===")
    print(
        dataset.loc[
            dataset["apto_entrenamiento"],
            "etiqueta_inicial"
        ].value_counts().to_string()
    )

    print("\nArchivos generados:")
    print(SALIDA)
    print(REPORTE)

if __name__ == "__main__":
    main()
