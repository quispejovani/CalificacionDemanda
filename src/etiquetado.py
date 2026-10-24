import re

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto.lower())


def analizar_auto(ruta):
    paginas = extraer_paginas(ruta)

    texto_total = "\n".join(
        f"\n[PAGINA {numero}]\n{texto}"
        for numero, texto in paginas
    )

    texto = normalizar(texto_total)

    marcadores = list(re.finditer(
        r"\b(?:se\s+resuelve|resuelvo|resuelven|"
        r"decision|parte\s+resolutiva)\s*:?",
        texto
    ))

    if not marcadores:
        return "REQUIERE_REVISION", []

    # Usar el último marcador como candidato,
    # no como garantía de sección resolutiva.
    inicio = marcadores[-1].end()
    seccion = texto[inicio:]

    patrones_decision = {
        "IMPROCEDENTE": (
            r"\b(?:declarar|declaro|declara|declararon|"
            r"declarase|se\s+declara)\s+"
            r"(?:la\s+demanda\s+)?improcedente\b"
        ),
        "INADMISIBLE": (
            r"\b(?:declarar|declaro|declara|declararon|"
            r"declarase|se\s+declara)\s+"
            r"(?:la\s+demanda\s+)?inadmisible\b"
        ),
        "ADMISIBLE": (
            r"\b(?:admitir|admito|admite|admitase|"
            r"se\s+admite)\b.{0,100}"
            r"\b(?:demanda|tramite)\b"
        )
    }

    coincidencias = []

    for etiqueta, patron in patrones_decision.items():
        for match in re.finditer(patron, seccion):
            coincidencias.append({
                "etiqueta": etiqueta,
                "pagina": "VERIFICAR",
                "fragmento": seccion[
                    max(0, match.start() - 100):
                    min(len(seccion), match.end() + 150)
                ]
            })

    etiquetas = set(
        c["etiqueta"] for c in coincidencias
    )

    if len(etiquetas) == 1:
        sugerencia = next(iter(etiquetas))
    elif len(etiquetas) > 1:
        sugerencia = "AMBIGUA"
    else:
        sugerencia = "REQUIERE_REVISION"

    return sugerencia, coincidencias

def identificar_objeto_decision(texto_resolutivo):
    texto = normalizar(texto_resolutivo)

    # Detectar primero actuaciones fuera del alcance.
    if re.search(
        r"\badmitir\b\s+(?:a\s+tramite\s+)?"
        r"la\s+solicitud\s+de\s+conciliacion\b",
        texto
    ):
        return "SOLICITUD_CONCILIACION"

    if re.search(
        r"\badmitir\b.{0,100}"
        r"\bdemanda\s+de\s+alimentos\b",
        texto,
        re.DOTALL
    ):
        return "POSIBLE_ADMISION_DEMANDA"

    return "REQUIERE_REVISION"
