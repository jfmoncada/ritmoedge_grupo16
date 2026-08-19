#include <Arduino.h>
#include <Wire.h>

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============================================================
// RITMOEDGE
// ESP32 + MPU6500 + OLED
// ============================================================

// ============================================================
// CONFIGURACIÓN I2C
// ============================================================

#define SDA_PIN 21
#define SCL_PIN 22

// ============================================================
// OLED
// ============================================================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDRESS 0x3C

Adafruit_SSD1306 display(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    &Wire,
    -1
);

// ============================================================
// MPU6500
// ============================================================

#define MPU6500_ADDRESS 0x68

// Registros principales
#define MPU6500_WHO_AM_I     0x75
#define MPU6500_PWR_MGMT_1   0x6B
#define MPU6500_ACCEL_CONFIG 0x1C
#define MPU6500_GYRO_CONFIG  0x1B

// Inicio de los registros de medición
#define MPU6500_ACCEL_XOUT_H 0x3B

// Identificación esperada
#define MPU6500_WHO_AM_I_VALUE 0x70

// ============================================================
// MUESTREO
// ============================================================

#define SAMPLE_RATE_HZ 50

const unsigned long SAMPLE_PERIOD_US =
    1000000UL / SAMPLE_RATE_HZ;

unsigned long lastSampleTime = 0;

// ============================================================
// DATOS DEL SENSOR
// ============================================================

float ax = 0.0;
float ay = 0.0;
float az = 0.0;

float gx = 0.0;
float gy = 0.0;
float gz = 0.0;

// ============================================================
// FUNCIONES I2C
// ============================================================

bool writeRegister(
    uint8_t deviceAddress,
    uint8_t registerAddress,
    uint8_t value
)
{
    Wire.beginTransmission(deviceAddress);

    Wire.write(registerAddress);
    Wire.write(value);

    return Wire.endTransmission() == 0;
}

// ============================================================

bool readRegisters(
    uint8_t deviceAddress,
    uint8_t registerAddress,
    uint8_t *buffer,
    uint8_t length
)
{
    Wire.beginTransmission(deviceAddress);

    Wire.write(registerAddress);

    if (Wire.endTransmission(false) != 0)
    {
        return false;
    }

    uint8_t received =
        Wire.requestFrom(
            deviceAddress,
            length,
            true
        );

    if (received != length)
    {
        return false;
    }

    for (uint8_t i = 0; i < length; i++)
    {
        buffer[i] = Wire.read();
    }

    return true;
}

// ============================================================
// INICIALIZAR OLED
// ============================================================

bool initOLED()
{
    Serial.println("Inicializando OLED...");

    if (!display.begin(
            SSD1306_SWITCHCAPVCC,
            OLED_ADDRESS))
    {
        Serial.println("ERROR: OLED no encontrada.");

        return false;
    }

    Serial.println("OLED OK");

    display.clearDisplay();

    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);

    display.setCursor(0, 0);
    display.println("RitmoEdge");

    display.setCursor(0, 15);
    display.println("Inicializando...");

    display.display();

    delay(1000);

    return true;
}

// ============================================================
// IDENTIFICAR MPU6500
// ============================================================

bool checkMPU6500()
{
    uint8_t whoAmI = 0;

    Serial.println("Comprobando MPU6500...");

    if (!readRegisters(
            MPU6500_ADDRESS,
            MPU6500_WHO_AM_I,
            &whoAmI,
            1))
    {
        Serial.println(
            "ERROR: No se pudo leer WHO_AM_I."
        );

        return false;
    }

    Serial.print("WHO_AM_I = 0x");

    if (whoAmI < 0x10)
    {
        Serial.print("0");
    }

    Serial.println(whoAmI, HEX);

    if (whoAmI != MPU6500_WHO_AM_I_VALUE)
    {
        Serial.println(
            "ERROR: El dispositivo no corresponde a MPU6500."
        );

        return false;
    }

    Serial.println("MPU6500 identificado correctamente.");

    return true;
}

// ============================================================
// INICIALIZAR MPU6500
// ============================================================

bool initMPU6500()
{
    Serial.println("Inicializando MPU6500...");

    // --------------------------------------------------------
    // Sacar el sensor del modo sleep
    // PWR_MGMT_1 = 0x00
    // --------------------------------------------------------

    if (!writeRegister(
            MPU6500_ADDRESS,
            MPU6500_PWR_MGMT_1,
            0x00))
    {
        Serial.println(
            "ERROR escribiendo PWR_MGMT_1."
        );

        return false;
    }

    delay(100);

    // --------------------------------------------------------
    // Acelerómetro ±8 g
    //
    // ACCEL_CONFIG:
    // 0x00 = ±2g
    // 0x08 = ±4g
    // 0x10 = ±8g
    // 0x18 = ±16g
    // --------------------------------------------------------

    if (!writeRegister(
            MPU6500_ADDRESS,
            MPU6500_ACCEL_CONFIG,
            0x10))
    {
        Serial.println(
            "ERROR configurando acelerometro."
        );

        return false;
    }

    // --------------------------------------------------------
    // Giroscopio ±500 °/s
    //
    // GYRO_CONFIG:
    // 0x00 = ±250 °/s
    // 0x08 = ±500 °/s
    // 0x10 = ±1000 °/s
    // 0x18 = ±2000 °/s
    // --------------------------------------------------------

    if (!writeRegister(
            MPU6500_ADDRESS,
            MPU6500_GYRO_CONFIG,
            0x08))
    {
        Serial.println(
            "ERROR configurando giroscopio."
        );

        return false;
    }

    Serial.println(
        "Configuracion MPU6500 OK."
    );

    return true;
}

// ============================================================
// CONVERTIR DOS BYTES A INT16
// ============================================================

int16_t combineBytes(
    uint8_t highByte,
    uint8_t lowByte
)
{
    return (int16_t)(
        ((uint16_t)highByte << 8) |
        lowByte
    );
}

// ============================================================
// LEER MPU6500
// ============================================================

bool readMPU6500()
{
    // --------------------------------------------------------
    // Desde 0x3B podemos leer consecutivamente:
    //
    // AX H
    // AX L
    // AY H
    // AY L
    // AZ H
    // AZ L
    // TEMP H
    // TEMP L
    // GX H
    // GX L
    // GY H
    // GY L
    // GZ H
    // GZ L
    // --------------------------------------------------------

    uint8_t data[14];

    if (!readRegisters(
            MPU6500_ADDRESS,
            MPU6500_ACCEL_XOUT_H,
            data,
            14))
    {
        return false;
    }

    int16_t rawAx =
        combineBytes(data[0], data[1]);

    int16_t rawAy =
        combineBytes(data[2], data[3]);

    int16_t rawAz =
        combineBytes(data[4], data[5]);

    int16_t rawGx =
        combineBytes(data[8], data[9]);

    int16_t rawGy =
        combineBytes(data[10], data[11]);

    int16_t rawGz =
        combineBytes(data[12], data[13]);

    // --------------------------------------------------------
    // Acelerómetro ±8g
    //
    // Sensibilidad:
    // 4096 LSB/g
    // --------------------------------------------------------

    const float ACCEL_SENSITIVITY = 4096.0;

    const float GRAVITY = 9.80665;

    ax =
        ((float)rawAx / ACCEL_SENSITIVITY)
        * GRAVITY;

    ay =
        ((float)rawAy / ACCEL_SENSITIVITY)
        * GRAVITY;

    az =
        ((float)rawAz / ACCEL_SENSITIVITY)
        * GRAVITY;

    // --------------------------------------------------------
    // Giroscopio ±500 °/s
    //
    // Sensibilidad:
    // 65.5 LSB/(°/s)
    // --------------------------------------------------------

    const float GYRO_SENSITIVITY = 65.5;

    gx =
        (float)rawGx / GYRO_SENSITIVITY;

    gy =
        (float)rawGy / GYRO_SENSITIVITY;

    gz =
        (float)rawGz / GYRO_SENSITIVITY;

    return true;
}

// ============================================================
// MOSTRAR EN OLED
// ============================================================

void updateOLED()
{
    display.clearDisplay();

    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);

    display.setCursor(0, 0);
    display.println("RitmoEdge");

    display.setCursor(0, 12);
    display.print("X: ");
    display.print(ax, 2);

    display.setCursor(0, 24);
    display.print("Y: ");
    display.print(ay, 2);

    display.setCursor(0, 36);
    display.print("Z: ");
    display.print(az, 2);

    display.setCursor(0, 52);
    display.println("MPU6500 OK");

    display.display();
}

// ============================================================
// ENVIAR ACELERÓMETRO AL PC
// ============================================================

void sendSerialData()
{
    unsigned long timestamp =
        millis();

    Serial.print(timestamp);
    Serial.print(",");

    Serial.print(ax, 4);
    Serial.print(",");

    Serial.print(ay, 4);
    Serial.print(",");

    Serial.println(az, 4);
}

// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);

    delay(1000);

    Serial.println();
    Serial.println("==============================");
    Serial.println("      RITMOEDGE - ESP32");
    Serial.println("==============================");

    // --------------------------------------------------------
    // I2C
    // --------------------------------------------------------

    Wire.begin(
        SDA_PIN,
        SCL_PIN
    );

    Serial.println("I2C iniciado.");
    Serial.println("SDA: GPIO21");
    Serial.println("SCL: GPIO22");

    // --------------------------------------------------------
    // OLED
    // --------------------------------------------------------

    if (!initOLED())
    {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("ERROR OLED");
        display.display();

        while (true)
        {
            delay(1000);
        }
    }

    // --------------------------------------------------------
    // MPU6500
    // --------------------------------------------------------

    if (!checkMPU6500())
    {
        display.clearDisplay();

        display.setCursor(0, 0);
        display.println("ERROR MPU6500");

        display.setCursor(0, 15);
        display.println("WHO_AM_I");

        display.display();

        while (true)
        {
            delay(1000);
        }
    }

    if (!initMPU6500())
    {
        display.clearDisplay();

        display.setCursor(0, 0);
        display.println("ERROR CONFIG");

        display.display();

        while (true)
        {
            delay(1000);
        }
    }

    // --------------------------------------------------------
    // Pantalla inicial
    // --------------------------------------------------------

    display.clearDisplay();

    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);

    display.setCursor(0, 0);
    display.println("RitmoEdge");

    display.setCursor(0, 12);
    display.println("MPU6500: OK");

    display.setCursor(0, 24);
    display.println("OLED: OK");

    display.setCursor(0, 36);
    display.println("Serial: OK");

    display.setCursor(0, 48);
    display.println("50 Hz");

    display.display();

    // --------------------------------------------------------
    // Encabezado CSV
    // --------------------------------------------------------

    Serial.println(
        "timestamp_ms,ax,ay,az"
    );

    Serial.println(
        "Sistema iniciado correctamente."
    );

    // --------------------------------------------------------
    // Temporizador
    // --------------------------------------------------------

    lastSampleTime = micros();
}

// ============================================================
// LOOP
// ============================================================

void loop()
{
    unsigned long currentTime =
        micros();

    if (
        currentTime - lastSampleTime
        >= SAMPLE_PERIOD_US
    )
    {
        lastSampleTime += SAMPLE_PERIOD_US;

        // Leer MPU6500
        if (readMPU6500())
        {
            // Mostrar en OLED
            updateOLED();

            // Enviar al PC
            sendSerialData();
        }
        else
        {
            Serial.println(
                "ERROR: fallo leyendo MPU6500."
            );
        }
    }
}