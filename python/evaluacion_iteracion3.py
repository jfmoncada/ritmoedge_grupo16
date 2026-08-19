"""
RitmoEdge - Iteración 3
-----------------------
Evaluación del modelo SVM.

Salida:
    resultados/iteracion_3/metricas.txt
    resultados/iteracion_3/matriz_confusion.csv
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
    / "dataset_iteracion2.csv"
)

ARCHIVO_MODELO = (
    BASE_DIR
    / "modelos"
    / "modelo_iteracion_3.pkl"
)

CARPETA_RESULTADOS = (
    BASE_DIR
    / "resultados"
    / "iteracion_3"
)


# ============================================================
# EVALUACIÓN
# ============================================================

def evaluar():

    print("=" * 60)
    print("       RITMOEDGE - EVALUACIÓN ITERACIÓN 3")
    print("=" * 60)

    if not ARCHIVO_DATASET.exists():

        raise FileNotFoundError(
            "No existe dataset_iteracion2.csv."
        )

    if not ARCHIVO_MODELO.exists():

        raise FileNotFoundError(
            "No existe modelo_iteracion_3.pkl."
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
    # División
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
    # Modelo
    # --------------------------------------------------------

    modelo = joblib.load(
        ARCHIVO_MODELO
    )

    # --------------------------------------------------------
    # Predicción
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
    # Mostrar
    # --------------------------------------------------------

    print(
        f"\nAccuracy: "
        f"{accuracy:.4f}"
    )

    print(
        "\nReporte:"
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
    # Guardar
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
            "RITMOEDGE - ITERACIÓN 3\n"
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
            "Reporte de clasificación:\n\n"
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
        f"\nResultados guardados en:"
        f"\n{CARPETA_RESULTADOS}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluar()