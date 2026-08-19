"""
RitmoEdge - Iteración 3
-----------------------
Entrenamiento utilizando SVM.

Características:
    Las mismas utilizadas en Iteración 2.

Cambio respecto a Iteración 2:
    Random Forest → SVM

Entrada:
    datos/dataset_iteracion2.csv

Salida:
    modelos/modelo_iteracion_3.pkl
"""

from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split
)

from sklearn.pipeline import (
    Pipeline
)

from sklearn.preprocessing import (
    StandardScaler
)

from sklearn.svm import (
    SVC
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

CARPETA_MODELOS = (
    BASE_DIR / "modelos"
)

ARCHIVO_MODELO = (
    CARPETA_MODELOS
    / "modelo_iteracion_3.pkl"
)


# ============================================================
# ENTRENAMIENTO
# ============================================================

def entrenar():

    print("=" * 60)
    print("      RITMOEDGE - ENTRENAMIENTO ITERACIÓN 3")
    print("=" * 60)

    if not ARCHIVO_DATASET.exists():

        raise FileNotFoundError(
            "No existe dataset_iteracion2.csv.\n"
            "Ejecuta primero la Iteración 2."
        )

    df = pd.read_csv(
        ARCHIVO_DATASET
    )

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------

    X = df.drop(
        columns=[
            "genero",
            "archivo"
        ]
    )

    y = df["genero"]

    print(
        f"\nMuestras: {len(X)}"
    )

    print(
        f"Características: "
        f"{X.shape[1]}"
    )

    print(
        "\nDistribución:"
    )

    print(
        y.value_counts()
    )

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
    # SVM
    # --------------------------------------------------------

    modelo = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler()
            ),
            (
                "classifier",
                SVC(
                    kernel="rbf",
                    C=1.0,
                    gamma="scale"
                )
            )
        ]
    )

    print(
        "\nEntrenando SVM..."
    )

    modelo.fit(
        X_train,
        y_train
    )

    print(
        "Entrenamiento completado."
    )

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------

    CARPETA_MODELOS.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        modelo,
        ARCHIVO_MODELO
    )

    print(
        f"\nModelo guardado:"
        f"\n{ARCHIVO_MODELO}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    entrenar()