
from pathlib import Path
from datetime import datetime
import shutil

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"

VALIDACION = PROCESSED / "validacion_juridica.csv"
PROPUESTAS = PROCESSED / "propuesta_paginas_evidencia.csv"

def main():
    if not VALIDACION.exists() or not PROPUESTAS.exists():
        print("ERROR: Faltan archivos de validacion.")
        return

    df = pd.read_csv(
        VALIDACION, dtype=str, keep_default_na=False
    )
    propuestas = pd.read_csv(
        PROPUESTAS, dtype=str, keep_default_na=False
    )

    if df["caso_id"].duplicated().any():
        print("ERROR: Hay casos duplicados.")
        return

    revisor = input(
        "Identificacion del revisor: "
    ).strip()

    if not revisor:
        print("ERROR: Debes identificar al revisor.")
        return

    cambios = 0

    for _, propuesta in propuestas.iterrows():
        caso = propuesta["caso_id"]
        paginas = propuesta["paginas_candidatas"]

        if propuesta["estado"] != "PENDIENTE_CONFIRMACION":
            continue

        coincidencias = df.index[df["caso_id"] == caso]

        if len(coincidencias) != 1:
            print(f"Se omite {caso}: vinculacion ambigua.")
            continue

        indice = coincidencias[0]

        print(f"\nCASO: {caso}")
        print(f"Etiqueta: {df.at[indice, 'etiqueta_validada']}")
        print(f"Pagina candidata: {paginas}")

        respuesta = input(
            "¿Confirmas la decision, la pagina y "
            "la correspondencia con la demanda? "
            "(SI/NO): "
        ).strip().upper()

        if respuesta != "SI":
            print("Se mantiene pendiente.")
            continue

        pagina = input(
            f"Pagina confirmada [{paginas}]: "
        ).strip() or paginas

        if not pagina.isdigit() or int(pagina) < 1:
            print("Pagina invalida. Se omite.")
            continue

        df.at[indice, "pagina_evidencia"] = pagina
        df.at[indice, "revisor"] = revisor
        df.at[indice, "estado_revision"] = "VALIDADO"
        cambios += 1

    if cambios == 0:
        print("\nNo se realizaron cambios.")
        return

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo = VALIDACION.with_name(
        f"validacion_juridica_backup_{marca}.csv"
    )

    shutil.copy2(VALIDACION, respaldo)

    df.to_csv(
        VALIDACION,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nCasos validados: {cambios}")
    print(f"Respaldo: {respaldo}")
    print(f"Archivo actualizado: {VALIDACION}")

if __name__ == "__main__":
    main()
