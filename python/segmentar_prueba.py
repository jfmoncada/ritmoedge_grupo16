"""
RitmoEdge - Segmentación de datos de prueba
-------------------------------------------
Divide los nuevos archivos CSV de evaluación
en ventanas temporales de 2 segundos.

Entrada:
    datos/nuevos/<genero>/*.csv

Salida:
    datos/nuevos_segmentos/<genero>/*.csv

IMPORTANTE:
Estos datos NO se utilizan para entrenamiento.
Son exclusivamente para evaluar el modelo ya entrenado.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CARPETA_ENTRADA = (
    BASE_DIR / "datos" / "nuevos"
)

CARPETA_SALIDA = (
    BASE_DIR / "datos" / "nuevos_segmentos"
)

GENEROS = [
    "salsa",
    "merengue",
    "electronica"
]

# Misma configuración utilizada
# para los datos originales
DURACION_SEGMENTO_MS = 2000

SOLAPAMIENTO = 0.50


# ============================================================
# SEGMENTAR UN ARCHIVO
# ============================================================

def segmentar_archivo(ruta_csv, genero):

    print(
        f"\n  Procesando: {ruta_csv.name}"
    )

    # --------------------------------------------------------
    # Leer CSV
    # --------------------------------------------------------

    df = pd.read_csv(ruta_csv)

    columnas_requeridas = [
        "timestamp",
        "ax",
        "ay",
        "az"
    ]

    # --------------------------------------------------------
    # Validar columnas
    # --------------------------------------------------------

    for columna in columnas_requeridas:

        if columna not in df.columns:

            raise ValueError(
                f"Falta la columna "
                f"'{columna}' en "
                f"{ruta_csv.name}"
            )

    # --------------------------------------------------------
    # Ordenar por timestamp
    # --------------------------------------------------------

    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    if len(df) < 2:

        print(
            "  Archivo ignorado: "
            "no tiene suficientes muestras."
        )

        return 0

    # --------------------------------------------------------
    # Rango temporal
    # --------------------------------------------------------

    inicio = (
        df["timestamp"].iloc[0]
    )

    fin = (
        df["timestamp"].iloc[-1]
    )

    # --------------------------------------------------------
    # Calcular paso de ventana
    # --------------------------------------------------------

    paso_ms = int(
        DURACION_SEGMENTO_MS
        * (1 - SOLAPAMIENTO)
    )

    # Para 2000 ms y 50%:
    # paso = 1000 ms

    print(
        f"  Duración: "
        f"{(fin - inicio) / 1000:.2f} segundos"
    )

    print(
        f"  Ventana: "
        f"{DURACION_SEGMENTO_MS} ms"
    )

    print(
        f"  Paso: "
        f"{paso_ms} ms"
    )

    # --------------------------------------------------------
    # Carpeta de salida
    # --------------------------------------------------------

    carpeta_salida = (
        CARPETA_SALIDA / genero
    )

    carpeta_salida.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Crear ventanas
    # --------------------------------------------------------

    segmento_numero = 1

    inicio_ventana = inicio

    while (
        inicio_ventana
        + DURACION_SEGMENTO_MS
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

        # ----------------------------------------------------
        # Guardar segmento
        # ----------------------------------------------------

        if len(segmento) > 0:

            nombre = (
                f"{genero}_prueba_"
                f"segmento_"
                f"{segmento_numero:03d}.csv"
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

    cantidad = segmento_numero - 1

    print(
        f"  Segmentos creados: "
        f"{cantidad}"
    )

    return cantidad


# ============================================================
# PROCESAR TODOS LOS GÉNEROS
# ============================================================

def ejecutar_segmentacion():

    print("=" * 65)

    print(
        "       RITMOEDGE - SEGMENTACIÓN DE PRUEBA"
    )

    print("=" * 65)

    print(
        "\nEstos datos serán utilizados "
        "únicamente para evaluación."
    )

    print(
        "No serán incorporados al entrenamiento."
    )

    total_segmentos = 0

    # --------------------------------------------------------
    # Recorrer géneros
    # --------------------------------------------------------

    for genero in GENEROS:

        carpeta = (
            CARPETA_ENTRADA / genero
        )

        print(
            f"\nGÉNERO: {genero.upper()}"
        )

        # ----------------------------------------------------
        # Verificar carpeta
        # ----------------------------------------------------

        if not carpeta.exists():

            print(
                f"  No existe la carpeta:"
                f"\n  {carpeta}"
            )

            continue

        # ----------------------------------------------------
        # Buscar CSV
        # ----------------------------------------------------

        archivos = sorted(
            carpeta.glob("*.csv")
        )

        if not archivos:

            print(
                "  No hay archivos CSV."
            )

            continue

        # ----------------------------------------------------
        # Procesar archivos
        # ----------------------------------------------------

        for archivo in archivos:

            cantidad = segmentar_archivo(
                archivo,
                genero
            )

            total_segmentos += cantidad

    # --------------------------------------------------------
    # Resultado final
    # --------------------------------------------------------

    print("\n" + "=" * 65)

    print(
        f"TOTAL SEGMENTOS CREADOS: "
        f"{total_segmentos}"
    )

    print("=" * 65)

    print(
        "\nSalida:"
    )

    print(
        CARPETA_SALIDA
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    ejecutar_segmentacion()