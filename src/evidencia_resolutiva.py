
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pymupdf


BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SALIDA = (
    BASE / "data" / "processed"
    / "evidencia_resolutiva.csv"
)

PATRONES = {
    "MARCADOR": (
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
    "CONCILIACION": (
        r"\bCONCILIACION\b"
    ),
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )
    return re.sub(
        r"\s+", " ", texto.upper()
    ).strip()


def extraer_evidencias(ruta):
    registros = []

    with pymupdf.open(ruta) as pdf:
        for pagina_num, pagina in enumerate(pdf, 1):
            texto = normalizar(pagina.get_text("text"))

            for categoria, patron in PATRONES.items():
                for coincidencia in re.finditer(
                    patron, texto
                ):
                    inicio = max(
                        0, coincidencia.start() - 100
                    )
                    fin = min(
                        len(texto),
                        coincidencia.end() + 220
                    )

                    fragmento = texto[inicio:fin]

                    registros.append({
                        "auto": ruta.name,
                        "pagina": pagina_num,
                        "categoria": categoria,
                        "fragmento": fragmento,
                    })

    return registros


def main():
    registros = []

    for ruta in sorted(RAW.rglob("auto_*.pdf")):
        try:
            registros.extend(
                extraer_evidencias(ruta)
            )
        except Exception as error:
            print(
                f"Error en {ruta.name}: "
                f"{type(error).__name__}"
            )

    columnas = [
        "auto",
        "pagina",
        "categoria",
        "fragmento",
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

    print("\nEXTRACCION DE EVIDENCIAS")
    print("=" * 45)
    print(f"Documentos analizados: {len(set(df['auto']))}")
    print(f"Fragmentos encontrados: {len(df)}")
    print(f"Archivo generado: {SALIDA}")
    print(
        "\nLos fragmentos contienen texto judicial."
        "\nNo subir este CSV a GitHub."
    )


if __name__ == "__main__":
    main()
