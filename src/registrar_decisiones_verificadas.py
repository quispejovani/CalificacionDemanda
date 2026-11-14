
from pathlib import Path
from datetime import datetime
import shutil

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ARCHIVO = BASE / "data" / "processed" / "validacion_juridica.csv"

ADMISIBLES = {
    "CASO_001", "CASO_002", "CASO_004",
    "CASO_006", "CASO_007", "CASO_008",
    "CASO_009", "CASO_010", "CASO_011"
}

INADMISIBLES = {"CASO_005"}

def main():
    if not ARCHIVO.exists():
        print("ERROR: No existe validacion_juridica.csv")
        return

    df = pd.read_csv(
        ARCHIVO,
        dtype=str,
        keep_default_na=False
    )

    if df["caso_id"].duplicated().any():
        print("ERROR: Existen casos duplicados.")
        return

    cambios = 0

    for indice, fila in df.iterrows():
        caso = fila["caso_id"].strip()

        if caso in ADMISIBLES:
            etiqueta = "ADMISIBLE"
            decision = "ADMITIR_DEMANDA"

        elif caso in INADMISIBLES:
            etiqueta = "INADMISIBLE"
            decision = "DECLARAR_INADMISIBLE"

        else:
            continue

        valores = {
            "materia_validada": "ALIMENTOS",
            "tipo_procedimiento": "DEMANDA_ALIMENTOS",
            "objeto_decision": "DEMANDA_ALIMENTOS",
            "decision_principal": decision,
            "etiqueta_validada": etiqueta,
        }

        for columna, valor in valores.items():
            actual = df.at[indice, columna].strip()

            if actual not in ("", valor):
                print(
                    f"CONFLICTO {caso}, {columna}: "
                    f"{actual} != {valor}"
                )
                continue

            if actual != valor:
                df.at[indice, columna] = valor
                cambios += 1

        if df.at[indice, "estado_revision"] != "VALIDADO":
            df.at[indice, "estado_revision"] = "EN_REVISION"

    if cambios == 0:
        print("No se encontraron campos nuevos.")
        return

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo = ARCHIVO.with_name(
        f"validacion_juridica_backup_{marca}.csv"
    )

    shutil.copy2(ARCHIVO, respaldo)

    df.to_csv(
        ARCHIVO,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nDECISIONES REGISTRADAS")
    print("=" * 55)
    print(
        df[
            [
                "caso_id",
                "decision_principal",
                "etiqueta_validada",
                "estado_revision"
            ]
        ].to_string(index=False)
    )
    print(f"\nCampos actualizados: {cambios}")
    print(f"Respaldo: {respaldo}")

if __name__ == "__main__":
    main()
