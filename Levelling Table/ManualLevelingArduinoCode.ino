#include <AccelStepper.h>
#define motorInterfaceType 1
AccelStepper steppers[2];

String command = "x";
float motorSpeed = 1000;
int directions[] = {0, 0};

void setup() {
  // Create the stepper objects and set their properties
  steppers[0] = AccelStepper(motorInterfaceType, 2, 5); // left motor
  steppers[1] = AccelStepper(motorInterfaceType, 3, 6); // right motor
  
  for (int i = 0; i < 2; i++) {
    steppers[i].setMaxSpeed(motorSpeed);
    steppers[i].setCurrentPosition(0);
  }
  
  // Initialize the serial connection to the computer
  Serial.begin(115200);
  Serial.setTimeout(1);
}

void loop() {
  if (Serial.available()) {
    command = Serial.readString();
  }
  
  if (command == "x") { directions[0] = 0; directions[1] = 0; }
  if (command == "w") { directions[0] =-1; directions[1] =-1; }
  if (command == "s") { directions[0] = 1; directions[1] = 1; }
  if (command == "a") { directions[0] = 1; directions[1] =-1; }
  if (command == "d") { directions[0] =-1; directions[1] = 1; }
  
  for (int i = 0; i < 2; i++) {
    steppers[i].setSpeed(motorSpeed*directions[i]);
    steppers[i].runSpeed();
  }
}
