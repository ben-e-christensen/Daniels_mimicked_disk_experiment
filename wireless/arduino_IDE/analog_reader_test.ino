// analog_reader.ino

#define PIN_A 2  // A0
#define PIN_B 3  // A1

float readVoltage(int pin) {
  return analogRead(pin) * (3.3 / 4095.0);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_A, INPUT);
  pinMode(PIN_B, INPUT);
}

void loop() {
  float va = readVoltage(PIN_A);
  float vb = readVoltage(PIN_B);
  Serial.print("Read A0: ");
  Serial.print(va, 3);
  Serial.print(" V, B1: ");
  Serial.print(vb, 3);
  Serial.println(" V");
  delay(100);  // ~10 Hz read rate (can match sender frequency if needed)
}
