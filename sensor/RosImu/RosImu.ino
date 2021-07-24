
#include <MPU6050_tockn.h>
#include <Wire.h>

MPU6050 mpu6050(Wire);

long timer = 0;

double weCalAngle = 0.0;
double givenCalAngle = 0.0;

double yawAngle = 0.0;
double integralYawAngle = 0.0;

double dt = 0.3;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu6050.begin();
  mpu6050.calcGyroOffsets(true);
  Serial.println();
}

void loop() {
  mpu6050.update();

  //if(millis() - timer > 200){
  
   // Serial.print("accX : ");Serial.print(mpu6050.getAccX());
   // Serial.print("\taccY : ");Serial.print(mpu6050.getAccY());
    //Serial.print("\taccZ : ");Serial.println(mpu6050.getAccZ());

  yawAngle = atan(sqrt(mpu6050.getGyroX()*mpu6050.getGyroX()+mpu6050.getGyroY()*mpu6050.getGyroY())/mpu6050.getGyroZ());
  integralYawAngle = integralYawAngle + yawAngle * dt;
  
   // Serial.print("gyroX : ");Serial.print(mpu6050.getGyroX());
   // Serial.print("\tgyroY : ");Serial.print(mpu6050.getGyroY());
   // Serial.print("\tgyroZ : ");Serial.println(mpu6050.getGyroZ());
  
  givenCalAngle = 0.98*(mpu6050.getAngleZ()+mpu6050.getGyroZ()*dt)+0.02*mpu6050.getAccZ();
  weCalAngle = 0.98*(yawAngle+mpu6050.getGyroZ()*dt)+0.02*mpu6050.getAccZ();
   
   // Serial.print("accAngleX : ");Serial.print(mpu6050.getAccAngleX());
    //Serial.print("\taccAngleY : ");Serial.println(mpu6050.getAccAngleY());
  
  //  Serial.print("gyroAngleX : ");Serial.print(mpu6050.getGyroAngleX());
  //  Serial.print("\tgyroAngleY : ");Serial.print(mpu6050.getGyroAngleY());
   // Serial.print("\tgyroAngleZ : ");Serial.println(mpu6050.getGyroAngleZ());
   
  //  Serial.print("angleX : ");Serial.print(mpu6050.getAngleX());
   // Serial.print("\tangleY : ");Serial.print(mpu6050.getAngleY());
   // Serial.print("\tangleZ : ");
//   Serial.print(yawAngle);
//   Serial.print("  ");
//   Serial.println(mpu6050.getAngleZ());
//   Serial.print("=======================================================\n");
 //  Serial.print("준걸로 계산한거 : "); 
     Serial.println(givenCalAngle);
    // Serial.println("=======================================================\n");
//   Serial.print("우리가 계산한 : "); Serial.println(weCalAngle);
//   Serial.println("=======================================================\n");
//   
//   Serial.print("적분한거  :  "); Serial.println(integralYawAngle);
//   Serial.println("=======================================================\n");
   // timer = millis();
   
   
   

   delay(10);
    
  

}
