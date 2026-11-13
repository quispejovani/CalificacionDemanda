
from pathlib import Path
import re
import unicodedata
import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", texto).upper()

PATRONES = {
    "IMPROCEDENTE": [
        r"\bDECLARAR?\s+IMPROCEDENTE\b",
        r"\bDECLARA(?:R|SE)?\s+IMPROCEDENTE\b",
        r"\bIMPROCEDENTE\s+LA\s+DEMANDA\b",
    ],
    "INADMISIBLE": [
        r"\bDECLARAR?\s+INADMISIBLE\b",
        r"\bDECLARA(?:R|SE)?\s+INADMISIBLE\b",
        r"\bINADMISIBLE\s+LA\s+DEMANDA\b",
    ],
    "ADMISIBLE": [
        r"\bADMIT(?:IR|E|ASE|IDA)\b.{0,100}\bDEMANDA\b",
        r"\bSE\s+ADMITE\b.{0,100}\bDEMANDA\b",
        r"\bADMITIR\s+A\s+TRAMITE\b",
    ],
}

MARCADORES = [
    r"\bSE\s+RESUELVE\b",
    r"\bRESUELVE\s*:",
    r"\bSE\s+DECIDE\b",
    r"\bDECIDE\s*:",
]

def extraer_resolutiva(texto):
    normal = normalizar(texto)
    posiciones = []

    for patron in MARCADORES:
        posiciones.extend(
            m.end() for m in re.finditer(patron, normal)
        )

    if not posiciones:
        return "", False

    # Se conserva desde el primer marcador hasta el final.
    # Esto puede incluir más de una resolución.
    return normal[min(posiciones):], True

def detectar_decisiones(texto):
    encontradas = set()

    for etiqueta, patrones in PATRONES.items():
        if any(re.search(p, texto) for p in patrones):
            encontradas.add(etiqueta)

    return sorted(encontradas)

def procesar_auto(ruta, caso_id):
    try:
        with pymupdf.open(ruta) as doc:
            texto = "\n".join(
                pagina.get_text("text") for pagina in doc
            )

        resolutiva, marcador = extraer_resolutiva(texto)
        decisiones = detectar_decisiones(resolutiva)

        # La etiqueta es una sugerencia, no verdad judicial.
        if len(decisiones) == 1 and marcador:
            sugerencia = decisiones[0]
        else:
            sugerencia = "REQUIERE_REVISION"

        return {
            "caso_id": caso_id,
            "documento": str(ruta.relative_to(RAW)),
            "marcador_resolutiva": marcador,
            "decisiones_detectadas": "|".join(decisiones),
            "etiqueta_sugerida": sugerencia,
            "evidencia_resolutiva": resolutiva[:2000],
            "estado": "OK",
        }

    except Exception as exc:
        return {
            "caso_id": caso_id,
            "documento": str(ruta.relative_to(RAW)),
            "marcador_resolutiva": False,
            "decisiones_detectadas": "",
            "etiqueta_sugerida": "REQUIERE_REVISION",
            "evidencia_resolutiva": "",
            "estado": f"ERROR: {exc}",
        }

registros = []

for carpeta in sorted(RAW.iterdir()):
    if not carpeta.is_dir():
        continue

    for ruta in sorted(carpeta.rglob("*.pdf")):
        if ruta.stem.lower().startswith("auto"):
            registros.append(
                procesar_auto(ruta, carpeta.name)
            )

df = pd.DataFrame(registros)

# Si un expediente contiene varios autos, exige revisión.
conteos = df.groupby("caso_id")["documento"].transform("count")
df.loc[conteos > 1, "etiqueta_sugerida"] = "REQUIERE_REVISION"

salida = OUT / "decisiones_autos_101.csv"
df.to_csv(salida, index=False, encoding="utf-8-sig")

print("\n=== RESULTADOS PRELIMINARES ===")
print("Autos procesados:", len(df))
print("Expedientes:", df["caso_id"].nunique())
print("\nDistribución de etiquetas sugeridas:")
print(df["etiqueta_sugerida"].value_counts().to_string())
print("\nArchivo:", salida)
print("\nIMPORTANTE: validar etiquetas antes de entrenar.")