// Motor Controller Implementation - 4 Omni-Directional Wheels
// Based on REX-RDT OmniBot specifications

#include "motor_controller.h"

MotorController::MotorController() {
    this->motorA1 = 15;
    this->motorA2 = 23;
    this->motorB1 = 32;
    this->motorB2 = 33;
    this->motorC1 = 5;
    this->motorC2 = 4;
    this->motorD1 = 27;
    this->motorD2 = 14;

    this->pwmChannelA1 = 4;
    this->pwmChannelA2 = 5;
    this->pwmChannelB1 = 6;
    this->pwmChannelB2 = 7;
    this->pwmChannelC1 = 8;
    this->pwmChannelC2 = 9;
    this->pwmChannelD1 = 10;
    this->pwmChannelD2 = 11;

    this->currentSpeed = 0;
    this->isMoving = false;
}

bool MotorController::initialize(int a1, int a2, int b1, int b2, int c1, int c2, int d1, int d2) {
    motorA1 = a1;
    motorA2 = a2;
    motorB1 = b1;
    motorB2 = b2;
    motorC1 = c1;
    motorC2 = c2;
    motorD1 = d1;
    motorD2 = d2;

    pinMode(motorA1, OUTPUT);
    pinMode(motorA2, OUTPUT);
    pinMode(motorB1, OUTPUT);
    pinMode(motorB2, OUTPUT);
    pinMode(motorC1, OUTPUT);
    pinMode(motorC2, OUTPUT);
    pinMode(motorD1, OUTPUT);
    pinMode(motorD2, OUTPUT);

    ledcSetup(pwmChannelA1, pwmFreq, pwmResolution);
    ledcAttachPin(motorA1, pwmChannelA1);
    ledcSetup(pwmChannelA2, pwmFreq, pwmResolution);
    ledcAttachPin(motorA2, pwmChannelA2);

    ledcSetup(pwmChannelB1, pwmFreq, pwmResolution);
    ledcAttachPin(motorB1, pwmChannelB1);
    ledcSetup(pwmChannelB2, pwmFreq, pwmResolution);
    ledcAttachPin(motorB2, pwmChannelB2);

    ledcSetup(pwmChannelC1, pwmFreq, pwmResolution);
    ledcAttachPin(motorC1, pwmChannelC1);
    ledcSetup(pwmChannelC2, pwmFreq, pwmResolution);
    ledcAttachPin(motorC2, pwmChannelC2);

    ledcSetup(pwmChannelD1, pwmFreq, pwmResolution);
    ledcAttachPin(motorD1, pwmChannelD1);
    ledcSetup(pwmChannelD2, pwmFreq, pwmResolution);
    ledcAttachPin(motorD2, pwmChannelD2);

    stop();
    return true;
}

void MotorController::setMotorSpeed(int pin, int channel, int speed) {
    int pwmValue = map(speed, 0, 255, 0, 255);
    ledcWrite(channel, pwmValue);
}

void MotorController::moveForward(int speed) {
    ledcWrite(pwmChannelA1, speed);
    ledcWrite(pwmChannelA2, 0);
    ledcWrite(pwmChannelB1, speed);
    ledcWrite(pwmChannelB2, 0);
    ledcWrite(pwmChannelC1, speed);
    ledcWrite(pwmChannelC2, 0);
    ledcWrite(pwmChannelD1, speed);
    ledcWrite(pwmChannelD2, 0);
    isMoving = true;
}

void MotorController::moveBackward(int speed) {
    ledcWrite(pwmChannelA1, 0);
    ledcWrite(pwmChannelA2, speed);
    ledcWrite(pwmChannelB1, 0);
    ledcWrite(pwmChannelB2, speed);
    ledcWrite(pwmChannelC1, 0);
    ledcWrite(pwmChannelC2, speed);
    ledcWrite(pwmChannelD1, 0);
    ledcWrite(pwmChannelD2, speed);
    isMoving = true;
}

void MotorController::moveLeft(int speed) {
    ledcWrite(pwmChannelA1, 0);
    ledcWrite(pwmChannelA2, speed);
    ledcWrite(pwmChannelB1, speed);
    ledcWrite(pwmChannelB2, 0);
    ledcWrite(pwmChannelC1, speed);
    ledcWrite(pwmChannelC2, 0);
    ledcWrite(pwmChannelD1, 0);
    ledcWrite(pwmChannelD2, speed);
    isMoving = true;
}

void MotorController::moveRight(int speed) {
    ledcWrite(pwmChannelA1, speed);
    ledcWrite(pwmChannelA2, 0);
    ledcWrite(pwmChannelB1, 0);
    ledcWrite(pwmChannelB2, speed);
    ledcWrite(pwmChannelC1, 0);
    ledcWrite(pwmChannelC2, speed);
    ledcWrite(pwmChannelD1, speed);
    ledcWrite(pwmChannelD2, 0);
    isMoving = true;
}

void MotorController::moveDirection(MoveDirection direction) {
    switch (direction) {
        case MOVE_FWD:
            moveForward(currentSpeed);
            break;
        case MOVE_BACK:
            moveBackward(currentSpeed);
            break;
        case MOVE_LEFT:
            moveLeft(currentSpeed);
            break;
        case MOVE_RIGHT:
            moveRight(currentSpeed);
            break;
    }
}

void MotorController::omniMove(OmniDirection omniDir, int speed) {
    currentSpeed = speed;

    switch (omniDir) {
        case OMNI_FORWARD:
            moveForward(speed);
            break;
        case OMNI_BACKWARD:
            moveBackward(speed);
            break;
        case OMNI_LEFT:
            moveLeft(speed);
            break;
        case OMNI_RIGHT:
            moveRight(speed);
            break;
        case OMNI_FORWARD_LEFT:
            ledcWrite(pwmChannelA1, 0);
            ledcWrite(pwmChannelA2, 0);
            ledcWrite(pwmChannelB1, speed);
            ledcWrite(pwmChannelB2, 0);
            ledcWrite(pwmChannelC1, speed);
            ledcWrite(pwmChannelC2, 0);
            ledcWrite(pwmChannelD1, 0);
            ledcWrite(pwmChannelD2, 0);
            isMoving = true;
            break;
        case OMNI_FORWARD_RIGHT:
            ledcWrite(pwmChannelA1, speed);
            ledcWrite(pwmChannelA2, 0);
            ledcWrite(pwmChannelB1, 0);
            ledcWrite(pwmChannelB2, 0);
            ledcWrite(pwmChannelC1, 0);
            ledcWrite(pwmChannelC2, 0);
            ledcWrite(pwmChannelD1, speed);
            ledcWrite(pwmChannelD2, 0);
            isMoving = true;
            break;
        case OMNI_BACKWARD_LEFT:
            ledcWrite(pwmChannelA1, 0);
            ledcWrite(pwmChannelA2, 0);
            ledcWrite(pwmChannelB1, 0);
            ledcWrite(pwmChannelB2, speed);
            ledcWrite(pwmChannelC1, 0);
            ledcWrite(pwmChannelC2, speed);
            ledcWrite(pwmChannelD1, 0);
            ledcWrite(pwmChannelD2, 0);
            isMoving = true;
            break;
        case OMNI_BACKWARD_RIGHT:
            ledcWrite(pwmChannelA1, 0);
            ledcWrite(pwmChannelA2, speed);
            ledcWrite(pwmChannelB1, 0);
            ledcWrite(pwmChannelB2, 0);
            ledcWrite(pwmChannelC1, 0);
            ledcWrite(pwmChannelC2, 0);
            ledcWrite(pwmChannelD1, 0);
            ledcWrite(pwmChannelD2, speed);
            isMoving = true;
            break;
        case OMNI_ROTATE_LEFT:
            ledcWrite(pwmChannelA1, 0);
            ledcWrite(pwmChannelA2, speed);
            ledcWrite(pwmChannelB1, speed);
            ledcWrite(pwmChannelB2, 0);
            ledcWrite(pwmChannelC1, 0);
            ledcWrite(pwmChannelC2, speed);
            ledcWrite(pwmChannelD1, speed);
            ledcWrite(pwmChannelD2, 0);
            isMoving = true;
            break;
        case OMNI_ROTATE_RIGHT:
            ledcWrite(pwmChannelA1, speed);
            ledcWrite(pwmChannelA2, 0);
            ledcWrite(pwmChannelB1, 0);
            ledcWrite(pwmChannelB2, speed);
            ledcWrite(pwmChannelC1, speed);
            ledcWrite(pwmChannelC2, 0);
            ledcWrite(pwmChannelD1, 0);
            ledcWrite(pwmChannelD2, speed);
            isMoving = true;
            break;
        case OMNI_STOP:
        default:
            stop();
            break;
    }
}

void MotorController::stop() {
    ledcWrite(pwmChannelA1, 0);
    ledcWrite(pwmChannelA2, 0);
    ledcWrite(pwmChannelB1, 0);
    ledcWrite(pwmChannelB2, 0);
    ledcWrite(pwmChannelC1, 0);
    ledcWrite(pwmChannelC2, 0);
    ledcWrite(pwmChannelD1, 0);
    ledcWrite(pwmChannelD2, 0);
    isMoving = false;
}

bool MotorController::isMotorMoving() {
    return isMoving;
}

void MotorController::setSpeed(int speed) {
    currentSpeed = constrain(speed, 0, 255);
}

void MotorController::setMotorA(int speed) {
    if (speed >= 0) {
        ledcWrite(pwmChannelA1, speed);
        ledcWrite(pwmChannelA2, 0);
    } else {
        ledcWrite(pwmChannelA1, 0);
        ledcWrite(pwmChannelA2, -speed);
    }
}

void MotorController::setMotorB(int speed) {
    if (speed >= 0) {
        ledcWrite(pwmChannelB1, speed);
        ledcWrite(pwmChannelB2, 0);
    } else {
        ledcWrite(pwmChannelB1, 0);
        ledcWrite(pwmChannelB2, -speed);
    }
}

void MotorController::setMotorC(int speed) {
    if (speed >= 0) {
        ledcWrite(pwmChannelC1, speed);
        ledcWrite(pwmChannelC2, 0);
    } else {
        ledcWrite(pwmChannelC1, 0);
        ledcWrite(pwmChannelC2, -speed);
    }
}

void MotorController::setMotorD(int speed) {
    if (speed >= 0) {
        ledcWrite(pwmChannelD1, speed);
        ledcWrite(pwmChannelD2, 0);
    } else {
        ledcWrite(pwmChannelD1, 0);
        ledcWrite(pwmChannelD2, -speed);
    }
}
