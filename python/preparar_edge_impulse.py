"""
RitmoEdge - Preparación de CSV para Edge Impulse
------------------------------------------------
Cambia únicamente el nombre de la columna:

    timestamp  ->  timestamp

Entrada:
    datos/segmentos/
        ├── electronica/*.csv
        ├── merengue/*.csv
        └── salsa/*.csv

No modifica los valores de:
    ax
    ay
    az
"""

from pathlib import Path
import csv


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CARPETA_SEGMENTOS = (
    BASE_DIR / "datos" / "segmentos"
)

GENEROS = [
    "salsa",
    "merengue",
    "electronica"
]


# ============================================================
# PREPARAR UN CSV
# ============================================================

def preparar_csv(ruta_csv: Path) -> bool:
    """
    Cambia únicamente:

        timestamp -> timestamp

    Retorna:
        True  = archivo modificado
        False = archivo omitido
    """

    try:

        with open(
            ruta_csv,
            mode="r",
            newline="",
            encoding="utf-8-sig"
        ) as archivo:

            filas = list(
                csv.reader(archivo)
            )

    except Exception as error:

        print(
            f"ERROR leyendo "
            f"{ruta_csv.name}: {error}"
        )

        return False


    # --------------------------------------------------------
    # Validar archivo vacío
    # --------------------------------------------------------

    if not filas:

        print(
            f"OMITIDO: "
            f"{ruta_csv.name} está vacío."
        )

        return False


    encabezado = filas[0]


    # --------------------------------------------------------
    # Validar columnas del acelerómetro
    # --------------------------------------------------------

    columnas_requeridas = [
        "ax",
        "ay",
        "az"
    ]

    for columna in columnas_requeridas:

        if columna not in encabezado:

            print(
                f"OMITIDO: "
                f"{ruta_csv.name} "
                f"no contiene '{columna}'."
            )

            return False


    # --------------------------------------------------------
    # Verificar si ya está preparado
    # --------------------------------------------------------

    if "timestamp" in encabezado:

        print(
            f"YA PREPARADO: "
            f"{ruta_csv.name}"
        )

        return False


    # --------------------------------------------------------
    # Verificar timestamp
    # --------------------------------------------------------

    if "timestamp" not in encabezado:

        print(
            f"OMITIDO: "
            f"{ruta_csv.name} "
            f"no contiene 'timestamp'."
        )

        return False


    # --------------------------------------------------------
    # Cambiar únicamente el nombre de la columna
    # --------------------------------------------------------

    nuevo_encabezado = []

    for columna in encabezado:

        if columna == "timestamp":

            nuevo_encabezado.append(
                "timestamp"
            )

        else:

            nuevo_encabezado.append(
                columna
            )


    filas[0] = nuevo_encabezado


    # --------------------------------------------------------
    # Guardar archivo
    # --------------------------------------------------------

    try:

        with open(
            ruta_csv,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as archivo:

            escritor = csv.writer(
                archivo
            )

            escritor.writerows(
                filas
            )

    except Exception as error:

        print(
            f"ERROR escribiendo "
            f"{ruta_csv.name}: {error}"
        )

        return False


    print(
        f"OK: {ruta_csv.name}"
    )

    return True


# ============================================================
# PROCESAR TODOS LOS GÉNEROS
# ============================================================

def ejecutar():

    print("=" * 60)

    print(
        "       RITMOEDGE - "
        "PREPARACIÓN EDGE IMPULSE"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # Verificar carpeta principal
    # --------------------------------------------------------

    if not CARPETA_SEGMENTOS.exists():

        print(
            "\nERROR: No existe la carpeta:"
        )

        print(
            CARPETA_SEGMENTOS
        )

        return


    total_archivos = 0
    archivos_modificados = 0


    # ========================================================
    # RECORRER GÉNEROS
    # ========================================================

    for genero in GENEROS:

        carpeta_genero = (
            CARPETA_SEGMENTOS / genero
        )


        print(
            f"\nGÉNERO: "
            f"{genero.upper()}"
        )

        print("-" * 40)


        # ----------------------------------------------------
        # Verificar carpeta del género
        # ----------------------------------------------------

        if not carpeta_genero.exists():

            print(
                f"No existe la carpeta: "
                f"{carpeta_genero}"
            )

            continue


        # ----------------------------------------------------
        # Buscar CSV
        # ----------------------------------------------------

        archivos = sorted(
            carpeta_genero.glob(
                "*.csv"
            )
        )


        if not archivos:

            print(
                "No hay archivos CSV."
            )

            continue


        print(
            f"Archivos encontrados: "
            f"{len(archivos)}"
        )


        # ----------------------------------------------------
        # Procesar archivos
        # ----------------------------------------------------

        for archivo in archivos:

            total_archivos += 1

            modificado = preparar_csv(
                archivo
            )

            if modificado:

                archivos_modificados += 1


    # ========================================================
    # RESUMEN
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "PROCESO FINALIZADO"
    )

    print(
        "=" * 60
    )

    print(
        f"Archivos revisados:   "
        f"{total_archivos}"
    )

    print(
        f"Archivos modificados: "
        f"{archivos_modificados}"
    )

    print(
        "=" * 60
    )


    print(
        "\nEncabezado esperado:"
    )

    print(
        "timestamp,ax,ay,az"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    ejecutar()