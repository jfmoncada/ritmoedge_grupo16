"""
RitmoEdge - Iteración 2
-----------------------
Procesamiento de señales del acelerómetro.

Cambio respecto a Iteración 1:
    Se incorpora la magnitud de aceleración.

Entrada:
    datos/segmentos/<genero>/*.csv

Salida:
    datos/dataset_iteracion2.csv
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
    BASE_DIR
    / "datos"
    / "dataset_iteracion2.csv"
)

GENEROS = [
    "salsa",
    "merengue",
    "electronica"
]


# ============================================================
# CARACTERÍSTICAS
# ============================================================

def calcular_caracteristicas(
    valores,
    prefijo
):
    """
    Calcula características estadísticas
    para una señal.
    """

    valores = np.asarray(
        valores,
        dtype=float
    )

    return {
        f"{prefijo}_mean":
            np.mean(valores),

        f"{prefijo}_std":
            np.std(valores),

        f"{prefijo}_min":
            np.min(valores),

        f"{prefijo}_max":
            np.max(valores),

        f"{prefijo}_rms":
            np.sqrt(
                np.mean(
                    valores ** 2
                )
            ),

        f"{prefijo}_energy":
            np.mean(
                valores ** 2
            )
    }


# ============================================================
# PROCESAR SEGMENTO
# ============================================================

def procesar_segmento(
    ruta,
    genero
):

    df = pd.read_csv(ruta)

    columnas = [
        "ax",
        "ay",
        "az"
    ]

    for columna in columnas:

        if columna not in df.columns:

            raise ValueError(
                f"La columna '{columna}' "
                f"no existe en {ruta.name}"
            )

    caracteristicas = {}

    # --------------------------------------------------------
    # X, Y, Z
    # --------------------------------------------------------

    for eje in columnas:

        nuevas = calcular_caracteristicas(
            df[eje],
            eje
        )

        caracteristicas.update(
            nuevas
        )

    # --------------------------------------------------------
    # MAGNITUD
    # --------------------------------------------------------

    magnitud = np.sqrt(
        df["ax"] ** 2
        +
        df["ay"] ** 2
        +
        df["az"] ** 2
    )

    nuevas = calcular_caracteristicas(
        magnitud,
        "magnitud"
    )

    caracteristicas.update(
        nuevas
    )

    # --------------------------------------------------------
    # Información adicional
    # --------------------------------------------------------

    caracteristicas["genero"] = genero
    caracteristicas["archivo"] = ruta.name

    return caracteristicas


# ============================================================
# PROCESAMIENTO GENERAL
# ============================================================

def procesar():

    print("=" * 60)
    print("     RITMOEDGE - PROCESAMIENTO ITERACIÓN 2")
    print("=" * 60)

    filas = []

    for genero in GENEROS:

        carpeta = (
            CARPETA_SEGMENTOS / genero
        )

        if not carpeta.exists():

            print(
                f"\nADVERTENCIA: "
                f"No existe {carpeta}"
            )

            continue

        archivos = sorted(
            carpeta.glob("*.csv")
        )

        print(
            f"\n{genero.upper()}: "
            f"{len(archivos)} segmentos"
        )

        for archivo in archivos:

            try:

                fila = procesar_segmento(
                    archivo,
                    genero
                )

                filas.append(
                    fila
                )

            except Exception as error:

                print(
                    f"ERROR en "
                    f"{archivo.name}: "
                    f"{error}"
                )

    if not filas:

        raise RuntimeError(
            "No se encontraron segmentos "
            "para procesar."
        )

    dataset = pd.DataFrame(
        filas
    )

    # --------------------------------------------------------
    # Ordenar columnas
    # --------------------------------------------------------

    columnas_identificacion = [
        "genero",
        "archivo"
    ]

    columnas_features = [
        columna
        for columna in dataset.columns
        if columna not in columnas_identificacion
    ]

    dataset = dataset[
        columnas_identificacion
        +
        columnas_features
    ]

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------

    ARCHIVO_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        ARCHIVO_SALIDA,
        index=False
    )

    print("\n" + "=" * 60)
    print("DATASET ITERACIÓN 2 GENERADO")
    print("=" * 60)

    print(
        f"Registros: "
        f"{len(dataset)}"
    )

    print(
        f"Características: "
        f"{len(columnas_features)}"
    )

    print(
        f"\nArchivo:"
        f"\n{ARCHIVO_SALIDA}"
    )

    print(
        "\nDistribución:"
    )

    print(
        dataset["genero"]
        .value_counts()
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    procesar()