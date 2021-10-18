import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MySignal(QObject):
    signal1 = pyqtSignal()
    signal2 = pyqtSignal(int, int) # 시그널로 int 값 두개의 데이터를 보낼 수 있다.
    # MySignal ----emit(1,2)---> MyWindow

    def run(self):
        self.signal1.emit() # signal1 발생
        self.signal2.emit(1, 2)  # *** signal2 발생 + 슬롯에게 데이터 전달



class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        mysignal = MySignal()
        mysignal.signal1.connect(self.signal1_emitted)
        mysignal.signal2.connect(self.signal2_emitted)
        mysignal.run()

    @pyqtSlot()
    def signal1_emitted(self):
        print("signal1 emitted")

    @pyqtSlot(int, int)
    def signal2_emitted(self, arg1, arg2):
        print("signal2 emitted", arg1, arg2) # signal2 발생과 동시에 시그널로부터 int 2개를 전달받음


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()

'''
==================[ STUDY POINT ]==================
<signal, slot 사용법 요약>
: "사용자정의 Signal"은 Signal객체 내의 클래스 변수로, "Slot"은 Window 객체 내에 메소드로 작성하면 됨
  step1. "사용자정의Signal클래스" 내에 signal을 클래스 변수로 생성, run메소드에서 emit되도록 하기
  step2. "Window객체" 내에 (1)"사용자정의Signal객체" 생성, (2) "Slot" 메소드를 작성한 뒤 
         해당 Signal객체 내의 "클래스변수"에 각각의 "Slot"을 할당(connect)하여 사용. 
===================================================
'''