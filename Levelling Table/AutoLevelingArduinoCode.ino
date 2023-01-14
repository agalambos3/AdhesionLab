#include <AccelStepper.h>
#define motorInterfaceType 1
AccelStepper steppers[2];

void setup() {
  // Create the stepper objects and set their properties
  steppers[0] = AccelStepper(motorInterfaceType, 2, 5); // left motor
  steppers[1] = AccelStepper(motorInterfaceType, 3, 6); // right motor
  
  for (int i = 0; i < 2; i++) {
    steppers[i].setCurrentPosition(0);
    steppers[i].setMaxSpeed(1000);
    steppers[i].setAcceleration(2000);
  }
  
  // Initialize the serial connection to the computer
  Serial.begin(115200);
  Serial.setTimeout(20);
}

void loop() {
  while (!Serial.available()) {} // wait for message
  int x = Serial.parseInt();     // read message
  Serial.print('a');             // send first acknoledgement
  while (!Serial.available()) {} // wait for message
  int y = Serial.parseInt();     // read message
  
  steppers[0].moveTo(x);
  steppers[1].moveTo(y);
  while (steppers[0].isRunning() || steppers[1].isRunning()) {
    for (int i = 0; i < 2; i++) {
      steppers[i].run();
    }
  }
  Serial.print('b');             // send second acknoledgement
}
