/*
 * Receiver Code for Seeed Studio XIAO ESP32 (S3 or C6)
 * Connects to Arduino Uno via UART (Serial)
 * * DEBUGGING MODE ENABLED
 */

#include <HardwareSerial.h>

// --- Pin Definitions ---
// Automatically detect board type to set correct pins
#if defined(ARDUINO_XIAO_ESP32S3)
  #define RX_PIN 44 // D7 on S3
  #define TX_PIN 43 // D6 on S3
  #define BOARD_NAME "XIAO S3"
#elif defined(ARDUINO_XIAO_ESP32C6)
  #define RX_PIN 17 // D7 on C6
  #define TX_PIN 16 // D6 on C6
  #define BOARD_NAME "XIAO C6"
#else
  #define RX_PIN 17 
  #define TX_PIN 16 
  #define BOARD_NAME "Unknown ESP32"
#endif

HardwareSerial arduinoSerial(1);

unsigned long lastDebugTime = 0;

void setup() {
  // 1. Start USB Serial (Computer Connection)
  Serial.begin(115200);
  
  // Give you time to open the monitor
  delay(2000); 

  // 2. Start Arduino Connection
  // CHANGED TO 4800 BAUD: This is more stable for SoftwareSerial on the Arduino side
  // IMPORTANT: You MUST change espSerial.begin(9600) to espSerial.begin(4800) on the Arduino!
  arduinoSerial.begin(4800, SERIAL_8N1, RX_PIN, TX_PIN);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); 

  Serial.println("\n--- ESP32 DIAGNOSTIC START ---");
  Serial.print("Board Detected: "); Serial.println(BOARD_NAME);
  Serial.print("Listening on RX Pin: "); Serial.println(RX_PIN);
  Serial.print("Talking on TX Pin: "); Serial.println(TX_PIN);
  Serial.println("Waiting for data...");
}

void loop() {
  // --- 1. Read Data ---
  if (arduinoSerial.available()) {
    // Read raw string
    String rawData = arduinoSerial.readStringUntil('\n');
    rawData.trim(); // Remove whitespace

    // DEBUG: Print EXACTLY what we received
    Serial.print("[Received]: '");
    Serial.print(rawData);
    Serial.println("'");

    if (rawData == "1") {
      Serial.println(">>> SUCCESS: Valid '1' Signal Received!");
      blinkLED();
    } else if (rawData.length() > 0) {
      Serial.println(">>> WARNING: Received garbage data. Check GND wire or Baud Rate.");
    }
  }

  // --- 2. Heartbeat (Alive Check) ---
  // Prints a dot every 5 seconds just to show the board is running
  if (millis() - lastDebugTime > 5000) {
    Serial.print("."); 
    lastDebugTime = millis();
  }
}

void blinkLED() {
  digitalWrite(LED_BUILTIN, LOW);  
  delay(100);
  digitalWrite(LED_BUILTIN, HIGH); 
  delay(100);
  digitalWrite(LED_BUILTIN, LOW);  
  delay(100);
  digitalWrite(LED_BUILTIN, HIGH); 
}