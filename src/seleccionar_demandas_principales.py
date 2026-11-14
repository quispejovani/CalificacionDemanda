
from pathlib import Path
import re
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DIR = BASE / "data" / "processed"

ORIGEN = DIR / "textos_demandas_ocr.csv"
SALIDA = DIR / "seleccion_documentos_demanda.csv"

# Selección confirmada por revisión humana.
CASOS_REVISADOS = {
    "CASO_009": "DEMANDA_009",
    "CASO_010": "DEMANDA_010",
    "CASO_021": "DEMANDA_021",
    "CASO_030": "DEMANDA_030",
    "CASO_069": "DEMANDA_069",
    "CASO_074": "DEMANDA_074",
    "CASO_079": "DEMANDA_079",
    "CASO_095": "DEMANDA_095",
    "CASO_097": "DEMANDA_097",
    "CASO_099": "DEMANDA_099",
    "CASO_101": "DEMANDA_101",
}

def nombre_normalizado(ruta):
    nombre = Path(str(ruta).replace("\\", "/")).stem.upper()

    # Reconocer DEMANTA como variante de DEMANDA.
    nombre = re.sub(r"^DEMANTA_", "DEMANDA_", nombre)

    # Normalizar únicamente la numeración del expediente.
    # DEMANDA_9 -> DEMANDA_009
    # DEMANDA_10 -> DEMANDA_010
    # DEMANDA_9.1 -> DEMANDA_009.1
    patron = re.fullmatch(r"DEMANDA_(\d+)(\.\d+)?", nombre)

    if patron:
        numero = int(patron.group(1))
        sufijo = patron.group(2) or ""
        return f"DEMANDA_{numero:03d}{sufijo}"

    return nombre

def main():
    df = pd.read_csv(ORIGEN, dtype=str).fillna("")
    df["caso_id"] = df["caso_id"].str.upper().str.strip()
    df["nombre_normalizado"] = df["documento"].map(
        nombre_normalizado
    )

    registros = []
    errores = []

    for caso, nombre_principal in CASOS_REVISADOS.items():
        grupo = df[df["caso_id"] == caso].copy()

        if grupo.empty:
            errores.append(f"{caso}: no aparece en OCR")
            continue

        coincidencias = grupo[
            grupo["nombre_normalizado"] == nombre_principal
        ]

        if len(coincidencias) != 1:
            errores.append(
                f"{caso}: se esperaban 1 documento principal, "
                f"se encontraron {len(coincidencias)}. "
                f"Disponibles: {grupo['documento'].tolist()}"
            )
            continue

        for _, fila in grupo.iterrows():
            principal = (
                fila["nombre_normalizado"] == nombre_principal
            )

            if principal:
                tipo = "DEMANDA_PRINCIPAL"
                incluir_texto = "SI"
            else:
                tipo = "COMPLEMENTARIO"
                incluir_texto = "NO"

            registros.append({
                "caso_id": caso,
                "documento": fila["documento"],
                "tipo_documento": tipo,
                "usar_texto_modelo": incluir_texto,
                "seleccion_validada": "SI",
                "observacion": (
                    "Demanda principal confirmada"
                    if principal else
                    "Documento complementario; no usar como demanda"
                )
            })

    if errores:
        print("\nERRORES DE VERIFICACION:")
        for error in errores:
            print("-", error)
        raise SystemExit(
            "No se generó el archivo. Revisar nombres."
        )

    resultado = pd.DataFrame(registros)

    if SALIDA.exists():
        raise FileExistsError(
            f"Ya existe {SALIDA}. "
            "Conserva el archivo o crea un respaldo antes de regenerarlo."
        )

    resultado.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    principales = resultado[
        resultado["usar_texto_modelo"] == "SI"
    ]

    print("\n=== DOCUMENTOS SELECCIONADOS ===")
    print("Casos revisados:", len(CASOS_REVISADOS))
    print("Demandas principales:", len(principales))
    print(
        "Documentos complementarios:",
        len(resultado) - len(principales)
    )

    print("\n=== DEMANDAS PRINCIPALES ===")
    print(
        principales[["caso_id", "documento"]]
        .to_string(index=False)
    )

    print("\nArchivo generado:", SALIDA)

if __name__ == "__main__":
    main()
