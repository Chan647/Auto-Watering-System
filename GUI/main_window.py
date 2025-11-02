from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from date_data_window import date_data_window
from waiting_dialog import WaitingDialog

class MainWindow(QMainWindow):
    def __init__(self, db_instance):
        super().__init__()
        self.is_connect_with_device = False
        self.tomorrow_weather = None
        self.db = db_instance
        self.setWindowTitle('스마트팜 모니터링')

        statusBar = self.statusBar()

        btn_box = QHBoxLayout()

        self.mode_label = QLabel('    자동 모드    ')
        self.mode_label.setStyleSheet("color: white;"
                      "background-color: #000000 ;"
                      "border-color: #000000;")

        self.auto_btn = QPushButton('자동 모드')
        self.auto_btn.setFixedSize(150, 60)
        self.auto_btn.setStyleSheet("color: black;"
                      "background-color: #dee2e6;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #868e96;"
                      "border-radius: 10px")
        self.auto_btn.clicked.connect(self.auto_mode)

        self.manual_btn = QPushButton('수동 모드')
        self.manual_btn.setFixedSize(150, 60)
        self.manual_btn.setStyleSheet("color: black;"
                      "background-color: #dee2e6;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #868e96;"
                      "border-radius: 10px")
        self.manual_btn.clicked.connect(self.manual_mode)

        btn_box.addStretch(1)
        btn_box.addWidget(self.auto_btn)
        btn_box.addStretch(1)
        btn_box.addWidget(self.mode_label)
        btn_box.addStretch(1)
        btn_box.addWidget(self.manual_btn)
        btn_box.addStretch(1)

        date_label = QLabel()
        current_date = QDate.currentDate()
        date_string = current_date.toString(Qt.ISODate)
        date_label.setText(date_string)

        # 날씨 라벨 추가 (상태바에)
        self.weather_label = QLabel('날씨: 확인 중...')
        
        self.flag_label = QLabel()
        self.flag_label.setText("아두이노 wifi 연결중...")

        statusBar.addPermanentWidget(self.weather_label, 0)
        statusBar.addPermanentWidget(date_label, 0)
        statusBar.addPermanentWidget(self.flag_label, 0)

        central = QWidget()
        self.setCentralWidget(central)
        self.setWindowIcon(QIcon('icon-temperature.png'))
        self.resize(1000, 800)
        vbox = QVBoxLayout(central)

        now_data_box = QHBoxLayout()

        font = QFont()
        font.setPointSize(20)

        self.tem_label = QLabel('온도: -- °C') 
        self.tem_label.setFont(font)
        self.hum_label = QLabel('습도: -- %')
        self.hum_label.setFont(font)
        self.smo_label = QLabel('토양 습도: -- %')
        self.smo_label.setFont(font)
        self.wlev_label = QLabel('급수탱크 수위: -- mm')
        self.wlev_label.setFont(font)

        now_data_box.addWidget(self.tem_label)
        now_data_box.addWidget(self.hum_label)
        now_data_box.addWidget(self.wlev_label)
        now_data_box.addWidget(self.smo_label)

        self.buzzer = QLabel(' Buzzer')
        self.buzzer.setFixedSize(60, 60)
        self.buzzer.setStyleSheet("color: white;"
                      "background-color: #922727 ;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 30px")

        
        self.watering_btn = QPushButton('물 주기')
        self.watering_btn.setStyleSheet("color: white;"
                      "background-color: #1E88E5;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #03A9F4;"
                      "border-radius: 10px")
        self.watering_btn.setFixedSize(200, 60)
        self.watering_btn.setCheckable(True)
        self.watering_btn.setEnabled(False)
        self.watering_btn.toggled.connect(self.watering)

        self.fill_tank_btn = QPushButton('수조 탱크 채우기')
        self.fill_tank_btn.setStyleSheet("color: white;"
                      "background-color: #1E88E5;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #03A9F4;"
                      "border-radius: 10px")
        self.fill_tank_btn.setFixedSize(200, 60)
        self.fill_tank_btn.setCheckable(True)
        self.fill_tank_btn.setEnabled(False)
        self.fill_tank_btn.toggled.connect(self.fill_tank)

        btn_center_layout = QHBoxLayout()
        btn_center_layout.addStretch(1)
        btn_center_layout.addWidget(self.buzzer)
        btn_center_layout.addStretch(1)
        btn_center_layout.addWidget(self.watering_btn)
        btn_center_layout.addStretch(1)
        btn_center_layout.addWidget(self.fill_tank_btn)
        btn_center_layout.addStretch(1)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['온도', '습도', '급수탱크 수위', '토양 습도', '측정 시각'])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        self.calender = QCalendarWidget(self)
        self.calender.setGridVisible(True)
        self.calender.clicked[QDate].connect(self.open_date_data_window)

        vbox.addLayout(btn_box)
        vbox.addLayout(now_data_box)
        vbox.addWidget(self.table)
        vbox.addWidget(self.calender)
        vbox.addLayout(btn_center_layout)

        self.load_data()
        # 센서 데이터 읽기 타이머 (30초마다)
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.read_arduino_data)
        self.timer.start()

        # 초기 날씨 정보 가져오기
        self.update_weather()
        # 날씨 업데이트 타이머 (1시간마다)
        self.weather_timer = QTimer(self)
        self.weather_timer.setInterval(3600000)  # 1시간
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start()

        # 초기 날씨 정보 가져오기
        self.update_weather()

        self.load_data()
        self.is_connect_with_device = False
        self.waitdlg = None

        # 시리얼이 열려 있고 아직 연결 확인 전이라면 대기창 표시
        if self.db.ser and self.db.ser.is_open:
            def on_wifi_timeout():
                self.flag_label.setText("장치 연결 실패(타임아웃). 장치를 확인하세요.")
                QMessageBox.warning(self, "연결 실패", "아두이노 연결 신호를 받지 못했습니다.\n장치/전원을 확인해 주세요.")
            self.waitdlg = WaitingDialog("아두이노 wifi 연결 대기 중...", timeout_ms=30000, on_timeout=on_wifi_timeout, parent=self)
            self.waitdlg.start()
        else:
            self.flag_label.setText("장치 포트 미연결. USB/포트를 확인하세요.")

    def update_weather(self):
        """날씨 정보 업데이트"""
        weather = self.db.get_weather()
        if weather:
            self.weather_label.setText(f"날씨: {weather['description']} ({weather['temperature']:.1f}°C)")
            
            # 비가 오면 상태바에 알림 표시만 (아두이노에는 전송 안 함)
            if weather['is_raining']:
                self.weather_label.setText("☔ 비가 오고 있습니다")
            else:
                if self.is_connect_with_device:
                    self.weather_label.setText(f"☀ {weather['description']}")
        else:
            self.weather_label.setText('날씨: 정보 없음')

    def load_data(self):
        rows = self.db.fetch_data()

        if len(rows) == 0 :
            return

        self.table.setRowCount(len(rows))
        lastest_tem, lastest_hum, lastest_wlev, lastest_smo,_ = rows[0]

        if rows: 
            self.tem_label.setText(f'온도: {lastest_tem} °C')
            self.hum_label.setText(f'습도: {lastest_hum} %')
            self.smo_label.setText(f'토양 습도: {lastest_smo} %')
            self.wlev_label.setText(f'급수탱크 수위: {lastest_wlev} mm')
        else:
            self.tem_label.setText('온도: -- °C')
            self.hum_label.setText('습도: -- %')
            self.smo_label.setText('토양 습도: -- %')
            self.wlev_label.setText('급수탱크 수위: -- mm')

        if lastest_tem < 25:
            self.tem_label.setStyleSheet("background-color: #ADD8E6;")
        elif lastest_tem < 35:
            self.tem_label.setStyleSheet("background-color: #90EE90;")
        else:
            self.tem_label.setStyleSheet("background-color: #F08080;")

        if lastest_hum < 60:
            self.hum_label.setStyleSheet("background-color: #ADD8E6;")
        elif lastest_hum < 80:
            self.hum_label.setStyleSheet("background-color: #90EE90;")
        else:
            self.hum_label.setStyleSheet("background-color: #F08080;")

        if lastest_smo < 50:
            self.smo_label.setStyleSheet("background-color: #F08080;")
        else:
            self.smo_label.setStyleSheet("background-color: #90EE90;")

        if lastest_wlev <= 20:
            self.wlev_label.setStyleSheet("background-color: #F08080;")
        else:
            self.wlev_label.setStyleSheet("background-color: #90EE90;")

        if lastest_smo < 50:
            self.buzzer.setStyleSheet("color: white;"
                      "background-color: #ff0000 ;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 30px")
        else:
            self.buzzer.setStyleSheet("color: white;"
                      "background-color: #922727 ;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 30px")

        for r, (tem, hum, wlev, smo, created_time) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(tem) + ' °C'))
            self.table.setItem(r, 1, QTableWidgetItem(str(hum) + ' %'))
            self.table.setItem(r, 2, QTableWidgetItem(str(wlev) + ' mm'))
            self.table.setItem(r, 3, QTableWidgetItem(str(smo) + ' %'))
            self.table.setItem(r, 4, QTableWidgetItem(str(created_time)))

            if tem < 25:
                self.table.item(r, 0).setBackground(QColor('#E0FFFF'))
            elif tem < 35:
                self.table.item(r, 0).setBackground(QColor('#98FB98'))
            else:
                self.table.item(r, 0).setBackground(QColor('#FFC0CB'))

            if hum < 60:
                self.table.item(r, 1).setBackground(QColor('#E0FFFF'))
            elif hum < 80:
                self.table.item(r, 1).setBackground(QColor('#98FB98'))
            else:
                self.table.item(r, 1).setBackground(QColor('#FFC0CB'))

            if wlev <= 20:
                self.table.item(r, 2).setBackground(QColor('#FFC0CB'))
            else:
                self.table.item(r, 2).setBackground(QColor('#98FB98'))

            if smo < 50:
                self.table.item(r, 3).setBackground(QColor('#FFC0CB'))
            else:
                self.table.item(r, 3).setBackground(QColor('#98FB98'))

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def read_arduino_data(self):
        if self.db.ser and self.db.ser.is_open:
            try:
                line = self.db.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    return
                
                if line.startswith("TOMORROW WEATHER :"):
                    # 날씨 정보 (처음 한 번만)
                    weather = line.replace("TOMORROW WEATHER :", "").strip()
                    self.tomorrow_weather = weather
                    return
                elif line.startswith("DATA :"):
                    # 센서 데이터 (계속 받음)
                    data_str = line.replace("DATA :", "").strip()
                    parts = [p.strip() for p in data_str.split(',')]
                    if len(parts) != 4:
                        return

                    # 첫 정상 수신 시: 대기창 닫기
                    if not self.is_connect_with_device:
                        self.is_connect_with_device = True
                        # 날씨 정보가 있으면 표시
                        weather = self.db.get_weather()
                        if weather:
                            self.flag_label.setText("")
                        
                        if self.waitdlg and self.waitdlg.isVisible():
                            self.waitdlg.close_when_done()

                        QMessageBox.information(self, "연결 성공", f'아두이노 연결 완료!\n내일 날씨: {self.tomorrow_weather}')

                    # 문자열 -> 숫자
                    temperature = float(parts[0])
                    humidity = float(parts[1])
                    water_level = float(parts[2])
                    soil_moisture = float(parts[3])

                    # DB 저장 + 화면 갱신
                    self.db.save_sensor_data(temperature, humidity, water_level, soil_moisture)
                    self.load_data()

            except Exception as e:
                print(f"시리얼 데이터 읽기 오류: {e}")
        else:
            print("아두이노 시리얼 포트가 연결되지 않았습니다.")


    def auto_mode(self):
        self.watering_btn.setEnabled(False)
        self.fill_tank_btn.setEnabled(False)
        self.mode_label.setText('    자동 모드    ')
        print('자동 모드 on')
        if self.db.ser and self.db.ser.is_open:
            self.db.ser.write(b'AUTO\n')

    def manual_mode(self):
        self.watering_btn.setEnabled(True)
        self.fill_tank_btn.setEnabled(True)
        self.mode_label.setText('    수동 모드    ')
        print('수동 모드 on')
        if self.db.ser and self.db.ser.is_open:
            self.db.ser.write(b'MANUAL\n')

    def watering(self):
        if self.watering_btn.isChecked():
            self.watering_btn.setStyleSheet("color: white;"
                      "background-color: #00BCD4;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #4DD0E1;"
                      "border-radius: 3px")
        else:
            self.watering_btn.setStyleSheet("color: white;"
                      "background-color: #1E88E5;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #03A9F4;"
                      "border-radius: 3px")
        
        if self.db.ser and self.db.ser.is_open:
            try:
                if self.watering_btn.isChecked():
                    self.db.ser.write(b'W1\n')
                    print("아두이노에 급수 시작 명령 전송: W1")
                else:
                    self.db.ser.write(b'W0\n')
                    print("아두이노에 급수 중지 명령 전송: W0")
            except Exception as e:
                print(f"아두이노 급수 명령 전송 실패: {e}")
        else:
            print("아두이노 시리얼 포트가 연결되지 않아 급수 명령을 보낼 수 없습니다.")
        
    def fill_tank(self):
        if self.fill_tank_btn.isChecked():
            self.fill_tank_btn.setStyleSheet("color: white;"
                      "background-color: #00BCD4;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #4DD0E1;"
                      "border-radius: 3px")
        else:
            self.fill_tank_btn.setStyleSheet("color: white;"
                      "background-color: #1E88E5;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #03A9F4;"
                      "border-radius: 3px")

        if self.db.ser and self.db.ser.is_open:
            try:
                if self.fill_tank_btn.isChecked():
                    self.db.ser.write(b'W2\n')
                    print("아두이노에 급수 시작 명령 전송: W2")
                else:
                    self.db.ser.write(b'W3\n')
                    print("아두이노에 급수 중지 명령 전송: W3")
            except Exception as e:
                print(f"아두이노 급수 명령 전송 실패: {e}")
        else:
            print("아두이노 시리얼 포트가 연결되지 않아 급수 명령을 보낼 수 없습니다.")
            
    def open_date_data_window(self):
        date = self.calender.selectedDate().toString(Qt.ISODate)
        self.date_data_dialog = date_data_window(date=date, db_instance=self.db)
        self.date_data_dialog.accepted.connect(self.load_data)
        self.date_data_dialog.exec_()