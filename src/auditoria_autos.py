
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pymupdf


BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SALIDA = (
    BASE / "data" / "processed"
    / "auditoria_autos.csv"
)

PATRONES = {
    "MARCADOR_RESOLUTIVO": (
        r"\bSE\s+RESUELVE\b|"
        r"\bRESUELVO\b|"
        r"\bRESUELVEN\b|"
        r"\bFALLO\b"
    ),
    "ADMISION": (
        r"\bADMITIR\b|"
        r"\bADMITASE\b|"
        r"\bSE\s+ADMITE\b"
    ),
    "INADMISIBILIDAD": (
        r"\bINADMISIBLE\b"
    ),
    "IMPROCEDENCIA": (
        r"\bIMPROCEDENTE\b"
    ),
    "SUBSANACION": (
        r"\bSUBSAN\w*\b"
    ),
    "APERCIBIMIENTO": (
        r"\bAPERCIBIMIENTO\b"
    ),
    "SOLICITUD_CONCILIACION": (
        r"\bSOLICITUD\s+DE\s+CONCILIACION\b"
    ),
    "DEMANDA_ALIMENTOS": (
        r"\bDEMANDA\s+DE\s+ALIMENTOS\b"
    ),
}


def normalizar(texto):
    texto = unicodedata.normalize(
        "NFKD", texto
    )
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(
        r"\s+", " ", texto.upper()
    ).strip()


def auditar_pdf(ruta):
    resultados = []

    with pymupdf.open(ruta) as pdf:
        for numero, pagina in enumerate(
            pdf, start=1
        ):
            texto = normalizar(
                pagina.get_text("text")
            )

            for categoria, patron in PATRONES.items():
                coincidencias = list(
                    re.finditer(patron, texto)
                )

                if coincidencias:
                    resultados.append({
                        "auto": ruta.name,
                        "pagina": numero,
                        "categoria": categoria,
                        "cantidad": len(coincidencias),
                    })

    return resultados


def main():
    registros = []

    for ruta in sorted(RAW.rglob("auto_*.pdf")):
        try:
            registros.extend(auditar_pdf(ruta))
        except Exception as error:
            print(
                f"No se pudo procesar "
                f"{ruta.name}: {type(error).__name__}"
            )

    columnas = [
        "auto", "pagina",
        "categoria", "cantidad"
    ]

    df = pd.DataFrame(
        registros, columns=columnas
    )

    SALIDA.parent.mkdir(
        parents=True, exist_ok=True
    )

    df.to_csv(
        SALIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nAUDITORIA DE AUTOS")
    print("=" * 45)

    if df.empty:
        print("Sin coincidencias detectadas.")
    else:
        resumen = df.pivot_table(
            index="auto",
            columns="categoria",
            values="cantidad",
            aggfunc="sum",
            fill_value=0
        )
        print(resumen.to_string())

    print(f"\nArchivo generado: {SALIDA}")


if __name__ == "__main__":
    main()
