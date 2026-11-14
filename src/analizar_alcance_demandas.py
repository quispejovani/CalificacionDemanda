
from pathlib import Path
import re
import unicodedata
import pandas as pd

BASE = Path(__file__).resolve().parents[1] / "data" / "processed"

ARCHIVO_ALCANCE = BASE / "validacion_alcance_101.csv"
ARCHIVO_DEMANDAS = BASE / "textos_demandas_ocr.csv"
ARCHIVO_AUTOS = BASE / "resolutivas_candidatas.csv"
ARCHIVO_SALIDA = BASE / "matriz_revision_alcance.csv"

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(
        c for c in texto if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto.upper()).strip()

def identificar_pretension(texto):
    # Priorizar el petitorio, no menciones aisladas en fundamentos.
    inicio = texto[:12000]

    patrones = {
        "AUMENTO_ALIMENTOS": (
            r"\b(?:DEMANDA|PRETENSION|PETITORIO)\b.{0,100}"
            r"\bAUMENTO\s+DE\s+(?:PENSION\s+DE\s+)?ALIMENTOS\b"
        ),
        "REDUCCION_ALIMENTOS": (
            r"\b(?:DEMANDA|PRETENSION|PETITORIO)\b.{0,100}"
            r"\bREDUCCION\s+DE\s+(?:PENSION\s+DE\s+)?ALIMENTOS\b"
        ),
        "EXONERACION_ALIMENTOS": (
            r"\b(?:DEMANDA|PRETENSION|PETITORIO)\b.{0,100}"
            r"\bEXONERACION\s+DE\s+(?:PENSION\s+DE\s+)?ALIMENTOS\b"
        ),
        "CONCILIACION": (
            r"\bSOLICITUD\s+DE\s+CONCILIACION\b"
        ),
    }

    encontrados = [
        nombre for nombre, patron in patrones.items()
        if re.search(patron, inicio)
    ]

    return "|".join(encontrados) if encontrados else "NO_DETERMINADO"

def identificar_procedimiento(texto):
    unico = bool(re.search(r"\bPROCESO\s+UNICO\b", texto))
    sumarisimo = bool(
        re.search(r"\bPROCESO\s+SUMARISIMO\b", texto)
    )

    if unico and sumarisimo:
        return "AMBOS_MENCIONADOS"
    if sumarisimo:
        return "INDICIO_SUMARISIMO"
    if unico:
        return "INDICIO_PROCESO_UNICO"
    return "NO_DETERMINADO"

def main():
    alcance = pd.read_csv(
        ARCHIVO_ALCANCE, dtype=str
    ).fillna("")

    demandas = pd.read_csv(
        ARCHIVO_DEMANDAS, dtype=str
    ).fillna("")

    autos = pd.read_csv(
        ARCHIVO_AUTOS, dtype=str
    ).fillna("")

    for df in [alcance, demandas, autos]:
        df["caso_id"] = df["caso_id"].str.upper().str.strip()

    # Agrupar todos los documentos de demanda por expediente.
    demandas_por_caso = demandas.groupby("caso_id")

    # Conservar referencias de los autos para revisión.
    autos_por_caso = autos.groupby("caso_id")

    registros = []

    for _, fila in alcance.iterrows():
        caso = fila["caso_id"]

        if caso in demandas_por_caso.groups:
            docs = demandas_por_caso.get_group(caso)
            texto_demanda = " ".join(
                docs["texto"].astype(str)
            )
            documentos = " | ".join(
                docs["documento"].astype(str)
            )
            numero_demandas = len(docs)
        else:
            texto_demanda = ""
            documentos = ""
            numero_demandas = 0

        if caso in autos_por_caso.groups:
            grupo_autos = autos_por_caso.get_group(caso)
            texto_auto = " ".join(
                grupo_autos["fragmento_resolutivo"].astype(str)
            )
        else:
            texto_auto = ""

        demanda_normalizada = normalizar(texto_demanda)
        auto_normalizado = normalizar(texto_auto)

        pretension = identificar_pretension(demanda_normalizada)

        procedimiento_demanda = identificar_procedimiento(
            demanda_normalizada[:15000]
        )

        procedimiento_auto = identificar_procedimiento(
            auto_normalizado
        )

        alertas = []

        if pretension != "NO_DETERMINADO":
            alertas.append("VERIFICAR_PRETENSION")

        if "SUMARISIMO" in procedimiento_auto:
            alertas.append("VERIFICAR_SUMARISIMO")

        if "SUMARISIMO" in procedimiento_demanda:
            alertas.append("VERIFICAR_SUMARISIMO_DEMANDA")

        if numero_demandas > 1:
            alertas.append("MULTIPLES_DEMANDAS")

        if not texto_demanda.strip():
            alertas.append("SIN_TEXTO_DEMANDA")

        registros.append({
            "caso_id": caso,
            "documentos_demanda": documentos,
            "numero_documentos_demanda": numero_demandas,
            "pretension_detectada": pretension,
            "procedimiento_demanda": procedimiento_demanda,
            "procedimiento_auto": procedimiento_auto,
            "dentro_alcance_actual": fila["dentro_alcance"],
            "estado_alcance_actual": fila["estado_alcance"],
            "alertas": "|".join(sorted(set(alertas))),
            "revision_humana": "PENDIENTE"
                if fila["dentro_alcance"] == "PENDIENTE"
                else "EXCLUSION_CONFIRMADA",
        })

    resultado = pd.DataFrame(registros)

    if ARCHIVO_SALIDA.exists():
        raise FileExistsError(
            f"El archivo ya existe: {ARCHIVO_SALIDA}. "
            "Haz una copia antes de regenerarlo."
        )

    resultado.to_csv(
        ARCHIVO_SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n=== TOTAL EXPEDIENTES ===")
    print(len(resultado))

    print("\n=== PRETENSIONES DETECTADAS ===")
    print(
        resultado["pretension_detectada"]
        .value_counts().to_string()
    )

    print("\n=== PROCEDIMIENTO SEGUN AUTO ===")
    print(
        resultado["procedimiento_auto"]
        .value_counts().to_string()
    )

    print("\n=== CASOS CON ALERTAS ===")
    print(
        resultado.loc[
            (resultado["alertas"] != "")
            & (resultado["dentro_alcance_actual"] == "PENDIENTE"),
            ["caso_id", "pretension_detectada",
             "procedimiento_auto", "alertas"]
        ].to_string(index=False)
    )

    print(f"\nArchivo generado: {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    main()

