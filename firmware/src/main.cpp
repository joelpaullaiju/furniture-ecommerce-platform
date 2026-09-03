#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>

// ESP32 Standard Hardware VSPI Pin Configuration for RC522
#define SS_PIN    5    // SDA / SS
#define RST_PIN   22   // Reset
#define SCK_PIN   18   // SCK
#define MISO_PIN  19   // MISO
#define MOSI_PIN  23   // MOSI

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);
  rfid.PCD_Init();
  
  Serial.println("ESP32 Edge Gate Initialized. Ready for RFID tags...");
}

void loop() {
  // Check for a new card
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Extract Tag UID as uppercase hex string
  String tagUID = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    tagUID += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    tagUID += String(rfid.uid.uidByte[i], HEX);
  }
  tagUID.toUpperCase();

  Serial.print("Scanned Tag UID: ");
  Serial.println(tagUID);

  // Halt PICC to prevent duplicate reads
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  delay(1000); 
}
