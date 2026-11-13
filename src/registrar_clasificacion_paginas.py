
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ARCHIVO = BASE / "data" / "processed" / "inventario_paginas.csv"

TIPOS = {
    "1": "DEMANDA",
    "2": "CARATULA_EXPEDIENTE",
    "3": "CARGO_INGRESO",
    "4": "DNI",
    "5": "BOLETA_COMPRA",
    "6": "FOTOGRAFIA_PERSONA",
    "7": "FOTOGRAFIA_INMUEBLE",
    "8": "FOTOGRAFIA_VIA_PUBLICA",
    "9": "ANEXO_TEXTUAL",
    "10": "OTRO",
}

def mostrar_casos(df):
    print("\nCASOS DISPONIBLES")
    print("=" * 45)

    for caso, grupo in df.groupby("caso_id", sort=True):
        pendientes = (
            grupo["estado_revision"] != "VALIDADO"
        ).sum()

        print(
            f"{caso}: {len(grupo)} paginas, "
            f"{pendientes} pendientes"
        )


def mostrar_paginas(df, caso):
    grupo = df[df["caso_id"] == caso]

    print(f"\nPAGINAS DE {caso}")
    print("=" * 65)

    print(
        grupo[
            [
                "documento",
                "pagina",
                "tipo_contenido",
                "estado_revision",
            ]
        ].to_string(index=False)
    )


def registrar(df):
    mostrar_casos(df)

    caso = input("\nIngrese el caso (ej. CASO_001): ").strip().upper()

    if caso not in df["caso_id"].values:
        print("Caso no encontrado.")
        return df

    mostrar_paginas(df, caso)

    documentos = df.loc[
        df["caso_id"] == caso, "documento"
    ].drop_duplicates().tolist()

    print("\nDOCUMENTOS")
    for i, documento in enumerate(documentos, 1):
        print(f"{i}. {documento}")

    try:
        indice = int(input("Numero de documento: "))
        documento = documentos[indice - 1]

        if indice < 1:
            raise ValueError()

        pagina = int(input("Numero de pagina: "))

    except (ValueError, IndexError):
        print("Seleccion invalida.")
        return df

    filtro = (
        (df["caso_id"] == caso)
        & (df["documento"] == documento)
        & (pd.to_numeric(
            df["pagina"], errors="coerce"
        ) == pagina)
    )

    if not filtro.any():
        print("Pagina no encontrada.")
        return df

    print("\nTIPOS DE CONTENIDO")
    for clave, tipo in TIPOS.items():
        print(f"{clave}. {tipo}")

    seleccion = input(
        "\nIngrese categorias separadas por coma (ej. 2,3): "
    ).strip().split(",")

    seleccion = [x.strip() for x in seleccion]

    if not seleccion or any(x not in TIPOS for x in seleccion):
        print("Categorias invalidas.")
        return df

    categorias = list(dict.fromkeys(
        TIPOS[x] for x in seleccion
    ))

    personales = input(
        "Contiene datos personales (SI/NO/PENDIENTE): "
    ).strip().upper()

    if personales not in ("SI", "NO", "PENDIENTE"):
        print("Valor invalido.")
        return df

    incluir = input(
        "Incluir en entrenamiento (SI/NO/PENDIENTE): "
    ).strip().upper()

    if incluir not in ("SI", "NO", "PENDIENTE"):
        print("Valor invalido.")
        return df

    observaciones = input(
        "Observaciones (sin datos personales): "
    ).strip()

    df.loc[filtro, "tipo_contenido"] = ";".join(categorias)
    df.loc[filtro, "contiene_datos_personales"] = personales
    df.loc[filtro, "incluir_entrenamiento"] = incluir
    df.loc[filtro, "estado_revision"] = "VALIDADO"
    df.loc[filtro, "observaciones"] = observaciones

    temporal = ARCHIVO.with_suffix(".tmp")
    df.to_csv(
        temporal,
        index=False,
        encoding="utf-8-sig"
    )
    temporal.replace(ARCHIVO)

    print("\nClasificacion guardada correctamente.")
    return df


def main():
    if not ARCHIVO.exists():
        print("Primero genere inventario_paginas.csv")
        return

    df = pd.read_csv(
        ARCHIVO,
        dtype=str,
        keep_default_na=False
    )

    while True:
        print("\nCLASIFICACION DOCUMENTAL")
        print("1. Registrar pagina")
        print("2. Ver avance")
        print("3. Salir")

        opcion = input("Seleccione: ").strip()

        if opcion == "1":
            df = registrar(df)

        elif opcion == "2":
            total = len(df)
            validadas = (
                df["estado_revision"] == "VALIDADO"
            ).sum()

            print(f"\nTotal: {total}")
            print(f"Validadas: {validadas}")
            print(f"Pendientes: {total - validadas}")

        elif opcion == "3":
            break

        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
