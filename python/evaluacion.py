"""
RitmoEdge - Evaluación
----------------------
Evalúa el modelo entrenado utilizando
el dataset procesado.

Salida:
    resultados/metricas.txt
    resultados/matriz_confusion.csv
"""

from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ARCHIVO_DATASET = (
    BASE_DIR
    / "datos"
    / "dataset_procesado.csv"
)

ARCHIVO_MODELO = (
    BASE_DIR
    / "modelos"
    / "modelo_random_forest.pkl"
)

CARPETA_RESULTADOS = (
    BASE_DIR / "resultados"
)


# ============================================================
# EVALUACIÓN
# ============================================================

def evaluar():

    print("=" * 60)
    print("       RITMOEDGE - EVALUACIÓN")
    print("=" * 60)

    if not ARCHIVO_DATASET.exists():

        raise FileNotFoundError(
            "No existe el dataset procesado."
        )

    if not ARCHIVO_MODELO.exists():

        raise FileNotFoundError(
            "No existe el modelo entrenado."
        )

    df = pd.read_csv(
        ARCHIVO_DATASET
    )

    X = df.drop(
        columns=[
            "genero",
            "archivo"
        ]
    )

    y = df["genero"]

    # --------------------------------------------------------
    # Misma división utilizada para evaluación
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    # --------------------------------------------------------
    # Cargar modelo
    # --------------------------------------------------------

    modelo = joblib.load(
        ARCHIVO_MODELO
    )

    # --------------------------------------------------------
    # Predicciones
    # --------------------------------------------------------

    y_pred = modelo.predict(
        X_test
    )

    # --------------------------------------------------------
    # Métricas
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    reporte = classification_report(
        y_test,
        y_pred
    )

    matriz = confusion_matrix(
        y_test,
        y_pred
    )

    # --------------------------------------------------------
    # Mostrar resultados
    # --------------------------------------------------------

    print(
        f"\nAccuracy: "
        f"{accuracy:.4f}"
    )

    print(
        "\nReporte de clasificación:"
    )

    print(
        reporte
    )

    print(
        "\nMatriz de confusión:"
    )

    print(
        matriz
    )

    # --------------------------------------------------------
    # Guardar resultados
    # --------------------------------------------------------

    CARPETA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    archivo_metricas = (
        CARPETA_RESULTADOS
        / "metricas.txt"
    )

    with open(
        archivo_metricas,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            "RITMOEDGE - RESULTADOS\n"
        )

        archivo.write(
            "=" * 50
            + "\n\n"
        )

        archivo.write(
            f"Accuracy: "
            f"{accuracy:.4f}\n\n"
        )

        archivo.write(
            "Reporte de clasificación:\n"
        )

        archivo.write(
            reporte
        )

    archivo_matriz = (
        CARPETA_RESULTADOS
        / "matriz_confusion.csv"
    )

    pd.DataFrame(
        matriz,
        index=modelo.classes_,
        columns=modelo.classes_
    ).to_csv(
        archivo_matriz
    )

    print(
        f"\nMétricas guardadas en:"
        f"\n{archivo_metricas}"
    )

    print(
        f"\nMatriz guardada en:"
        f"\n{archivo_matriz}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluar()