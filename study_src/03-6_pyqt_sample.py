import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import pykorbit

form_class = uic.loadUiType("./ui/test.ui")[0]

class MyWindow(QMainWindow, form_class):  # 인자로 받은 클래스를 상속 (QT제공 디폴트윈도우, QTdesigner ui파일)
    def __init__(self):
        super().__init__() # 부모클래스(QMainWindow)의 초기화자를 호출

        # 상속된 부모클래스(form_class)내의 setupUi 함수를 통해 현재 윈도우를 위의 test.ui로 셋팅
        self.setupUi(self)

        # 1) 클릭 시마다 콜백함수 호출
        # self.pushButton.clicked.connect(self.inquery)
        # -> 상속된 부모클래스(form_class,test.ui)의 위젯객체변수(pushButton)가 '클릭(clicked)'될 시,
        #    클래스 내의 콜백함수(inquery)를 '연결(connect)'해서 실행되도록 함

        # 2) timeout이벤트 발생시마다 콜백함수 호출
        self.timer = QTimer(self) # QTimer 객체 생성
        self.timer.start(1000) # 1초 간격으로 timeout 이벤트 발생시킴
        self.timer.timeout.connect(self.inquery) # timeout시 마다 inquery 함수 연결

    def inquery(self):
        cur_time = QTime.currentTime() # 현재 시간을 str로 변환해서
        str_time = cur_time.toString("hh:mm:ss")
        self.statusBar().showMessage(str_time) # statusBar쪽에 출력.

        price = pykorbit.get_current_price("BTC") # 비트코인 시세 조회해서
        self.lineEdit.setText(str(price))  # 위젯객체(객체변수명=lineEdit)에 가격을 텍스트로 입력.(setText)


app = QApplication(sys.argv)  # QApplication 클래스의 인스턴스

window = MyWindow() # 객체 생성
window.show() # 객체 보이기

app.exec_()  # 이벤트 루프 -> 윈도우가 출력되고 윈도우를 닫을 때까지 프로그램이 계속해서 실행됨

''' 
==================[ STUDY POINT ]==================
import pykorbit  # python pakage설치 -> 시작 > anaconda3 prompt에서 pip를 통해 설치 (의존성 등의 문제를 아나콘다에서 관리해줌)
A.connect        # (모듈/클래스/객체)에서 (함수/변수/등)을 연달아 호출
===================================================
'''