import sys
from PyQt5.QtWidgets import QApplication
from login_dialog import LoginDialog
from main_window import MainWindow
from db_helper import DB, DB_CONFIG

if __name__ == "__main__":
    app = QApplication(sys.argv)

    db_instance = DB(**DB_CONFIG)

    login = LoginDialog(db_instance=db_instance)
    if login.exec_() == LoginDialog.Accepted:
        w = MainWindow(db_instance=db_instance)
        w.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)