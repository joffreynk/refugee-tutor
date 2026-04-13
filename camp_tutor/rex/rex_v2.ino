// Camp Tutor - REX Controller v2 (Single File for Arduino IDE)
// ESP32-based REX robot controller with I2C + Serial (USB) interface

#include <Wire.h>
#include <Arduino.h>

// ============ CONSTANTS ============
#define REX_I2C_ADDRESS 0x42
#define CMD_BUFFER_SIZE 32

// Pin Definitions - 2x Servo (MG95R)
#define SERVO1_PIN       2   // Pan
#define SERVO2_PIN       26  // Tilt

// Pin Definitions - Ultrasonic
#define ULTRASONIC_TRIG   17
#define ULTRASONIC_ECHO  16

// Pin Definitions - 4x DC Motors
#define MOTOR_A1         15  // Front Left
#define MOTOR_A2         23
#define MOTOR_B1         32  // Front Right
#define MOTOR_B2         33
#define MOTOR_C1         5   // Rear Left
#define MOTOR_C2         4
#define MOTOR_D1         27  // Rear Right
#define MOTOR_D2         14

// Pin Definitions - Other
#define BUZZER_PIN       25
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

// ============ MOTOR (4x DC Motors) ============
class MotorController {
  public:
    int m1a, m1b, m2a, m2b, m3a, m3b, m4a, m4b;
    int speed = DEFAULT_MOTOR_SPEED;
    
    void init(int a1, int a2, int b1, int b2, int c1, int c2, int d1, int d2) {
      m1a = a1; m1b = a2; m2a = b1; m2b = b2;
      m3a = c1; m3b = c2; m4a = d1; m4b = d2;
      
      pinMode(m1a, OUTPUT); pinMode(m1b, OUTPUT);
      pinMode(m2a, OUTPUT); pinMode(m2b, OUTPUT);
      pinMode(m3a, OUTPUT); pinMode(m3b, OUTPUT);
      pinMode(m4a, OUTPUT); pinMode(m4b, OUTPUT);
      
      stop();
    }
    
    // Omni-drive: All motors forward (holonomic)
    void forward() {
      digitalWrite(m1a, HIGH); digitalWrite(m1b, LOW);
      digitalWrite(m2a, HIGH); digitalWrite(m2b, LOW);
      digitalWrite(m3a, HIGH); digitalWrite(m3b, LOW);
      digitalWrite(m4a, HIGH); digitalWrite(m4b, LOW);
    }
    
    // All motors backward
    void backward() {
      digitalWrite(m1a, LOW); digitalWrite(m1b, HIGH);
      digitalWrite(m2a, LOW); digitalWrite(m2b, HIGH);
      digitalWrite(m3a, LOW); digitalWrite(m3b, HIGH);
      digitalWrite(m4a, LOW); digitalWrite(m4b, HIGH);
    }
    
    // Strafe left
    void strafeLeft() {
      digitalWrite(m1a, LOW); digitalWrite(m1b, HIGH);
      digitalWrite(m2a, HIGH); digitalWrite(m2b, LOW);
      digitalWrite(m3a, HIGH); digitalWrite(m3b, LOW);
      digitalWrite(m4a, LOW); digitalWrite(m4b, HIGH);
    }
    
    // Strafe right
    void strafeRight() {
      digitalWrite(m1a, HIGH); digitalWrite(m1b, LOW);
      digitalWrite(m2a, LOW); digitalWrite(m2b, HIGH);
      digitalWrite(m3a, LOW); digitalWrite(m3b, HIGH);
      digitalWrite(m4a, HIGH); digitalWrite(m4b, LOW);
    }
    
    // Rotate left (front right + rear left)
    void rotateLeft() {
      digitalWrite(m1a, LOW); digitalWrite(m1b, HIGH);
      digitalWrite(m2a, HIGH); digitalWrite(m2b, LOW);
      digitalWrite(m3a, LOW); digitalWrite(m3b, HIGH);
      digitalWrite(m4a, HIGH); digitalWrite(m4b, LOW);
    }
    
    // Rotate right
    void rotateRight() {
      digitalWrite(m1a, HIGH); digitalWrite(m1b, LOW);
      digitalWrite(m2a, LOW); digitalWrite(m2b, HIGH);
      digitalWrite(m3a, HIGH); digitalWrite(m3b, LOW);
      digitalWrite(m4a, LOW); digitalWrite(m4b, HIGH);
    }
    
    // Stop all
    void stop() {
      digitalWrite(m1a, LOW); digitalWrite(m1b, LOW);
      digitalWrite(m2a, LOW); digitalWrite(m2b, LOW);
      digitalWrite(m3a, LOW); digitalWrite(m3b, LOW);
      digitalWrite(m4a, LOW); digitalWrite(m4b, LOW);
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
    int distance = ultrasonic->readDistanceCm();
    snprintf(responseBuffer, CMD_BUFFER_SIZE, "DIST:%d", distance);
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
    char* dir = cmdBuffer + 5;
    if (strcmp(dir, "LEFT") == 0) {
      servo1.write(180);  // Pan left
      servo2.write(90);
    } else if (strcmp(dir, "RIGHT") == 0) {
      servo1.write(0);    // Pan right
      servo2.write(90);
    } else if (strcmp(dir, "UP") == 0) {
      servo1.write(90);
      servo2.write(0);    // Tilt up
    } else if (strcmp(dir, "DOWN") == 0) {
      servo1.write(90);
      servo2.write(180);  // Tilt down
    } else {
      servo1.write(90);   // Center
      servo2.write(90);
    }
    buildResponse("OK");
  }
  // SHAKE - Head shake animation (yes)
  else if (strncmp(cmdBuffer, "SHAKE", 5) == 0) {
    // Nod animation: left -> center -> right -> center -> left -> center
    servo1.write(45);
    delay(150);
    servo1.write(135);
    delay(150);
    servo1.write(45);
    delay(150);
    servo1.write(135);
    delay(150);
    servo1.write(90);  // Center
    buildResponse("SHAKE:OK");
  }
  // NOD - Head nod animation
  else if (strncmp(cmdBuffer, "NOD", 3) == 0) {
    servo2.write(45);
    delay(200);
    servo2.write(135);
    delay(200);
    servo2.write(45);
    delay(200);
    servo2.write(135);
    delay(200);
    servo2.write(90);
    buildResponse("NOD:OK");
  }
  // WIGGLE - Full head wiggle
  else if (strncmp(cmdBuffer, "WIGGLE", 6) == 0) {
    for(int i=0; i<3; i++) {
      servo1.write(30);
      servo2.write(30);
      delay(100);
      servo1.write(150);
      servo2.write(150);
      delay(100);
    }
    servo1.write(90);
    servo2.write(90);
    buildResponse("WIGGLE:OK");
  }
  // SERVO:PAN:angle or SERVO:TILT:angle
  else if (strncmp(cmdBuffer, "SERVO:", 6) == 0) {
    char* servo = cmdBuffer + 6;
    char* angleStr = strchr(servo, ':');
    if (angleStr) {
      int angle = atoi(angleStr + 1);
      if (strncmp(servo, "PAN", 3) == 0) {
        servo1.write(constrain(angle, 0, 180));
      } else if (strncmp(servo, "TILT", 4) == 0) {
        servo2.write(constrain(angle, 0, 180));
      }
    }
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
  
  // Init 4x DC motors
  motors.init(MOTOR_A1, MOTOR_A2, MOTOR_B1, MOTOR_B2, MOTOR_C1, MOTOR_C2, MOTOR_D1, MOTOR_D2);
  
  // Init 2x Servo (MG95R)
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo1.write(90);  // Center
  servo2.write(90);  // Center
  
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