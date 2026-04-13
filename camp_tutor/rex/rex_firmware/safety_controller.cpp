// Safety Controller Implementation

#include "safety_controller.h"

SafetyController::SafetyController() {
    this->minSafeDistance = 20;
    this->maxRetryAttempts = 3;
    this->currentRetries = 0;
    this->emergencyStopActive = false;
    this->obstacleDetected = false;
    this->moveTimeout = 5000;
}

void SafetyController::initialize() {
    emergencyStopActive = false;
    obstacleDetected = false;
    currentRetries = 0;
}

bool SafetyController::checkPathClear(int distanceCm) {
    if (distanceCm < 0) {
        obstacleDetected = true;
        return false;
    }
    
    if (distanceCm < minSafeDistance) {
        obstacleDetected = true;
        currentRetries++;
        return false;
    }
    
    obstacleDetected = false;
    return true;
}

bool SafetyController::canMove() {
    if (emergencyStopActive) {
        return false;
    }
    
    if (currentRetries >= maxRetryAttempts) {
        return false;
    }
    
    return true;
}

void SafetyController::triggerEmergencyStop() {
    emergencyStopActive = true;
    obstacleDetected = true;
}

void SafetyController::clearEmergencyStop() {
    emergencyStopActive = false;
    currentRetries = 0;
}

void SafetyController::recordMoveAttempt() {
    lastMoveTime = millis();
}

bool SafetyController::shouldRetry() {
    return currentRetries < maxRetryAttempts;
}

void SafetyController::setMinSafeDistance(int cm) {
    minSafeDistance = cm;
}

void SafetyController::setMoveTimeout(unsigned long ms) {
    moveTimeout = ms;
}

bool SafetyController::isEmergencyStop() {
    return emergencyStopActive;
}

bool SafetyController::isObstacleDetected() {
    return obstacleDetected;
}

RexState SafetyController::getSafetyState() {
    if (emergencyStopActive) {
        return STATE_STOP;
    }
    if (obstacleDetected) {
        return STATE_ERROR;
    }
    return STATE_IDLE;
}
