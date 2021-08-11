#include <Servo.h>

Servo esc_r; //서보 라이브러리를 통해 쉽게 조작할 수 있다.
Servo esc_b;

const int st = 90;
int red = st; //모터로 들어가는 초기black , 최솟
int black = st;
int pr_red = st;
int pr_black = st;
const int hs = 10;




void setup() 
{
  Serial.begin(9600); 
  esc_r.attach(9, 1000, 2000); 
  esc_b.attach(10, 1000, 2000);
  

  Serial.setTimeout(50); 
  esc_r.write(0);
  esc_b.write(0);
}

void loop() {
 
   esc_r.write(red);
   esc_b.write(black);
   Serial.print(red);
   Serial.print(",");
   Serial.print(black);
   Serial.println('\t');
  
  while (Serial.available()) 
  {
    red = Serial.parseInt();
    Serial.read();
    black = Serial.parseInt();
  if(Serial.read() == '\n'){
    del(pr_red,pr_black,red,black,hs);

  if(0 <= red && red <90 ){ //역회전
   esc_r.write(90);
   esc_b.write(90);
   delay(300);
   esc_r.write(red);
   esc_b.write(black);
   Serial.print(red);
   Serial.print(",");
   Serial.print(black);
   Serial.println('\t');
   }
   if(0 <= black && black <90 ){ //역회전
   esc_r.write(90);
   esc_b.write(90);
   delay(300);
   esc_r.write(red);
   esc_b.write(black);
   Serial.print(red);
   Serial.print(",");
   Serial.print(black);
   Serial.println('\t');
   }
   
  else if(90 < red && red <= 180){  //정회전
   esc_r.write(red);
   esc_b.write(black);
   Serial.print(red);
   Serial.print(",");
   Serial.print(black);
   Serial.println('\t');
  }
  else if(90 <  black &&  black <= 180){  //정회전
   esc_r.write(red);
   esc_b.write(black);
   Serial.print(red);
   Serial.print(",");
   Serial.print(black);
   Serial.println('\t');
  }
  
  else if(red == 90){                     // 90(정지)
    esc_r.write(90);
    esc_b.write(90);
    Serial.print("정지");
    Serial.println('\t');  
  }
   else if(black == 90){                     // 90(정지)
    esc_r.write(90);
    esc_b.write(90);
    Serial.print("정지");
    Serial.println('\t');  
  }
  }
  pr_red = red;
  pr_black = black;
}
}

void del(int pr_red,int pr_black,int red,int black,int hs){
  int red_out = pr_red;
  int black_out = pr_black;
  while(red_out != red || black_out != black){
    if(red_out > red){
      red_out--;
    }else if(red_out < red){
      red_out++;
    }
    if(black_out>black){
      black_out--;
    }else if(black_out<black){
      black_out++;
    }
    esc_b.write(black_out);
    esc_r.write(red_out);
    delay(hs);
  }
}
