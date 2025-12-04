#include <SPI.h>
#include <LoRa.h>
#include "DHT.h"
#include "esp_sleep.h"
#include <math.h>

#define LORA_SS 5
#define LORA_RST 27
#define LORA_DIO0 2

#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

const char* SALA = "rack3";
const long FREQ = 433E6;

const uint64_t INTERVALO_ENVIO_US = 60ULL * 1000000ULL;  // 60 s

RTC_DATA_ATTR float lastTemp = NAN;
RTC_DATA_ATTR float lastUmid = NAN;
RTC_DATA_ATTR float lastPoeira = NAN;
RTC_DATA_ATTR int ciclosSemEnvio = 0;

const float DELTA_TEMP = 0.5;
const float DELTA_UMID = 2.0;
const float DELTA_POEIRA = 5.0;

void dormir() {
  esp_sleep_enable_timer_wakeup(INTERVALO_ENVIO_US);
  esp_deep_sleep_start();
}

void setup() {
  Serial.begin(9600);
  dht.begin();
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(FREQ)) {
    while (true);
  }
}

void loop() {
  // Dados simulados
  float temp = 20.0 + (float)random(0, 100) / 10.0;
  float umid = 40.0 + (float)random(0, 400) / 10.0;
  
  // Usando sensor DHT11
  // float temp = dht.readTemperature();
  // float umid = dht.readHumidity();
  float poeira = (float)random(0, 1000) / 10.0;

  if (isnan(temp) || isnan(umid)) {
    Serial.println("Falha na leitura do DHT11");
    delay(2000);
    return;
  }

  bool mudouTemp = !isnan(lastTemp) && fabs(temp - lastTemp) >= DELTA_TEMP;
  bool mudouUmid = !isnan(lastUmid) && fabs(umid - lastUmid) >= DELTA_UMID;
  bool mudouPoeira = !isnan(lastPoeira) && fabs(poeira - lastPoeira) >= DELTA_POEIRA;
  bool alerta = temp > 35.0 || umid < 25.0;

  bool primeiraLeitura = isnan(lastTemp) || isnan(lastUmid) || isnan(lastPoeira);
  bool precisaEnviar = false;

  if (primeiraLeitura) {
    precisaEnviar = true;
    ciclosSemEnvio = 0;
  } else if (mudouTemp || mudouUmid || mudouPoeira || alerta) {
    precisaEnviar = true;
    ciclosSemEnvio = 0;
  } else {
    ciclosSemEnvio++;
    if (ciclosSemEnvio >= 10) {
      precisaEnviar = true;
      ciclosSemEnvio = 0;
    }
  }

  if (!precisaEnviar) {
    Serial.println("Sem envio, abaixo do delta, ciclos sem envio: " + String(ciclosSemEnvio));
    dormir();
  }

  lastTemp = temp;
  lastUmid = umid;
  lastPoeira = poeira;

  String line = "id=" + String(SALA)
                + ";temp=" + String(temp, 2)
                + ";umid=" + String(umid, 2)
                + ";poeira=" + String(poeira, 2);

  LoRa.beginPacket();
  LoRa.print(line);
  LoRa.endPacket();

  Serial.println(line);

  esp_sleep_enable_timer_wakeup(INTERVALO_ENVIO_US);
  esp_deep_sleep_start();
}
