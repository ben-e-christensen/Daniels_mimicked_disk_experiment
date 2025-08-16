// Xiao ESP32C3 — 500 Hz sampler, 100 Hz single BLE notify (20 bytes)
// Payload: 10 x uint16_le -> [A0_0..A0_4, A1_0..A1_4]

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>

const int PIN_A0 = A0;
const int PIN_A1 = A1;

const uint32_t N = 5;               // samples per channel per packet
const uint32_t GAP_US = 2000;       // 2 ms between samples -> 500 Hz
const uint32_t PERIOD_US = 10000;   // 10 ms per packet -> 100 Hz

uint16_t a0[N], a1[N];

static const char* SVC_UUID  = "c0de0001-0000-4a6f-9e00-000000000001";
static const char* CHR_UUID  = "c0de1000-0000-4a6f-9e00-000000000001";

BLECharacteristic* chr = nullptr;

static inline void u16le(uint8_t* b, uint16_t v) { b[0] = v; b[1] = v >> 8; }

class ServerCallbacks : public BLEServerCallbacks {
  void onDisconnect(BLEServer* s) override { s->getAdvertising()->start(); }
};

void setup() {
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && (millis() - t0 < 2000)) {}

  analogReadResolution(12);                // 0..4095
  analogSetPinAttenuation(PIN_A0, ADC_11db);
  analogSetPinAttenuation(PIN_A1, ADC_11db);

  BLEDevice::init("XiaoC3-Analog-100Hz");
  auto* server  = BLEDevice::createServer();
  server->setCallbacks(new ServerCallbacks());
  auto* service = server->createService(SVC_UUID);

  chr = service->createCharacteristic(
      CHR_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  chr->addDescriptor(new BLE2902());       // CCCD for notify

  service->start();
  auto* adv = BLEDevice::getAdvertising();
  adv->addServiceUUID(SVC_UUID);
  adv->setScanResponse(true);
  adv->setMinPreferred(0x06);
  adv->setMaxPreferred(0x12);
  server->getAdvertising()->start();

  Serial.println("Advertising. Single char notify (A0x5 + A1x5).");
}

void loop() {
  const uint32_t t0 = micros();

  for (uint8_t i = 0; i < N; i++) {
    a0[i] = analogRead(PIN_A0);
    a1[i] = analogRead(PIN_A1);
    if (i < N - 1) delayMicroseconds(GAP_US);
  }

  // Pack 10 x u16 into 20-byte buffer: A0[5], then A1[5]
  uint8_t buf[20];
  for (uint8_t i = 0; i < N; i++) u16le(&buf[2*i],       a0[i]);
  for (uint8_t i = 0; i < N; i++) u16le(&buf[2*(N+i)],   a1[i]);

  chr->setValue(buf, sizeof(buf));
  chr->notify();

  // (Optional) quick preview on serial
  Serial.print("pkt:");
  for (uint8_t i = 0; i < N; i++) { Serial.print(' '); Serial.print(a0[i]); }
  Serial.print(" |");
  for (uint8_t i = 0; i < N; i++) { Serial.print(' '); Serial.print(a1[i]); }
  Serial.println();

  const uint32_t dt = micros() - t0;
  if (dt < PERIOD_US) delayMicroseconds(PERIOD_US - dt);
}
