
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROCESADOS = BASE / "data" / "processed"

ARCHIVO_PRE = PROCESADOS / "pre_etiquetas_101.csv"
ARCHIVO_AUTOS = PROCESADOS / "resolutivas_candidatas.csv"
ARCHIVO_SALIDA = PROCESADOS / "validacion_alcance_101.csv"

# Exclusiones confirmadas durante la revisión.
# No son inferencias automáticas.
EXCLUSIONES = {
    "CASO_003": ("CONCILIACION", "Solicitud de conciliación"),
    "CASO_016": ("AUMENTO_ALIMENTOS", "Demanda de aumento de alimentos"),
    "CASO_038": ("PROCESO_SUMARISIMO", "Admisión en proceso sumarísimo"),
    "CASO_091": ("PROCESO_SUMARISIMO", "Admisión en proceso sumarísimo"),
    "CASO_092": ("PROCESO_SUMARISIMO", "Admisión en proceso sumarísimo"),
    "CASO_093": ("PROCESO_SUMARISIMO", "Admisión en proceso sumarísimo"),
    "CASO_094": ("PROCESO_SUMARISIMO", "Admisión en proceso sumarísimo"),
}

def main():
    if not ARCHIVO_PRE.exists():
        raise FileNotFoundError(ARCHIVO_PRE)

    if ARCHIVO_SALIDA.exists():
        raise FileExistsError(
            f"El archivo ya existe: {ARCHIVO_SALIDA}. "
            "Realiza una copia de seguridad antes de regenerarlo."
        )

    pre = pd.read_csv(ARCHIVO_PRE, dtype=str).fillna("")
    autos = pd.read_csv(ARCHIVO_AUTOS, dtype=str).fillna("")

    columnas_pre = {"caso_id", "estado", "sugerencia_inicial"}
    columnas_autos = {"caso_id", "fragmento_resolutivo"}

    if not columnas_pre.issubset(pre.columns):
        raise ValueError("Faltan columnas requeridas en pre_etiquetas_101.csv")

    if not columnas_autos.issubset(autos.columns):
        raise ValueError("Faltan columnas requeridas en resolutivas_candidatas.csv")

    if pre["caso_id"].duplicated().any():
        raise ValueError("Hay casos duplicados en el archivo de preetiquetas.")

    if len(pre) != 101:
        raise ValueError(
            f"Se esperaban 101 expedientes; se encontraron {len(pre)}."
        )

    faltantes = set(EXCLUSIONES) - set(pre["caso_id"])
    if faltantes:
        raise ValueError(f"No se encontraron estos casos: {sorted(faltantes)}")

    # Se agrupan los fragmentos para conservar evidencia de varios autos.
    fragmentos = (
        autos.groupby("caso_id")["fragmento_resolutivo"]
        .apply(lambda valores: " | ".join(v for v in valores if v))
        .to_dict()
    )

    registros = []

    for _, fila in pre.iterrows():
        caso = fila["caso_id"]
        texto = fragmentos.get(caso, "").upper()

        # Indicadores de búsqueda, no decisiones definitivas.
        indicio_unico = "PROCESO UNICO" in texto
        indicio_sumarisimo = "PROCESO SUMARISIMO" in texto
        indicio_conciliacion = (
            "SOLICITUD DE CONCILIACION" in texto
        )

        if caso in EXCLUSIONES:
            motivo_codigo, motivo = EXCLUSIONES[caso]
            dentro_alcance = "NO"
            estado_alcance = "EXCLUSION_CONFIRMADA"
        else:
            motivo_codigo = ""
            motivo = ""
            dentro_alcance = "PENDIENTE"
            estado_alcance = "PENDIENTE_VALIDACION"

        registros.append({
            "caso_id": caso,
            "dentro_alcance": dentro_alcance,
            "estado_alcance": estado_alcance,
            "motivo_exclusion_codigo": motivo_codigo,
            "motivo_exclusion": motivo,
            "indicio_proceso_unico": indicio_unico,
            "indicio_sumarisimo": indicio_sumarisimo,
            "indicio_conciliacion": indicio_conciliacion,
            "pretension_validada": "",
            "procedimiento_validado": "",
            "observaciones_revision": "",
            "estado_etiqueta": fila["estado"],
            "sugerencia_inicial": fila["sugerencia_inicial"],
        })

    resultado = pd.DataFrame(registros)

    PROCESADOS.mkdir(parents=True, exist_ok=True)

    resultado.to_csv(
        ARCHIVO_SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n=== VALIDACION DE ALCANCE ===")
    print(resultado["dentro_alcance"].value_counts().to_string())

    print("\n=== MOTIVOS DE EXCLUSION ===")
    print(
        resultado.loc[
            resultado["dentro_alcance"] == "NO",
            ["caso_id", "motivo_exclusion"]
        ].to_string(index=False)
    )

    print("\n=== INDICIOS PARA REVISION ===")
    for columna in [
        "indicio_proceso_unico",
        "indicio_sumarisimo",
        "indicio_conciliacion",
    ]:
        print(f"{columna}: {resultado[columna].sum()}")

    print(f"\nArchivo generado: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()