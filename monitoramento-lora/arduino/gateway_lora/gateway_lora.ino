#include <SPI.h>
#include <LoRa.h>

#define LORA_SS 5
#define LORA_RST 27
#define LORA_DIO0 2

const long FREQ = 433E6;

void setup() {
  Serial.begin(9600);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(FREQ)) {
    while (true);
  }
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String line = "";
    while (LoRa.available()) {
      line += (char)LoRa.read();
    }
    line.trim();
    if (line.length() > 0) {
      Serial.println(line);
    }
  }
}
