// Xiao ESP32-C3: pick the active analog pin and print only that one
// Minimal: reads A0 & A1, prints whichever is above THRESH_MV (higher one if both)

const int PIN0 = A0;
const int PIN1 = A1;

const int THRESH_MV = 50;    // treat anything under ~50 mV as "no value"
const unsigned long LOOP_DELAY_MS = 33; // ~30 Hz

void setup() {
  Serial.begin(115200);
  pinMode(PIN0, INPUT);
  pinMode(PIN1, INPUT);

  analogReadResolution(12);               // 0..4095
  analogSetPinAttenuation(PIN0, ADC_11db); // 0..~3.3V
  analogSetPinAttenuation(PIN1, ADC_11db);

  Serial.println("ms,pin,raw,mV,volts");
}

void loop() {
  // Read both pins
  int raw0 = analogRead(PIN0);
  int mv0  = analogReadMilliVolts(PIN0);

  int raw1 = analogRead(PIN1);
  int mv1  = analogReadMilliVolts(PIN1);

  // Decide which pin "has a value"
  int chosenPin   = -1;
  int chosenRaw   = 0;
  int chosenMilli = 0;

  bool p0_active = (mv0 >= THRESH_MV);
  bool p1_active = (mv1 >= THRESH_MV);

  if (p0_active && !p1_active) {
    chosenPin = PIN0; chosenRaw = raw0; chosenMilli = mv0;
  } else if (!p0_active && p1_active) {
    chosenPin = PIN1; chosenRaw = raw1; chosenMilli = mv1;
  } else if (p0_active && p1_active) {
    // both active → pick the higher voltage
    if (mv0 >= mv1) { chosenPin = PIN0; chosenRaw = raw0; chosenMilli = mv0; }
    else            { chosenPin = PIN1; chosenRaw = raw1; chosenMilli = mv1; }
  } else {
    // neither active → print nothing this cycle
  }

  if (chosenPin != -1) {
    float volts = chosenMilli / 1000.0f;
    Serial.print(millis()); Serial.print(",");
    // Print which pin by Arduino name
    if (chosenPin == PIN0)      Serial.print("A0,");
    else if (chosenPin == PIN1) Serial.print("A1,");
    else                        Serial.print("UNK,");
    Serial.print(chosenRaw); Serial.print(",");
    Serial.print(chosenMilli); Serial.print(",");
    Serial.println(volts, 3);
  }

  delay(LOOP_DELAY_MS);
}
 