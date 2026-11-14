
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"

inventarios = sorted(
    PROCESSED.glob("inventario_ingesta_*.csv")
)

if not inventarios:
    raise FileNotFoundError("No se encontró el inventario.")

ruta = inventarios[-1]
df = pd.read_csv(ruta)

df["paginas"] = pd.to_numeric(
    df["paginas"], errors="coerce"
).fillna(0)

df["paginas_sin_texto"] = pd.to_numeric(
    df["paginas_sin_texto"], errors="coerce"
).fillna(0)

resumen = df.pivot_table(
    index="caso_id",
    columns="tipo_documento",
    values="documento",
    aggfunc="count",
    fill_value=0
)

for columna in ["DEMANDA", "AUTO"]:
    if columna not in resumen.columns:
        resumen[columna] = 0

resumen["par_completo"] = (
    (resumen["DEMANDA"] >= 1) &
    (resumen["AUTO"] >= 1)
)

resumen["requiere_revision"] = (
    (resumen["DEMANDA"] != 1) |
    (resumen["AUTO"] != 1)
)

sin_texto = df.groupby("tipo_documento")[
    ["paginas", "paginas_sin_texto"]
].sum()

print("\n=== DIAGNÓSTICO ===")
print("Expedientes:", len(resumen))
print("Con demanda y auto:", resumen["par_completo"].sum())
print("Sin par completo:", (~resumen["par_completo"]).sum())
print("Con cantidad de documentos a revisar:",
      resumen["requiere_revision"].sum())

print("\n=== PÁGINAS POR TIPO ===")
print(sin_texto.to_string())

print("\n=== CASOS A REVISAR ===")
print(
    resumen[resumen["requiere_revision"]].to_string()
)

salida = PROCESSED / "diagnostico_101_casos.csv"
resumen.reset_index().to_csv(
    salida, index=False, encoding="utf-8-sig"
)

print("\nGuardado en:", salida)
