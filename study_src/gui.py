import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QPainter


class ChartWidget(QWidget):
    def __init__(self, parent=None, ticker='BTC'):
        super().__init__(parent)
        uic.loadUi('./ui/chart.ui', self)
        self.ticker = ticker

        self.viewLimit = 128
        self.priceData = QLineSeries()
        self.priceData.append(0,10)
        self.priceData.append(1,20)
        self.priceData.append(2,10)

        self.priceChart = QChart()
        self.priceChart.addSeries(self.priceData)

        self.priceView.setChart(self.priceChart)



        axisX = QDateTimeAxis()
        axisX.setFormat('hh:mm:ss')
        axisX.setTickCount(4)
        dt = QDateTime.currentDateTime()
        axisX.setRange(dt, dt.addSecs(self.viewLimit))

        axisY = QValueAxis()
        axisY.setVisible(False)

        self.priceChart.addAxis(axisX, Qt.AlignBottom)
        self.priceChart.addAxis(axisY, Qt.AlignRight)
        self.priceData.attachAxis(axisX)
        self.priceData.attachAxis(axisY)
        self.priceChart.layout().setContentsMargins(0,0,0,0)

        self.priceChart.legend().hide()
        self.priceView.setRenderHints(QPainter.Antialiasing)


    def appendData(self, currPirce):
        if len(self.priceData) == self.viewLimit :
              self.priceData.remove(0)
        dt = QDateTime.currentDateTime()
        self.priceData.append(dt.toMSecsSinceEpoch(), currPirce)
        self.__updateAxis()

    def __updateAxis(self):
        pvs = self.priceData.pointsVector()
        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))
        if len(self.priceData) == self.viewLimit:
            dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x()))
        else:
            dtLast = dtStart.addSecs(self.viewLimit)

        ax = self.priceChart.axisX()
        ax.setRange(dtStart, dtLast)

        ay = self.priceChart.axisY()
        dataY = [v.y() for v in pvs]
        ay.setRange(min(dataY), max(dataY))

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    cw = ChartWidget()
    cw.show()
    exit(app.exec_())

