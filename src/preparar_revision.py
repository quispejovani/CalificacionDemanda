
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "processed"

textos = pd.read_csv(
    OUT / "textos_demandas_ocr.csv", dtype=str
).fillna("")

autos = pd.read_csv(
    OUT / "decisiones_autos_101.csv", dtype=str
).fillna("")

validadas = pd.read_csv(
    OUT / "etiquetas_validadas.csv", dtype=str
).fillna("")

for df in [textos, autos, validadas]:
    df["caso_id"] = df["caso_id"].str.upper().str.strip()

# Resumen de documentos por expediente.
demandas = textos.groupby("caso_id").agg(
    n_demandas=("documento", "count"),
    documentos_demanda=("documento", lambda x: " | ".join(x))
).reset_index()

# Mantener todas las sugerencias, incluso autos múltiples.
resumen_autos = autos.groupby("caso_id").agg(
    n_autos=("documento", "count"),
    documentos_auto=("documento", lambda x: " | ".join(x)),
    etiquetas_sugeridas=("etiqueta_sugerida", lambda x: " | ".join(x))
).reset_index()

revision = demandas.merge(
    resumen_autos, on="caso_id", how="left"
)

revision = revision.merge(
    validadas[
        ["caso_id", "etiqueta_inicial", "estado_revision"]
    ],
    on="caso_id",
    how="left"
)

revision["etiqueta_inicial"] = revision["etiqueta_inicial"].fillna("")
revision["estado_revision"] = revision["estado_revision"].fillna(
    "PENDIENTE"
)

revision["observacion"] = ""

salida = OUT / "matriz_revision_101.csv"
revision.to_csv(
    salida, index=False, encoding="utf-8-sig"
)

print("\n=== MATRIZ DE REVISIÓN ===")
print("Expedientes:", len(revision))
print("Validados:", (revision["estado_revision"] == "VALIDADO").sum())
print("Pendientes:", (revision["estado_revision"] != "VALIDADO").sum())
print("Archivo:", salida)
