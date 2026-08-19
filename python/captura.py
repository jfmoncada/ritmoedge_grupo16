"""
RitmoEdge
---------
Captura los datos del acelerómetro enviados
por el ESP32 mediante USB/Serial.

Clases de captura:
    - salsa
    - merengue
    - electronica

Salida:
    datos/crudos/<genero>/<genero>_YYYYMMDD_HHMMSS.csv
"""

from pathlib import Path
from datetime import datetime
import csv
import serial
import serial.tools.list_ports


# ============================================================
# CONFIGURACIÓN
# ============================================================

BAUDRATE = 115200

# Duración de cada captura
DURACION_SEGUNDOS = 30

# Géneros disponibles
GENEROS = [
    "salsa",
    "merengue",
    "electronica"
]

# Carpeta principal de datos crudos
CARPETA_SALIDA = (
    Path(__file__).resolve().parent.parent
    / "datos"
    / "crudos"
)


# ============================================================
# SELECCIONAR GÉNERO
# ============================================================

def seleccionar_genero():
    """
    Permite seleccionar el género musical
    correspondiente a la captura.
    """

    print("\n" + "=" * 40)
    print("       RITMOEDGE - CAPTURA")
    print("=" * 40)

    print("\nSelecciona el género musical:")

    for i, genero in enumerate(GENEROS, start=1):
        print(f"[{i}] {genero.capitalize()}")

    while True:

        try:

            opcion = int(
                input("\nOpción: ")
            )

            if 1 <= opcion <= len(GENEROS):

                genero = GENEROS[opcion - 1]

                print(
                    f"\nGénero seleccionado: "
                    f"{genero.upper()}"
                )

                return genero

        except ValueError:
            pass

        print(
            "Opción inválida. "
            "Selecciona uno de los géneros disponibles."
        )


# ============================================================
# BUSCAR PUERTO ESP32
# ============================================================

def listar_puertos():
    """
    Muestra los puertos serial disponibles.
    """

    puertos = list(
        serial.tools.list_ports.comports()
    )

    if not puertos:

        print(
            "No se encontraron puertos serial."
        )

        return []

    print("\nPuertos disponibles:")

    for i, puerto in enumerate(puertos):

        print(
            f"[{i}] {puerto.device} - "
            f"{puerto.description}"
        )

    return puertos


# ============================================================
# SELECCIONAR PUERTO
# ============================================================

def seleccionar_puerto():

    puertos = listar_puertos()

    if not puertos:

        raise RuntimeError(
            "No hay puertos serial disponibles."
        )

    while True:

        try:

            opcion = int(
                input(
                    "\nSelecciona el número "
                    "del ESP32: "
                )
            )

            if 0 <= opcion < len(puertos):

                return puertos[opcion].device

        except ValueError:

            pass

        print(
            "Opción inválida. "
            "Intenta nuevamente."
        )


# ============================================================
# CREAR CARPETA DEL GÉNERO
# ============================================================

def crear_carpeta_genero(genero):
    """
    Crea la carpeta correspondiente al género
    si todavía no existe.
    """

    carpeta_genero = (
        CARPETA_SALIDA
        / genero
    )

    carpeta_genero.mkdir(
        parents=True,
        exist_ok=True
    )

    return carpeta_genero


# ============================================================
# CREAR ARCHIVO CSV
# ============================================================

def crear_archivo(genero):
    """
    Crea el nombre y la ruta del archivo CSV.
    """

    carpeta_genero = (
        crear_carpeta_genero(genero)
    )

    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    nombre = (
        f"{genero}_{fecha}.csv"
    )

    ruta = (
        carpeta_genero
        / nombre
    )

    return ruta


# ============================================================
# CAPTURA DE DATOS
# ============================================================

def capturar():

    # --------------------------------------------------------
    # 1. Seleccionar género
    # --------------------------------------------------------

    genero = seleccionar_genero()

    # --------------------------------------------------------
    # 2. Seleccionar ESP32
    # --------------------------------------------------------

    puerto = seleccionar_puerto()

    print(
        f"\nConectando al ESP32 en {puerto}..."
    )

    # --------------------------------------------------------
    # 3. Abrir puerto serial
    # --------------------------------------------------------

    try:

        dispositivo = serial.Serial(
            port=puerto,
            baudrate=BAUDRATE,
            timeout=1
        )

    except serial.SerialException as error:

        print(
            f"\nERROR al abrir el puerto:\n{error}"
        )

        return

    print(
        "ESP32 conectado correctamente."
    )

    # --------------------------------------------------------
    # 4. Dar tiempo al ESP32 para reiniciarse
    # --------------------------------------------------------

    dispositivo.reset_input_buffer()

    # --------------------------------------------------------
    # 5. Crear archivo
    # --------------------------------------------------------

    ruta_csv = crear_archivo(
        genero
    )

    print(
        f"\nArchivo de salida:"
        f"\n{ruta_csv}"
    )

    print(
        f"\nGénero: {genero.upper()}"
    )

    print(
        f"Duración: "
        f"{DURACION_SEGUNDOS} segundos"
    )

    print(
        "\nPreparado..."
    )

    print(
        "La captura comenzará ahora."
    )

    # --------------------------------------------------------
    # 6. Iniciar captura
    # --------------------------------------------------------

    tiempo_inicio = datetime.now()

    contador = 0

    with open(
        ruta_csv,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        # ----------------------------------------------------
        # Encabezado CSV
        # ----------------------------------------------------

        escritor.writerow(
            [
                "timestamp",
                "ax",
                "ay",
                "az"
            ]
        )

        # ----------------------------------------------------
        # Bucle de captura
        # ----------------------------------------------------

        while True:

            tiempo_actual = (
                datetime.now()
            )

            segundos = (
                tiempo_actual
                - tiempo_inicio
            ).total_seconds()

            # ----------------------------------------------
            # Finalizar cuando se alcance la duración
            # ----------------------------------------------

            if segundos >= DURACION_SEGUNDOS:

                break

            # ----------------------------------------------
            # Leer línea del ESP32
            # ----------------------------------------------

            linea = (
                dispositivo.readline()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
                .strip()
            )

            if not linea:

                continue

            # ----------------------------------------------
            # Ignorar encabezados del ESP32
            # ----------------------------------------------

            if linea.startswith(
                "timestamp"
            ):

                continue

            # ----------------------------------------------
            # Separar datos
            # ----------------------------------------------

            partes = linea.split(",")

            if len(partes) != 4:

                continue

            # ----------------------------------------------
            # Convertir datos
            # ----------------------------------------------

            try:

                timestamp = int(
                    partes[0]
                )

                ax = float(
                    partes[1]
                )

                ay = float(
                    partes[2]
                )

                az = float(
                    partes[3]
                )

            except ValueError:

                continue

            # ----------------------------------------------
            # Guardar muestra
            # ----------------------------------------------

            escritor.writerow(
                [
                    timestamp,
                    ax,
                    ay,
                    az
                ]
            )

            contador += 1

            # ----------------------------------------------
            # Mostrar progreso
            # ----------------------------------------------

            if contador % 25 == 0:

                print(
                    f"\rMuestras: "
                    f"{contador} | "
                    f"Tiempo: "
                    f"{segundos:.1f}s",
                    end=""
                )

    # --------------------------------------------------------
    # 7. Cerrar puerto
    # --------------------------------------------------------

    dispositivo.close()

    # --------------------------------------------------------
    # 8. Mostrar resumen
    # --------------------------------------------------------

    print(
        "\n\n" + "=" * 40
    )

    print(
        "CAPTURA FINALIZADA"
    )

    print(
        "=" * 40
    )

    print(
        f"Género: {genero.upper()}"
    )

    print(
        f"Muestras registradas: "
        f"{contador}"
    )

    print(
        f"Archivo:"
        f"\n{ruta_csv}"
    )

    print(
        "=" * 40
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    capturar()