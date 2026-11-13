
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ENTRADA = BASE / "data" / "processed" / "validacion_juridica.csv"
SALIDA = BASE / "data" / "processed" / "reporte_validacion.csv"

COLUMNAS = [
    "caso_id",
    "auto",
    "palabras_clave",
    "materia_validada",
    "tipo_procedimiento",
    "objeto_decision",
    "decision_principal",
    "etiqueta_validada",
    "pagina_evidencia",
    "observaciones",
    "revisor",
    "estado_revision",
]

ETIQUETAS_VALIDAS = {
    "ADMISIBLE",
    "INADMISIBLE",
    "IMPROCEDENTE",
}

def normalizar(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip().upper()

def validar():
    if not ENTRADA.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {ENTRADA}"
        )

    df = pd.read_csv(
        ENTRADA,
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False
    )

    faltantes = [
        columna for columna in COLUMNAS
        if columna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Columnas faltantes: {faltantes}"
        )

    duplicados = set(
        df.loc[
            df["caso_id"].duplicated(keep=False),
            "caso_id"
        ]
    )

    resultados = []

    for _, fila in df.iterrows():
        caso = fila["caso_id"].strip()
        materia = normalizar(fila["materia_validada"])
        procedimiento = normalizar(
            fila["tipo_procedimiento"]
        )
        etiqueta = normalizar(fila["etiqueta_validada"])
        estado = normalizar(fila["estado_revision"])

        observaciones = []

        if caso in duplicados:
            observaciones.append("CASO_DUPLICADO")

        if not caso:
            observaciones.append("SIN_IDENTIFICADOR")

        if procedimiento == "CONCILIACION_ALIMENTOS":
            situacion = "FUERA_ALCANCE"

        elif procedimiento != "DEMANDA_ALIMENTOS":
            situacion = "PENDIENTE_PROCEDIMIENTO"

        elif materia != "ALIMENTOS":
            situacion = "PENDIENTE_MATERIA"

        elif estado != "VALIDADO":
            situacion = "PENDIENTE_VALIDACION"

        elif etiqueta not in ETIQUETAS_VALIDAS:
            situacion = "ETIQUETA_NO_VALIDA"

        elif not fila["pagina_evidencia"].strip():
            situacion = "SIN_EVIDENCIA"

        elif not fila["revisor"].strip():
            situacion = "SIN_REVISOR"

        elif caso in duplicados:
            situacion = "CASO_DUPLICADO"

        else:
            situacion = "APTO_PRELIMINAR"

        resultados.append({
            "caso_id": caso,
            "tipo_procedimiento": procedimiento,
            "etiqueta_validada": etiqueta,
            "estado_revision": estado,
            "situacion_dataset": situacion,
            "alertas": ";".join(observaciones),
        })

    reporte = pd.DataFrame(resultados)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    reporte.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nREPORTE DE VALIDACION")
    print("=" * 45)
    print(f"Total de casos: {len(reporte)}")

    print("\nDistribucion:")
    print(
        reporte["situacion_dataset"]
        .value_counts()
        .to_string()
    )

    print(f"\nReporte generado: {SALIDA}")

if __name__ == "__main__":
    validar()
