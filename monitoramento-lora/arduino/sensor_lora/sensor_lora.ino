#include <SPI.h>
#include <LoRa.h>

#define LORA_SS 5
#define LORA_RST 27
#define LORA_DIO0 2

const char* SALA = "rack3";
const long FREQ = 433E6;

void setup() {
  Serial.begin(9600);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(FREQ)) {
    while (true);
  }
}

void loop() {
  float temp = 20.0 + (float)random(0, 100) / 10.0;
  float umid = 40.0 + (float)random(0, 400) / 10.0;
  float poeira = (float)random(0, 1000) / 10.0;

  String line = "id=" + String(SALA) + ";temp=" + String(temp, 2) + ";umid=" + String(umid, 2) + ";poeira=" + String(poeira, 2);

  LoRa.beginPacket();
  LoRa.print(line);
  LoRa.endPacket();

  Serial.println(line);

  delay(2000);
}
