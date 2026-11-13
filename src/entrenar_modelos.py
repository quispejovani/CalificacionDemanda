
from pathlib import Path
from datetime import datetime
import json
import time

import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import LeaveOneOut
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix
)

BASE = Path(__file__).resolve().parents[1]
DATOS = BASE / "data" / "processed" / "dataset_filtrado_101.csv"
SALIDA = BASE / "results"
MODELOS = BASE / "models"

SALIDA.mkdir(exist_ok=True)
MODELOS.mkdir(exist_ok=True)

SEED = 42

def crear_modelos():
    return {
        "E0_TFIDF_LOGREG": Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 1),
                min_df=1,
                max_features=3000,
                sublinear_tf=True
            )),
            ("modelo", LogisticRegression(
                max_iter=1000,
                random_state=SEED,
                class_weight="balanced"
            ))
        ]),
        "E1_TFIDF_BIGRAM_LOGREG": Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                max_features=5000,
                sublinear_tf=True
            )),
            ("modelo", LogisticRegression(
                max_iter=1000,
                random_state=SEED,
                class_weight="balanced"
            ))
        ]),
        "E2_TFIDF_NB": Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                max_features=5000
            )),
            ("modelo", MultinomialNB(alpha=1.0))
        ])
    }

def main():
    df = pd.read_csv(DATOS, dtype=str).fillna("")

    df["caso_id"] = df["caso_id"].str.upper().str.strip()
    df["apto_entrenamiento"] = (
        df["apto_entrenamiento"].str.lower() == "true"
    )

    datos = df[
        df["apto_entrenamiento"]
        & df["etiqueta_inicial"].isin([
            "ADMISIBLE", "INADMISIBLE", "IMPROCEDENTE"
        ])
        & (df["texto"].str.strip() != "")
    ].copy()

    if datos["caso_id"].duplicated().any():
        raise ValueError("Hay expedientes duplicados.")

    X = datos["texto"].tolist()
    y = datos["etiqueta_inicial"].tolist()
    casos = datos["caso_id"].tolist()

    print("\n=== DATOS PARA ENTRENAMIENTO ===")
    print("Expedientes:", len(datos))
    print(datos["etiqueta_inicial"].value_counts())

    if len(datos) < 4 or len(set(y)) < 2:
        raise ValueError(
            "Se necesitan al menos cuatro registros "
            "y dos clases para esta demostracion."
        )

    resultados = []
    predicciones = []

    for nombre, pipeline in crear_modelos().items():
        print(f"\nEntrenando {nombre}...")

        inicio = time.perf_counter()
        reales = []
        predichos = []

        # Validación Leave-One-Out.
        for train_idx, test_idx in LeaveOneOut().split(X):
            x_train = [X[i] for i in train_idx]
            y_train = [y[i] for i in train_idx]
            x_test = [X[i] for i in test_idx]

            modelo = crear_modelos()[nombre]

            modelo.fit(x_train, y_train)
            pred = modelo.predict(x_test)[0]

            reales.append(y[test_idx[0]])
            predichos.append(pred)

            predicciones.append({
                "experimento": nombre,
                "caso_id": casos[test_idx[0]],
                "real": y[test_idx[0]],
                "prediccion": pred
            })

        duracion = time.perf_counter() - inicio

        
        resultados.append({
            "experimento": nombre,
            "n_casos": len(datos),
            "accuracy": accuracy_score(
                reales, predichos
            ),
            "f1_macro": f1_score(
                reales,
                predichos,
                average="macro",
                labels=["ADMISIBLE", "INADMISIBLE"],
                zero_division=0
            ),
            "precision_macro": precision_score(
                reales,
                predichos,
                average="macro",
                labels=["ADMISIBLE", "INADMISIBLE"],
                zero_division=0
            ),
            "recall_macro": recall_score(
                reales,
                predichos,
                average="macro",
                labels=["ADMISIBLE", "INADMISIBLE"],
                zero_division=0
            ),
            "tiempo_cv_segundos": round(duracion, 4)
        })

        # Modelo final entrenado con los cuatro casos.
        modelo_final = crear_modelos()[nombre]
        modelo_final.fit(X, y)
        joblib.dump(
            modelo_final,
            MODELOS / f"{nombre}.joblib"
        )

    resultados_df = pd.DataFrame(resultados)
    predicciones_df = pd.DataFrame(predicciones)

    resultados_df.to_csv(
        SALIDA / "comparacion_experimentos.csv",
        index=False,
        encoding="utf-8-sig"
    )

    predicciones_df.to_csv(
        SALIDA / "predicciones_validacion.csv",
        index=False,
        encoding="utf-8-sig"
    )

    metadata = {
        "fecha": datetime.now().isoformat(),
        "semilla": SEED,
        "validacion": "Leave-One-Out",
        "n_casos": len(datos),
        "clases_observadas": sorted(set(y)),
        "clases_objetivo": [
            "ADMISIBLE", "INADMISIBLE", "IMPROCEDENTE"
        ],
        "limitacion": (
            "Experimento exploratorio con muestra muy reducida. "
            "No valida el rendimiento para uso judicial."
        )
    }

    with open(
        SALIDA / "metadata_experimentos.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("\n=== COMPARACION DE EXPERIMENTOS ===")
    print(resultados_df.to_string(index=False))

    print("\nArchivos generados:")
    print(SALIDA / "comparacion_experimentos.csv")
    print(SALIDA / "predicciones_validacion.csv")
    print(SALIDA / "metadata_experimentos.json")
    print(MODELOS)

     # E3: Baseline trivial (clase mayoritaria)
    pred_dummy = []

    for train_idx, test_idx in LeaveOneOut().split(X):
        x_train = [X[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]
        x_test = [X[i] for i in test_idx]

        dummy = DummyClassifier(strategy="most_frequent")
        dummy.fit(x_train, y_train)

        pred_dummy.append(dummy.predict(x_test)[0])

    # Fuera del FOR, pero dentro de main()
    print("\n=== E3: BASELINE TRIVIAL ===")

    print(
        "Accuracy:",
        round(accuracy_score(y, pred_dummy), 4)
    )

    print(
        "F1 macro:",
        round(
            f1_score(
                y,
                pred_dummy,
                average="macro",
                labels=["ADMISIBLE", "INADMISIBLE"],
                zero_division=0
            ),
            4
        )
    )


if __name__ == "__main__":
    main()
