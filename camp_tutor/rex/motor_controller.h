// Motor Controller - 4 Omni-Directional Wheel Drive
// Based on REX-RDT OmniBot specifications

#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>
#include "i2c_protocol.h"

class MotorController {
private:
    // Motor A pins
    int motorA1;
    int motorA2;
    // Motor B pins
    int motorB1;
    int motorB2;
    // Motor C pins
    int motorC1;
    int motorC2;
    // Motor D pins
    int motorD1;
    int motorD2;

    // PWM channels (ESP32 LEDC)
    int pwmChannelA1, pwmChannelA2;
    int pwmChannelB1, pwmChannelB2;
    int pwmChannelC1, pwmChannelC2;
    int pwmChannelD1, pwmChannelD2;

    // PWM settings
    const int pwmFreq = 50;
    const int pwmResolution = 8;

    int currentSpeed;
    bool isMoving;

    void setMotorSpeed(int pin, int channel, int speed);

public:
    MotorController();

    bool initialize(int a1, int a2, int b1, int b2, int c1, int c2, int d1, int d2);

    void moveForward(int speed = 150);
    void moveBackward(int speed = 150);
    void moveLeft(int speed = 150);
    void moveRight(int speed = 150);

    // Omni-directional movements
    void moveDirection(MoveDirection direction);
    void omniMove(OmniDirection omniDir, int speed = 150);

    void stop();

    bool isMotorMoving();

    void setSpeed(int speed);

    // Individual motor control for debugging
    void setMotorA(int speed);
    void setMotorB(int speed);
    void setMotorC(int speed);
    void setMotorD(int speed);
};

#endif
