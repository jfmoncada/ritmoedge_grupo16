"""
RitmoEdge - Procesamiento
-------------------------
Extrae características estadísticas de los segmentos
del acelerómetro.

Entrada:
    datos/segmentos/<genero>/*.csv

Salida:
    datos/dataset_procesado.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CARPETA_SEGMENTOS = (
    BASE_DIR / "datos" / "segmentos"
)

ARCHIVO_SALIDA = (
    BASE_DIR / "datos" / "dataset_procesado.csv"
)

GENEROS = [
    "salsa",
    "merengue",
    "electronica"
]


# ============================================================
# EXTRAER CARACTERÍSTICAS
# ============================================================

def extraer_caracteristicas(df):

    resultado = {}

    ejes = [
        "ax",
        "ay",
        "az"
    ]

    for eje in ejes:

        valores = df[eje].astype(float)

        resultado[f"{eje}_mean"] = (
            valores.mean()
        )

        resultado[f"{eje}_std"] = (
            valores.std()
        )

        resultado[f"{eje}_min"] = (
            valores.min()
        )

        resultado[f"{eje}_max"] = (
            valores.max()
        )

        resultado[f"{eje}_rms"] = (
            np.sqrt(
                np.mean(
                    valores ** 2
                )
            )
        )

        resultado[f"{eje}_energy"] = (
            np.mean(
                valores ** 2
            )
        )

    return resultado


# ============================================================
# PROCESAR SEGMENTOS
# ============================================================

def procesar():

    filas = []

    for genero in GENEROS:

        carpeta = (
            CARPETA_SEGMENTOS / genero
        )

        archivos = sorted(
            carpeta.glob("*.csv")
        )

        print(
            f"\nProcesando "
            f"{genero.upper()}: "
            f"{len(archivos)} segmentos"
        )

        for archivo in archivos:

            df = pd.read_csv(
                archivo
            )

            caracteristicas = (
                extraer_caracteristicas(df)
            )

            caracteristicas[
                "genero"
            ] = genero

            caracteristicas[
                "archivo"
            ] = archivo.name

            filas.append(
                caracteristicas
            )

    if not filas:

        raise RuntimeError(
            "No se encontraron segmentos."
        )

    dataset = pd.DataFrame(
        filas
    )

    columnas = [
        "genero",
        "archivo"
    ]

    dataset = dataset[
        columnas
        +
        [
            c for c in dataset.columns
            if c not in columnas
        ]
    ]

    ARCHIVO_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        ARCHIVO_SALIDA,
        index=False
    )

    print("\n" + "=" * 60)
    print("DATASET PROCESADO")
    print("=" * 60)

    print(
        f"Registros: {len(dataset)}"
    )

    print(
        f"Archivo: {ARCHIVO_SALIDA}"
    )

    print("\nDistribución:")

    print(
        dataset["genero"]
        .value_counts()
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    procesar()