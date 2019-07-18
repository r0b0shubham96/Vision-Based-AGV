int dir_motor1 = 4;  //IN1  for direction // right motor
int dir_motor2 = 7;  //IN2                // left motor
int speed_motor1 = 5;   //AN1 for speed
int speed_motor2 = 6;


//high gives you forward movement(towards plate/arduino).

void setup()
{
  Serial.begin(9600);
  pinMode(dir_motor1, OUTPUT);  //left motor
  pinMode(dir_motor2, OUTPUT);  //right motor
  pinMode(speed_motor1, OUTPUT);
  pinMode(speed_motor2, OUTPUT);
  delay(200);
}

void loop()
{
if (Serial.available() > 0)
  {
    char a = Serial.read();
    if (a == 'T')
    {
      forward();
    }
    else if (a == 'R')
    {
      slight_right();
    }
    else if (a == 'L')
    {
      slight_left();
    }
    else if (a == 'X') // right 90
    {
      right90();
    }
    else if (a == 'Y') // left 90
    {
     left90();
    }
    else if (a == 'S')
    {
      halt();
    }
    else
    { halt();
    }
  }
}

