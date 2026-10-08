#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

// --- Pin Definitions (ESP32 Standard VSPI) ---
#define SS_PIN    5   // RC522 SDA/SS
#define RST_PIN   22  // RC522 RST
#define LED_GREEN 2   // Onboard/External Success LED
#define LED_RED   4   // Error LED

// --- Network & Server Credentials ---
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
// Point to your FastAPI endpoint (use machine local IP for LAN testing, e.g., http://192.168.1.50:8000/api/v1/inventory/scan)
const char* SERVER_URL    = "http://192.168.1.X:8000/api/v1/inventory/scan";
const char* READER_ID     = "GATE_READER_01";

// --- State Variables ---
MFRC522 rfid(SS_PIN, RST_PIN);
unsigned long lastScanTime = 0;
const unsigned long SCAN_COOLDOWN_MS = 2500; // Prevent duplicate scanning spam
String lastScannedUID = "";

void connectToWiFi() {
    Serial.print("Connecting to Wi-Fi");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    unsigned long startAttemptTime = millis();
    // Non-blocking timeout attempt: 10 seconds max per try
    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
        delay(500);
        Serial.print(".");
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WiFi] Connected! Local IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("\n[WiFi] Connection timeout. Retrying in background...");
    }
}

void sendScanPayload(String uid) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[HTTP] Wi-Fi not connected. Attempting reconnection...");
        connectToWiFi();
        if (WiFi.status() != WL_CONNECTED) {
            digitalWrite(LED_RED, HIGH);
            delay(300);
            digitalWrite(LED_RED, LOW);
            return;
        }
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    // Construct JSON payload
    String payload = "{\"tag_id\":\"" + uid + "\",\"reader_id\":\"" + String(READER_ID) + "\"}";
    Serial.println("[HTTP] Dispatching: " + payload);

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.printf("[HTTP] Code: %d | Response: %s\n", httpResponseCode, response.c_str());

        if (httpResponseCode == 200 || httpResponseCode == 201) {
            digitalWrite(LED_GREEN, HIGH);
            delay(400);
            digitalWrite(LED_GREEN, LOW);
        } else {
            digitalWrite(LED_RED, HIGH);
            delay(400);
            digitalWrite(LED_RED, LOW);
        }
    } else {
        Serial.printf("[HTTP] POST failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
        digitalWrite(LED_RED, HIGH);
        delay(600);
        digitalWrite(LED_RED, LOW);
    }

    http.end();
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_RED, OUTPUT);

    SPI.begin();       // Init SPI bus (SCK=18, MISO=19, MOSI=23)
    rfid.PCD_Init();   // Init RC522

    Serial.println("\n--- ESP32 RFID Inventory Edge Node Initialized ---");
    connectToWiFi();
}

void loop() {
    // Keep Wi-Fi active if disconnected
    if (WiFi.status() != WL_CONNECTED) {
        static unsigned long lastReconnectAttempt = 0;
        if (millis() - lastReconnectAttempt > 10000) {
            lastReconnectAttempt = millis();
            connectToWiFi();
        }
    }

    // Look for new RFID tags
    if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
        return;
    }

    // Convert UID bytes to uppercase hex string
    String currentUID = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) currentUID += "0";
        currentUID += String(rfid.uid.uidByte[i], HEX);
    }
    currentUID.toUpperCase();

    // Check debounce conditions
    if (currentUID == lastScannedUID && (millis() - lastScanTime < SCAN_COOLDOWN_MS)) {
        rfid.PICC_HaltA();
        rfid.PCD_StopCrypto1();
        return;
    }

    lastScannedUID = currentUID;
    lastScanTime = millis();

    Serial.println("\n[RFID] Detected Tag UID: " + currentUID);
    sendScanPayload(currentUID);

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
}
