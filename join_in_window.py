from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
# from db_helper import DB, DB_CONFIG

class join_in_window(QDialog):
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.setWindowTitle("회원가입")
        self.setWindowIcon(QIcon('icon-join_in.png'))
        # self.db = DB(**DB_CONFIG)

        self.db = db_instance

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.btn_join = QPushButton('회원가입')
        self.btn_join.setStyleSheet("color: blue;"
                       "background-color: #87CEFA;"
                       "border-style: solid;"
                       "border-width: 3px;"
                       "border-color: #87CEFA")
        self.btn_join.clicked.connect(self.try_join_in)
        self.password.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("아이디", self.username)
        form.addRow("비밀번호", self.password)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_join)
        self.setLayout(layout)

    def try_join_in(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username:
            QMessageBox.warning(self, '오류', '아이디를 입력하세요.')
            return
        
        if not password:
            QMessageBox.warning(self, '오류', '비밀번호를 입력하세요')
            return
        
        ok = self.db.insert_user(username, password)
        if ok:
            QMessageBox.critical(self, "회원가입 실패", "존재하는 아이디거나 비밀번호 입니다")
        else:
            QMessageBox.information(self, "회원가입 완료", "회원가입 완료")
            self.accept()