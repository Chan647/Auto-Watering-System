# waiting_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer

class WaitingDialog(QDialog):
    def __init__(self, text="아두이노 wifi 연결중...", timeout_ms=30000, on_timeout=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("연결 상태")
        # 닫기 버튼/최소화 등 제거 + 항상 위 + 모달
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(360, 120)

        layout = QVBoxLayout(self)
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)  # 무한 진행바(스피너 역할)
        layout.addWidget(self.label)
        layout.addWidget(self.bar)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)
        self._on_timeout_cb = on_timeout
        self._timeout_ms = timeout_ms

    def start(self):
        self._timer.start(self._timeout_ms)
        self.show()

    def close_when_done(self):
        if self._timer.isActive():
            self._timer.stop()
        # 사용자 임의 닫기 방지: 외부에서만 닫히도록 accept 사용
        self.accept()

    def _on_timeout(self):
        # 타임아웃 시 외부 콜백 호출 후 닫기
        if callable(self._on_timeout_cb):
            self._on_timeout_cb()
        self.accept()