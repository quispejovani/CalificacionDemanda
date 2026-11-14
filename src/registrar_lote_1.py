
from pathlib import Path
from datetime import datetime
import pandas as pd
import shutil
import os

BASE = Path(__file__).resolve().parents[1]
DIR = BASE / "data" / "processed"

RUTA_ALCANCE = DIR / "validacion_alcance_101.csv"
RUTA_ETIQUETAS = DIR / "etiquetas_validadas.csv"

CASOS = [
    "CASO_001",
    "CASO_002",
    "CASO_004",
    "CASO_006",
    "CASO_007",
    "CASO_008",
    "CASO_009",
    "CASO_010",
    "CASO_011",
    "CASO_012",
]

def leer(ruta):
    df = pd.read_csv(ruta, dtype=str).fillna("")
    df["caso_id"] = df["caso_id"].str.upper().str.strip()

    if df["caso_id"].duplicated().any():
        raise ValueError(f"Identificadores duplicados: {ruta}")

    return df

def main():
    alcance = leer(RUTA_ALCANCE)
    etiquetas = leer(RUTA_ETIQUETAS)

    if len(alcance) != 101:
        raise ValueError("El inventario de alcance no contiene 101 casos.")

    columnas_alcance = [
        "dentro_alcance",
        "estado_alcance",
        "pretension_validada",
        "procedimiento_validado",
        "motivo_exclusion_codigo",
        "motivo_exclusion",
        "observaciones_revision",
    ]

    columnas_etiquetas = [
        "etiqueta_inicial",
        "estado_revision",
    ]

    for columna in columnas_alcance:
        if columna not in alcance.columns:
            raise ValueError(f"Falta columna de alcance: {columna}")

    for columna in columnas_etiquetas:
        if columna not in etiquetas.columns:
            raise ValueError(f"Falta columna de etiquetas: {columna}")

    # Verificar todos los casos antes de realizar cambios.
    for caso in CASOS:
        filas = alcance[alcance["caso_id"] == caso]

        if len(filas) != 1:
            raise ValueError(f"Expediente no encontrado: {caso}")

        estado = filas.iloc[0]["dentro_alcance"]

        if estado not in ("PENDIENTE", "SI"):
            raise ValueError(
                f"{caso}: conflicto de alcance ({estado})"
            )

        anterior = etiquetas.loc[
            etiquetas["caso_id"] == caso,
            "etiqueta_inicial"
        ]

        if not anterior.empty:
            valor = anterior.iloc[0]
            if valor not in ("", "ADMISIBLE"):
                raise ValueError(
                    f"{caso}: conflicto de etiqueta ({valor})"
                )

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    respaldo_alcance = DIR / (
        f"validacion_alcance_respaldo_lote1_{fecha}.csv"
    )
    respaldo_etiquetas = DIR / (
        f"etiquetas_validadas_respaldo_lote1_{fecha}.csv"
    )

    shutil.copy2(RUTA_ALCANCE, respaldo_alcance)
    shutil.copy2(RUTA_ETIQUETAS, respaldo_etiquetas)

    # Actualizar el alcance.
    for caso in CASOS:
        mask = alcance["caso_id"] == caso

        alcance.loc[mask, "dentro_alcance"] = "SI"
        alcance.loc[mask, "estado_alcance"] = "VALIDADO"
        alcance.loc[
            mask, "pretension_validada"
        ] = "FIJACION_INICIAL_ALIMENTOS"
        alcance.loc[
            mask, "procedimiento_validado"
        ] = "PROCESO_UNICO"

        alcance.loc[mask, "motivo_exclusion_codigo"] = ""
        alcance.loc[mask, "motivo_exclusion"] = ""
        alcance.loc[
            mask, "observaciones_revision"
        ] = "Alcance confirmado por revision experta - lote 1."

    # Registrar etiquetas sin modificar las anteriores.
    nuevas = []

    for caso in CASOS:
        mask = etiquetas["caso_id"] == caso

        if mask.any():
            etiquetas.loc[
                mask, "etiqueta_inicial"
            ] = "ADMISIBLE"
            etiquetas.loc[
                mask, "estado_revision"
            ] = "VALIDADO"
        else:
            registro = {
                columna: ""
                for columna in etiquetas.columns
            }

            registro["caso_id"] = caso
            registro["etiqueta_inicial"] = "ADMISIBLE"
            registro["estado_revision"] = "VALIDADO"

            nuevas.append(registro)

    if nuevas:
        etiquetas = pd.concat(
            [etiquetas, pd.DataFrame(nuevas)],
            ignore_index=True
        )

    # Validaciones antes de guardar.
    conteos = alcance["dentro_alcance"].value_counts()

    if (
        conteos.get("SI", 0) != 14
        or conteos.get("NO", 0) != 11
        or conteos.get("PENDIENTE", 0) != 76
    ):
        raise ValueError(
            f"Conteos inesperados: {conteos.to_dict()}"
        )

    if etiquetas["caso_id"].duplicated().any():
        raise ValueError("Etiquetas duplicadas.")

    # Preparar ambos archivos antes de reemplazar originales.
    temporal_alcance = DIR / f".alcance_{fecha}.tmp"
    temporal_etiquetas = DIR / f".etiquetas_{fecha}.tmp"

    try:
        alcance.to_csv(
            temporal_alcance,
            index=False,
            encoding="utf-8-sig"
        )

        etiquetas.to_csv(
            temporal_etiquetas,
            index=False,
            encoding="utf-8-sig"
        )

        os.replace(temporal_alcance, RUTA_ALCANCE)
        os.replace(temporal_etiquetas, RUTA_ETIQUETAS)

    except Exception:
        # Recuperar ambos originales desde los respaldos.
        shutil.copy2(respaldo_alcance, RUTA_ALCANCE)
        shutil.copy2(respaldo_etiquetas, RUTA_ETIQUETAS)
        raise

    finally:
        temporal_alcance.unlink(missing_ok=True)
        temporal_etiquetas.unlink(missing_ok=True)

    print("\n=== ALCANCE ACTUALIZADO ===")
    print(conteos.to_string())

    print("\n=== ETIQUETAS VALIDADAS ===")
    print(etiquetas["etiqueta_inicial"].value_counts().to_string())

    print("\n=== CASOS DEL LOTE 1 ===")
    print(
        etiquetas[
            etiquetas["caso_id"].isin(CASOS)
        ][["caso_id", "etiqueta_inicial", "estado_revision"]]
        .sort_values("caso_id")
        .to_string(index=False)
    )

    print("\nRespaldos:")
    print(respaldo_alcance)
    print(respaldo_etiquetas)

if __name__ == "__main__":
    main()
