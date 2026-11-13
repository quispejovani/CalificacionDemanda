
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "processed"

autos = pd.read_csv(
    OUT / "resolutivas_candidatas.csv",
    dtype=str
).fillna("")

validadas = pd.read_csv(
    OUT / "etiquetas_validadas.csv",
    dtype=str
).fillna("")

for df in (autos, validadas):
    df["caso_id"] = df["caso_id"].str.upper().str.strip()

if validadas["caso_id"].duplicated().any():
    raise ValueError("Hay etiquetas validadas duplicadas.")

registros = []

for caso_id, grupo in autos.groupby("caso_id"):
    validacion = validadas[
        validadas["caso_id"] == caso_id
    ]

    esta_validado = (
        not validacion.empty
        and validacion.iloc[0]["estado_revision"].upper()
        == "VALIDADO"
    )

    etiqueta_validada = (
        validacion.iloc[0]["etiqueta_inicial"]
        if esta_validado else ""
    )

    # No inferimos cronología únicamente por el nombre del archivo.
    if len(grupo) == 1:
        sugerencia = grupo.iloc[0]["sugerencia"]
        estado = "PENDIENTE_VALIDACION"
    else:
        sugerencia = "REQUIERE_REVISION"
        estado = "VERIFICAR_CRONOLOGIA"

    if esta_validado:
        estado = "VALIDADO"

    registros.append({
        "caso_id": caso_id,
        "n_autos": len(grupo),
        "documentos_auto": " | ".join(grupo["auto"]),
        "sugerencias_autos": " | ".join(grupo["sugerencia"]),
        "sugerencia_inicial": sugerencia,
        "etiqueta_validada": etiqueta_validada,
        "estado": estado
    })

df = pd.DataFrame(registros)

salida = OUT / "pre_etiquetas_101.csv"
df.to_csv(
    salida, index=False, encoding="utf-8-sig"
)

print("\n=== PREETIQUETADO POR EXPEDIENTE ===")
print("Expedientes:", len(df))

print("\nEstados:")
print(df["estado"].value_counts().to_string())

print("\nSugerencias:")
print(df["sugerencia_inicial"].value_counts().to_string())

print("\nEtiquetas validadas:")
print(
    df.loc[
        df["estado"] == "VALIDADO",
        "etiqueta_validada"
    ].value_counts().to_string()
)

print("\nArchivo:", salida)
