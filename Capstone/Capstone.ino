#include <eventtimer.h>


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
bool fastMode;


void setup() {
  Serial.begin (9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  runningAvg = 0;
  baseline = establishBaseline();
  lastReportedValue = baseline;
  fastMode = false;
}

void loop() {

  if(fastMode) {
    
  }
  else {
    
  }

  
}

//getDistance - Function that gets a single distance point from the ultrasonic sensor-----------------------------------------------------------------------
// Function based heavily off of Arduino tutorial code found here https://www.instructables.com/id/Simple-Arduino-and-HC-SR04-Example/
int getDistance()
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
void sendData() {

}

//sleepLowPower - Puts the arduino to sleep for a specified amount of time------------------------------------------------------------------------------------------
void sleepLowPower() {
  
}

