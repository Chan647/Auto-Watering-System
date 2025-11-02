# 🌿 Auto Watering System Project
> Arduino + PyQt5 기반 환경 모니터링 & 자동 제어 시스템 
> 식물에게 자동으로 물을 주는 프로그램

---

## 📘 프로젝트 개요
 **센서 기반 자동 제어**와 **GUI 시각화**를 결합하여  자동 급수 시스템을 구현한 프로젝트 
토양, 수분, 온습도 등의 데이터를 실시간으로 측정하고  
자동 급수, 날씨 예측, 데이터 로깅을 수행

---

## 🧩  프로젝트

| 기술 이름  | 주요 기능 | 핵심 기술 |
|:------------|:------------|:------------|
| 🌱 **Auto Watering System** | 토양 수분이 일정 이하일 때 **자동 급수**, LCD에 **온습도 표시** | Arduino, DHT11, Soil Sensor, L9110, Water Pump |
| ☁️ **Weather Station** | **ESP-01 Wi-Fi**로 **OpenWeather API** 연결, **내일 날씨 정보** 획득 | Arduino + ESP-01, API 통신 |
| 📊 **Data Logger** | **시리얼 데이터 실시간 수집**, PyQt 그래프 시각화 | Python, PyQt5, Serial |
| 🌾 **Real-time monitoring** | LCD에 **온도, 습도, 수위, 토양 수분** 표시 | Arduino, LCD I2C 16x2, DHT11, Soil & Water Sensor |

---

## ⚙️ 사용 기술 및 부품
### 🧠 소프트웨어
- **Arduino C++**
- **Python (PyQt5, Serial)**
- **OpenWeatherMap API**

### 🔌 하드웨어
- Arduino Uno  
- ESP-01 (ESP8266)  
- DHT11 (온습도 센서)  
- Soil Moisture Sensor v2.0  
- Water Level Sensor  
- L9110 Motor Driver  
- Water Pump  
- LCD I2C 16x2  

---

## 🖼️ 시스템 구성 예시

| PyQt GUI | 회로도 |
|-----------|----------|
| ![gui](GUI.png) | ![circuit](circuit_diagram.png) |


---

## 📂 디렉토리 구조

```
📁 Auto_Watering_System/
 ┃ ┗ AutoWater.ino
 ┣ 📂 Data_Logger/
 ┃ ┗ main.py
 ┣ 📂 SmartFarm_Monitor/
 ┃ ┗ SmartFarmMonitor.ino
 ┣ 📂 images/
 ┃ ┣ gui.png
 ┃ ┗ circuit.png
 ┗ README.md
```

---


## 📊 주요 기능 흐름도

```mermaid
flowchart TD
    A  내일 날씨 정보 획득
    B [센서 데이터 수집] --> B{토양 수분 상태 확인}
    C -- 낮음 --> C[펌프 작동]
    D -- 충분함 --> D[대기 상태 유지]
    E --> E[LCD 상태 표시]
    F --> F[PyQt GUI 표시]
```

---

## 💡 개선 아이디어

- 여러 개의 화분에 독립적으로 급수
- 원격 제어(앱에서 직접 급수 시작/정지 가능)
- 데이터 저장 및 분석 시스템 구축
- 태양광 전원 시스템 적용
- 영양제 자동 투입(물과 함께 액체 비료를 일정량 투입)
- AI 카메라 / 추가적인 센서 연동 > 해충 탐지 및 관리 기능

---



