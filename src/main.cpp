#include <Arduino.h>
#include <Wire.h>

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <RitmoEdge_2_inferencing.h>


// ============================================================
// CONFIGURACIÓN I2C
// ============================================================

#define SDA_PIN 21
#define SCL_PIN 22

#define MPU_ADDR 0x68

#define OLED_ADDR 0x3C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    &Wire,
    -1
);


// ============================================================
// REGISTROS MPU6500 / COMPATIBLE
// ============================================================

#define REG_WHO_AM_I       0x75
#define REG_PWR_MGMT_1    0x6B
#define REG_ACCEL_CONFIG  0x1C
#define REG_ACCEL_XOUT_H  0x3B


// ============================================================
// CONFIGURACIÓN DEL ACELERÓMETRO
// ============================================================

// ±2g
#define ACCEL_SCALE 16384.0f

// Conversión de g → m/s²
#define GRAVITY 9.80665f


// ============================================================
// VARIABLES PARA EDGE IMPULSE
// ============================================================

static float *features = nullptr;

static size_t feature_index = 0;


// ============================================================
// ESCRIBIR REGISTRO I2C
// ============================================================

void writeRegister(uint8_t reg, uint8_t value)
{
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(reg);
    Wire.write(value);
    Wire.endTransmission();
}


// ============================================================
// LEER REGISTRO I2C
// ============================================================

uint8_t readRegister(uint8_t reg)
{
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(reg);
    Wire.endTransmission(false);

    Wire.requestFrom(MPU_ADDR, (uint8_t)1);

    if (Wire.available())
    {
        return Wire.read();
    }

    return 0xFF;
}


// ============================================================
// INICIALIZAR MPU6500
// ============================================================

bool initMPU()
{
    Serial.println();
    Serial.println("Inicializando sensor...");

    uint8_t whoami = readRegister(REG_WHO_AM_I);

    Serial.print("WHO_AM_I = 0x");

    if (whoami < 16)
        Serial.print("0");

    Serial.println(whoami, HEX);

    if (whoami != 0x70 && whoami != 0x68)
    {
        Serial.println("ERROR: Identificacion desconocida.");
        return false;
    }

    // Sacar sensor del modo sleep
    writeRegister(REG_PWR_MGMT_1, 0x00);

    delay(100);

    // Acelerómetro ±2g
    writeRegister(REG_ACCEL_CONFIG, 0x00);

    delay(100);

    Serial.println("Sensor inicializado correctamente.");

    return true;
}


// ============================================================
// LEER ACELERÓMETRO
// ============================================================

bool readAcceleration(
    float &ax,
    float &ay,
    float &az
)
{
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(REG_ACCEL_XOUT_H);

    if (Wire.endTransmission(false) != 0)
    {
        return false;
    }

    uint8_t received = Wire.requestFrom(
        MPU_ADDR,
        (uint8_t)6
    );

    if (received != 6)
    {
        return false;
    }

    int16_t raw_ax =
        ((int16_t)Wire.read() << 8) |
        Wire.read();

    int16_t raw_ay =
        ((int16_t)Wire.read() << 8) |
        Wire.read();

    int16_t raw_az =
        ((int16_t)Wire.read() << 8) |
        Wire.read();


    // Convertir a g
    ax = ((float)raw_ax / ACCEL_SCALE) * GRAVITY;
    ay = ((float)raw_ay / ACCEL_SCALE) * GRAVITY;
    az = ((float)raw_az / ACCEL_SCALE) * GRAVITY;

    return true;
}


// ============================================================
// CALLBACK PARA EDGE IMPULSE
// ============================================================

static int get_signal_data(
    size_t offset,
    size_t length,
    float *out_ptr
)
{
    if (features == nullptr)
    {
        Serial.println("ERROR: features es NULL");
        return -1;
    }

    if (offset + length > EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE)
    {
        Serial.println("ERROR: Edge Impulse solicita datos fuera del buffer");

        Serial.print("offset = ");
        Serial.println(offset);

        Serial.print("length = ");
        Serial.println(length);

        Serial.print("offset + length = ");
        Serial.println(offset + length);

        Serial.print("buffer disponible = ");
        Serial.println(EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE);

        return -1;
    }

    memcpy(
        out_ptr,
        features + offset,
        length * sizeof(float)
    );

    return 0;
}

// ============================================================
// MOSTRAR RESULTADOS
// ============================================================

void printClassification(
    ei_impulse_result_t &result
)
{
    Serial.println();
    Serial.println("========================================");
    Serial.println("        RITMOEDGE - RESULTADO");
    Serial.println("========================================");

    for (size_t i = 0;
         i < EI_CLASSIFIER_LABEL_COUNT;
         i++)
    {
        Serial.print(
            result.classification[i].label
        );

        Serial.print(": ");

        Serial.print(
            result.classification[i].value * 100.0f,
            2
        );

        Serial.println("%");
    }

#if EI_CLASSIFIER_HAS_ANOMALY == 1

    Serial.print("Anomaly: ");

    Serial.println(
        result.anomaly,
        3
    );

#endif

    Serial.println();
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);

    delay(2000);

    Serial.println();
    Serial.println("========================================");
    Serial.println("          RITMOEDGE");
    Serial.println("   Edge Impulse + ESP32 + MPU6500");
    Serial.println("========================================");


    // --------------------------------------------------------
    // I2C
    // --------------------------------------------------------

    Wire.begin(
        SDA_PIN,
        SCL_PIN
    );

    delay(500);


    // --------------------------------------------------------
    // OLED
    // --------------------------------------------------------

    if (!display.begin(
            SSD1306_SWITCHCAPVCC,
            OLED_ADDR))
    {
        Serial.println(
            "OLED no encontrado."
        );
    }
    else
    {
        display.clearDisplay();

        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);

        display.setCursor(0, 0);

        display.println("RITMOEDGE");

        display.println();
        display.println("Inicializando...");

        display.display();
    }


    // --------------------------------------------------------
    // SENSOR
    // --------------------------------------------------------

    if (!initMPU())
    {
        Serial.println();
        Serial.println(
            "ERROR: sensor no encontrado."
        );

        while (true)
        {
            delay(1000);
        }
    }


    // --------------------------------------------------------
    // OLED OK
    // --------------------------------------------------------

    display.clearDisplay();

    display.setCursor(0, 0);

    display.println("RITMOEDGE");
    display.println();
    display.println("Sensor OK");
    display.println();
    display.println("Esperando...");

    display.display();


    Serial.println();
    Serial.println("Sistema listo.");
    Serial.println();
    Serial.print("Frecuencia modelo: ");
    Serial.print(EI_CLASSIFIER_FREQUENCY);
    Serial.println(" Hz");
}


// ============================================================
// LOOP
// ============================================================

void loop()
{
    // --------------------------------------------------------
    // Crear buffer para una ventana completa
    // --------------------------------------------------------

    const size_t sample_count =
    EI_CLASSIFIER_RAW_SAMPLE_COUNT;

    const size_t feature_count =
        sample_count * 3;


    Serial.println();
    Serial.println("========================================");
    Serial.println("CONFIGURACION EDGE IMPULSE");
    Serial.println("========================================");

    Serial.print("Frecuencia: ");
    Serial.println(EI_CLASSIFIER_FREQUENCY);

    Serial.print("Muestras por ventana: ");
    Serial.println(sample_count);

    Serial.print("Valores por muestra: ");
    Serial.println(3);

    Serial.print("Tamano buffer: ");
    Serial.println(feature_count);

    Serial.print("DSP input frame size: ");
    Serial.println(EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE);

    Serial.println("========================================");

    if (features != nullptr)
    {
        delete[] features;
        features = nullptr;
    }

    features = new float[feature_count];

    if (features == nullptr)
    {
        Serial.println(
            "ERROR: No hay memoria suficiente."
        );

        delay(2000);

        return;
    }


    // --------------------------------------------------------
    // Frecuencia de muestreo definida por Edge Impulse
    // --------------------------------------------------------

    const uint32_t sample_period_us =
        (uint32_t)(
            1000000.0f /
            EI_CLASSIFIER_FREQUENCY
        );


    Serial.println();
    Serial.println(
        "Capturando ventana..."
    );


    // --------------------------------------------------------
    // CAPTURA
    // --------------------------------------------------------

    uint32_t next_sample =
        micros();


    for (size_t i = 0;
         i < sample_count;
         i++)
    {
        // Esperar hasta el siguiente sample
        while ((int32_t)(
            micros() - next_sample
        ) < 0)
        {
            delayMicroseconds(50);
        }


        next_sample += sample_period_us;


        float ax;
        float ay;
        float az;


        if (!readAcceleration(
                ax,
                ay,
                az))
        {
            Serial.println(
                "ERROR leyendo acelerometro."
            );

            delete[] features;
            features = nullptr;

            return;
        }


        // ----------------------------------------------------
        // IMPORTANTE:
        // Edge Impulse espera:
        //
        // ax, ay, az
        // ax, ay, az
        // ...
        // ----------------------------------------------------

        features[i * 3 + 0] = ax;
        features[i * 3 + 1] = ay;
        features[i * 3 + 2] = az;


        // Mostrar algunos valores
        // solamente durante la captura
        if (i < 5)
        {
            Serial.print("ax=");
            Serial.print(ax, 3);

            Serial.print(" ay=");
            Serial.print(ay, 3);

            Serial.print(" az=");
            Serial.println(az, 3);
        }
    }


    // --------------------------------------------------------
    // CREAR SIGNAL
    // --------------------------------------------------------

    signal_t signal;

    signal.total_length =
        feature_count;

    signal.get_data =
        &get_signal_data;


    // --------------------------------------------------------
    // INFERENCIA EDGE IMPULSE
    // --------------------------------------------------------

    ei_impulse_result_t result = {};

    EI_IMPULSE_ERROR res =
        run_classifier(
            &signal,
            &result,
            false
        );


    // --------------------------------------------------------
    // RESULTADO
    // --------------------------------------------------------

    if (res != EI_IMPULSE_OK)
    {
        Serial.print(
            "ERROR Edge Impulse: "
        );

        Serial.println(res);
    }
    else
    {
        printClassification(result);
    }


    // --------------------------------------------------------
    // OLED
    // --------------------------------------------------------

    if (display.width() > 0)
    {
        display.clearDisplay();

        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);

        display.setCursor(0, 0);

        display.println("RITMOEDGE");

        for (size_t i = 0;
             i < EI_CLASSIFIER_LABEL_COUNT;
             i++)
        {
            display.print(
                result.classification[i].label
            );

            display.print(": ");

            display.print(
                result.classification[i].value * 100.0f,
                0
            );

            display.println("%");
        }

        display.display();
    }


    // --------------------------------------------------------
    // Esperar antes de la siguiente ventana
    // --------------------------------------------------------

    delete[] features;
    features = nullptr;

    delay(500);
}