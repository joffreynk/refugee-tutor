// Safety Controller - Emergency stop and safety enforcement

#ifndef SAFETY_CONTROLLER_H
#define SAFETY_CONTROLLER_H

#include <Arduino.h>
#include "i2c_protocol.h"

class SafetyController {
private:
    int minSafeDistance;
    int maxRetryAttempts;
    int currentRetries;
    
    bool emergencyStopActive;
    bool obstacleDetected;
    
    unsigned long moveTimeout;
    unsigned long lastMoveTime;
    
public:
    SafetyController();
    
    void initialize();
    
    bool checkPathClear(int distanceCm);
    
    bool canMove();
    
    void triggerEmergencyStop();
    void clearEmergencyStop();
    
    void recordMoveAttempt();
    bool shouldRetry();
    
    void setMinSafeDistance(int cm);
    void setMoveTimeout(unsigned long ms);
    
    bool isEmergencyStop();
    bool isObstacleDetected();
    
    RexState getSafetyState();
};

#endif
