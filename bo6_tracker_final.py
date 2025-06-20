import sys, cv2, numpy as np
import pyautogui, time, random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QThread
from pynput.mouse import Controller

class TrackerThread(QThread):
    def __init__(self, speed):
        super().__init__()
        self.speed = speed
        self.running = False
        self.mouse = Controller()
        self.target_color = np.array([201, 0, 141])
    def run(self):
        self.running = True
        while self.running:
            img = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            th = cv2.cvtColor(np.uint8([[self.target_color]]), cv2.COLOR_BGR2HSV)[0][0]
            lower = np.array([max(0, th[0]-10),50,50])
            upper = np.array([min(179, th[0]+10),255,255])
            mask = cv2.inRange(hsv, lower, upper)
            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if cnts:
                c = max(cnts, key=cv2.contourArea)
                M = cv2.moments(c)
                if M["m00"] != 0:
                    x = int(M["m10"]/M["m00"]); y = int(M["m01"]/M["m00"])
                    self.move_mouse(x, y)
            time.sleep(0.02)
    def move_mouse(self, x, y):
        cx, cy = self.mouse.position
        dx, dy = x - cx, y - cy
        steps = max(1, int(max(abs(dx), abs(dy))*self.speed))
        for i in range(steps):
            nx = cx + dx*(i/steps) + random.gauss(0,1)
            ny = cy + dy*(i/steps) + random.gauss(0,1)
            self.mouse.position = (nx, ny)
            time.sleep(0.005)
    def stop(self):
        self.running = False
        self.wait()

class AimAssistApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BO6 Aim Assist")
        self.setFixedSize(400, 300)
        self.thread = None
        layout = QVBoxLayout()
        for lvl, speed in [("Lite",0.1),("Normal",0.3),("Middle",0.6),("Super",1.0)]:
            h = QHBoxLayout()
            start = QPushButton(f"{lvl} AimAssist"); stop = QPushButton(f"Stop {lvl}")
            h.addWidget(start); h.addWidget(stop); layout.addLayout(h)
            start.clicked.connect(lambda _,s=speed: self.start(s))
            stop.clicked.connect(lambda _,: self.stop())
        self.target_box = QLabel("Target: Random"); layout.addWidget(self.target_box)
        hb = QHBoxLayout()
        for t in ["Head","Random","Chest"]:
            b = QPushButton(t); hb.addWidget(b)
            b.clicked.connect(lambda _,t=t: (self.target_box.setText(f"Target: {t}")))
        layout.addLayout(hb)
        self.setLayout(layout)
    def start(self, speed):
        self.stop()
        self.thread = TrackerThread(speed)
        self.thread.start()
    def stop(self):
        if self.thread: self.thread.stop(); self.thread = None
    def closeEvent(self, e):
        self.stop(); e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AimAssistApp(); w.show()
    sys.exit(app.exec_())
