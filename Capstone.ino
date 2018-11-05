#include <eventtimer.h>

#define trigPin 13
#define echoPin 12

int base;
EventTimer timer;

void setup() {
  Serial.begin (9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  base = 0;
}

void loop() {
  for (int i = 0; i < 12; i++)
  {
    Serial.println("loopstart");
    timer.start(5000);
    while(!timer.checkExpired());
    base += getDistance();
    Serial.println(base);
  }
  Serial.print("Averaging");
  Serial.println(base / 12);
  base = 0;
}

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

