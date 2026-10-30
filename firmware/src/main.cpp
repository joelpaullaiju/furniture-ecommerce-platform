#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// --- PIN CONFIGURATION (ESP32 Dev Module) ---
#define SS_PIN    5   // SDA / SS Pin
#define RST_PIN   22  // Reset Pin
#define LED_PIN   2   // Built-in LED Pin

MFRC522 rfid(SS_PIN, RST_PIN);

// --- WI-FI ACCESS POINT CREDENTIALS ---
const char* ap_ssid = "Furniture_Demo_Net";
const char* ap_password = "password123";

// --- BACKEND API ENDPOINT ---
const char* serverUrl = "http://your_ip:8000/api/scan";

// Scan cooldown to prevent duplicate rapid triggers
unsigned long lastScanTime = 0;
const unsigned long scanDelay = 2000; // 2-second debounce delay
String lastScannedUID = "";

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Initialize SPI bus & MFRC522 module
  SPI.begin();
  rfid.PCD_Init();

  // Configure ESP32 as Access Point (AP)
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ap_ssid, ap_password);

  Serial.println("\n==========================================");
  Serial.println("   ESP32 RFID EDGE GATEWAY INITIALIZED   ");
  Serial.println("==========================================");
  Serial.print("Wi-Fi Access Point Name: ");
  Serial.println(ap_ssid);
  Serial.print("Gateway IP Address: ");
  Serial.println(WiFi.softAPIP());
  Serial.println("Target API URL: " + String(serverUrl));
  Serial.println("Ready to scan tags...\n");
}

void loop() {
  // Check for new RFID tag
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // Read card UID
  String scannedUID = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      scannedUID += "0";
    }
    scannedUID += String(rfid.uid.uidByte[i], HEX);
  }
  scannedUID.toUpperCase();

  // Debounce check
  if (scannedUID == lastScannedUID && (millis() - lastScanTime < scanDelay)) {
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    return;
  }

  lastScannedUID = scannedUID;
  lastScanTime = millis();

  Serial.println("[RFID] Scanned UID: " + scannedUID);

  // Blink onboard LED to indicate card detected
  digitalWrite(LED_PIN, HIGH);

  // Send POST request to FastAPI backend
  if (WiFi.softAPgetStationNum() > 0) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"rfid_uid\": \"" + scannedUID + "\"}";
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("[HTTP] Server Response Code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("[HTTP] Request Failed! Error: ");
      Serial.println(http.errorToString(httpResponseCode).c_str());
    }

    http.end();
  } else {
    Serial.println("[WARN] No laptop connected to ESP32 Wi-Fi AP!");
  }

  digitalWrite(LED_PIN, LOW);

  // Halt RFID card reading
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}