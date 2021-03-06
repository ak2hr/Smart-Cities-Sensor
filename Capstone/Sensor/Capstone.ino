#include <LowPower.h>
#include <eventtimer.h>
#include <TheThingsNetwork.h>
const char *appEui = "70B3D57ED0014EEF";
const char *appKey = "F8ABB3938C5FBBCED8EFD664CA370760";

#define loraSerial Serial1
#define debugSerial Serial

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_US915

TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);

//Pins
#define trigPin 13
#define echoPin 12

//Const Variables
// Values lowered for monitoring values during testing
const int slowModeIntervalTime = 10; //15*60
const int fastModeIntervalTime = 1; //60

//Global Variables
int runningAvg;
int baseline;
EventTimer timer;
int lastReportedValue;
int thisReportedValue;
bool fastMode;

void setup() {    
  loraSerial.begin(57600);
  debugSerial.begin(9600);  
  pinMode(A0, INPUT);
  runningAvg = 0;
  //baseline = getDistance();
  debugSerial.print("BASELINE: ");
  debugSerial.println(baseline);
  thisReportedValue = baseline;
  fastMode = false;
  ttn.showStatus();
  debugSerial.println("-- JOIN");
  ttn.join(appEui, appKey);  
}

void loop() {
  // Will need to keep in fastmode as levels rise, maybe different criteria for if already in fastmode
//    if (thisReportedValue > (lastReportedValue >> 4))
//    {
//        fastMode = true;
//    }
//    else
//    {
//        fastMode = false;
//    }
//
//    lastReportedValue = thisReportedValue;
    if(fastMode) {
      sendData(getDistance());
      //sleepLowPower(fastModeIntervalTime);
    }
    else {
      sendData(getDistance());
      //sleepLowPower(slowModeIntervalTime);
    }
    delay(5000);
}

//getDistance - Function that gets a single distance point from the ultrasonic sensor-----------------------------------------------------------------------
// Function based heavily off of Arduino tutorial code found here https://www.instructables.com/id/Simple-Arduino-and-HC-SR04-Example/
int getDistance()
{
  float val; 
  long cm = 0;
  float avg;

  for (int i = 0; i < 60; i++){
    timer.start(1000);
    val = analogRead(A0) * 5.0/1023;
    cm += (val/0.0049);
    debugSerial.print("Distance Value ");
    debugSerial.print(i);
    debugSerial.print(": ");
    debugSerial.print(val/0.0049);
    debugSerial.print(", total value: ");
    debugSerial.println(cm);
    while(!timer.checkExpired()) {
      continue;
    }
  }

  avg = cm / 60.0;
  debugSerial.print("Average Value: ");
  debugSerial.println(avg);
  return avg;
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
