#include "BluetoothSerial.h"
// Access Wifi Library & Asynchronous Web Server for ESP32
#include <WiFi.h>
#include <HTTPClient.h>

// LED 1
#define LED1_RED 15   // GPIO 15
#define LED1_GREEN 2  // GPIO 2
#define LED1_BLUE 4   // GPIO 4

// LED 2
#define LED2_RED 5     // GPIO 5
#define LED2_GREEN 18  // GPIO 18
#define LED2_BLUE 19   // GPIO 19

// LED 3
#define LED3_RED 21    // GPIO 21
#define LED3_GREEN 22  // GPIO 22
#define LED3_BLUE 23   // GPIO 23

// ACS712 Sensor
#define ACS712 17  // GPIO 17

// Setting PWM Properties
#define FREQUENCY 5000
// Channel for LED 1
#define LED1_CHANNEL_RED 0    // Channel 0
#define LED1_CHANNEL_GREEN 1  // Channel 1
#define LED1_CHANNEL_BLUE 2   // Channel 2
// Channel for LED 2
#define LED2_CHANNEL_RED 3    // Channel 3
#define LED2_CHANNEL_GREEN 4  // Channel 4
#define LED2_CHANNEL_BLUE 5   // Channel 5
// Channel for LED 3
#define LED3_CHANNEL_RED 6    // Channel 6
#define LED3_CHANNEL_GREEN 7  // Channel 7
#define LED3_CHANNEL_BLUE 8   // Channel 8
#define RESOLUTION 8

// Setting Configuration for Network ESP32
const char *ssid = "ESP32-SMART-LAMP";
const char *password = "adikberadik97";

// Const url for api call
const char *baseApiPath = "http://127.0.0.1:500/api";

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);
  getWifiConnection(); // Get wifi connection

  // Set LED 1  Pin Mode
  setLEDPinMode(LED1_RED, LED1_GREEN, LED1_BLUE, OUTPUT);
  // Set LED 2 Pin Mode
  setLEDPinMode(LED2_RED, LED2_GREEN, LED2_BLUE, OUTPUT);
  // Set LED 3 Pin Mode
  setLEDPinMode(LED3_RED, LED3_GREEN, LED3_BLUE, OUTPUT);

  // Set LED 1 "OFF" By Default
  setDefaultLEDState(LED1_RED, LED1_GREEN, LED1_BLUE, LOW);
  // Set LED 2 "OFF" By Default
  setDefaultLEDState(LED2_RED, LED2_GREEN, LED2_BLUE, LOW);
  // Set LED 3 "OFF" By Default
  setDefaultLEDState(LED3_RED, LED3_GREEN, LED3_BLUE, LOW);

  // Configure Each LED Channel to It's PWM Functionalities
  pwmConfiguration(LED1_CHANNEL_RED, LED1_CHANNEL_GREEN, LED1_CHANNEL_BLUE, FREQUENCY, RESOLUTION);
  pwmConfiguration(LED2_CHANNEL_RED, LED2_CHANNEL_GREEN, LED2_CHANNEL_BLUE, FREQUENCY, RESOLUTION);
  pwmConfiguration(LED3_CHANNEL_RED, LED3_CHANNEL_GREEN, LED3_CHANNEL_BLUE, FREQUENCY, RESOLUTION);

  // Set Each LED to It's Channel
  pwmAttachPin(LED1_RED, LED1_GREEN, LED1_BLUE, LED1_CHANNEL_RED, LED1_CHANNEL_GREEN, LED1_CHANNEL_BLUE);
  pwmAttachPin(LED2_RED, LED2_GREEN, LED2_BLUE, LED2_CHANNEL_RED, LED2_CHANNEL_GREEN, LED2_CHANNEL_BLUE);
  pwmAttachPin(LED3_RED, LED3_GREEN, LED3_BLUE, LED3_CHANNEL_RED, LED3_CHANNEL_GREEN, LED3_CHANNEL_BLUE);
}

void loop() {
  // put your main code here, to run repeatedly:
  // Check if wifi connection successful then do the HTTP request
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String endpoint = serverName + "/get_lamps";
    http.begin(serverPath.c_str());

    // Send HTTP GET request
    int response = http.GET();
  }
}

// Function for Connecting to Wi-Fi Network with SSID and Password
void getWifiConnection() {
  WiFi.begin(ssid, password);
  Serial.println("Connecting to ");
  Serial.print(ssid);
  if (WiFi.status() == WL_IDLE_STATUS) {
    Serial.println("Wifi connection failed. Please check your credentials");
  } else {
    Serial.println("Wifi connected.");
    Serial.println("IP address: ");
    Serial.print(WiFi.localIP());
    Serial.println("");
  }
}

// Function to Set Pin Mode
void setLEDPinMode(int red, int green, int blue, uint8_t mode) {
  pinMode(red, mode);
  pinMode(green, mode);
  pinMode(blue, mode);
}

// Function to Set Default State of LEDs
void setDefaultLEDState(int red, int green, int blue, int state) {
  digitalWrite(red, state);
  digitalWrite(green, state);
  digitalWrite(blue, state);
}

// Function to Configure LED PWM Functionalitites
void pwmConfiguration(int rChannel, int gChannel, int bChannel, int frequency, int resolution) {
  ledcSetup(rChannel, frequency, resolution);
  ledcSetup(gChannel, frequency, resolution);
  ledcSetup(bChannel, frequency, resolution);
}

// Function to Attach the Channel to The GPIO to be Controlled
void pwmAttachPin(int red, int green, int blue, int rChannel, int gChannel, int bChannel) {
  ledcAttachPin(red, rChannel);
  ledcAttachPin(green, gChannel);
  ledcAttachPin(blue, bChannel);
}
