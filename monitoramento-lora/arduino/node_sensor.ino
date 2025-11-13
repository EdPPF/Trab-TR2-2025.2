#include <SPI.h>
#include <LoRa.h>

#define LORA_SS 10
#define LORA_RST 9
#define LORA_DIO0 2

const char* SALA = "rack1";
const long FREQ = 915E6;

void setup() {
   pinMode(LORA_RST, OUTPUT);
   digitalWrite(LORA_RST, HIGH);
   Serial.begin(9600);
   LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
   if (!LoRa.begin(FREQ)) {
      while (true);
   }
}

void loop() {
   float temp = 20.0 + (rand() % 100) / 10.0;
   float umid = 40.0 + (rand() % 400) / 10.0;
   float poeira = (rand() % 1000) / 10.0;

   String line = String("id=") + SALA + ";temp=" + String(temp, 2) + ";umid=" + String(umid, 2) + ";poeira=" + String(poeira, 2);

   LoRa.beginPacket();
   LoRa.print(line);
   LoRa.endPacket();

   delay(2000);
}
