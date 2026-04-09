// Ultrasonic Sensor Implementation

#include "ultrasonic.h"

UltrasonicSensor::UltrasonicSensor(int triggerPin, int echoPin) {
    this->triggerPin = triggerPin;
    this->echoPin = echoPin;
    this->timeout_us = 30000;
}

bool UltrasonicSensor::initialize() {
    pinMode(triggerPin, OUTPUT);
    pinMode(echoPin, INPUT);
    digitalWrite(triggerPin, LOW);
    return true;
}

int UltrasonicSensor::readDistanceCm() {
    digitalWrite(triggerPin, LOW);
    delayMicroseconds(2);
    digitalWrite(triggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(triggerPin, LOW);
    
    long duration = pulseIn(echoPin, HIGH, timeout_us);
    
    if (duration == 0) {
        return -1;
    }
    
    int distance = duration / 58;
    
    if (distance > 400 || distance < 2) {
        return -1;
    }
    
    return distance;
}

int UltrasonicSensor::readDistanceMm() {
    digitalWrite(triggerPin, LOW);
    delayMicroseconds(2);
    digitalWrite(triggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(triggerPin, LOW);
    
    long duration = pulseIn(echoPin, HIGH, timeout_us);
    
    if (duration == 0) {
        return -1;
    }
    
    return duration / 2.91;
}

void UltrasonicSensor::setTimeout(unsigned long timeout) {
    this->timeout_us = timeout;
}
