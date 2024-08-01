#include <pm2008_i2c.h>
#include <DHT11.h>

struct SensorValues {
  float pm2p5Value;
  float pm10Value;
  float humidity;
  float temperature;
  int analogValue;
};

PM2008_I2C pm2008_i2c;
DHT11 dht11(A1);

// Fine Dust Sensor, DHT11, Flame Detection Sensor setting
void setup() {
  // wait for PM2008N to be changed to I2C mode
  delay(5000);
  
  pm2008_i2c.begin();
  Serial.begin(9600);
  pm2008_i2c.command();

  pinMode(A0, INPUT);
}

// Measure sensor values
SensorValues getValue() {
  SensorValues values;

  uint8_t ret = pm2008_i2c.read();
  if (ret == 0) {
    values.pm2p5Value = pm2008_i2c.pm2p5_grimm;
  } else {
    values.pm2p5Value = -1.0;
  }

  ret = pm2008_i2c.read();
  if (ret == 0) {
    values.pm10Value = pm2008_i2c.pm10_grimm;
  } else {
    values.pm10Value = -1.0;
  }

  int i;
  float humi, temp;
  if ((i = dht11.read(humi, temp)) == 0) {
    values.humidity = humi;
    values.temperature = temp;
  } else {
    values.humidity = -1.0;
    values.temperature = -1.0;
  }

  values.analogValue = analogRead(A0);

  return values;
}

// Print sensor values
void printValue(const SensorValues& values) {
  Serial.print(values.pm2p5Value);
  Serial.print(",");
  Serial.print(values.pm10Value);
  Serial.print(",");
  Serial.print(values.humidity);
  Serial.print(",");
  Serial.print(values.temperature);
  Serial.print(",");
  Serial.println(values.analogValue);
  delay(1000);
}

// Start home sensor
void loop() {
  SensorValues values = getValue();
  printValue(values);
}
