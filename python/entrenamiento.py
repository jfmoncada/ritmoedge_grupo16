"""
RitmoEdge - Entrenamiento
-------------------------
Entrena un clasificador Random Forest
para reconocer el género musical.

Entrada:
    datos/dataset_procesado.csv

Salida:
    modelos/modelo_random_forest.pkl
"""

from pathlib import Path
import pandas as pd

from sklearn.model_selection import (
    train_test_split
)

from sklearn.ensemble import (
    RandomForestClassifier
)

from sklearn.preprocessing import (
    StandardScaler
)

from sklearn.pipeline import (
    Pipeline
)

import joblib


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ARCHIVO_DATASET = (
    BASE_DIR
    / "datos"
    / "dataset_procesado.csv"
)

CARPETA_MODELOS = (
    BASE_DIR / "modelos"
)

ARCHIVO_MODELO = (
    CARPETA_MODELOS
    / "modelo_random_forest.pkl"
)


# ============================================================
# ENTRENAMIENTO
# ============================================================

def entrenar():

    print("=" * 60)
    print("       RITMOEDGE - ENTRENAMIENTO")
    print("=" * 60)

    if not ARCHIVO_DATASET.exists():

        raise FileNotFoundError(
            "No existe dataset_procesado.csv. "
            "Ejecuta primero procesamiento.py"
        )

    df = pd.read_csv(
        ARCHIVO_DATASET
    )

    if len(df) < 3:

        raise RuntimeError(
            "No hay suficientes registros."
        )

    columnas_excluir = [
        "genero",
        "archivo"
    ]

    X = df.drop(
        columns=columnas_excluir
    )

    y = df["genero"]

    print(
        f"\nCaracterísticas: "
        f"{X.shape[1]}"
    )

    print(
        f"Muestras: "
        f"{X.shape[0]}"
    )

    print(
        "\nDistribución:"
    )

    print(
        y.value_counts()
    )

    # --------------------------------------------------------
    # División entrenamiento / prueba
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

    print(
        f"\nEntrenamiento: "
        f"{len(X_train)}"
    )

    print(
        f"Prueba: "
        f"{len(X_test)}"
    )

    # --------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------

    modelo = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler()
            ),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced"
                )
            )
        ]
    )

    print(
        "\nEntrenando modelo..."
    )

    modelo.fit(
        X_train,
        y_train
    )

    print(
        "Entrenamiento terminado."
    )

    # --------------------------------------------------------
    # Guardar modelo
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
        f"\nModelo guardado en:"
        f"\n{ARCHIVO_MODELO}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    entrenar()