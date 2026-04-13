// Servo Controller - Pan and Tilt head control
// Based on REX-RDT ArmBot specifications

#ifndef SERVO_CONTROLLER_H
#define SERVO_CONTROLLER_H

#include <ESP32Servo.h>
#include "i2c_protocol.h"

class ServoController {
private:
    Servo servo1;
    Servo servo2;

    int servo1Pin;
    int servo2Pin;

    int servo1Angle;
    int servo2Angle;

    int servo1Home;
    int servo2Home;

    int minPulseWidth;
    int maxPulseWidth;

public:
    ServoController(int s1Pin, int s2Pin);

    bool initialize();

    void setServo1Angle(int angle);
    void setServo2Angle(int angle);
    void setAngles(int angle1, int angle2);

    void setLookDirection(LookDirection direction);

    void goHome();

    int getServo1Angle();
    int getServo2Angle();

    void calibrate(int home1, int home2);

    void sweep();
};

#endif
