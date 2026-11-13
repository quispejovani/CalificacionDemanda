
from pathlib import Path
from datetime import datetime

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ARCHIVO = BASE / "data" / "processed" / "validacion_juridica.csv"

CASOS_OTORGADOS = {
    "CASO_001",
    "CASO_002",
    "CASO_004",
    "CASO_006",
    "CASO_007",
    "CASO_008",
    "CASO_009",
    "CASO_010",
    "CASO_011",
}

def main():
    if not ARCHIVO.exists():
        print("ERROR: No existe validacion_juridica.csv")
        return

    df = pd.read_csv(
        ARCHIVO,
        dtype=str,
        keep_default_na=False
    )

    columna = "decision_asignacion_anticipada"

    if columna not in df.columns:
        df[columna] = "PENDIENTE"

    for indice, fila in df.iterrows():
        caso = fila["caso_id"].strip()

        if caso in CASOS_OTORGADOS:
            actual = str(df.at[indice, columna]).strip()

            if actual in ("", "PENDIENTE", "OTORGADA"):
                df.at[indice, columna] = "OTORGADA"
            else:
                print(
                    f"Conflicto en {caso}: "
                    f"valor existente {actual}. "
                    "No se modificó."
                )

        elif caso == "CASO_003":
            actual = str(df.at[indice, columna]).strip()
            if actual in ("", "PENDIENTE", "NO_APLICA"):
                df.at[indice, columna] = "NO_APLICA"

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo = ARCHIVO.with_name(
        f"validacion_juridica_backup_{marca}.csv"
    )

    respaldo.write_bytes(ARCHIVO.read_bytes())

    df.to_csv(
        ARCHIVO,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nREGISTRO DE ASIGNACION ANTICIPADA")
    print("=" * 50)

    print(
        df[
            ["caso_id", columna]
        ].to_string(index=False)
    )

    print(f"\nRespaldo: {respaldo}")
    print(f"Actualizado: {ARCHIVO}")

if __name__ == "__main__":
    main()
