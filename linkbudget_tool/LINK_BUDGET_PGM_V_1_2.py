#! /usr/bin/python
"""
Created on Sat Aug 27 2016

@author: VU3VWB
"""
from PyQt4 import QtCore, QtGui
from PyQt4 import Qt
import numpy as np
import sys

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(483, 605)
        self.calculate = QtGui.QPushButton(Form)
        self.calculate.setGeometry(QtCore.QRect(170, 470, 171, 27))
        self.calculate.setObjectName(_fromUtf8("calculate"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(60, 70, 141, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.freq_sb = QtGui.QDoubleSpinBox(Form)
        self.freq_sb.setGeometry(QtCore.QRect(180, 60, 151, 31))
        self.freq_sb.setMaximum(10000000.0)
        self.freq_sb.setSingleStep(0.01)
        self.freq_sb.setProperty("value", 0.1)
        self.freq_sb.setObjectName(_fromUtf8("freq_sb"))
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(360, 70, 66, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.result_lb = QtGui.QLabel(Form)
        self.result_lb.setGeometry(QtCore.QRect(50, 540, 381, 20))
        self.result_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.result_lb.setObjectName(_fromUtf8("result_lb"))
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(360, 170, 66, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(60, 170, 141, 17))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.tx_p_sb = QtGui.QDoubleSpinBox(Form)
        self.tx_p_sb.setGeometry(QtCore.QRect(180, 160, 151, 31))
        self.tx_p_sb.setMinimum(-300.0)
        self.tx_p_sb.setMaximum(300.0)
        self.tx_p_sb.setSingleStep(0.01)
        self.tx_p_sb.setProperty("value", 0.0)
        self.tx_p_sb.setObjectName(_fromUtf8("tx_p_sb"))
        self.label_5 = QtGui.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(360, 270, 66, 21))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.tx_a_gain_sb = QtGui.QDoubleSpinBox(Form)
        self.tx_a_gain_sb.setGeometry(QtCore.QRect(180, 260, 151, 31))
        self.tx_a_gain_sb.setMinimum(-300.0)
        self.tx_a_gain_sb.setMaximum(300.0)
        self.tx_a_gain_sb.setSingleStep(0.01)
        self.tx_a_gain_sb.setProperty("value", 0.0)
        self.tx_a_gain_sb.setObjectName(_fromUtf8("tx_a_gain_sb"))
        self.label_6 = QtGui.QLabel(Form)
        self.label_6.setGeometry(QtCore.QRect(360, 220, 66, 21))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(Form)
        self.label_7.setGeometry(QtCore.QRect(60, 220, 141, 17))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(Form)
        self.label_8.setGeometry(QtCore.QRect(60, 270, 141, 17))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.tx_loss_sb = QtGui.QDoubleSpinBox(Form)
        self.tx_loss_sb.setGeometry(QtCore.QRect(180, 210, 151, 31))
        self.tx_loss_sb.setMinimum(-300.0)
        self.tx_loss_sb.setMaximum(300.0)
        self.tx_loss_sb.setSingleStep(0.01)
        self.tx_loss_sb.setProperty("value", 0.0)
        self.tx_loss_sb.setObjectName(_fromUtf8("tx_loss_sb"))
        self.label_9 = QtGui.QLabel(Form)
        self.label_9.setGeometry(QtCore.QRect(60, 320, 141, 17))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(Form)
        self.label_10.setGeometry(QtCore.QRect(360, 320, 66, 21))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.rx_a_gain_sb = QtGui.QDoubleSpinBox(Form)
        self.rx_a_gain_sb.setGeometry(QtCore.QRect(180, 310, 151, 31))
        self.rx_a_gain_sb.setMinimum(-300.0)
        self.rx_a_gain_sb.setMaximum(300.0)
        self.rx_a_gain_sb.setSingleStep(0.01)
        self.rx_a_gain_sb.setProperty("value", 0.0)
        self.rx_a_gain_sb.setObjectName(_fromUtf8("rx_a_gain_sb"))
        self.label_11 = QtGui.QLabel(Form)
        self.label_11.setGeometry(QtCore.QRect(60, 420, 141, 17))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_12 = QtGui.QLabel(Form)
        self.label_12.setGeometry(QtCore.QRect(60, 370, 141, 17))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.label_13 = QtGui.QLabel(Form)
        self.label_13.setGeometry(QtCore.QRect(360, 370, 66, 21))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.label_14 = QtGui.QLabel(Form)
        self.label_14.setGeometry(QtCore.QRect(360, 420, 66, 21))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.rx_loss_sb = QtGui.QDoubleSpinBox(Form)
        self.rx_loss_sb.setGeometry(QtCore.QRect(180, 360, 151, 31))
        self.rx_loss_sb.setMinimum(-300.0)
        self.rx_loss_sb.setMaximum(300.0)
        self.rx_loss_sb.setSingleStep(0.01)
        self.rx_loss_sb.setProperty("value", 0.0)
        self.rx_loss_sb.setObjectName(_fromUtf8("rx_loss_sb"))
        self.rx_sens_sb = QtGui.QDoubleSpinBox(Form)
        self.rx_sens_sb.setGeometry(QtCore.QRect(180, 410, 151, 31))
        self.rx_sens_sb.setMinimum(-400.0)
        self.rx_sens_sb.setMaximum(400.0)
        self.rx_sens_sb.setSingleStep(0.01)
        self.rx_sens_sb.setProperty("value", 0.0)
        self.rx_sens_sb.setObjectName(_fromUtf8("rx_sens_sb"))
        self.label_15 = QtGui.QLabel(Form)
        self.label_15.setGeometry(QtCore.QRect(360, 120, 66, 21))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.distance_sb = QtGui.QDoubleSpinBox(Form)
        self.distance_sb.setGeometry(QtCore.QRect(180, 110, 151, 31))
        self.distance_sb.setMaximum(1000000000.0)
        self.distance_sb.setSingleStep(0.01)
        self.distance_sb.setProperty("value", 0.1)
        self.distance_sb.setObjectName(_fromUtf8("distance_sb"))
        self.label_16 = QtGui.QLabel(Form)
        self.label_16.setGeometry(QtCore.QRect(60, 120, 141, 17))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.label_17 = QtGui.QLabel(Form)
        self.label_17.setGeometry(QtCore.QRect(60, 20, 321, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Ubuntu"))
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_17.setFont(font)
        self.label_17.setTextFormat(QtCore.Qt.AutoText)
        self.label_17.setObjectName(_fromUtf8("label_17"))

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.calculate, QtCore.SIGNAL(_fromUtf8("clicked()")), self.compute)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Link Budget Calculator v1.1.0", "Link Budget Calculator v1.1.0", None))
        self.calculate.setText(_translate("Form", "Calculate Link Margin", None))
        self.label.setText(_translate("Form", "Frequency", None))
        self.label_2.setText(_translate("Form", "MHz", None))
        self.result_lb.setText(_translate("Form", "Result to be calculated", None))
        self.label_3.setText(_translate("Form", "dBm", None))
        self.label_4.setText(_translate("Form", "Tx Power", None))
        self.label_5.setText(_translate("Form", "dBi", None))
        self.label_6.setText(_translate("Form", "dB", None))
        self.label_7.setText(_translate("Form", "Tx Line Loss", None))
        self.label_8.setText(_translate("Form", "Tx Antenna Gain", None))
        self.label_9.setText(_translate("Form", "Rx Antenna Gain", None))
        self.label_10.setText(_translate("Form", "dBi", None))
        self.label_11.setText(_translate("Form", "Rx Sensitivity", None))
        self.label_12.setText(_translate("Form", "Rx Line Loss", None))
        self.label_13.setText(_translate("Form", "dB", None))
        self.label_14.setText(_translate("Form", "dBm", None))
        self.label_15.setText(_translate("Form", "km", None))
        self.label_16.setText(_translate("Form", "Distance", None))
        self.label_17.setText(_translate("Form", "Developed  by  Jishnu, VU3VWB", None))

        
    def compute(self):
        tx_pow=float(self.tx_p_sb.value())
        tx_line_loss=float(self.tx_loss_sb.value())
        freq=float(self.freq_sb.value())
        dist=float(self.distance_sb.value())*1000.0
        tx_a_gain=float(self.tx_a_gain_sb.value())
        rx_a_gain=float(self.rx_a_gain_sb.value())
        rx_line_loss=float(self.rx_loss_sb.value())
        rx_sens=float(self.rx_sens_sb.value())  
        
        lamb=300/freq
        
        path_loss=10*np.log10(lamb*lamb/(4*3.14159*dist*4*3.14159*dist))    
        rx_power=tx_pow - tx_line_loss + tx_a_gain + rx_a_gain - rx_line_loss + path_loss     
        l_budget=rx_power-rx_sens
        if l_budget<0.0:
            self.result_lb.setText("Link Margin is <font color=red>"+str(l_budget)+"</font> dBm")
        else:
            self.result_lb.setText("Link Margin is <font color=green>"+str(l_budget)+"</font> dBm")

def del_splash():
    #window.show()
    window.show()
    splash_sc.finish(window)
    splash_sc.close()
        
if __name__=='__main__':
    app=Qt.QApplication(sys.argv)
    window=Qt.QWidget()
    widge=Ui_Form()
    widge.setupUi(window)
    splash_sc=Qt.QSplashScreen()
    splash_sc.setPixmap(Qt.QPixmap("antenna_1.jpg"))
    splash_sc.show()
    splas_time=Qt.QTimer()
    splas_time.setSingleShot(1)    
    splas_time.timeout.connect(del_splash)
    splas_time.start(500)   
    app.exec_()
    

