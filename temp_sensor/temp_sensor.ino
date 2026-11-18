#include <OneWire.h>
#include <DallasTemperature.h>
#include <SoftwareSerial.h>

const uint8_t PIN_STATE = 5; //module stat

OneWire oneWire(3); //DS18B20
DallasTemperature sensor(&oneWire);
SoftwareSerial bt(A4, A5);

void setup() {
  pinMode(PIN_STATE, INPUT);
  Serial.begin(9600);
  bt.begin(9600);
  sensor.begin();
}

void loop() {
  sensor.requestTemperatures();
  float celsius = sensor.getTempCByIndex(0);

  if (digitalRead(PIN_STATE) == HIGH) {
    bt.print("T:");
    bt.println(celsius, 2);
  }

  Serial.print("T=");
  Serial.print(celsius, 2);
  Serial.print("\n");
  Serial.print("B=");
  Serial.print(digitalRead(PIN_STATE));
  Serial.print("\n");

  delay(2000);
}
