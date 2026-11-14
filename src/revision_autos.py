
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pymupdf


BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

SALIDA = PROCESSED / "revision_autos_mejorada.csv"

MARCADORES = re.compile(
    r"\b(?:"
    r"SE\s+RESUELVE|"
    r"RESUELVE|"
    r"RESUELVO|"
    r"RESUELVEN|"
    r"FALLO"
    r")\s*:?",
    re.IGNORECASE
)

# Expresiones que indican una decisión actual.
PATRONES = {
    "ADMISIBLE": [
        r"\bADMITIR(?:\s+A\s+TRAMITE)?\b",
        r"\bADMITASE(?:\s+A\s+TRAMITE)?\b",
        r"\bSE ADMITE\b",
    ],
    "INADMISIBLE": [
        r"\bDECLARAR\s+INADMISIBLE\b",
        r"\bSE DECLARA\s+INADMISIBLE\b",
        r"\bDECLARESE\s+INADMISIBLE\b",
    ],
    "IMPROCEDENTE": [
        r"\bDECLARAR\s+IMPROCEDENTE\b",
        r"\bSE DECLARA\s+IMPROCEDENTE\b",
        r"\bDECLARESE\s+IMPROCEDENTE\b",
    ],
}

CONDICIONALES = [
    r"\bBAJO\s+APERCIBIMIENTO\b",
    r"\bDE\s+NO\s+SUBSANAR\b",
    r"\bDE\s+NO\s+CUMPLIR\b",
    r"\bCASO\s+CONTRARIO\b",
    r"\bEN\s+CASO\s+DE\s+INCUMPLIMIENTO\b",
]

SUBSANACION = re.compile(
    r"\bSUBSAN\w*\b|\bCUMPLA\s+CON\b"
)

CONCILIACION = re.compile(
    r"\bSOLICITUD\s+DE\s+CONCILIACION\b|"
    r"\bAUDIENCIA\s+DE\s+CONCILIACION\b"
)

DEMANDA = re.compile(
    r"\bDEMANDA\b|\bDEMANDA\s+DE\s+ALIMENTOS\b"
)

PATRON_ASIGNACION = re.compile(
    r"\bASIGNACION\s+ANTICIPADA\b|"
    r"\bALIMENTOS\s+PROVISIONALES\b"
)

ALIMENTOS = re.compile(r"\bALIMENTOS\b")


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    texto = texto.upper()
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def detectar_asignacion_anticipada(texto):
    texto = normalizar(texto)

    patron = re.compile(
        r"\bASIGNACION\s+ANTICIPADA\b|"
        r"\bALIMENTOS\s+PROVISIONALES\b"
    )

    return bool(patron.search(texto))


def extraer_pdf(ruta):
    paginas = []

    with pymupdf.open(ruta) as documento:
        for numero, pagina in enumerate(documento, start=1):
            texto = pagina.get_text("text")
            paginas.append((numero, texto))

    return paginas


def obtener_resolutiva(texto):
    coincidencias = list(MARCADORES.finditer(texto))

    if not coincidencias:
        return texto, False

    # Utilizar el primer marcador encontrado.
    # Si hay varios, exigir revisión posterior.
    inicio = coincidencias[0].end()

    return texto[inicio:], len(coincidencias) == 1


def es_condicional(fragmento_previo):
    return any(
        re.search(patron, fragmento_previo)
        for patron in CONDICIONALES
    )


def analizar_decisiones(texto):
    hallazgos = []

    for etiqueta, patrones in PATRONES.items():
        for patron in patrones:
            for coincidencia in re.finditer(patron, texto):
                inicio = coincidencia.start()

                # Revisar el contexto previo inmediato.
                previo = texto[max(0, inicio - 180):inicio]

                # Evitar confundir advertencias con
                # declaraciones actuales.
                condicionada = es_condicional(previo)

                # Evitar tomar como decisión una
                # expresión negada.
                negacion = bool(re.search(
                    r"\b(?:NO|SIN)\s+$",
                    previo[-20:]
                ))

                hallazgos.append({
                    "etiqueta": etiqueta,
                    "inicio": inicio,
                    "expresion": coincidencia.group(),
                    "condicionada": condicionada,
                    "negada": negacion,
                })

    return hallazgos


def analizar_auto(ruta):
    paginas = extraer_pdf(ruta)

    texto_completo = normalizar(
        " ".join(texto for _, texto in paginas)
    )

    resolutiva, marcador_unico = obtener_resolutiva(
        texto_completo
    )

    hay_conciliacion = bool(
        CONCILIACION.search(resolutiva)
    )

    hay_demanda = bool(
        DEMANDA.search(resolutiva)
    )

    requiere_subsanacion = bool(
        SUBSANACION.search(resolutiva)
    )

    hay_asignacion_anticipada = detectar_asignacion_anticipada(
    resolutiva
    )
    
    apercibimiento = any(
        re.search(patron, resolutiva)
        for patron in CONDICIONALES
    )

    hallazgos = analizar_decisiones(resolutiva)

    efectivas = [
        h for h in hallazgos
        if not h["condicionada"] and not h["negada"]
    ]

    etiquetas = sorted({
        h["etiqueta"] for h in efectivas
    })

    alertas = []

    if not marcador_unico:
        alertas.append("VERIFICAR_PARTE_RESOLUTIVA")

    if hay_conciliacion:
        alertas.append("VERIFICAR_CONCILIACION")

    if not hay_demanda:
        alertas.append("OBJETO_DEMANDA_NO_CONFIRMADO")

    if len(etiquetas) > 1:
        alertas.append("MULTIPLES_DECISIONES")

    if not etiquetas:
        alertas.append("DECISION_NO_IDENTIFICADA")

    if requiere_subsanacion:
        alertas.append("REQUIERE_SUBSANACION")

    if apercibimiento:
        alertas.append("CONTIENE_APERCIBIMIENTO")

    # La presencia de conciliación no siempre
    # excluye una demanda. Solo sugerimos
    # FUERA_ALCANCE si no hay indicios de demanda.
    if hay_conciliacion and not hay_demanda:
        sugerencia = "FUERA_ALCANCE"

    elif (
        marcador_unico
        and hay_demanda
        and not hay_conciliacion
        and len(etiquetas) == 1
    ):
        sugerencia = etiquetas[0]

    else:
        sugerencia = "REQUIERE_REVISION"

    return {
        "auto": ruta.name,
        "etiqueta_sugerida": sugerencia,
        "decisiones_detectadas": ";".join(etiquetas),
        "requiere_subsanacion": (
            "SI" if requiere_subsanacion else "NO"
        ),
        "menciona_asignacion_anticipada": ("SI" if hay_asignacion_anticipada else "NO"),
        "apercibimiento": (
            "SI" if apercibimiento else "NO"
        ),
        "alertas": ";".join(alertas),
        "estado": "PENDIENTE_VALIDACION_JURIDICA",
    }


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)

    archivos = sorted(
        RAW.rglob("auto_*.pdf")
    )

    if not archivos:
        print(f"No se encontraron autos en: {RAW}")
        return

    resultados = []

    for ruta in archivos:
        try:
            resultado = analizar_auto(ruta)

            coincidencia = re.search(
                r"auto_(\d+)\.pdf$",
                ruta.name,
                re.IGNORECASE
            )

            numero = (
                int(coincidencia.group(1))
                if coincidencia else None
            )

            resultado["caso_id"] = (
                f"CASO_{numero:03d}"
                if numero is not None
                else ""
            )

            resultados.append(resultado)

            print(
                resultado["caso_id"],
                resultado["etiqueta_sugerida"]
            )

        except Exception as error:
            print(f"ERROR {ruta.name}: {error}")

    df = pd.DataFrame(resultados)
    
    columnas = [
        "caso_id",
        "auto",
        "etiqueta_sugerida",
        "decisiones_detectadas",
        "requiere_subsanacion",
        "menciona_asignacion_anticipada",
        "apercibimiento",
        "alertas",
        "estado",
    ]

    df = df[columnas]

    df.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nRESUMEN")
    print("=" * 45)
    print(
        df["etiqueta_sugerida"]
        .value_counts()
        .to_string()
    )

    print(f"\nArchivo generado: {SALIDA}")


if __name__ == "__main__":
    main()