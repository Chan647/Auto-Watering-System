from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# from db_helper import DB, DB_CONFIG

class date_data_window(QDialog):
    def __init__(self, date, db_instance):
        super().__init__()
        # self.db = DB(**DB_CONFIG)
        self.db = db_instance
        self.date = date

        self.setWindowTitle("해당 날짜 데이터")
        self.setWindowIcon(QIcon('icon-temperature.png'))
        self.setGeometry(300, 300, 800, 700)

        layout = QVBoxLayout()
        self.setLayout(layout)
    

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['온도', '습도', '급수탱크 수위', '토양 습도', '측정 시각'])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        self.show_date_data()
        self.timer = QTimer(self)
        self.timer.setInterval(30000)
        self.timer.timeout.connect(self.show_date_data)
        self.timer.start()

    def show_date_data(self):
        rows = self.db.fetch_date_data(self.date)
        self.table.setRowCount(len(rows))
        for r, (tem, hum, smo, wlev, created_time) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(tem)))
            self.table.setItem(r, 1, QTableWidgetItem(str(hum)))
            self.table.setItem(r, 2, QTableWidgetItem(str(wlev)))
            self.table.setItem(r, 3, QTableWidgetItem(str(smo)))
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

            if smo < 50:
                self.table.item(r, 2).setBackground(QColor('#FFC0CB'))
            else:
                self.table.item(r, 2).setBackground(QColor('#98FB98'))

            if wlev < 20:
                self.table.item(r, 3).setBackground(QColor('#FFC0CB'))
            else:
                self.table.item(r, 3).setBackground(QColor('#98FB98'))
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)