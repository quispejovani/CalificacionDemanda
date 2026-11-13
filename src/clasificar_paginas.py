
from pathlib import Path, PureWindowsPath
import re
import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parents[1]
RAW = (BASE / "data" / "raw").resolve()
PROCESSED = BASE / "data" / "processed"

ENTRADA = PROCESSED / "dataset_entrenamiento.csv"
SALIDA = PROCESSED / "inventario_paginas.csv"

COLUMNAS_REVISION = [
    "tipo_contenido",
    "contiene_datos_personales",
    "incluir_entrenamiento",
    "estado_revision",
    "observaciones",
]

CATEGORIAS = {
    "DEMANDA",
    "DNI",
    "BOLETA_COMPRA",
    "FOTOGRAFIA_PERSONA",
    "FOTOGRAFIA_INMUEBLE",
    "FOTOGRAFIA_VIA_PUBLICA",
    "ANEXO_TEXTUAL",
    "OTRO",
}

def ruta_segura(nombre, caso):
    partes = PureWindowsPath(nombre).parts

    if (
        not partes
        or PureWindowsPath(nombre).is_absolute()
        or any(p in ("", ".", "..") for p in partes)
    ):
        raise ValueError(f"Ruta invalida: {nombre}")

    ruta = RAW.joinpath(*partes).resolve()
    carpeta_caso = (RAW / caso.lower()).resolve()

    if not ruta.is_relative_to(carpeta_caso):
        raise ValueError(f"Ruta fuera del caso: {nombre}")

    if not re.fullmatch(
        r"demanda_\d+(?:\.\d+)?\.pdf",
        ruta.name,
        re.IGNORECASE,
    ):
        raise ValueError(f"Nombre no permitido: {nombre}")

    if not ruta.is_file():
        raise FileNotFoundError(ruta)

    return ruta


def inventariar():
    df = pd.read_csv(
        ENTRADA,
        dtype=str,
        keep_default_na=False,
    )

    registros = []

    for _, fila in df.iterrows():
        caso = fila["caso_id"].strip()

        documentos = [
            fila["demanda_principal"].strip()
        ]

        documentos += [
            x.strip()
            for x in fila[
                "documentos_complementarios"
            ].split(";")
            if x.strip()
        ]

        for nombre in documentos:
            ruta = ruta_segura(nombre, caso)

            with pymupdf.open(ruta) as pdf:
                for numero, pagina in enumerate(pdf, 1):
                    texto = pagina.get_text("text").strip()

                    registros.append({
                        "caso_id": caso,
                        "documento": nombre,
                        "pagina": numero,
                        "tiene_texto_digital": (
                            "SI" if texto else "NO"
                        ),
                        "caracteres_digitales": len(texto),
                        "imagenes_incrustadas": len(
                            pagina.get_images(full=True)
                        ),
                        "tipo_contenido": "",
                        "contiene_datos_personales": "PENDIENTE",
                        "incluir_entrenamiento": "PENDIENTE",
                        "estado_revision": "PENDIENTE",
                        "observaciones": "",
                    })

    return pd.DataFrame(registros)


def conservar_revisiones(nuevo):
    if not SALIDA.exists():
        return nuevo

    anterior = pd.read_csv(
        SALIDA,
        dtype=str,
        keep_default_na=False,
    )

    claves = ["caso_id", "documento", "pagina"]

    anterior = anterior[
        claves + COLUMNAS_REVISION
    ].drop_duplicates(subset=claves, keep="last")

    nuevo = nuevo.drop(
        columns=COLUMNAS_REVISION
    ).merge(
        anterior,
        on=claves,
        how="left",
        validate="one_to_one",
    )

    valores_defecto = {
        "tipo_contenido": "",
        "contiene_datos_personales": "PENDIENTE",
        "incluir_entrenamiento": "PENDIENTE",
        "estado_revision": "PENDIENTE",
        "observaciones": "",
    }

    for columna, defecto in valores_defecto.items():
        nuevo[columna] = (
            nuevo[columna].fillna(defecto)
        )

    return nuevo


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)

    nuevo = inventariar()
    resultado = conservar_revisiones(nuevo)

    resultado.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nINVENTARIO DOCUMENTAL")
    print("=" * 60)
    print("Casos:", resultado["caso_id"].nunique())
    print("Documentos:", resultado[
        ["caso_id", "documento"]
    ].drop_duplicates().shape[0])
    print("Paginas:", len(resultado))

    print("\nPaginas por caso:")
    print(
        resultado.groupby("caso_id")
        .size()
        .to_string()
    )

    print("\nArchivo generado:", SALIDA)


if __name__ == "__main__":
    main()
