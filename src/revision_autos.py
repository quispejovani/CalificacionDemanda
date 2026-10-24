
from pathlib import Path
import csv
import re
import unicodedata
import pymupdf

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

ENTRADA = PROCESSED / "dataset_casos.csv"
SALIDA = PROCESSED / "revision_autos.csv"


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto.lower())


def revisar_auto(ruta):
    paginas = []

    with pymupdf.open(ruta) as documento:
        for pagina in documento:
            paginas.append(pagina.get_text("text"))

    texto = normalizar("\n".join(paginas))

    marcadores = list(re.finditer(
        r"\b(?:se\s+resuelve|resuelvo|"
        r"resuelven|fallo)\s*:?",
        texto
    ))

    if not marcadores:
        return "SIN_MARCADOR", "NO_DETERMINADO", ""

    # Último marcador: candidato a sección resolutiva.
    seccion = texto[marcadores[-1].end():]

    patrones = {
        "solicitud_conciliacion":
            r"\bsolicitud\s+de\s+conciliacion\b",
        "demanda_alimentos":
            r"\bdemanda\s+de\s+alimentos\b",
        "admitir":
            r"\badmitir\b|\badmitase\b|\bse\s+admite\b",
        "inadmisible":
            r"\binadmisib\w*\b",
        "improcedente":
            r"\bimprocedent\w*\b",
        "subsanar":
            r"\bsubsan\w*\b",
        "archivo":
            r"\barchiv\w*\b"
    }

    hallazgos = [
        nombre
        for nombre, patron in patrones.items()
        if re.search(patron, seccion)
    ]

    # Solo una alerta de revisión, no una etiqueta.
    if "solicitud_conciliacion" in hallazgos:
        alerta = "REVISAR_CONCILIACION"
    else:
        alerta = "VERIFICAR_OBJETO_Y_DECISION"

    return "MARCADOR_ENCONTRADO", alerta, ";".join(hallazgos)


def ejecutar():
    resultados = []

    with ENTRADA.open(
        encoding="utf-8-sig", newline=""
    ) as archivo:
        casos = list(csv.DictReader(archivo))

    for caso in casos:
        auto = caso["auto_judicial"]

        estado = "SIN_AUTO"
        alerta = "REQUIERE_REVISION"
        hallazgos = ""

        if auto:
            try:
                estado, alerta, hallazgos = revisar_auto(
                    RAW / auto
                )
            except Exception as error:
                estado = f"ERROR_{type(error).__name__}"

        resultados.append({
            "caso_id": caso["caso_id"],
            "auto": auto,
            "estado_extraccion": estado,
            "alerta": alerta,
            "palabras_clave": hallazgos,
            "tipo_procedimiento_validado": "",
            "decision_validada": "",
            "revisor": "",
            "estado_revision": "PENDIENTE"
        })

        print(
            f"{caso['caso_id']}: "
            f"{alerta} | {hallazgos}"
        )

    with SALIDA.open(
        "w", newline="", encoding="utf-8-sig"
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=resultados[0].keys()
        )
        escritor.writeheader()
        escritor.writerows(resultados)

    print(f"\nReporte generado: {SALIDA}")


if __name__ == "__main__":
    ejecutar()

PATRONES_OBJETO = {
    "CONCILIACION_ALIMENTOS": (
        r"\badmitir\s+la\s+solicitud\s+de\s+"
        r"conciliacion\b.{0,250}\bsobre\s+alimentos\b"
    ),
    "ADMISION_DEMANDA_ALIMENTOS": (
        r"\badmitir\b.{0,150}"
        r"\bdemanda\b.{0,100}\balimentos\b"
    ),
}