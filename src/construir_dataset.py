
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "processed"

textos = pd.read_csv(
    OUT / "textos_demandas_ocr.csv",
    dtype=str
).fillna("")

etiquetas = pd.read_csv(
    OUT / "etiquetas_validadas.csv",
    dtype=str
).fillna("")

# Normalizar identificadores.
textos["caso_id"] = textos["caso_id"].str.upper().str.strip()
etiquetas["caso_id"] = etiquetas["caso_id"].str.upper().str.strip()

# Controlar duplicados de etiquetas.
if etiquetas["caso_id"].duplicated().any():
    raise ValueError("Hay etiquetas duplicadas por expediente.")

# Los casos con varias demandas requieren selección documental.
conteos = textos.groupby("caso_id").size()
casos_multiples = set(conteos[conteos > 1].index)

# Solo los expedientes con una demanda tienen selección inequívoca.
unicos = textos[
    ~textos["caso_id"].isin(casos_multiples)
].copy()

dataset = unicos.merge(
    etiquetas[
        ["caso_id", "etiqueta_inicial", "estado_revision"]
    ],
    on="caso_id",
    how="left"
)

dataset["etiqueta_inicial"] = (
    dataset["etiqueta_inicial"].fillna("")
)
dataset["estado_revision"] = (
    dataset["estado_revision"].fillna("PENDIENTE")
)

dataset["apto_entrenamiento"] = (
    dataset["estado_revision"].eq("VALIDADO")
    & dataset["etiqueta_inicial"].isin(
        ["ADMISIBLE", "INADMISIBLE", "IMPROCEDENTE"]
    )
    & dataset["texto"].str.len().ge(100)
)

# Guardar todos los casos con demanda única.
dataset.to_csv(
    OUT / "dataset_preliminar_101.csv",
    index=False,
    encoding="utf-8-sig"
)

# Guardar documentos de casos con múltiples demandas para revisión.
multiples = textos[
    textos["caso_id"].isin(casos_multiples)
].copy()

multiples[
    ["caso_id", "documento", "caracteres"]
].to_csv(
    OUT / "demandas_multiples_revision.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n========== DATASET ==========")
print("Expedientes originales:", textos["caso_id"].nunique())
print("Expedientes con múltiples demandas:", len(casos_multiples))
print("Expedientes con demanda única:", len(dataset))
print("Aptos para entrenamiento:", dataset["apto_entrenamiento"].sum())

print("\nEtiquetas validadas aptas:")
print(
    dataset.loc[
        dataset["apto_entrenamiento"],
        "etiqueta_inicial"
    ].value_counts().to_string()
)

print("\nArchivos generados:")
print("dataset_preliminar_101.csv")
print("demandas_multiples_revision.csv")
