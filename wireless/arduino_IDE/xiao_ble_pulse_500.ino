#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define PIN_A0 2
#define PIN_A1 3

BLEServer* pServer = nullptr;
BLECharacteristic* pChar = nullptr;
bool deviceConnected = false;

const uint32_t SAMPLE_US = 2000;  // 500 Hz
const uint32_t SEND_US   = 10000; // 100 Hz (5 samples)
uint32_t lastSample = 0;
uint32_t lastSend   = 0;

struct Sample { uint32_t t_ms; bool a0; bool a1; };
Sample buf[5];
int bufIndex = 0;

class MyCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* s) override {
    deviceConnected = true;
    Serial.println("Client connected");
  }
  void onDisconnect(BLEServer* s) override {
    deviceConnected = false;
    Serial.println("Client disconnected — restarting advertising");
    s->startAdvertising();
  }
};

void setup() {
  Serial.begin(115200);
  pinMode(PIN_A0, INPUT_PULLDOWN);
  pinMode(PIN_A1, INPUT_PULLDOWN);

  BLEDevice::init("Seeed_BLE");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyCallbacks());

  BLEService* svc = pServer->createService("12345678-1234-1234-1234-123456789abc");
  pChar = svc->createCharacteristic(
    "abcdefab-1234-5678-1234-abcdefabcdef",
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pChar->addDescriptor(new BLE2902());
  pChar->setValue("READY");
  svc->start();

  BLEAdvertising* adv = BLEDevice::getAdvertising();
  adv->addServiceUUID("12345678-1234-1234-1234-123456789abc");
  adv->start();

  lastSample = micros();
  lastSend   = micros();
  Serial.println("BLE advertising started...");
}

void loop() {
  uint32_t now = micros();

  // 500 Hz sampling
  if (now - lastSample >= SAMPLE_US) {
    lastSample += SAMPLE_US; // reduce drift
    uint32_t t_ms = millis();
    bool a0 = digitalRead(PIN_A0);
    bool a1 = digitalRead(PIN_A1);

    if (bufIndex < 5) {
      buf[bufIndex++] = { t_ms, a0, a1 };
    } else {
      bufIndex = 5; // safety
    }
  }

  // 100 Hz transmit (bundle 5 samples)
  if (deviceConnected && (now - lastSend >= SEND_US) && bufIndex == 5) {
    lastSend += SEND_US;

    // payload: "t,A0,HIGH,A1,LOW; t,A0,LOW,A1,HIGH; ..."
    String payload;
    payload.reserve(5 * 24);
    for (int i = 0; i < 5; i++) {
      payload += String(buf[i].t_ms); payload += ',';
      payload += "A0,"; payload += (buf[i].a0 ? "HIGH" : "LOW"); payload += ',';
      payload += "A1,"; payload += (buf[i].a1 ? "HIGH" : "LOW");
      if (i < 4) payload += ';';
    }

    pChar->setValue(payload.c_str());
    pChar->notify();
    // Debug print
    Serial.println(payload);
    bufIndex = 0;
  }
}
