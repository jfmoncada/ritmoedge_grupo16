"""
RitmoEdge - Captura de datos para evaluación
---------------------------------------------
Captura nuevos datos del acelerómetro para
evaluar el modelo con información que NO fue
utilizada durante entrenamiento.

Salida:
    datos/nuevos/<genero>/
        <genero>_prueba_YYYYMMDD_HHMMSS.csv
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

DURACION_SEGUNDOS = 30

GENEROS = [
    "salsa",
    "merengue",
    "electronica"
]

BASE_DIR = Path(__file__).resolve().parent.parent

CARPETA_SALIDA = BASE_DIR / "datos" / "nuevos"


# ============================================================
# BUSCAR PUERTOS
# ============================================================

def listar_puertos():

    puertos = list(
        serial.tools.list_ports.comports()
    )

    if not puertos:
        print("No se encontraron puertos serial.")
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

        print("Opción inválida.")


# ============================================================
# SELECCIONAR GÉNERO
# ============================================================

def seleccionar_genero():

    print("\nGéneros disponibles:")

    for i, genero in enumerate(GENEROS):

        print(
            f"[{i}] {genero}"
        )

    while True:

        try:

            opcion = int(
                input(
                    "\nSelecciona el género "
                    "que vas a capturar: "
                )
            )

            if 0 <= opcion < len(GENEROS):

                return GENEROS[opcion]

        except ValueError:
            pass

        print("Opción inválida.")


# ============================================================
# CREAR ARCHIVO
# ============================================================

def crear_archivo(genero):

    carpeta = (
        CARPETA_SALIDA / genero
    )

    carpeta.mkdir(
        parents=True,
        exist_ok=True
    )

    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    nombre = (
        f"{genero}_prueba_{fecha}.csv"
    )

    return carpeta / nombre


# ============================================================
# CAPTURA
# ============================================================

def capturar():

    genero = seleccionar_genero()

    puerto = seleccionar_puerto()

    print(
        f"\nGénero seleccionado: "
        f"{genero.upper()}"
    )

    print(
        f"Conectando al ESP32 en {puerto}..."
    )

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

    dispositivo.reset_input_buffer()

    ruta_csv = crear_archivo(genero)

    print(
        f"\nArchivo de salida:\n{ruta_csv}"
    )

    print(
        f"\nDuración: "
        f"{DURACION_SEGUNDOS} segundos"
    )

    print(
        "\nPrepárate..."
    )

    input(
        "Presiona ENTER para comenzar "
        "la captura..."
    )

    print(
        "\nCOMIENZA LA CAPTURA\n"
    )

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

        escritor.writerow(
            [
                "timestamp",
                "ax",
                "ay",
                "az"
            ]
        )

        while True:

            tiempo_actual = datetime.now()

            segundos = (
                tiempo_actual
                - tiempo_inicio
            ).total_seconds()

            if segundos >= DURACION_SEGUNDOS:
                break

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

            if linea.startswith(
                "timestamp"
            ):
                continue

            partes = linea.split(",")

            if len(partes) != 4:
                continue

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

            escritor.writerow(
                [
                    timestamp,
                    ax,
                    ay,
                    az
                ]
            )

            contador += 1

            if contador % 25 == 0:

                print(
                    f"\rMuestras: "
                    f"{contador} | "
                    f"Tiempo: "
                    f"{segundos:.1f}s",
                    end=""
                )

    dispositivo.close()

    print(
        "\n\nCaptura finalizada."
    )

    print(
        f"Muestras registradas: "
        f"{contador}"
    )

    print(
        f"Archivo:\n{ruta_csv}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    capturar()