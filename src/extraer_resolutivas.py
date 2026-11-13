
from pathlib import Path
import re
import unicodedata
import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"

def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.upper())
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", texto).strip()

marcador = re.compile(
    r"\b(?:SE RESUELVE|RESUELVE|DECISION)\s*[:.]?"
)


decisiones = {
    "INADMISIBLE": re.compile(
        r"\b(?:DECLARAR|DECLARA|DECLARESE)\s*[:.,]?\s*"
        r"(?:LA\s+DEMANDA\s+)?INADMISIBLE\b"
        r"|\bINADMISIBLE\s+LA\s+DEMANDA\b"
    ),

    "IMPROCEDENTE": re.compile(
        r"\b(?:DECLARAR|DECLARA|DECLARESE)\s*[:.,]?\s*"
        r"(?:LA\s+DEMANDA\s+)?IMPROCEDENTE\b"
        r"|\bIMPROCEDENTE\s+LA\s+DEMANDA\b"
    ),

    "ADMISIBLE": re.compile(
        r"\b(?:ADMITIR|ADMITASE|SE\s+ADMITE)"
        r"(?:\s+ADMITIR){0,3}\s+"
        r"(?:A\s+TRAMITE|EN\s+PROCESO\s+UNICO)"
        r"[\s,.:;-]*(?:LA\s+)?DEMANDA\b"
        r"|\bADMITIR\s+LA\s+DEMANDA\b"
    )
}

registros = []

for carpeta in sorted(RAW.iterdir()):
    if not carpeta.is_dir():
        continue

    for archivo in sorted(carpeta.rglob("*.pdf")):
        if not archivo.stem.lower().startswith("auto"):
            continue

        try:
            with pymupdf.open(archivo) as doc:
                texto = normalizar(
                    " ".join(p.get_text("text") for p in doc)
                )

            marcadores = list(marcador.finditer(texto))

            # Usar el último marcador como candidato,
            # sin asumir que siempre es la parte resolutiva.
            if marcadores:
                resolutiva = texto[marcadores[-1].end():]
                metodo = "ULTIMO_MARCADOR"
            else:
                resolutiva = texto
                metodo = "SIN_MARCADOR"

            encontrados = []

            for etiqueta, patron in decisiones.items():
                if patron.search(resolutiva):
                    encontrados.append(etiqueta)

            sugerencia = (
                encontrados[0]
                if len(encontrados) == 1
                else "REQUIERE_REVISION"
            )
            alerta_subsanacion = bool(
                 re.search(r"\bSUBSAN\w*\b", resolutiva)
            )
            alerta_conciliacion = bool(
                re.search(
                    r"\b(?:SOLICITUD|AUDIENCIA)\s+DE\s+CONCILIACION\b",
                    resolutiva
                    )
            )
            if alerta_conciliacion:sugerencia = "VERIFICAR_FUERA_ALCANCE"              
            
            registros.append({
                "caso_id": carpeta.name.upper(),
                "auto": str(archivo.relative_to(RAW)),
                "metodo": metodo,
                "etiquetas_detectadas": " | ".join(encontrados),
                "sugerencia": sugerencia,
                "alerta_subsanacion": alerta_subsanacion,
                "alerta_conciliacion": alerta_conciliacion,
                "fragmento_resolutivo": resolutiva[:1200]
            })

        except Exception as exc:
            print("ERROR:", archivo, exc)

df = pd.DataFrame(registros)

OUT.mkdir(parents=True, exist_ok=True)

salida = OUT / "resolutivas_candidatas.csv"
df.to_csv(salida, index=False, encoding="utf-8-sig")

print("\n=== RESOLUTIVAS CANDIDATAS ===")
print("Autos:", len(df))
print("Expedientes:", df["caso_id"].nunique())
print("\nSugerencias:")
print(df["sugerencia"].value_counts().to_string())

print("\nMétodo de extracción:")
print(df["metodo"].value_counts().to_string())

print("\nArchivo:", salida)
