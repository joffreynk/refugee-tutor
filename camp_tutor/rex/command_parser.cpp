// I2C Protocol Implementation - Command Parser

#include "i2c_protocol.h"
#include <string.h>
#include <stdio.h>

Command parseCommand(const char* cmdString) {
    Command cmd;
    cmd.isValid = false;
    cmd.type = CMD_UNKNOWN;
    cmd.lookDir = LOOK_CENTER;
    cmd.moveDir = MOVE_FWD;
    cmd.omniDir = OMNI_STOP;

    if (cmdString == NULL || strlen(cmdString) == 0) {
        return cmd;
    }

    char cmdCopy[CMD_BUFFER_SIZE];
    strncpy(cmdCopy, cmdString, CMD_BUFFER_SIZE - 1);
    cmdCopy[CMD_BUFFER_SIZE - 1] = '\0';

    char* colon = strchr(cmdCopy, ':');
    char* cmdPart;
    char* paramPart = NULL;

    if (colon) {
        *colon = '\0';
        cmdPart = cmdCopy;
        paramPart = colon + 1;
    } else {
        cmdPart = cmdCopy;
    }

    // LOOK command - Control servo head position
    if (strcmp(cmdPart, "LOOK") == 0) {
        cmd.type = CMD_LOOK;
        if (paramPart) {
            if (strcmp(paramPart, "LEFT") == 0) {
                cmd.lookDir = LOOK_LEFT;
            } else if (strcmp(paramPart, "RIGHT") == 0) {
                cmd.lookDir = LOOK_RIGHT;
            } else if (strcmp(paramPart, "CENTER") == 0) {
                cmd.lookDir = LOOK_CENTER;
            } else if (strcmp(paramPart, "HOME") == 0) {
                cmd.lookDir = LOOK_HOME;
            } else {
                cmd.lookDir = LOOK_CENTER;
            }
        }
        cmd.isValid = true;
    }
    // DIST? - Get distance from ultrasonic sensor
    else if (strcmp(cmdPart, "DIST?") == 0) {
        cmd.type = CMD_DIST;
        cmd.isValid = true;
    }
    // MOVE command - Basic movement (for differential drive)
    else if (strcmp(cmdPart, "MOVE") == 0) {
        cmd.type = CMD_MOVE;
        if (paramPart) {
            if (strcmp(paramPart, "FWD") == 0 || strcmp(paramPart, "FORWARD") == 0) {
                cmd.moveDir = MOVE_FWD;
            } else if (strcmp(paramPart, "BACK") == 0 || strcmp(paramPart, "BACKWARD") == 0) {
                cmd.moveDir = MOVE_BACK;
            } else if (strcmp(paramPart, "LEFT") == 0) {
                cmd.moveDir = MOVE_LEFT;
            } else if (strcmp(paramPart, "RIGHT") == 0) {
                cmd.moveDir = MOVE_RIGHT;
            }
        }
        cmd.isValid = true;
    }
    // OMNI command - Omni-directional movement (for 4-wheel omni bot)
    else if (strcmp(cmdPart, "OMNI") == 0) {
        cmd.type = CMD_OMNI;
        if (paramPart) {
            if (strcmp(paramPart, "FWD") == 0 || strcmp(paramPart, "FORWARD") == 0) {
                cmd.omniDir = OMNI_FORWARD;
            } else if (strcmp(paramPart, "BACK") == 0 || strcmp(paramPart, "BACKWARD") == 0) {
                cmd.omniDir = OMNI_BACKWARD;
            } else if (strcmp(paramPart, "LEFT") == 0) {
                cmd.omniDir = OMNI_LEFT;
            } else if (strcmp(paramPart, "RIGHT") == 0) {
                cmd.omniDir = OMNI_RIGHT;
            } else if (strcmp(paramPart, "FL") == 0 || strcmp(paramPart, "FORWARD_LEFT") == 0) {
                cmd.omniDir = OMNI_FORWARD_LEFT;
            } else if (strcmp(paramPart, "FR") == 0 || strcmp(paramPart, "FORWARD_RIGHT") == 0) {
                cmd.omniDir = OMNI_FORWARD_RIGHT;
            } else if (strcmp(paramPart, "BL") == 0 || strcmp(paramPart, "BACK_LEFT") == 0) {
                cmd.omniDir = OMNI_BACKWARD_LEFT;
            } else if (strcmp(paramPart, "BR") == 0 || strcmp(paramPart, "BACK_RIGHT") == 0) {
                cmd.omniDir = OMNI_BACKWARD_RIGHT;
            } else if (strcmp(paramPart, "RL") == 0 || strcmp(paramPart, "ROTATE_LEFT") == 0) {
                cmd.omniDir = OMNI_ROTATE_LEFT;
            } else if (strcmp(paramPart, "RR") == 0 || strcmp(paramPart, "ROTATE_RIGHT") == 0) {
                cmd.omniDir = OMNI_ROTATE_RIGHT;
            } else if (strcmp(paramPart, "STOP") == 0) {
                cmd.omniDir = OMNI_STOP;
            }
        }
        cmd.isValid = true;
    }
    // STOP - Emergency stop
    else if (strcmp(cmdPart, "STOP") == 0) {
        cmd.type = CMD_STOP;
        cmd.isValid = true;
    }
    // RESET - Reset system after emergency stop
    else if (strcmp(cmdPart, "RESET") == 0) {
        cmd.type = CMD_RESET;
        cmd.isValid = true;
    }
    // STATUS? - Get current state
    else if (strcmp(cmdPart, "STATUS?") == 0) {
        cmd.type = CMD_STATUS;
        cmd.isValid = true;
    }
    // HOME - Return to home position
    else if (strcmp(cmdPart, "HOME") == 0) {
        cmd.type = CMD_HOME;
        cmd.isValid = true;
    }
    // CALIBRATE - Run calibration routine
    else if (strcmp(cmdPart, "CALIBRATE") == 0) {
        cmd.type = CMD_CALIBRATE;
        cmd.isValid = true;
    }
    // PING - Check if REX is responding
    else if (strcmp(cmdPart, "PING") == 0) {
        cmd.type = CMD_PING;
        cmd.isValid = true;
    }
    // BUZZER - Control buzzer
    else if (strcmp(cmdPart, "BUZZER") == 0) {
        cmd.type = CMD_BUZZER;
        if (paramPart) {
            if (strcmp(paramPart, "SHORT") == 0 || strcmp(paramPart, "1") == 0) {
                cmd.lookDir = LOOK_LEFT;
            } else if (strcmp(paramPart, "LONG") == 0 || strcmp(paramPart, "3") == 0) {
                cmd.lookDir = LOOK_RIGHT;
            } else {
                cmd.lookDir = LOOK_CENTER;
            }
        }
        cmd.isValid = true;
    }

    return cmd;
}

const char* getErrorMessage(ErrorCode code) {
    switch (code) {
        case ERR_NONE: return "NONE";
        case ERR_INVALID_COMMAND: return "INVALID_COMMAND";
        case ERR_INVALID_DIRECTION: return "INVALID_DIRECTION";
        case ERR_SERVO_ERROR: return "SERVO_ERROR";
        case ERR_ULTRASONIC_ERROR: return "ULTRASONIC_ERROR";
        case ERR_MOTOR_ERROR: return "MOTOR_ERROR";
        case ERR_TIMEOUT: return "TIMEOUT";
        case ERR_SAFETY_STOP: return "SAFETY_STOP";
        default: return "UNKNOWN";
    }
}

void buildResponse(char* buffer, const char* response) {
    strncpy(buffer, response, CMD_BUFFER_SIZE - 1);
    buffer[CMD_BUFFER_SIZE - 1] = '\0';
}

void buildDistanceResponse(char* buffer, int distance) {
    snprintf(buffer, CMD_BUFFER_SIZE, "DIST:%d", distance);
}

void buildStatusResponse(char* buffer, RexState state) {
    const char* stateStr;
    switch (state) {
        case STATE_IDLE: stateStr = "IDLE"; break;
        case STATE_READY: stateStr = "READY"; break;
        case STATE_LOOKING: stateStr = "LOOKING"; break;
        case STATE_MEASURING: stateStr = "MEASURING"; break;
        case STATE_MOVING: stateStr = "MOVING"; break;
        case STATE_STOP: stateStr = "STOP"; break;
        case STATE_ERROR: stateStr = "ERROR"; break;
        default: stateStr = "UNKNOWN"; break;
    }
    snprintf(buffer, CMD_BUFFER_SIZE, "STATUS:%s", stateStr);
}

void buildErrorResponse(char* buffer, ErrorCode code) {
    snprintf(buffer, CMD_BUFFER_SIZE, "ERROR:%s", getErrorMessage(code));
}
