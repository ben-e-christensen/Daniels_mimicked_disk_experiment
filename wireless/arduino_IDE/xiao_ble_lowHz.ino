#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLE2902.h>

BLEServer *pServer;
BLEService *pService;
BLECharacteristic *pCharacteristic;
BLEAdvertising *pAdvertising;

volatile bool deviceConnected = false;

const int pins[3] = {2, 3, 4};  // Pi GPIO 23, 24, 25 → Xiao GPIO 2, 3, 4
unsigned long startMs[3] = {0, 0, 0};
bool wasHigh[3] = {false, false, false};

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) override {
    deviceConnected = true;
    Serial.println("Client connected");
  }
  void onDisconnect(BLEServer* pServer) override {
    deviceConnected = false;
    Serial.println("Client disconnected — restarting advertising");
    pServer->startAdvertising();
  }
};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 3; i++) pinMode(pins[i], INPUT_PULLDOWN);

  BLEDevice::init("Seeed_BLE");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  pService = pServer->createService("12345678-1234-1234-1234-123456789abc");
  pCharacteristic = pService->createCharacteristic(
    "abcdefab-1234-5678-1234-abcdefabcdef",
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristic->addDescriptor(new BLE2902());
  pCharacteristic->setValue("Hello BLE!");
  pService->start();

  pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID("12345678-1234-1234-1234-123456789abc");

  BLEAdvertisementData advData;
  advData.setName("Seeed_BLE");
  advData.setManufacturerData("Seeed");
  pAdvertising->setAdvertisementData(advData);

  pAdvertising->start();
  Serial.println("BLE advertising started...");
}

void loop() {
  for (int i = 0; i < 3; i++) {
    bool nowHigh = digitalRead(pins[i]);

    if (nowHigh && !wasHigh[i]) {
      startMs[i] = millis();
      wasHigh[i] = true;
    }
    else if (!nowHigh && wasHigh[i]) {
      unsigned long dur = millis() - startMs[i];
      wasHigh[i] = false;

      char msg[48];
      snprintf(msg, sizeof(msg), "%d,%lu,%lu\n", pins[i], startMs[i], dur);
      if (deviceConnected) {
        pCharacteristic->setValue((uint8_t*)msg, strlen(msg));
        pCharacteristic->notify();
      }
      Serial.print("Pulse: ");
      Serial.print(msg); // includes newline
    }
  }
  delay(2);
}