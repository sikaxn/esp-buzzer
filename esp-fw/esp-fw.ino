#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include "time.h"
//#include "esp_sntp.h"
// WiFi config
const char* ssid = "CMCC-QueensU";
const char* password = "02140214";

// Server info
const char* SERVER_IP = "10.0.0.155";
const int UDP_PORT = 4210;

WiFiUDP udp;
IPAddress serverIP;
String macAddress;

const int BUTTON1_PIN = 16;
const int BUTTON2_PIN = 17;

void connectWiFiAndNTP() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected.");
  Serial.println("Local IP: " + WiFi.localIP().toString());

  macAddress = WiFi.macAddress();
  serverIP.fromString(SERVER_IP);

  // Use time.windows.com as NTP server
  configTime(0, 0, "10.0.0.1");

  Serial.println("[NTP] Using 10.0.0.1");
}

void printNTPStatus(void* pv) {
  while (true) {
    // Reconfigure time sync every 10 seconds to ensure resync
    configTime(0, 0, "10.0.0.1");  // Use default gateway as NTP server

    struct timeval tv;
    if (gettimeofday(&tv, NULL) == 0) {
      unsigned long long now_ms = (unsigned long long)tv.tv_sec * 1000 + tv.tv_usec / 1000;
      Serial.printf("[NTP] UTC time: %llu ms\n", now_ms);
    } else {
      Serial.println("[NTP] Failed to obtain time");
    }

    vTaskDelay(pdMS_TO_TICKS(10000));  // wait 10 seconds
  }
}


void sendBuzz(int buttonID) {
  struct timeval tv;
  gettimeofday(&tv, NULL);
  unsigned long long now_ms = (unsigned long long)tv.tv_sec * 1000 + tv.tv_usec / 1000;

  StaticJsonDocument<128> doc;
  doc["type"] = "buzz";
  doc["mac"] = macAddress;
  doc["button"] = buttonID;
  doc["timestamp"] = now_ms;

  char buffer[128];
  size_t len = serializeJson(doc, buffer);
  udp.beginPacket(serverIP, UDP_PORT);
  udp.write((uint8_t*)buffer, len);
  udp.endPacket();

  Serial.printf("[BUZZ] MAC %s - Button %d at %llu ms (UTC)\n", macAddress.c_str(), buttonID, now_ms);
}

void TaskButtons(void* pv) {
  bool last1 = HIGH, last2 = HIGH;
  while (1) {
    bool curr1 = digitalRead(BUTTON1_PIN);
    bool curr2 = digitalRead(BUTTON2_PIN);

    if (last1 == HIGH && curr1 == LOW) sendBuzz(1);
    if (last2 == HIGH && curr2 == LOW) sendBuzz(2);

    last1 = curr1;
    last2 = curr2;
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON1_PIN, INPUT_PULLUP);
  pinMode(BUTTON2_PIN, INPUT_PULLUP);
  connectWiFiAndNTP();

  xTaskCreatePinnedToCore(printNTPStatus, "NTPStatus", 4096, NULL, 1, NULL, 1);
  xTaskCreatePinnedToCore(TaskButtons, "Buttons", 4096, NULL, 1, NULL, 1);
}

void loop() {}
