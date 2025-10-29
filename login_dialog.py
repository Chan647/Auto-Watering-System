from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
# from db_helper import DB, DB_CONFIG
from join_in_window import join_in_window

class LoginDialog(QDialog):
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.setWindowTitle("로그인")
        self.setWindowIcon(QIcon('icon-login.png'))
        # self.db = DB(**DB_CONFIG)

        self.db = db_instance

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("아이디", self.username)
        form.addRow("비밀번호", self.password)

        self.btn_login = QPushButton("로그인")
        self.btn_login.setStyleSheet("color: green;"
                      "background-color: #7FFFD4;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #7FFFD4;"
                      "border-radius: 3px;"
                      "background-color: #7FFFD4")
        self.btn_login.clicked.connect(self.try_login)

        self.btn_join = QPushButton("회원가입")
        self.btn_join.setStyleSheet("color: blue;"
                       "background-color: #87CEFA;"
                       "border-style: solid;"
                       "border-width: 3px;"
                       "border-color: #87CEFA")
        self.btn_join.clicked.connect(self.open_join_in_window)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_join)
        self.setLayout(layout)

    def try_login(self):
        uid = self.username.text().strip()
        pw = self.password.text().strip()
        if not uid or not pw:
            QMessageBox.warning(self, "오류", "아이디와 비밀번호를 모두 입력하세요.")
            return

        ok = self.db.verify_user(uid, pw)
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "아이디 또는 비밀번호가 올바르지 않습니다.")

    def open_join_in_window(self):
        self.join_dialog = join_in_window(db_instance=self.db)
        # self.add_dialog.accepted.connect(self)
        self.join_dialog.exec_()