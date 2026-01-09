#include <Wire.h>
#include <VL53L0X.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ================= USER CONFIGURATION =================
const char* ssid = "TP-Link_E41B";             
const char* password = "03876794"; 

// Target Settings (Where to send the Trigger)
const char* udpAddress = "192.168.0.107";     
const int qlabPort = 53001;   // Send triggers HERE (QLab)

// Listening Settings (Where to listen for Reset)
const int localPort = 4000;   // Listen HERE for "RESETSAFE"
// ======================================================

VL53L0X sensor;
WiFiUDP udp;
char packetBuffer[255]; // Buffer to hold incoming packet

// XIAO ESP32C6 I2C Pins
#define SDA_PIN D4
#define SCL_PIN D5

// Variable to lock the script after firing
bool taskCompleted = false;

void setup() {
  Serial.begin(115200);
  delay(2000); 

  // --- WiFi Setup ---
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
  Serial.print("My IP: ");
  Serial.println(WiFi.localIP());

  // --- Start UDP Listening ---
  // We listen on Port 4000 (localPort) for the Reset signal
  udp.begin(localPort);
  Serial.printf("Listening for resets on UDP port %d\n", localPort);
  Serial.printf("Sending triggers to %s:%d\n", udpAddress, qlabPort);

  // --- Sensor Setup ---
  Wire.begin(SDA_PIN, SCL_PIN);
  sensor.setTimeout(500);

  if (!sensor.init()) {
    Serial.println("Failed to detect sensor! Check wiring.");
    while (1) {}
  }

  sensor.startContinuous();
  Serial.println("System Ready. Waiting for trigger...");
}

void loop() {
  // 1. ALWAYS CHECK FOR INCOMING RESET COMMANDS (On Port 4000)
  checkResetCommand();

  // 2. SENSOR LOGIC
  if (!taskCompleted) {
    
    uint16_t distance = sensor.readRangeContinuousMillimeters();

    // Print distance for debugging
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" mm");

    // 3. TRIGGER LOGIC
    // Trigger if distance is > 350mm AND valid reading (< 8000)
    if (distance > 350 && distance < 8000) {
      
      // Send the message to QLab (Port 63000)
      sendUdpMessage("/cue/SAFE/go");
      
      // Lock the system
      taskCompleted = true;
      
      Serial.println("-----------------------------------");
      Serial.println("TRIGGER SENT. SYSTEM LOCKED.");
      Serial.println("Waiting for 'RESETSAFE' command on Port 4000...");
      Serial.println("-----------------------------------");
      
      sensor.stopContinuous(); 
    }
  }
  
  delay(50); 
}

void sendUdpMessage(const char* msg) {
  Serial.print("Sending UDP to QLab: ");
  Serial.println(msg);
  
  // Send packet specifically to QLab Port (53000)
  udp.beginPacket(udpAddress, qlabPort);
  udp.print(msg);
  udp.endPacket();
}

void checkResetCommand() {
  // Check if any packets have arrived on our listening port (4000)
  int packetSize = udp.parsePacket();
  
  if (packetSize) {
    int len = udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;

    Serial.print("Received UDP on Port 4000: ");
    Serial.println(packetBuffer);

    // Check if the message contains "RESETSAFE"
    if (strstr(packetBuffer, "RESETSAFE") != NULL) {
      Serial.println("!!! RESET COMMAND RECEIVED !!!");
      
      // 1. Start the sensor
      sensor.startContinuous();
      
      // 2. STABILIZATION DELAY (5 seconds)
      // Prevent immediate re-triggering while you move away
      Serial.println("Stabilizing sensor (5 seconds)...");
      delay(5000); 

      // 3. Re-Arm the system
      taskCompleted = false;
      Serial.println("System Re-Armed and Active.");
    }
  }
}