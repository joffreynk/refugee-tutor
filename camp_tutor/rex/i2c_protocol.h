// Camp Tutor - REX I2C Protocol Definitions
// Transport-agnostic command and response definitions

#ifndef I2C_PROTOCOL_H
#define I2C_PROTOCOL_H

#include <Arduino.h>

// I2C Address
#define REX_I2C_ADDRESS 0x42

// Command Buffer Size
#define CMD_BUFFER_SIZE 32

// Command Types
enum CommandType {
    CMD_LOOK,
    CMD_DIST,
    CMD_MOVE,
    CMD_OMNI,
    CMD_STOP,
    CMD_RESET,
    CMD_STATUS,
    CMD_HOME,
    CMD_CALIBRATE,
    CMD_PING,
    CMD_BUZZER,
    CMD_UNKNOWN
};

// Look Directions
enum LookDirection {
    LOOK_LEFT,
    LOOK_CENTER,
    LOOK_RIGHT,
    LOOK_HOME
};

// Move Directions
enum MoveDirection {
    MOVE_FWD,
    MOVE_BACK,
    MOVE_LEFT,
    MOVE_RIGHT
};

// Omni-Directional Movements (for 4-wheel omni bot)
enum OmniDirection {
    OMNI_FORWARD,
    OMNI_BACKWARD,
    OMNI_LEFT,
    OMNI_RIGHT,
    OMNI_FORWARD_LEFT,
    OMNI_FORWARD_RIGHT,
    OMNI_BACKWARD_LEFT,
    OMNI_BACKWARD_RIGHT,
    OMNI_ROTATE_LEFT,
    OMNI_ROTATE_RIGHT,
    OMNI_STOP
};

// REX States
enum RexState {
    STATE_IDLE,
    STATE_READY,
    STATE_LOOKING,
    STATE_MEASURING,
    STATE_MOVING,
    STATE_STOP,
    STATE_ERROR
};

// Command Structure
struct Command {
    CommandType type;
    LookDirection lookDir;
    MoveDirection moveDir;
    OmniDirection omniDir;
    bool isValid;
};

// Response Messages
const char* const RESP_OK = "OK";
const char* const RESP_ERROR_PREFIX = "ERROR:";
const char* const RESP_DIST_PREFIX = "DIST:";
const char* const RESP_STATUS_PREFIX = "STATUS:";
const char* const RESP_BLOCKED = "BLOCKED";
const char* const RESP_READY = "READY";
const char* const RESP_RESET = "RESET";

// Error Codes
enum ErrorCode {
    ERR_NONE = 0,
    ERR_INVALID_COMMAND,
    ERR_INVALID_DIRECTION,
    ERR_SERVO_ERROR,
    ERR_ULTRASONIC_ERROR,
    ERR_MOTOR_ERROR,
    ERR_TIMEOUT,
    ERR_SAFETY_STOP
};

// Command Parser Functions
Command parseCommand(const char* cmdString);
const char* getErrorMessage(ErrorCode code);

// Response Builder Functions
void buildResponse(char* buffer, const char* response);
void buildDistanceResponse(char* buffer, int distance);
void buildStatusResponse(char* buffer, RexState state);
void buildErrorResponse(char* buffer, ErrorCode code);

#endif // I2C_PROTOCOL_H
