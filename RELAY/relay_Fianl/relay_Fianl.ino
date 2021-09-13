#include <SoftwareSerial.h>
 
#define HC06RX A0 //HC-06의 TX Pin - Arduino Uno의 RX
#define HC06TX A1 //HC-06의 RX Pin - Arduino Uno의 TX
 
SoftwareSerial HC06(HC06RX,HC06TX);
int relay = 5;
int relay1 = 6;
int relay2 = 7;
int relay3 = 8;
int relay4 = 9;
int relay5 = 10;
char a = HIGH;
char b = LOW;

 
void setup(){
 
    pinMode(relay,OUTPUT);
   pinMode(relay1,OUTPUT);
    pinMode(relay2,OUTPUT);
     pinMode(relay3,OUTPUT);
      pinMode(relay4,OUTPUT);
       pinMode(relay5,OUTPUT);
 
    Serial.begin(9600);
    HC06.begin(9600);
    
 
   // Serial.println("HC06 Setting...");
    delay(500);
    
    HC06.print("AT");
  //  Serial.println("Arduino -> HC06 : AT");
    hc06ResponseCheck();
 
    HC06.print("AT+PIN0000");
   // Serial.println("Arduino -> HC06 : AT+PIN0000");
    hc06ResponseCheck();
 
    HC06.print("AT+NAMEmyHC06");
  //  Serial.println("Arduino -> HC06 : AT+NAMEmyHC06");
    hc06ResponseCheck();
 
    HC06.print("AT+BAUD4");
  //  Serial.println("Arduino -> HC06 : AT+BAUD4");
    hc06ResponseCheck();
   
 
}
 
void loop(){
    char temp;
    if(HC06.available()){
        temp = HC06.read();
  
        if(temp == '1'){
            digitalWrite(relay,a);
        digitalWrite(relay1,a);
        digitalWrite(relay2,a);
        digitalWrite(relay3,a);
        digitalWrite(relay4,a);
        digitalWrite(relay5,a);
        }
        else if(temp == '0'){
            digitalWrite(relay,b);
      digitalWrite(relay1,b);
      digitalWrite(relay2,b);
      digitalWrite(relay3,b);
      digitalWrite(relay4,b);
      digitalWrite(relay5,b);
       }
    }
}
 
void hc06ResponseCheck(){
    boolean flag = false;
    delay(500);
    if(HC06.available()){
        flag = true;
    }
    if(flag){
    //    Serial.print("HC06 -> Arduino : ");
        while(HC06.available()){
            Serial.write(HC06.read()); 
        }
     //   Serial.println("");
    }
    else{
      //  Serial.print("HC06 -> Arduino : ");
      //  Serial.println("No Response!");
    }
}
