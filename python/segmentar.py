"""
RitmoEdge - Segmentación
------------------------
Divide los archivos CSV crudos del acelerómetro
en ventanas temporales.

Entrada:
    datos/crudos/<genero>/*.csv

Salida:
    datos/segmentos/<genero>/*.csv
"""

from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CARPETA_CRUDOS = BASE_DIR / "datos" / "crudos"
CARPETA_SEGMENTOS = BASE_DIR / "datos" / "segmentos"

GENEROS = [
    "salsa",
    "merengue",
    "electronica"
]

# Duración de cada ventana
DURACION_SEGMENTO_MS = 2000

# Solapamiento del 50 %
SOLAPAMIENTO = 0.50


# ============================================================
# SEGMENTAR UN ARCHIVO
# ============================================================

def segmentar_archivo(ruta_csv, genero):

    df = pd.read_csv(ruta_csv)

    columnas_requeridas = [
        "timestamp",
        "ax",
        "ay",
        "az"
    ]

    for columna in columnas_requeridas:
        if columna not in df.columns:
            raise ValueError(
                f"Falta la columna '{columna}' "
                f"en {ruta_csv.name}"
            )

    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    if len(df) < 2:
        print(
            f"Archivo ignorado: {ruta_csv.name}"
        )
        return 0

    inicio = df["timestamp"].iloc[0]
    fin = df["timestamp"].iloc[-1]

    paso_ms = int(
        DURACION_SEGMENTO_MS
        * (1 - SOLAPAMIENTO)
    )

    segmento_numero = 1
    inicio_ventana = inicio

    carpeta_salida = (
        CARPETA_SEGMENTOS / genero
    )

    carpeta_salida.mkdir(
        parents=True,
        exist_ok=True
    )

    while (
        inicio_ventana + DURACION_SEGMENTO_MS
        <= fin
    ):

        fin_ventana = (
            inicio_ventana
            + DURACION_SEGMENTO_MS
        )

        segmento = df[
            (df["timestamp"] >= inicio_ventana)
            &
            (df["timestamp"] < fin_ventana)
        ].copy()

        if len(segmento) > 0:

            nombre = (
                f"{genero}_"
                f"segmento_{segmento_numero:03d}.csv"
            )

            ruta_salida = (
                carpeta_salida / nombre
            )

            segmento.to_csv(
                ruta_salida,
                index=False
            )

            segmento_numero += 1

        inicio_ventana += paso_ms

    return segmento_numero - 1


# ============================================================
# PROCESAR TODOS LOS ARCHIVOS
# ============================================================

def ejecutar_segmentacion():

    print("=" * 60)
    print("       RITMOEDGE - SEGMENTACIÓN")
    print("=" * 60)

    total_segmentos = 0

    for genero in GENEROS:

        carpeta = (
            CARPETA_CRUDOS / genero
        )

        if not carpeta.exists():

            print(
                f"\nNo existe la carpeta: "
                f"{carpeta}"
            )

            continue

        archivos = sorted(
            carpeta.glob("*.csv")
        )

        if not archivos:

            print(
                f"\nNo hay CSV en: "
                f"{carpeta}"
            )

            continue

        print(
            f"\nGÉNERO: {genero.upper()}"
        )

        for archivo in archivos:

            print(
                f"  Procesando: "
                f"{archivo.name}"
            )

            cantidad = segmentar_archivo(
                archivo,
                genero
            )

            print(
                f"  Segmentos creados: "
                f"{cantidad}"
            )

            total_segmentos += cantidad

    print("\n" + "=" * 60)
    print(
        f"TOTAL SEGMENTOS: "
        f"{total_segmentos}"
    )
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    ejecutar_segmentacion()