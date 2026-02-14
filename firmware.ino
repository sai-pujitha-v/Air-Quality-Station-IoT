#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define GM_PIN D2      
#define BUZ_PIN D5    
#define LOG_PERIOD 15000 

volatile unsigned long pulseCount = 0; 
unsigned long lastMillis = 0;
const float J305_FACTOR = 0.0057; 

void IRAM_ATTR handle_pulse() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);
  pinMode(GM_PIN, INPUT_PULLUP);
  pinMode(BUZ_PIN, OUTPUT);
  
  attachInterrupt(digitalPinToInterrupt(GM_PIN), handle_pulse, FALLING);

  WiFi.begin("SSID", "PASS");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nRadiation Monitor Online.");
}

void loop() {
  unsigned long currentMillis = millis();

  if (pulseCount > 0) {
    digitalWrite(BUZ_PIN, HIGH);
    delayMicroseconds(50); 
    digitalWrite(BUZ_PIN, LOW);
  }

  if (currentMillis - lastMillis >= LOG_PERIOD) {
    float cpm = pulseCount * (60000.0 / LOG_PERIOD);
    float dose = cpm * J305_FACTOR;

    Serial.print("CPM: "); Serial.print(cpm);
    Serial.print(" | Dose: "); Serial.println(dose);

    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;
      http.begin(client, "http://YOUR_LOCAL_IP:8501/update");
      http.addHeader("Content-Type", "application/json");
      String json = "{\"cpm\":" + String(cpm) + ",\"usvh\":" + String(dose) + "}";
      http.POST(json);
      http.end();
    }

    pulseCount = 0;
    lastMillis = currentMillis;
  }
}
