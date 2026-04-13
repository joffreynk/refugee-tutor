// Servo Controller Implementation - REX ArmBot spec
// Servo1: Right/Left (GPIO 2)
// Servo2: Up/Down (GPIO 26)

#include "servo_controller.h"

ServoController::ServoController(int s1Pin, int s2Pin) {
    this->servo1Pin = s1Pin;
    this->servo2Pin = s2Pin;
    this->servo1Angle = 90;
    this->servo2Angle = 90;
    this->servo1Home = 90;
    this->servo2Home = 90;
    this->minPulseWidth = 600;
    this->maxPulseWidth = 2500;
}

bool ServoController::initialize() {
    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);

    servo1.setPeriodHertz(50);
    servo2.setPeriodHertz(50);

    bool s1Ok = servo1.attach(servo1Pin, minPulseWidth, maxPulseWidth);
    bool s2Ok = servo2.attach(servo2Pin, minPulseWidth, maxPulseWidth);

    if (s1Ok && s2Ok) {
        delay(100);
        servo1.write(servo1Home);
        servo2.write(servo2Home);
        delay(500);
        return true;
    }
    return false;
}

void ServoController::setServo1Angle(int angle) {
    angle = constrain(angle, 0, 180);
    servo1Angle = angle;
    servo1.write(angle);
}

void ServoController::setServo2Angle(int angle) {
    angle = constrain(angle, 0, 180);
    servo2Angle = angle;
    servo2.write(angle);
}

void ServoController::setAngles(int angle1, int angle2) {
    setServo1Angle(angle1);
    setServo2Angle(angle2);
}

void ServoController::setLookDirection(LookDirection direction) {
    switch (direction) {
        case LOOK_LEFT:
            setServo1Angle(40);
            setServo2Angle(90);
            break;
        case LOOK_RIGHT:
            setServo1Angle(140);
            setServo2Angle(90);
            break;
        case LOOK_CENTER:
        case LOOK_HOME:
        default:
            setServo1Angle(servo1Home);
            setServo2Angle(servo2Home);
            break;
    }
}

void ServoController::goHome() {
    setLookDirection(LOOK_HOME);
}

int ServoController::getServo1Angle() {
    return servo1Angle;
}

int ServoController::getServo2Angle() {
    return servo2Angle;
}

void ServoController::calibrate(int home1, int home2) {
    servo1Home = constrain(home1, 0, 180);
    servo2Home = constrain(home2, 0, 180);
    goHome();
}

void ServoController::sweep() {
    for (int angle = 0; angle <= 180; angle += 10) {
        servo1.write(angle);
        delay(50);
    }
    for (int angle = 180; angle >= 0; angle -= 10) {
        servo1.write(angle);
        delay(50);
    }
}
