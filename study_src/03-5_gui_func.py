import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

class MyWindow(QMainWindow) :
    def __init__(self):
        super().__init__()  # 부모클래스(QMainWindow)의 초기화자를 호출
        self.setGeometry(100, 200, 300, 400)    # 윈도우 사이즈 (위치가로, 위치세로, 너비가로, 너비세로)
        self.setWindowTitle("PyQt")
        self.setWindowIcon(QIcon("../image/icon5.png"))

        btn = QPushButton("버튼1", self)
        btn.move(10, 10)
        # btn이라는 변수가 바인딩하는 QPushButton이 클릭될 때 btn_clicked()라는 메서드가 호출되도록 함
        btn.clicked.connect(self.btn_clicked) # 버튼 이벤트 콜백함수

        btn2 = QPushButton("버튼2", self)
        btn2.move(10, 40)

    def btn_clicked(self): # 콜백함수 (이벤트루프가 메서드를 호출함)
        print("버튼 클릭")

app = QApplication(sys.argv)    # QApplication 클래스의 인스턴스

window = MyWindow()
window.show()

app.exec_() # 이벤트 루프 -> 윈도우가 출력되고 윈도우를 닫을 때까지 프로그램이 계속해서 실행됨