
from pathlib import Path
from datetime import datetime
import shutil
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RUTA = BASE / "data" / "processed" / "validacion_alcance_101.csv"

VALIDACIONES = {
    "CASO_018": {
        "dentro_alcance": "SI",
        "estado_alcance": "VALIDADO",
        "pretension_validada": "FIJACION_INICIAL_ALIMENTOS",
        "procedimiento_validado": "PROCESO_UNICO",
        "motivo_exclusion_codigo": "",
        "motivo_exclusion": "",
        "observaciones_revision": "Alcance confirmado por revision experta."
    },
    "CASO_030": {
        "dentro_alcance": "NO",
        "estado_alcance": "EXCLUSION_CONFIRMADA",
        "pretension_validada": "",
        "procedimiento_validado": "PROCESO_SUMARISIMO",
        "motivo_exclusion_codigo": "PROCESO_SUMARISIMO",
        "motivo_exclusion": "Demanda tramitada en proceso sumarisimo.",
        "observaciones_revision": "Exclusion confirmada por revision experta."
    },
    "CASO_032": {
        "dentro_alcance": "NO",
        "estado_alcance": "EXCLUSION_CONFIRMADA",
        "pretension_validada": "OTRA_PRETENSION",
        "procedimiento_validado": "",
        "motivo_exclusion_codigo": "OTRA_PRETENSION",
        "motivo_exclusion": "Pretension distinta de fijacion inicial de alimentos.",
        "observaciones_revision": "Tipo especifico de pretension no informado."
    },
    "CASO_046": {
        "dentro_alcance": "SI",
        "estado_alcance": "VALIDADO",
        "pretension_validada": "FIJACION_INICIAL_ALIMENTOS",
        "procedimiento_validado": "PROCESO_UNICO",
        "motivo_exclusion_codigo": "",
        "motivo_exclusion": "",
        "observaciones_revision": "Alcance confirmado por revision experta."
    }
}

def main():
    df = pd.read_csv(RUTA, dtype=str).fillna("")
    df["caso_id"] = df["caso_id"].str.upper().str.strip()

    if df["caso_id"].duplicated().any():
        raise ValueError("Existen casos duplicados.")

    if len(df) != 101:
        raise ValueError(f"Se esperaban 101 casos; encontrados: {len(df)}")

    for caso, cambios in VALIDACIONES.items():
        if (df["caso_id"] == caso).sum() != 1:
            raise ValueError(f"No se encontro exactamente una fila: {caso}")

        faltantes = set(cambios) - set(df.columns)
        if faltantes:
            raise ValueError(f"Columnas faltantes: {faltantes}")

    # Respaldo antes de modificar.
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo = RUTA.with_name(
        f"validacion_alcance_respaldo_{fecha}.csv"
    )
    shutil.copy2(RUTA, respaldo)

    for caso, cambios in VALIDACIONES.items():
        mascara = df["caso_id"] == caso

        for columna, valor in cambios.items():
            df.loc[mascara, columna] = valor

    # Validar el resultado antes de guardar.
    conteo = df["dentro_alcance"].value_counts()

    if (
        conteo.get("SI", 0) != 4
        or conteo.get("NO", 0) != 11
        or conteo.get("PENDIENTE", 0) != 86
    ):
        raise ValueError(
            f"Conteos inesperados: {conteo.to_dict()}. "
            f"El respaldo esta en {respaldo}"
        )

    df.to_csv(RUTA, index=False, encoding="utf-8-sig")

    print("\n=== RESUMEN ACTUALIZADO ===")
    print(conteo.to_string())

    print("\n=== CASOS ACTUALIZADOS ===")
    print(
        df[df["caso_id"].isin(VALIDACIONES)][
            ["caso_id", "dentro_alcance",
             "procedimiento_validado",
             "motivo_exclusion_codigo"]
        ].to_string(index=False)
    )

    print("\nRespaldo:", respaldo)
    print("Archivo actualizado:", RUTA)
    print("Las etiquetas judiciales NO fueron modificadas.")

if __name__ == "__main__":
    main()
