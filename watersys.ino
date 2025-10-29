#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>
#include "DHT.h"

#define DEBUG true
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

unsigned long last_manual = 0;
unsigned long lastdisplay = 0;
unsigned long lastbuzz = 0;
unsigned long lastled = 0;
unsigned long lastsoil = 0;
unsigned long lastsend = 0;
unsigned long lastDhtRead = 0;

const int low_water = 100;  
const int nor_water = 150;  
const int low_soil  = 600;  
const int nor_soil  = 580;

SoftwareSerial esp(12,13);

String ssid = "JJanni";
String pass = "1q2w3e4r";
String apiKey = "803d087ba957880e946afca96308e974";   
String city = "Seoul,KR";

String sendData(String cmd, int wait) {
  String res = "";
  esp.print(cmd);
  long t = millis();
  while (millis() - t < wait) {
    while (esp.available()) res += (char)esp.read();
  }
  Serial.print(res);
  return res;
}


void setup() {
  pinMode(AA, OUTPUT);
  pinMode(AB, OUTPUT);
  pinMode(RLED, OUTPUT);
  pinMode(BLED, OUTPUT);
  pinMode(GLED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  lcd.init();        
  lcd.backlight();  

  Serial.begin(9600);
  dht.begin();
  esp.begin(9600);
  delay(2000);

  Serial.println("\n[ESP8266 초기화]");
  sendData("AT\r\n", 1000);
  sendData("AT+RST\r\n", 2000);
  sendData("ATE0\r\n", 1000);
  sendData("AT+CWMODE=1\r\n", 1000);
  delay(1000);
  sendData("AT+CWJAP=\"" + ssid + "\",\"" + pass + "\"\r\n", 15000);
  delay(3000);
  sendData("AT+CIPRECVMODE=0\r\n", 1000);
  sendData("AT+CIFSR\r\n", 1000);

  delay(2000);
  getWeather();
}
void on_waterpump(){
  digitalWrite(AA, HIGH);
  digitalWrite(AB, LOW);
  pumpOn = true;
}

void off_waterpump(){
  digitalWrite(AA, LOW);
  digitalWrite(AB, LOW);
  pumpOn = false;
}

void readDHT_safely() {
  bool wasPumpOn = pumpOn; 
  if (wasPumpOn) off_waterpump();
  delay(30);           

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (wasPumpOn) on_waterpump(); 

  if (!isnan(h) && !isnan(t)) {
    lastH = h; lastT = t;       
  }

}

void on_tankpump(){
  digitalWrite(BA, HIGH);
  digitalWrite(BB, LOW);
  delay(3000);
}

void off_tankpump(){
  digitalWrite(BA,LOW);
  digitalWrite(BB,LOW);
  delay(3000);
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


void loop() { 
  unsigned long now = millis();
  String cmd = "";

  waterlevel = analogRead(watersensorpin);
  soilmoisture= analogRead(soilsensorpin);

  float mm = (40 * waterlevel / 1023) + 10;
  int per = (1023 - soilmoisture) / 1023.0 * 100.0;
 
  float wat_lv = waterlevel;
  float soil_moi = soilmoisture; 

  if (now - lastDhtRead >= 2000) {
  lastDhtRead = now;
  readDHT_safely();
}


  if (cmd == "AUTO") {
    manual_mode = false;
    off_waterpump();
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

    if (cmd == "W1") { 
        manual_mode = true;
        manual_pump = true;
        last_manual = millis();
        on_waterpump();
        Serial.println("WATERPUMP_ON");
    }
    else if (cmd == "W0") { 
        manual_mode = true;
        manual_pump = false;
        last_manual = millis();
        off_waterpump();
        Serial.println("WATERPUMP_OFF");
    }
  }

  if (manual_mode) {
    if (millis() - last_manual > 30000) {
        manual_mode = false;
        off_waterpump();
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

  if (now - lastsend >= 1000){
    lastsend = now;
    if(isnan(lastT) || isnan(lastH)) return; 
    
    Serial.print(lastT); Serial.print(',');
    Serial.print(lastH); Serial.print(',');
    Serial.print(mm); Serial.print(',');
    Serial.print(per); Serial.print('\n');
  }
  

  if (mode != 2 && per <= 40) {
    mode = 2;  
  }
  else if (mode == 2 && per >= 45) {
    if (waterlevel <= low_water){
      mode = 1;
    }
    else{
      mode = 0;
    }  
  }
  else {
    if (mode != 1 && waterlevel <= low_water) {
      mode = 1;
    }
    else if (mode == 1 && waterlevel >= nor_water) {
      mode = 0;
    }
  }
 
   switch (mode) {
    case 0: 
      off_waterpump();
      off_tankpump();
      off_led();
      noTone(BUZZER);

      if (now - lastdisplay >= 2000) {
        lastdisplay = now;
        screenID = (screenID+1) % 4;
        reset_sen();
      }

        switch (screenID) {
          case 0:
            show_val("Soil Moisture",per);
            lcd.print("%");
            break;

          case 1:
            show_val("Temperature",lastT);
            lcd.write(byte(223));
            lcd.print("C");
            break;

          case 2:
            show_val("Humidity",lastH);
            lcd.print("%");
            break;

          case 3:
            show_val("Water Level",waterlevel);
            break;
        }
      break;

    case 1:
       off_waterpump();
       on_tankpump();
       noTone(BUZZER);
       off_led();

       if (now - lastled >= 500) {
        lastled = now;
        ledcon = !ledcon;
        digitalWrite(RLED, ledcon);
        digitalWrite(GLED, ledcon);
        digitalWrite(BLED, LOW);
        reset_sen();
        show_sen("Water Shortage!","Fill the Bottle!");
        break;
       }
      break;

    case 2:
      on_waterpump();
      if (now - lastsoil >= 500) {
        
        lastsoil= now;
        ledcon = !ledcon;
        digitalWrite(RLED, HIGH);
        digitalWrite(GLED, LOW);
        digitalWrite(BLED, LOW);
        reset_sen();
        show_sen("Soil is Dry!","Water the Plants!");
        break;
      }
      break;
  }

}

void getWeather() {
  String host = "api.openweathermap.org";
  String url = "/data/2.5/forecast?q=" + city + "&appid=" + apiKey + "&units=metric&lang=kr";

  sendData("AT+CIPSTART=\"TCP\",\"" + host + "\",80\r\n", 5000);

  String req = "GET " + url + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n";
  sendData("AT+CIPSEND=" + String(req.length()) + "\r\n", 2000);
  esp.print(req);

  delay(10000);  

  String res = "";
  while (esp.available()) res += (char)esp.read();
  sendData("AT+CIPCLOSE\r\n", 1000);

  String clean = "";
  for (int i = 0; i < res.length(); i++) {
    char c = res[i];
    if (c >= 32 && c <= 126) clean += c;
  }

  int idx = clean.indexOf("\"main\":\"");
  if (idx > 0) {
    int s = idx + 8;
    int e = clean.indexOf('"', s);
    String desc = clean.substring(s, e);
    Serial.println("\n☀ 내일 날씨: " + desc); 
    if (desc == "Rain"){
    off_waterpump();
    }
    mode = 0; 
  }
  else {
    mode = 0;  } 
}