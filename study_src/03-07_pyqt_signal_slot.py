import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MySignal(QObject): # 사용자정의 시그널(=이벤트,ex.클릭,우클릭)를 정의하기 위해 클래스 생성
    # pyqtSignal 객체를 클래스 변수로 바인딩 / # "signal1"이 시그널(이벤트)의 이름이 됨
    signal1 = pyqtSignal() # *** signal1이 MySignal 클래스 내에 정의된 'clicked'와 같은 시그널(이벤트)임

    def run(self):  # 시그널을 발생시키는 함수
        self.signal1.emit()  # pyqtSignal 객체 내에 있는 emit 함수


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # mysignal이라는 변수가 바인딩하는 Mysignal 객체가 signal1에 해당하는 동작을 할때 signal_emitted라는 메서드가 호출되도록 함
        mysignal = MySignal()  # MySignal 객체 생성
        mysignal.signal1.connect(self.signal1_emitted) # 시그널(signal1)(이벤트)과 슬롯(signal_emitted)(이벤트 발생시 호출되는 함수,매소드)를 연결
        mysignal.run()  # 시그널 발생 ( run -> signal_emitted)

    @pyqtSlot()
    def signal1_emitted(self): # 시그널 발생시 호출되는 함수 = 슬롯
        print("signal1 emitted")


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()

''' 
==================[ STUDY POINT ]==================
- 클래스 네임스페이스 : 변수가 객체를 바인딩 할 때('varA = classB'), classB라는 객체가 저장된 주소 // https://wikidocs.net/1743

- 클래스 변수 <-> 인스턴스 변수 : (결론) 인스턴스 간에 서로 공유해야 하는 값은 클래스 변수를 통해 바인딩해야한다.
    --------------------------------------------
    >>> class Account:
        num_accounts = 0                    # "클래스 변수" ex.계좌 생성시마다 늘어난 계좌 갯수 값 
        def __init__(self, name):
                self.name = name            # "인스턴스 변수" ex. 각 계좌의 이름
                Account.num_accounts += 1
        def __del__(self):
                Account.num_accounts -= 1
    --------------------------------------------
    . 클래스 변수 : 클래스 내부에 선언된 변수 
                  =  클래스의 네임스페이스에 위치함
    . 인스턴스 변수 : 클래스의 __init__함수 안에 선언된 self가 붙어있는 변수
                  = 인스턴스의 네임 스페이스에 위치함   
    ※ 값을 찾는 순서 : 인스턴스의 네임스페이스 >> (없을시) 클래스의 네임스페이스 로 이동해서 값을 찾으므로,
                     인스턴스간 공유해야 하는 값은 클래스 변수로 정의해야한다.  
    // https://wikidocs.net/1744

- 함수 vs 매서드
  : 함수가 메서드를 포함하는 더 큰 개념이다. 
    . 함수 = function = 독립적으로 실행되기도 하는 함수 
    . 매서드 = method = 클래스,객체 안에 정의된 함수  -> 괄호 없이 사용하는 경우가 있는것같다. 
===================================================
'''