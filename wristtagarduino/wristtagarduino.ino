/*
 * Arduino Uno R4 WiFi - Dual UDP Sender
 * FIXED for Python Relay
 */

#include <SPI.h>
#include <MFRC522.h>
#include <WiFiS3.h>
#include <WiFiUdp.h>

// --- WIFI CONFIGURATION ---
const char ssid[] = "TP-Link_E41B";
const char pass[] = "03876794";   

// --- UDP CONFIGURATION ---
IPAddress remoteIp(192, 168, 0, 107);

// --- UPDATE 1: MATCH PYTHON LISTENER PORT ---
unsigned int pythonPort = 53001;  // WAS 4000, NOW 53001 to match your Python Script

// Local port for the Arduino
unsigned int localPort = 8888;

// --- HARDWARE CONFIGURATION ---
#define SS_PIN  10
#define RST_PIN 9

MFRC522 mfrc522(SS_PIN, RST_PIN);
WiFiUDP Udp;

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; }

  // 1. Initialize Hardware
  SPI.begin();
  mfrc522.PCD_Init();

  // 2. Connect to WiFi
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    while (true);
  }

  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nConnected to network");
  Serial.print("My IP address: ");
  Serial.println(WiFi.localIP());

  // 3. Start UDP Engine
  Udp.begin(localPort);
  Serial.println("System Ready. Scan a card...");
}

void loop() {
  // --- RFID DETECTION ---
  if ( ! mfrc522.PICC_IsNewCardPresent()) { return; }
  if ( ! mfrc522.PICC_ReadCardSerial()) { return; }

  // --- CARD FOUND ---
  Serial.println("Card Detected! Sending to Python...");

  // --- UPDATE 2: SEND TO PYTHON (Port 53001) ---
  Udp.beginPacket(remoteIp, pythonPort);
  
  // We send the EXACT text Python is looking for
  // Python Relay will receive this, trigger the sound, and forward to QLab
  Udp.write("/cue/NOTED/go"); 
  
  Udp.endPacket();
  Serial.println(" -> Sent '/cue/NOTED/go' to Python (53001)");

  // --- RESET RFID STATE ---
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  // Debounce
  delay(300); // Increased slightly to prevent double-triggering
}