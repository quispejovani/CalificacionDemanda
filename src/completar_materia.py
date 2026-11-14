
from pathlib import Path
from datetime import datetime
import shutil
import pandas as pd

BASE = Path(__file__).resolve().parents[1]

ARCHIVO = (
    BASE / "data" / "processed"
    / "validacion_juridica.csv"
)

def main():
    if not ARCHIVO.exists():
        raise FileNotFoundError(ARCHIVO)

    df = pd.read_csv(
        ARCHIVO,
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False
    )

    mascara = (
        df["tipo_procedimiento"]
        .str.strip()
        .str.upper()
        .eq("DEMANDA_ALIMENTOS")
        &
        df["materia_validada"]
        .str.strip()
        .eq("")
    )

    print("Casos que se actualizarán:")
    print(
        df.loc[mascara, "caso_id"]
        .to_string(index=False)
    )

    cantidad = int(mascara.sum())
    print(f"\nTotal: {cantidad}")

    if cantidad == 0:
        print("No hay registros pendientes.")
        return

    respuesta = input(
        "\n¿Confirmas que todos son demandas "
        "de alimentos? (SI/NO): "
    ).strip().upper()

    if respuesta != "SI":
        print("Operación cancelada.")
        return

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo = ARCHIVO.with_name(
        f"validacion_juridica_backup_{fecha}.csv"
    )

    shutil.copy2(ARCHIVO, respaldo)

    df.loc[mascara, "materia_validada"] = "ALIMENTOS"

    df.to_csv(
        ARCHIVO,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nRegistros actualizados: {cantidad}")
    print(f"Copia de seguridad: {respaldo}")
    print(f"Archivo actualizado: {ARCHIVO}")

if __name__ == "__main__":
    main()
