#include <eventtimer.h>
#include <TheThingsNetwork.h>

// Set your AppEUI and AppKey
const char *appEui = "0000000000000000";
const char *appKey = "00000000000000000000000000000000";

#define loraSerial Serial1
#define debugSerial Serial

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_US915

TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);


//Pins
#define trigPin 13
#define echoPin 12


//Const Variables
const int slowModeIntervalTime = 15*60;
const int fastModeIntervalTime = 60;



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
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  runningAvg = 0;
  baseline = establishBaseline();
  thisReportedValue = baseline;
  fastMode = false;
  ttn.join(appEui, appKey);
}

void loop() 
{
  // Check if most recently recorded value is within 6.25%. This value used instead of 5% so bit-shifting can be used
  // as this is slightly less computationally intensive than multiplying by 0.05
  if (thisReportedValue > (lastReportedValue >> 4))
  {
    fastMode = true;
  }
  else
  {
    fastMode = false;
  }
  
  lastReportedValue = thisReportedValue;
  if(fastMode) 
  {
    // for loop to force minute of sleep
    // take reading
  }
  else 
  {
    // for loop to force 15 minutes of sleep
    // take reading
  }
  
}


//getDistance - Function that gets a single distance point from the ultrasonic sensor-----------------------------------------------------------------------
// Function based heavily off of Arduino tutorial code found here https://www.instructables.com/id/Simple-Arduino-and-HC-SR04-Example/
long getDistance()
{
  long duration, distance;
  digitalWrite(trigPin, LOW);  // Added this line
  delayMicroseconds(2); // Added this line
  timer.start(2);
  while(!timer.checkExpired()){;}
  digitalWrite(trigPin, HIGH);
  timer.start(10);
  while(!timer.checkExpired()){;}
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;
  return distance;
}

//establishBaseline - sets the value of the unflooded street distance---------------------------------------------------------------------------------------
int establishBaseline()
{

  int value = 0;
  int iterations = 0;
  timer.start(60000);
  while(!timer.checkExpired())
  {
    value += getDistance();
    iterations += 1;
  }
  return value / iterations;
}

//sendData - Sends the flood level reading data point to the Things Network/Database------------------------------------------------------------------------
void sendData(long measurement) {
  byte payload[4];
  payload[0] = (measurement & 0xFF000000) >> 24;
  payload[1] = (measurement & 0x00FF0000) >> 16;
  payload[2] = (measurement & 0x0000FF00) >> 8;
  payload[3] = (measurement & 0x000000FF);
  ttn.sendBytes(payload, sizeof(payload));
}

//sleepLowPower - Puts the arduino to sleep for a specified amount of time------------------------------------------------------------------------------------------
void sleepLowPower() {
  
}

