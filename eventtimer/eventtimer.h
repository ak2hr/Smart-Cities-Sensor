/* timer! */ 

#ifndef EventTimer_h
#define EventTimer_h

#include "Arduino.h" 

class EventTimer
{
  private: 
    unsigned long startTime; 
    unsigned long duration; 
  public:
    boolean isRunning; 
	EventTimer(){
		isRunning = false; 
		startTime = 0; 
		duration = 0; 
	}
	
	void start(unsigned long howlong){
       isRunning = true; 
       duration = howlong;
       startTime = millis();	   
    }
  boolean checkExpired(void)
    {
      if(( millis() - startTime >= duration) && isRunning)
      {
        isRunning = false; 
        return true; 
      }
      return false; 
    }
    void cancel(void){
      isRunning = false; 
    }
};

#endif
