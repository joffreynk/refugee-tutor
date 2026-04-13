// Ultrasonic Sensor Module - Distance measurement

#ifndef ULTRASONIC_H
#define ULTRASONIC_H

#include <Arduino.h>

class UltrasonicSensor {
private:
    int triggerPin;
    int echoPin;
    
    unsigned long timeout_us;
    
public:
    UltrasonicSensor(int triggerPin, int echoPin);
    
    bool initialize();
    
    int readDistanceCm();
    int readDistanceMm();
    
    void setTimeout(unsigned long timeout);
};

#endif
