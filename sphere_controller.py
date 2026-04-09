"""Logitech Sphere Pan/Tilt Controller GUI (PySide6)."""

import os
import subprocess
import sys
from datetime import datetime

VERSION = "0.1.0"
BUILD_DATE = os.environ.get("BUILD_DATE", datetime.now().strftime("%Y-%m-%d"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


def _find_motor_bin():
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(sys._MEIPASS, "motor_final")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "motor_final")


MOTOR_BIN = _find_motor_bin()


class MotorDaemon:
    def __init__(self):
        self._proc = None

    def start(self):
        self._proc = subprocess.Popen(
            [MOTOR_BIN, "--daemon"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        import time
        time.sleep(0.1)
        return self._proc.poll() is None

    def _send(self, cmd: str):
        if not self._proc or self._proc.poll() is not None:
            self.start()
        try:
            self._proc.stdin.write(f"{cmd}\n".encode())
            self._proc.stdin.flush()
        except (BrokenPipeError, OSError):
            self.start()

    def move(self, pan, tilt):
        self._send(f"move {pan} {tilt}")

    def stop_move(self):
        self._send("stop")

    def reset(self):
        self._send("reset")

    def quit(self):
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.stdin.write(b"quit\n")
                self._proc.stdin.flush()
                self._proc.wait(timeout=2)
            except Exception:
                self._proc.kill()


MOTOR = MotorDaemon()

DIRECTIONS = {
    "left": (-64, 0), "right": (64, 0),
    "up": (0, -64), "down": (0, 64),
}


class DirectionPad(QWidget):
    _BUTTON_COLORS = {
        "up":    ("#2ecc71", "#27ae60", "#1e8449"),
        "down":  ("#2ecc71", "#27ae60", "#1e8449"),
        "left":  ("#3498db", "#2980b9", "#2471a3"),
        "right": ("#3498db", "#2980b9", "#2471a3"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._degrees = 5
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        row_top = QHBoxLayout()
        row_top.addStretch()
        row_top.addWidget(self._make_button("Up", "up"))
        row_top.addStretch()
        layout.addLayout(row_top)

        row_mid = QHBoxLayout()
        row_mid.setSpacing(4)
        btn_reset = QPushButton("Reset")
        btn_reset.setMinimumSize(70, 70)
        btn_reset.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; "
            "font-weight: bold; min-width: 70px; min-height: 70px; border-radius: 35px; }"
            "QPushButton:hover { background-color: #c0392b; }"
            "QPushButton:pressed { background-color: #a93226; }"
        )
        btn_reset.clicked.connect(MOTOR.reset)
        row_mid.addStretch()
        row_mid.addWidget(self._make_button("Left", "left"))
        row_mid.addWidget(btn_reset)
        row_mid.addWidget(self._make_button("Right", "right"))
        row_mid.addStretch()
        layout.addLayout(row_mid)

        row_bot = QHBoxLayout()
        row_bot.addStretch()
        row_bot.addWidget(self._make_button("Down", "down"))
        row_bot.addStretch()
        layout.addLayout(row_bot)

    def _make_button(self, label, command):
        btn = QPushButton(label)
        btn.setMinimumSize(70, 70)
        bg, hover, pressed = self._BUTTON_COLORS.get(command, ("#3498db", "#2980b9", "#2471a3"))
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {bg}; color: white; "
            f"font-weight: bold; font-size: 14px; border-radius: 35px; }}"
            f"QPushButton:hover {{ background-color: {hover}; }}"
            f"QPushButton:pressed {{ background-color: {pressed}; }}"
        )
        btn.pressed.connect(lambda cmd=command: self._on_press(cmd))
        btn.released.connect(self._on_release)
        return btn

    def _on_press(self, command):
        d = DIRECTIONS[command]
        MOTOR.move(d[0] * self._degrees, d[1] * self._degrees)

    def _on_release(self):
        MOTOR.stop_move()

    def set_degrees(self, degrees):
        self._degrees = degrees


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Logitech Sphere Controller v{VERSION}")
        self.setFixedSize(350, 420)
        self._held_key = None
        self._init_ui()
        self._connect_motor()

    def _connect_motor(self):
        if MOTOR.start():
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("font-size: 13px; color: #27ae60;")
        else:
            self.status_label.setText("motor_final failed to start")
            self.status_label.setStyleSheet("font-size: 13px; color: #e74c3c; font-weight: bold;")

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)

        self.status_label = QLabel("Connecting...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        layout.addWidget(self.status_label)

        pad_group = QGroupBox("Pan / Tilt")
        pad_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        pad_layout = QVBoxLayout(pad_group)
        self.dpad = DirectionPad()
        pad_layout.addWidget(self.dpad)
        layout.addWidget(pad_group)

        slider_group = QGroupBox("Step Size")
        slider_layout = QVBoxLayout(slider_group)
        slider_row = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(2)
        self.slider.setMaximum(10)
        self.slider.setValue(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)

        self.degree_label = QLabel("5°")
        self.degree_label.setMinimumWidth(35)
        self.degree_label.setAlignment(Qt.AlignCenter)
        self.degree_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.slider.valueChanged.connect(self._on_slider_changed)

        slider_row.addWidget(QLabel("2°"))
        slider_row.addWidget(self.slider)
        slider_row.addWidget(QLabel("10°"))
        slider_row.addWidget(self.degree_label)
        slider_layout.addLayout(slider_row)
        layout.addWidget(slider_group)

        version_label = QLabel(f"v{VERSION} | Build: {BUILD_DATE}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 11px; color: #95a5a6;")
        layout.addWidget(version_label)

        self._shortcuts = {
            Qt.Key_Up: "up", Qt.Key_Down: "down",
            Qt.Key_Left: "left", Qt.Key_Right: "right",
            Qt.Key_Space: "reset", Qt.Key_R: "reset",
        }

    def _on_slider_changed(self, value):
        self.degree_label.setText(f"{value}°")
        self.dpad.set_degrees(value)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        cmd = self._shortcuts.get(event.key())
        if cmd:
            if cmd == "reset":
                MOTOR.reset()
            else:
                self._held_key = cmd
                d = DIRECTIONS[cmd]
                deg = self.slider.value()
                MOTOR.move(d[0] * deg, d[1] * deg)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if self._shortcuts.get(event.key()) == self._held_key:
            MOTOR.stop_move()
            self._held_key = None
        else:
            super().keyReleaseEvent(event)

    def closeEvent(self, event):
        MOTOR.quit()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
