#include <LowPower.h>
#include <eventtimer.h>
#include <TheThingsNetwork.h>
const char *appEui = "70B3D57ED0014EEF";
const char *appKey = "D5A057BD36B7E74F65183907A5D9424A";

#define loraSerial Serial1
#define debugSerial Serial

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_US915

TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);

//Pins
#define trigPin  8
#define readPin   A0

//Const Variables
// Values lowered for monitoring values during testing
const int slowModeIntervalTime = 15*60; // 15 minutes * 60 seconds = number of seconds to sleep for

//Global Variables
int runningAvg;
int baseline;
EventTimer timer;
int lastReportedValue;
bool fastMode;
bool baselineCheck = true;

void setup() {    
  loraSerial.begin(57600);
  debugSerial.begin(9600);  
  pinMode(readPin, INPUT);  
  pinMode(trigPin, OUTPUT);
  digitalWrite(trigPin, LOW);
  runningAvg = 0;
  delay(120000);
  baseline = getDistance();
  baselineCheck = false;
  debugSerial.print("BASELINE: ");
  debugSerial.println(baseline);
  lastReportedValue = baseline;
  fastMode = true;
  ttn.showStatus();
  debugSerial.println("-- JOIN");
  ttn.join(appEui, appKey);  
}

void loop() {  
    if(fastMode) {
      sendData(getDistance());      
    }
    else {
      sendData(getDistance());
      sleepLowPower(slowModeIntervalTime);
    }    
}

//getDistance - Function that gets a single distance point from the ultrasonic sensor-----------------------------------------------------------------------
// Function based heavily off of Arduino tutorial code found here https://www.instructables.com/id/Simple-Arduino-and-HC-SR04-Example/
int getDistance()
{
  float val; 
  long cm = 0;
  float avg;
  int count = 0;
  digitalWrite(trigPin, HIGH);
  for (int i = 0; i < 60; i++){
    timer.start(1000);            
    val = (analogRead(A0) * 5.0/1023)/0.0049;    
    if(val < lastReportedValue + 20 && val > lastReportedValue - 20) {
      cm += val;  
      count++;    
    }
    else if(baselineCheck) {
      cm += val;  
      count++;
    }
    else {
      debugSerial.print("REJECTED - ");
    }
    debugSerial.print("Distance Value ");
    debugSerial.print(i);
    debugSerial.print(": ");
    debugSerial.print(val);
    debugSerial.print(", total value: ");
    debugSerial.println(cm);
    while(!timer.checkExpired()) {
      continue;
    }
  }
  digitalWrite(trigPin, LOW);
  if(count == 0) {
    avg = 0;
  }
  else {
    avg = cm / count;
  }
  debugSerial.print("Average Value: ");
  debugSerial.println(baseline - avg);
  if(baselineCheck) {
    baselineCheck = false;
    return avg;
  }
  if(avg > baseline) {
    return baseline;
  }
  else {
    return baseline - avg;
  }
}

//sendData - Sends the flood level reading data point to the Things Network/Database------------------------------------------------------------------------
void sendData(int measurement) {
  debugSerial.print("Sending measurement: ");
  debugSerial.println(measurement);
  byte payload[2];    
  payload[0] = (measurement & 0xFF00) >> 8;
  payload[1] = (measurement & 0x00FF);
  ttn.sendBytes(payload, sizeof(payload));
  debugSerial.println("Data Sent");
}

//sleepLowPower - Puts the arduino to sleep for a specified amount of time------------------------------------------------------------------------------------------
void sleepLowPower(int seconds) {
  int sleepTime = seconds/8;
  for(int i = 0; i < sleepTime; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
}
