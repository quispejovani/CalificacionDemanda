
from pathlib import Path
import pymupdf
import re

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

CASOS = [
    "caso_003",
    "caso_005",
    "CASO_018",
    "CASO_030",
    "CASO_046",
]

MARCADORES = re.compile(
    r"SE\s+RESUELVE|RESUELVE\s*:|"
    r"SE\s+DECIDE|DECIDE\s*:|"
    r"DECLAR[AO]|ADMIT[IO]|IMPROCEDENTE|INADMISIBLE",
    re.IGNORECASE,
)

lineas = []

for caso in CASOS:
    carpeta = RAW / caso

    if not carpeta.exists():
        continue

    for ruta in sorted(carpeta.glob("*.pdf")):
        if not ruta.stem.lower().startswith("auto"):
            continue

        lineas.append(f"\n{'=' * 70}")
        lineas.append(f"CASO: {caso} | AUTO: {ruta.name}")

        with pymupdf.open(ruta) as doc:
            for numero, pagina in enumerate(doc, start=1):
                texto = pagina.get_text("text")
                coincidencias = list(
                    MARCADORES.finditer(texto)
                )

                if not coincidencias:
                    continue

                lineas.append(f"\n--- PÁGINA {numero} ---")

                for m in coincidencias:
                    inicio = max(0, m.start() - 180)
                    fin = min(len(texto), m.end() + 450)

                    fragmento = texto[inicio:fin]
                    lineas.append(fragmento)
                    lineas.append("-" * 30)

salida = OUT / "revision_autos_prioritarios.txt"
salida.write_text(
    "\n".join(lineas), encoding="utf-8"
)

print("Reporte generado:", salida)
print("Casos revisados:", len(CASOS))
