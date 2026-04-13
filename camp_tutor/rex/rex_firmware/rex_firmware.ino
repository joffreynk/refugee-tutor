// Camp Tutor - REX Controller Main Firmware
// ESP32-based REX robot controller with I2C interface
// Based on REX-RDT OmniBot/SonicBot/ArmBot specifications
//
// Pin Configuration:
// - Servo1 (Right/Left): GPIO 2
// - Servo2 (Up/Down): GPIO 26
// - HC-SR04 Ultrasonic: Trig=17, Echo=16
// - 4 Omni Motors:
//   MotorA: Forward=15, Backward=23
//   MotorB: Forward=32, Backward=33
//   MotorC: Forward=5, Backward=4
//   MotorD: Forward=27, Backward=14
// - Buzzer: GPIO 25

#include <Wire.h>
#include <Arduino.h>
#include "i2c_protocol.h"
#include "servo_controller.h"
#include "ultrasonic.h"
#include "motor_controller.h"
#include "safety_controller.h"

// REX-RDT Pin Definitions
#define SERVO1_PIN          2   // Right/Left
#define SERVO2_PIN          26  // Up/Down

#define ULTRASONIC_TRIG     17
#define ULTRASONIC_ECHO     16

#define MOTOR_A1            15  // Forward
#define MOTOR_A2            23  // Backward
#define MOTOR_B1            32  // Forward
#define MOTOR_B2            33  // Backward
#define MOTOR_C1            5   // Forward
#define MOTOR_C2            4   // Backward
#define MOTOR_D1            27  // Forward
#define MOTOR_D2            14  // Backward

#define BUZZER_PIN          25
#define EMERGENCY_STOP_PIN   34  // Emergency stop button (GPIO 34 - input only)

// Nokia 5110 LCD Pins (SPI interface)
#define LCD_RST   4   // Reset
#define LCD_DC    0   // Data/Command
#define LCD_MOSI  23  // SPI MOSI
#define LCD_CLK   18  // SPI Clock
#define LCD_CS    5   // Chip Select

// Default motor speed
#define DEFAULT_MOTOR_SPEED 150

// Ready state flag - true when system is fully initialized
bool systemReady = false;

// State Variables
RexState currentState = STATE_IDLE;
ErrorCode lastError = ERR_NONE;

// Async State
bool lookPending = false;
bool movePending = false;
LookDirection pendingLookDir;
MoveDirection pendingMoveDir;
OmniDirection pendingOmniDir;

// Controllers
ServoController* servos;
UltrasonicSensor* ultrasonic;
MotorController* motors;
SafetyController* safety;

// I2C Command Buffer
char cmdBuffer[CMD_BUFFER_SIZE];
char responseBuffer[CMD_BUFFER_SIZE];

// Serial Command Buffer (USB UART)
char serialCmdBuffer[CMD_BUFFER_SIZE];
int serialCmdIndex = 0;

// Task handles
TaskHandle_t lookTaskHandle = NULL;
TaskHandle_t moveTaskHandle = NULL;
TaskHandle_t measureTaskHandle = NULL;

// Buzzer functions
void buzzerOn(int durationMs = 100) {
    digitalWrite(BUZZER_PIN, HIGH);
    if (durationMs > 0) {
        delay(durationMs);
        digitalWrite(BUZZER_PIN, LOW);
    }
}

void buzzerOff() {
    digitalWrite(BUZZER_PIN, LOW);
}

void buzzerBeep(int count = 1, int onTime = 100, int offTime = 100) {
    for (int i = 0; i < count; i++) {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(onTime);
        digitalWrite(BUZZER_PIN, LOW);
        if (i < count - 1) {
            delay(offTime);
        }
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("Camp Tutor REX starting...");
    Serial.println("REX-RDT Configuration:");
    Serial.println("  Servo1 (Right/Left): GPIO 2");
    Serial.println("  Servo2 (Up/Down): GPIO 26");
    Serial.println("  HC-SR04: Trig=17, Echo=16");
    Serial.println("  Motors: A(15/23), B(32/33), C(5/4), D(27/14)");
    Serial.println("  Buzzer: GPIO 25");
    Serial.println("  Emergency Stop: GPIO 34");
    
    // Initialize buzzer
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    
    // Initialize emergency stop button (active LOW - pulled up internally)
    pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
    
    // Initialize I2C
    Wire.begin(21, 22);
    Wire.onRequest(onI2CRequest);
    Wire.onReceive(onI2CReceive);
    
    // Initialize controllers
    servos = new ServoController(SERVO1_PIN, SERVO2_PIN);
    ultrasonic = new UltrasonicSensor(ULTRASONIC_TRIG, ULTRASONIC_ECHO);
    motors = new MotorController();
    safety = new SafetyController();
    
    if (!servos->initialize()) {
        Serial.println("Servo init failed");
        currentState = STATE_ERROR;
        lastError = ERR_SERVO_ERROR;
    }
    
    if (!ultrasonic->initialize()) {
        Serial.println("Ultrasonic init failed");
        currentState = STATE_ERROR;
        lastError = ERR_ULTRASONIC_ERROR;
    }
    
    if (!motors->initialize(MOTOR_A1, MOTOR_A2, MOTOR_B1, MOTOR_B2, 
                            MOTOR_C1, MOTOR_C2, MOTOR_D1, MOTOR_D2)) {
        Serial.println("Motor init failed");
        currentState = STATE_ERROR;
        lastError = ERR_MOTOR_ERROR;
    }
    
    safety->initialize();
    safety->setMinSafeDistance(20);
    safety->setMoveTimeout(5000);
    
    // Ensure all systems are stopped at startup
    servos->goHome();
    motors->stop();
    safety->clearEmergencyStop();
    motors->setSpeed(DEFAULT_MOTOR_SPEED);
    currentState = STATE_IDLE;
    
    // Check emergency stop button state on startup
    if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        Serial.println("Emergency stop is ACTIVE at startup!");
        safety->triggerEmergencyStop();
        currentState = STATE_STOP;
    }
    
    // System is now ready - immediate response enabled
    systemReady = true;
    
    // Ready beep - quick double beep indicates system is online
    buzzerBeep(2, 50, 30);
    
    Serial.println("REX ready - waiting for commands");
}

void loop() {
    // Check emergency stop button - active LOW (pressed = LOW)
    bool emergencyPressed = (digitalRead(EMERGENCY_STOP_PIN) == LOW);
    
    // Handle emergency stop button press
    if (emergencyPressed && !safety->isEmergencyStop()) {
        safety->triggerEmergencyStop();
        motors->stop();
        currentState = STATE_STOP;
        buzzerBeep(3, 200, 100);
        Serial.println("EMERGENCY STOP pressed!");
    }
    
    // Handle emergency stop release - auto-resume when button released
    if (!emergencyPressed && safety->isEmergencyStop() && currentState == STATE_STOP) {
        safety->clearEmergencyStop();
        currentState = STATE_IDLE;
        buzzerBeep(2, 50, 30);
        Serial.println("Emergency stop released - system ready");
    }
    
    // Handle async operations in main loop
    if (lookPending) {
        currentState = STATE_LOOKING;
        servos->setLookDirection(pendingLookDir);
        delay(300);
        currentState = STATE_IDLE;
        buildResponse(responseBuffer, RESP_OK);
        lookPending = false;
    }
    
    if (movePending) {
        currentState = STATE_MOVING;
        
        // Check distance before moving
        int distance = ultrasonic->readDistanceCm();
        if (!safety->checkPathClear(distance)) {
            motors->stop();
            buzzerBeep(3, 100, 50);
            buildResponse(responseBuffer, RESP_BLOCKED);
            currentState = STATE_STOP;
            movePending = false;
            return;
        }
        
        motors->moveDirection(pendingMoveDir);
        safety->recordMoveAttempt();
        
        // Movement continues until stop or obstacle
        currentState = STATE_IDLE;
        buildResponse(responseBuffer, RESP_OK);
        movePending = false;
    }
    
    // Continuous check for emergency during operation
    if (safety->isEmergencyStop()) {
        motors->stop();
        currentState = STATE_STOP;
    }
    
    // Process Serial commands (USB UART)
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            if (serialCmdIndex > 0) {
                serialCmdBuffer[serialCmdIndex] = '\0';
                strncpy(cmdBuffer, serialCmdBuffer, CMD_BUFFER_SIZE - 1);
                cmdBuffer[CMD_BUFFER_SIZE - 1] = '\0';
                processCommand();
                Serial.println(responseBuffer);
                serialCmdIndex = 0;
            }
        } else if (serialCmdIndex < CMD_BUFFER_SIZE - 2) {
            serialCmdBuffer[serialCmdIndex++] = c;
        }
    }
    
    delay(10);
}

void onI2CReceive(int count) {
    int i = 0;
    while (Wire.available() && i < CMD_BUFFER_SIZE - 1) {
        cmdBuffer[i] = Wire.read();
        i++;
    }
    cmdBuffer[i] = '\0';
    
    processCommand();
}

void onI2CRequest() {
    Wire.write(responseBuffer);
}

void processCommand() {
    cmdBuffer[CMD_BUFFER_SIZE - 1] = '\0';
    
    Command cmd = parseCommand(cmdBuffer);
    
    if (!cmd.isValid) {
        buildErrorResponse(responseBuffer, ERR_INVALID_COMMAND);
        return;
    }
    
    switch (cmd.type) {
        case CMD_LOOK:
            handleLookAsync(cmd.lookDir);
            break;
            
        case CMD_DIST:
            handleDistanceAsync();
            break;
            
        case CMD_MOVE:
            handleMoveAsync(cmd.moveDir);
            break;
            
        case CMD_OMNI:
            handleOmniAsync(cmd.omniDir);
            break;
            
        case CMD_STOP:
            handleStop();
            break;
            
        case CMD_RESET:
            handleReset();
            break;
            
        case CMD_STATUS:
            handleStatus();
            break;
            
        case CMD_HOME:
            handleHome();
            break;
            
        case CMD_CALIBRATE:
            handleCalibrate();
            break;
            
        case CMD_PING:
            buildResponse(responseBuffer, "PONG");
            break;
            
        case CMD_BUZZER:
            handleBuzzer(cmd.lookDir);
            break;
            
        default:
            buildErrorResponse(responseBuffer, ERR_INVALID_COMMAND);
            break;
    }
}

void handleLookAsync(LookDirection direction) {
    if (safety->isEmergencyStop()) {
        buildResponse(responseBuffer, RESP_BLOCKED);
        return;
    }
    
    pendingLookDir = direction;
    lookPending = true;
    buildResponse(responseBuffer, RESP_OK);
}

void handleDistanceAsync() {
    int distance = ultrasonic->readDistanceCm();
    
    if (distance < 0) {
        buildErrorResponse(responseBuffer, ERR_ULTRASONIC_ERROR);
    } else {
        buildDistanceResponse(responseBuffer, distance);
    }
}

void handleMoveAsync(MoveDirection direction) {
    if (safety->isEmergencyStop()) {
        buildResponse(responseBuffer, RESP_BLOCKED);
        return;
    }
    
    int distance = ultrasonic->readDistanceCm();
    if (!safety->checkPathClear(distance)) {
        buildResponse(responseBuffer, RESP_BLOCKED);
        return;
    }
    
    if (!safety->canMove()) {
        buildErrorResponse(responseBuffer, ERR_SAFETY_STOP);
        return;
    }
    
    pendingMoveDir = direction;
    movePending = true;
    motors->moveDirection(direction);
    safety->recordMoveAttempt();
    
    buildResponse(responseBuffer, RESP_OK);
}

void handleOmniAsync(OmniDirection direction) {
    if (safety->isEmergencyStop()) {
        buildResponse(responseBuffer, RESP_BLOCKED);
        return;
    }
    
    int distance = ultrasonic->readDistanceCm();
    if (!safety->checkPathClear(distance)) {
        buildResponse(responseBuffer, RESP_BLOCKED);
        return;
    }
    
    pendingOmniDir = direction;
    motors->omniMove(direction, DEFAULT_MOTOR_SPEED);
    safety->recordMoveAttempt();
    
    buildResponse(responseBuffer, RESP_OK);
}

void handleStop() {
    motors->stop();
    servos->goHome();
    safety->triggerEmergencyStop();
    currentState = STATE_STOP;
    buzzerBeep(2, 150, 50);
    buildResponse(responseBuffer, RESP_OK);
}

void handleStatus() {
    RexState state = safety->isEmergencyStop() ? STATE_STOP : currentState;
    buildStatusResponse(responseBuffer, state);
}

void handleHome() {
    servos->goHome();
    motors->stop();
    safety->clearEmergencyStop();
    currentState = STATE_IDLE;
    buzzerBeep(1, 80, 0);
    buildResponse(responseBuffer, RESP_OK);
}

void handleReset() {
    // Full system reset - clears emergency stop and re-initializes
    motors->stop();
    servos->goHome();
    safety->clearEmergencyStop();
    currentState = STATE_IDLE;
    
    // Quick triple beep to confirm reset
    buzzerBeep(3, 50, 30);
    
    Serial.println("System reset complete");
    buildResponse(responseBuffer, RESP_RESET);
}

void handleCalibrate() {
    servos->goHome();
    delay(200);
    int homeDistance = ultrasonic->readDistanceCm();
    Serial.print("Home distance: ");
    Serial.println(homeDistance);
    
    // Test all motors briefly
    motors->omniMove(OMNI_FORWARD, 100);
    delay(200);
    motors->omniMove(OMNI_BACKWARD, 100);
    delay(200);
    motors->omniMove(OMNI_LEFT, 100);
    delay(200);
    motors->omniMove(OMNI_RIGHT, 100);
    delay(200);
    motors->stop();
    
    buzzerBeep(3, 100, 50);
    buildResponse(responseBuffer, RESP_OK);
}

void handleBuzzer(LookDirection direction) {
    // Use look direction to control buzzer duration
    int duration = 100;
    switch (direction) {
        case LOOK_LEFT: duration = 50; break;
        case LOOK_RIGHT: duration = 200; break;
        case LOOK_CENTER: duration = 100; break;
        case LOOK_HOME: duration = 150; break;
    }
    buzzerOn(duration);
    buildResponse(responseBuffer, RESP_OK);
}
