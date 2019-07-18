void forward()
{
  digitalWrite(dir_motor1, HIGH);
  digitalWrite(dir_motor2, HIGH);
  analogWrite(speed_motor1, 100);
  analogWrite(speed_motor2, 100);
}
void halt()
{
  digitalWrite(dir_motor1, HIGH);
  digitalWrite(dir_motor2, HIGH);
  analogWrite(speed_motor1, 0);
  analogWrite(speed_motor2, 0);
}

void slight_left() {
  digitalWrite(dir_motor1, HIGH);
  digitalWrite(dir_motor2, LOW);
  analogWrite(speed_motor1, 100);
  analogWrite(speed_motor2, 50);
}
void slight_right() {
  digitalWrite(dir_motor1, LOW);
  digitalWrite(dir_motor2, HIGH);
  analogWrite(speed_motor1, 50);
  analogWrite(speed_motor2, 100);
}
void left90()
{
  char b = Serial.read();
  digitalWrite(dir_motor1, HIGH);
  digitalWrite(dir_motor2, HIGH);
  analogWrite(speed_motor1, 100);
  analogWrite(speed_motor2, 50);
  //    delay(200);
  while (b != 'T')
  {
    b = Serial.read();
  }
  halt();
}


void right90()
{
  char b = Serial.read();
  digitalWrite(dir_motor1, HIGH);
  digitalWrite(dir_motor2, HIGH);
  analogWrite(speed_motor1, 50);
  analogWrite(speed_motor2, 100);
  //  delay(200);
  while (b != 'T')
  {
    b = Serial.read();
  }
  halt();
}

