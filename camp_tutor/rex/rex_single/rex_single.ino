// Camp Tutor - REX Controller (Single File for Arduino IDE)
// ESP32-based REX robot controller with I2C + Serial (USB) interface

#include <Wire.h>
#include <Arduino.h>

// ============ CONSTANTS ============
#define REX_I2C_ADDRESS 0x42
#define CMD_BUFFER_SIZE 32

// Pin Definitions
#define SERVO1_PIN       2
#define SERVO2_PIN        26
#define ULTRASONIC_TRIG   17
#define ULTRASONIC_ECHO   16
#define MOTOR_A1          15
#define MOTOR_A2          23
#define MOTOR_B1          32
#define MOTOR_B2          33
#define MOTOR_C1          5
#define MOTOR_C2          4
#define MOTOR_D1          27
#define MOTOR_D2          14
#define BUZZER_PIN        25
#define EMERGENCY_STOP_PIN 34

#define DEFAULT_MOTOR_SPEED 150

// ============ ENUMS ============
enum RexState { STATE_IDLE, STATE_READY, STATE_LOOKING, STATE_MEASURING, STATE_MOVING, STATE_STOP, STATE_ERROR };
enum ErrorCode { ERR_NONE, ERR_INVALID_COMMAND, ERR_INVALID_DIRECTION, ERR_SERVO_ERROR, ERR_ULTRASONIC_ERROR, ERR_MOTOR_ERROR, ERR_TIMEOUT, ERR_SAFETY_STOP };

// ============ GLOBAL VARIABLES ============
bool systemReady = false;
RexState currentState = STATE_IDLE;
ErrorCode lastError = ERR_NONE;

bool lookPending = false;
bool movePending = false;

// Command buffers
char cmdBuffer[CMD_BUFFER_SIZE];
char responseBuffer[CMD_BUFFER_SIZE];
char serialCmdBuffer[CMD_BUFFER_SIZE];
int serialCmdIndex = 0;

// ============ ULTRASONIC ============
class Ultrasonic {
  public:
    int trigPin, echoPin;
    Ultrasonic(int t, int e) { trigPin = t; echoPin = e; }
    bool initialize() {
      pinMode(trigPin, OUTPUT);
      pinMode(echoPin, INPUT);
      return true;
    }
    int readDistanceCm() {
      digitalWrite(trigPin, LOW);
      delayMicroseconds(2);
      digitalWrite(trigPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(trigPin, LOW);
      long duration = pulseIn(echoPin, HIGH, 30000);
      return (int)(duration * 0.034 / 2);
    }
};

// ============ SERVO ============
#include <ESP32Servo.h>
Servo servo1, servo2;

// ============ MOTOR ============
class Motor {
  public:
    int a1, a2, b1, b2;
    int speed = DEFAULT_MOTOR_SPEED;
    void init(int a_1, int a_2, int b_1, int b_2) {
      a1 = a_1; a2 = a_2; b1 = b_1; b2 = b_2;
      pinMode(a1, OUTPUT); pinMode(a2, OUTPUT);
      pinMode(b1, OUTPUT); pinMode(b2, OUTPUT);
      digitalWrite(a1, LOW); digitalWrite(a2, LOW);
      digitalWrite(b1, LOW); digitalWrite(b2, LOW);
    }
    void forward() {
      digitalWrite(a1, HIGH); digitalWrite(a2, LOW);
      digitalWrite(b1, HIGH); digitalWrite(b2, LOW);
    }
    void backward() {
      digitalWrite(a1, LOW); digitalWrite(a2, HIGH);
      digitalWrite(b1, LOW); digitalWrite(b2, HIGH);
    }
    void left() {
      digitalWrite(a1, LOW); digitalWrite(a2, HIGH);
      digitalWrite(b1, HIGH); digitalWrite(b2, LOW);
    }
    void right() {
      digitalWrite(a1, HIGH); digitalWrite(a2, LOW);
      digitalWrite(b1, LOW); digitalWrite(b2, HIGH);
    }
    void stop() {
      digitalWrite(a1, LOW); digitalWrite(a2, LOW);
      digitalWrite(b1, LOW); digitalWrite(b2, LOW);
    }
};

// ============ COMMAND PARSER ============
void buildResponse(const char* resp) {
  strncpy(responseBuffer, resp, CMD_BUFFER_SIZE - 1);
  responseBuffer[CMD_BUFFER_SIZE - 1] = '\0';
}

void buildStatusResponse(RexState state) {
  const char* s = "IDLE";
  if (state == STATE_READY) s = "READY";
  else if (state == STATE_MOVING) s = "MOVING";
  else if (state == STATE_STOP) s = "STOP";
  snprintf(responseBuffer, CMD_BUFFER_SIZE, "STATUS:%s", s);
}

void processCommand() {
  if (cmdBuffer[0] == '\0') return;
  
  // STATUS?
  if (strncmp(cmdBuffer, "STATUS?", 7) == 0) {
    buildStatusResponse(currentState);
  }
  // DISTANCE?
  else if (strncmp(cmdBuffer, "DISTANCE?", 9) == 0) {
    // Not implemented in this simple version
    snprintf(responseBuffer, CMD_BUFFER_SIZE, "DIST:0");
  }
  // MOVE:FWD or MOVE:FORWARD
  else if (strncmp(cmdBuffer, "MOVE:", 5) == 0) {
    char* dir = cmdBuffer + 5;
    if (strcmp(dir, "FWD") == 0 || strcmp(dir, "FORWARD") == 0) {
      currentState = STATE_MOVING;
      buildResponse("OK");
    } else if (strcmp(dir, "BACK") == 0 || strcmp(dir, "BACKWARD") == 0) {
      currentState = STATE_MOVING;
      buildResponse("OK");
    } else if (strcmp(dir, "LEFT") == 0) {
      currentState = STATE_MOVING;
      buildResponse("OK");
    } else if (strcmp(dir, "RIGHT") == 0) {
      currentState = STATE_MOVING;
      buildResponse("OK");
    } else {
      buildResponse("ERROR:INVALID_DIRECTION");
    }
    currentState = STATE_IDLE;
  }
  // LOOK:LEFT, LOOK:RIGHT, LOOK:CENTER
  else if (strncmp(cmdBuffer, "LOOK:", 5) == 0) {
    buildResponse("OK");
  }
  // STOP
  else if (strcmp(cmdBuffer, "STOP") == 0) {
    currentState = STATE_IDLE;
    buildResponse("OK");
  }
  // RESET
  else if (strcmp(cmdBuffer, "RESET") == 0) {
    currentState = STATE_READY;
    buildResponse("OK");
  }
  // HOME
  else if (strcmp(cmdBuffer, "HOME") == 0) {
    buildResponse("OK");
  }
  // PING
  else if (strcmp(cmdBuffer, "PING") == 0) {
    buildResponse("READY");
  }
  else {
    buildResponse("ERROR:INVALID_COMMAND");
  }
}

// ============ GLOBALS ============
Ultrasonic* ultrasonic;
Motor motors;

// ============ SETUP ============
void setup() {
  Serial.begin(115200);
  Serial.println("REX starting...");
  
  // I2C
  Wire.begin(21, 22);
  Wire.onRequest([]() { Wire.write((uint8_t*)responseBuffer, strlen(responseBuffer)); });
  Wire.onReceive([]() {
    int i = 0;
    while (Wire.available() && i < CMD_BUFFER_SIZE - 1) cmdBuffer[i++] = Wire.read();
    cmdBuffer[i] = '\0';
    processCommand();
  });
  
  // Init motors (using only 2 motors for simplicity)
  motors.init(MOTOR_A1, MOTOR_A2, MOTOR_B1, MOTOR_B2);
  
  // Init ultrasonic
  ultrasonic = new Ultrasonic(ULTRASONIC_TRIG, ULTRASONIC_ECHO);
  ultrasonic->initialize();
  
  // Buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Emergency stop
  pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
  
  currentState = STATE_READY;
  Serial.println("REX ready");
}

// ============ LOOP ============
void loop() {
  // Check emergency stop
  if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
    motors.stop();
    currentState = STATE_STOP;
    Serial.println("EMERGENCY STOP!");
  }
  
  // Process Serial commands
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (serialCmdIndex > 0) {
        serialCmdBuffer[serialCmdIndex] = '\0';
        strncpy(cmdBuffer, serialCmdBuffer, CMD_BUFFER_SIZE - 1);
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