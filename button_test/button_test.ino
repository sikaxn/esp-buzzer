const int BUTTON1_PIN = 16;
const int BUTTON2_PIN = 17;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON1_PIN, INPUT_PULLUP);
  pinMode(BUTTON2_PIN, INPUT_PULLUP);

  Serial.println("Button test ready. Waiting for presses...");
}

void loop() {
  if (digitalRead(BUTTON1_PIN) == LOW) {
    Serial.println("Button 1 (GPIO 16) pressed");
    delay(200);  // simple debounce
  }

  if (digitalRead(BUTTON2_PIN) == LOW) {
    Serial.println("Button 2 (GPIO 17) pressed");
    delay(200);  // simple debounce
  }

  delay(10);
}
