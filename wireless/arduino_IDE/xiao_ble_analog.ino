#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer* pServer;
BLECharacteristic* pCharacteristic;
bool deviceConnected = false;

const int pinA = A0;  // match to Pico output A (GPIO14)
const int pinB = A1;  // match to Pico output B (GPIO15)

struct Sample {
  char channel;       // 'A' or 'B'
  uint32_t time_ms;   // timestamp
  float voltage;      // measured voltage
};

Sample buffer[5];
int bufIndex = 0;

unsigned long lastSample = 0;
unsigned long lastSend = 0;
const float VREF = 3.3;

class MyCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) override {
    deviceConnected = true;
    Serial.println("BLE client connected");
  }
  void onDisconnect(BLEServer* pServer) override {
    deviceConnected = false;
    Serial.println("BLE client disconnected — restarting advertising");
    pServer->startAdvertising();
  }
};

void setup() {
  Serial.begin(115200);

  BLEDevice::init("Seeed_BLE");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyCallbacks());

  BLEService* pService = pServer->createService("12345678-1234-1234-1234-123456789abc");

  pCharacteristic = pService->createCharacteristic(
    "abcdefab-1234-5678-1234-abcdefabcdef",
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristic->addDescriptor(new BLE2902());
  pCharacteristic->setValue("Ready.");
  pService->start();

  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID("12345678-1234-1234-1234-123456789abc");
  pAdvertising->start();

  Serial.println("BLE advertising started...");
}

void loop() {
  unsigned long now = millis();

  // 500 Hz sampling
  if (now - lastSample >= 2) {
    lastSample = now;

    int rawA = analogRead(pinA);
    int rawB = analogRead(pinB);
    float vA = rawA * VREF / 4095.0;
    float vB = rawB * VREF / 4095.0;

    // Only one should be active at a time
    if (vA > 0.1 && vA > vB) {
      buffer[bufIndex++] = {'A', now, vA};
    } else if (vB > 0.1) {
      buffer[bufIndex++] = {'B', now, vB};
    }

    if (bufIndex >= 5) bufIndex = 5;  // safety cap
  }

  // 100 Hz BLE packet send
  if (deviceConnected && now - lastSend >= 10 && bufIndex == 5) {
    lastSend = now;

    String payload = "";
    for (int i = 0; i < 5; i++) {
      payload += String(buffer[i].channel) + "," + buffer[i].time_ms + "," + String(buffer[i].voltage, 3);
      if (i < 4) payload += ";";
    }

    pCharacteristic->setValue(payload.c_str());
    pCharacteristic->notify();
    Serial.println("Sent: " + payload);

    bufIndex = 0;
  }
}
