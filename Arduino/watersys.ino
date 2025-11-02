#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>
#include "DHT.h"

#define DEBUG false
#define DHTTYPE DHT11 
#define DHTPIN 2  
#define AA  3
#define AB  4
#define RLED 5
#define GLED 6
#define BLED 7
#define BA  8
#define BB  9
#define BUZZER 10
#define watersensorpin A3
#define soilsensorpin A0

LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHTPIN, DHTTYPE);

int mode = 0;
int waterlevel = 0;
int soilmoisture = 0;
int screenID = 0;
int tones = 4186;
int pre_mode = -1;
float lastT = NAN, lastH = NAN;

bool ledcon = LOW;
bool buzcon = LOW;
bool manual_mode = false;
bool manual_pump = false;
bool pumpOn = false;
bool tpumpOn = false;

unsigned long last_manual = 0;
unsigned long lastdisplay = 0;
unsigned long lastbuzz = 0;
unsigned long lastled = 0;
unsigned long lastsoil = 0;
unsigned long lastsend = 0;
unsigned long lastDhTread = 0;
unsigned long lastsmsg = 0;
unsigned long lastwmsg = 0;

unsigned long boot_t0 = 0;

SoftwareSerial esp8266(12,13);

String ssid = "202호 강의실 2.4";  
String password = "4719222202";     
String apiKey = "273cf286f730b3ade1525fd0361770cb"; 
String city = "Seoul,KR";
String ans = " ";


void setup() {
  pinMode(AA, OUTPUT);
  pinMode(AB, OUTPUT);
  pinMode(BA, OUTPUT);
  pinMode(BB, OUTPUT);
  pinMode(RLED, OUTPUT);
  pinMode(BLED, OUTPUT);
  pinMode(GLED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  lcd.init();        
  lcd.backlight();  

  Serial.begin(9600);
  esp8266.begin(9600);

  Serial.print("Please Wait...");
  sendData("AT+RST\r\n", 2000, DEBUG);
  sendData("AT+CWMODE=1\r\n", 1000, DEBUG);
  sendData("AT+CWJAP=\"" + ssid + "\",\"" + password + "\"\r\n", 6000, DEBUG);

  Serial.print("Please Wait 5 more second...");
  delay(5000);
  Serial.print("WiFi Connected! ");

  
  sendData("AT+CIFSR\r\n",1000,DEBUG);


  String cm = "AT+CIPSTART=\"TCP\",\"api.openweathermap.org\",80\r\n";
  sendData(cm, 3000, DEBUG);


  String getStr = "GET /data/2.5/weather?q=" + city + "&appid=" + apiKey + "&units=metric HTTP/1.1\r\n"
                  "Host: api.openweathermap.org\r\n"
                  "Connection: close\r\n\r\n";

  
  cm = "AT+CIPSEND=" + String(getStr.length()) + "\r\n";
  sendData(cm, 20000, DEBUG);


  String response = sendData(getStr, 20000, DEBUG);
  String weather;
  int start = response.indexOf("main");
  int end = response.indexOf("\",");
  weather = response.substring(start + 7, end);
  Serial.println(response);
  Serial.print("Tomorrow Weather: ");
  Serial.println(weather);
  ans = weather;
}

void on_waterpump(){
  digitalWrite(AA, HIGH);
  digitalWrite(AB, LOW);
  pumpOn = false;
}

void off_waterpump(){
  digitalWrite(AA, LOW);
  digitalWrite(AB, LOW);
  pumpOn = false;
}

void on_tankpump(){
  digitalWrite(BA, HIGH);
  digitalWrite(BB, LOW);
  tpumpOn = false;
}

void off_tankpump(){
  digitalWrite(BA,LOW);
  digitalWrite(BB,LOW);
  tpumpOn = false;
}

void readDHT_safely() {
  bool wasPumpOn = pumpOn; 
  if (wasPumpOn) off_waterpump();
  delay(30);       

  bool wastPumpOn = tpumpOn;
  if (wastPumpOn) off_tankpump();
  delay(30);    

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (wasPumpOn) on_waterpump(); 
  if (wastPumpOn) on_tankpump();

  if (!isnan(h) && !isnan(t)) {
    lastH = h; lastT = t;       
  }

}


void show_sen(const char* s1, const char* s2){
  lcd.setCursor(0,0); lcd.print(s1);
  lcd.setCursor(0,1); lcd.print(s2);
}

void show_val(const char* s1, float val){
  lcd.setCursor(0,0); lcd.print(s1);
  lcd.setCursor(0,1); lcd.print(val);
}

void reset_sen(){
  lcd.setCursor(0,0); lcd.print("                 ");
  lcd.setCursor(0,1); lcd.print("                 ");
}

void off_led(){
  digitalWrite(RLED, LOW);
  digitalWrite(GLED, LOW);
  digitalWrite(BLED, LOW);
}

String sendData(String command, const int timeout, boolean debug) {
  String response = "";
  esp8266.print(command);
  long int time = millis();
  while ((millis() - time) < timeout) {
    while (esp8266.available()) {
      char c = esp8266.read();
      response += c;
    }
  }
  if (debug) {
    Serial.print(response);
  }
  Serial.println();
  return response;
}


void loop() { 
  unsigned long now = millis();
  String cmd = "";

  waterlevel = analogRead(watersensorpin);
  soilmoisture= analogRead(soilsensorpin);

  float mm = (40 * waterlevel / 1023) + 10;
  int per = (1023 - soilmoisture) / 1023.0 * 100.0;
 
  float wat_lv = waterlevel;
  float soil_moi = soilmoisture; 

  if (now - lastDhTread >= 2000) {
  lastDhTread = now;
  readDHT_safely();
  }


  if (cmd == "AUTO") {
    manual_mode = false;
    off_waterpump();
    off_tankpump();
    Serial.println("MODE_AUTO");
  }
  else if (cmd == "MANUAL") {
    manual_mode = true;
    manual_pump = false;
    Serial.println("MODE_MANUAL");
  }

  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "W0") { 
        manual_mode = true;
        manual_pump = false;
        last_manual = millis();
        off_waterpump();
  }
    

    else if (cmd == "W1") { 
        manual_mode = true;
        manual_pump = true;
        last_manual = millis();
        on_waterpump();
    }

    else if (cmd == "W2") { 
        manual_mode = true;
        manual_pump = true;
        last_manual = millis();
        on_tankpump();
  }

  else if (cmd == "W3") { 
        manual_mode = true;
        manual_pump = true;
        last_manual = millis();
        off_tankpump();
  }
}

  if (manual_mode) {
    if (millis() - last_manual > 30000) {
        manual_mode = false;
        off_waterpump();
        off_tankpump();
        Serial.println("AUTO_MODE_RESUME");
    }
    else {
        return; 
    }
  }


  if (mode != pre_mode) {
    pre_mode = mode;
    ledcon = LOW;
    lastled = now;
    lastsoil = now;
  }

  if (now - lastsend >= 30000){
    if(ans.length() > 2){
      lastsend = now;
      if(isnan(lastT) || isnan(lastH)) return;

      Serial.print("DATA :");
      Serial.print(lastT); Serial.print(',');
      Serial.print(lastH); Serial.print(',');
      Serial.print(mm); Serial.print(',');
      Serial.print(per); Serial.print('\n');
    }
  }
  

  if (mode != 2 && per <= 50) {
    mode = 2;  
  }
  else if (mode == 2 && per > 60) {
    if (mm <= 20){
      mode = 1;
    }
    else{
      mode = 0;
    }  
  }
  else {
    if (mode != 1 && mm <= 20) {
      mode = 1;
    }
    else if (mode == 1 && mm > 25) {
      mode = 0;
    }
  }
 
   switch (mode) {
    case 0: 
      off_led();
      off_waterpump();
      off_tankpump();
      noTone(BUZZER);

      if (now - lastdisplay >= 2000) {
        lastdisplay = now;
        screenID = (screenID+1) % 4;
        reset_sen();
      }

        switch (screenID) {
          
          case 0:
            show_val("Temperature",lastT);
            lcd.write(byte(223));
            lcd.print("C");
            break;

          case 1:
            show_val("Humidity",lastH);
            lcd.print("%");
            break;

          case 2:
            show_val("Water Level",mm);
            break;

          case 3:
            show_val("Soil Moisture",per);
            lcd.print("%");
            break;

        }
      break;

    case 1:
       on_tankpump();
       off_waterpump();
       noTone(BUZZER);
       show_sen("Water Shortage!","Fill the Bottle!");
      
       
       if (now - lastsend >= 30000){
        lastsend = now;
        if(isnan(lastT) || isnan(lastH)) return;
        
        Serial.print(lastT); Serial.print(',');
        Serial.print(lastH); Serial.print(',');
        Serial.print(mm); Serial.print(',');
        Serial.print(per); Serial.print('\n');
        }
      
       if (now - lastled >= 500) {
        lastled = now;
        ledcon = !ledcon;
        digitalWrite(RLED, LOW);
        digitalWrite(GLED, ledcon);
        digitalWrite(BLED, LOW);
        break;
       }
      break;

    case 2:
        on_waterpump();
        show_sen("Soil is Dry!","Water the Plants!");

      if (now - lastsend >= 30000){
        lastsend = now;
        if(isnan(lastT) || isnan(lastH)) return;
        
        Serial.print(lastT); Serial.print(',');
        Serial.print(lastH); Serial.print(',');
        Serial.print(mm); Serial.print(',');
        Serial.print(per); Serial.print('\n');
        }

      if (now - lastsoil >= 500) {
        lastsoil= now;
        ledcon = !ledcon;
        digitalWrite(RLED, ledcon);
        digitalWrite(GLED, LOW);
        digitalWrite(BLED, LOW);
      }

      if (millis() - lastbuzz >= 1000){
        tone(BUZZER, tones, 200);
        lastbuzz = millis();
        break;
      }
      break;
  }
}

