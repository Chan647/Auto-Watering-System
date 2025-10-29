import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# from db_helper import DB, DB_CONFIG
from date_data_window import date_data_window

class MainWindow(QMainWindow):
    def __init__(self, db_instance):
        super().__init__()
        # self.db = DB(**DB_CONFIG)
        self.is_connect_with_device = False
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

        
        self.flag_label = QLabel()
        self.flag_label.setText("아직 기기와 연결되지 않았습니다.")

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

        
        self.watering_btn = QPushButton('급수')
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

        btn_center_layout = QHBoxLayout()
        btn_center_layout.addStretch(1)
        btn_center_layout.addWidget(self.buzzer)
        btn_center_layout.addStretch(1)
        btn_center_layout.addWidget(self.watering_btn)
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

        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.read_arduino_data)
        self.timer.start()

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

        if lastest_smo < 40:
            self.smo_label.setStyleSheet("background-color: #F08080;")
        else:
            self.smo_label.setStyleSheet("background-color: #90EE90;")

        if lastest_wlev < 20:
            self.wlev_label.setStyleSheet("background-color: #90EE90;")
        else:
            self.wlev_label.setStyleSheet("background-color: #F08080;")

        if lastest_smo < 40 :
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

            if wlev < 20:
                self.table.item(r, 2).setBackground(QColor('#FFC0CB'))
            else:
                self.table.item(r, 2).setBackground(QColor('#98FB98'))

            if smo < 40:
                self.table.item(r, 3).setBackground(QColor('#FFC0CB'))
            else:
                self.table.item(r, 3).setBackground(QColor('#98FB98'))

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def read_arduino_data(self):
        if self.db.ser and self.db.ser.is_open:
            try:
                line = self.db.ser.readline().decode('utf-8').strip()
                if line:
                    print(f"아두이노에서 수신: {line}")
                    
                    parts = line.split(',')
                    if len(parts) == 4 and not self.is_connect_with_device:
                        self.is_connect_with_device = True
                        print("드디어 정상적으로 값이 오기 시작했다!")
                        self.flag_label.setText("")
                    else :
                        return

                    temperature = parts[0]
                    humidity = parts[1]
                    water_level = parts[2]
                    soil_moisture = parts[3]

                    if all(v is not None for v in [temperature, humidity, water_level, soil_moisture]):
                        self.db.save_sensor_data(temperature, humidity, water_level, soil_moisture)
                        self.load_data()
                    else:
                        print(f"수신된 데이터 파싱 오류: {line}")
                
            except Exception as e:
                print(f"시리얼 데이터 읽기 오류: {e}")
        else:
            print("아두이노 시리얼 포트가 연결되지 않았습니다.")

    def auto_mode(self):
        self.watering_btn.setEnabled(False)
        self.mode_label.setText('    자동 모드    ')
        print('자동 모드 on')
        if self.db.ser and self.db.ser.is_open:
            self.db.ser.write(b'AUTO\n')

    def manual_mode(self):
        self.watering_btn.setEnabled(True)
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
                if self.watering_btn.isChecked(): # 버튼이 켜진 상태 (급수 시작)
                    self.db.ser.write(b'W1\n') # 'W1' (급수 시작) 명령 전송
                    print("아두이노에 급수 시작 명령 전송: W1")
                else: # 버튼이 꺼진 상태 (급수 중지)
                    self.db.ser.write(b'W0\n') # 'W0' (급수 중지) 명령 전송
                    print("아두이노에 급수 중지 명령 전송: W0")
            except Exception as e:
                print(f"아두이노 급수 명령 전송 실패: {e}")
        else:
            print("아두이노 시리얼 포트가 연결되지 않아 급수 명령을 보낼 수 없습니다.")
            
    def open_date_data_window(self):
        date = self.calender.selectedDate().toString(Qt.ISODate)
        self.date_data_dialog = date_data_window(date=date, db_instance=self.db)
        self.date_data_dialog.accepted.connect(self.load_data)
        self.date_data_dialog.exec_()
        

# if __name__ == "__main__" :
#     app = QApplication(sys.argv) 
#     myWindow = MainWindow() 
#     myWindow.show()
#     app.exec_()