# -*- coding: utf-8 -*-
"""
Created on Monday 2023 06 26
Widget to control BNC pulse Generator

@author: loa
"""



#import serial.tools.list_ports
#serial_port = serial.tools.list_ports.comports()
#for port in serial_port:
#    print(f"{port.name} // {port.device} // D={port.description}")




from PyQt6 import QtCore
import qdarkstyle

from PyQt6.QtWidgets import QApplication,QLabel,QComboBox,QToolButton,QAbstractSpinBox
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QPushButton,QHBoxLayout,QDoubleSpinBox,QFrame
import qdarkstyle
import time
import sys,os
import pyvisa
from PyQt6.QtGui import QColor,QIcon
from PyQt6.QtCore import Qt
import pathlib

class BNCBOX(QWidget):
     
    def __init__(self,com='com3',parent=None):
        
        super(BNCBOX, self).__init__(parent)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        sepa=os.sep
        p = pathlib.Path(__file__)
        self.icon=str(p.parent) + sepa+'icons'+sepa
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.com=com
        self.confBNC=QtCore.QSettings("confBNC.ini", QtCore.QSettings.Format.IniFormat)
        #self.ser=serial.Serial("/dev/ttyUSB0")
        rm=pyvisa.ResourceManager()
        
        # Ouverture du BNC
        self.bnc=rm.open_resource(self.com)
        self.bnc.term_chars='\r\n'
        self.bnc.read_termination='\r\n'
        self.bnc.send_end=True
        self.bnc.baud_rate=9600
        
        self.bnc.query("*IDN?")
        numSerie=self.bnc.read()
        print('connected) @',numSerie)
        self.setWindowTitle('Berkley Nucleonics Corporation' + ' s/n: ' + str(numSerie) )
        self.bnc.write(":PULSE0:STAT OFF") # not running at starting
        self.bnc.write(":PULS:EXT:LEV 2.1")
        self.bnc.write(":PULS:EXT:EDGERIS")
        self.bnc.write(":PULS:EXT:POL:HIGH")
        self.isrunnig=False
        self.onehzIsRunning=False
        self.threadOneHz=THREADONEHZ(parent=self)
        self.setup()
        self.actionButton()
        self.iniValue()

    def setup(self):

        vbox=QVBoxLayout()
        hbox=QHBoxLayout()

        self.trig=QComboBox(self)
        self.trig.addItem('Triggered')
        self.trig.addItem('Gated')
        self.trig.addItem('Disable')
        hbox.addWidget(self.trig)

        self.mode=QComboBox(self)
        self.mode.addItem('Continuous')
        self.mode.addItem('Duty circle')
        self.mode.addItem('Burst')
        self.mode.addItem('Single Shot')
        hbox.addWidget(self.mode)

        self.startButton=QToolButton(self)
        self.startButton.setText("run")
        hbox.addWidget(self.startButton)
        vbox.addLayout(hbox)

        self.widCh1=WIDGETBNC(channel='PULSE1',conf=self.confBNC,color='blue',parent=self)
        vbox.addWidget(self.widCh1)
        self.widCh2=WIDGETBNC(channel='PULSE2',conf=self.confBNC,color='red',parent=self)
        vbox.addWidget(self.widCh2)
        self.widCh3=WIDGETBNC(channel='PULSE3',conf=self.confBNC,color='magenta',parent=self)
        vbox.addWidget(self.widCh3)
        self.widCh4=WIDGETBNC(channel='PULSE4',conf=self.confBNC,color='cyan',parent=self)
        vbox.addWidget(self.widCh4)

        self.softTriggButton=QToolButton()
        self.softTriggButton.setText('Soft Trig')
        hbox.addWidget(self.softTriggButton)
        self.OneHzTriggButton=QToolButton()
        self.OneHzTriggButton.setText('1hz')
        hbox.addWidget(self.OneHzTriggButton)
        delayLabel=QLabel('Delay 1hz')
        hbox.addWidget(delayLabel)
        self.hzDelay=QDoubleSpinBox()
        hbox.addWidget(self.hzDelay)
        self.setLayout(vbox)
    
    def actionButton(self):
         
         self.trig.currentIndexChanged.connect(self.TRIG)
         self.mode.currentIndexChanged.connect(self.MODE)
         self.startButton.clicked.connect(self.RUN)
         self.softTriggButton.clicked.connect(self.SOFT)
         self.OneHzTriggButton.clicked.connect(self.ONEHZ)
         self.hzDelay.editingFinished.connect(self.DELAYHZ)
                                               


    def TRIG(self):

        if self.trig.currentIndex()==0:
            self.bnc.write(':PULSE0:EXT:MOD TRIG')
            self.confBNC.setValue('T0/trig','TRIG')
        elif  self.trig.currentIndex()==1:
            self.bnc.write(':PULSE0:EXT:MOD GATE')
            self.confBNC.setValue('T0/trig','GATE')
        elif  self.trig.currentIndex()==2:
            self.bnc.write(':PULSE0:EXT:MOD DIS')
            self.confBNC.setValue('T0/trig','Dis')
            
    
    def MODE(self):

        if self.mode.currentIndex()==0:
            self.bnc.write(':PULSE0:MODe NORM')
            self.confBNC.setValue('T0/mode','NORM')
        if self.mode.currentIndex()==1:
            self.bnc.write(':PULSE0:MODe DCYC')
            self.confBNC.setValue('T0/mode','DCYC')
        if self.mode.currentIndex()==2:
            self.bnc.write(':PULSE0:MODE BURS')
            self.confBNC.setValue('T0/mode','BURS')
        if self.mode.currentIndex()==3:
            self.bnc.write(':PULSE0:MODE SING')
            self.confBNC.setValue('T0/mode','SING')

    def RUN(self):

        if self.isrunnig==False:
            self.bnc.write(":PULSE0:STAT ON") 
            self.startButton.setStyleSheet("background-color: green")
            self.startButton.setText("Running")
            self.anim = QtCore.QPropertyAnimation(self.startButton, b"size",self)
            self.anim.setStartValue(QtCore.QSize(20, 25))
            self.anim.setEndValue(QtCore.QSize(60, 25))
            self.anim.start()
            self.anim.setDuration(3000)
            self.anim.setLoopCount(-1)
            self.isrunnig=True
        else :
            self.bnc.write(":PULSE0:STAT OFF") 
            self.startButton.setStyleSheet("background-color: transparent")
            self.startButton.setText("Run")
            self.isrunnig=False
            self.anim.stop()

    def ONEHZ(self):
        # print(self.onehzIsRunning)
        if self.onehzIsRunning==False:
            if self.isrunnig==False:
                self.RUN() 
            self.onehzIsRunning=True
            self.OneHzTriggButton.setStyleSheet("background-color: red")
            
            self.widCh1.state.setCurrentIndex(1)
            # mess=':PULSE1:STATE OFF '
            # self.bnc.write(mess)
            self.widCh2.state.setCurrentIndex(1)
            # mess=':PULSE2:STATE OFF '
            # self.bnc.write(mess)

            d = self.delayHz #♦0.940-(0/1000)
            v3=self.widCh3.boxDelay.value()
            v4=self.widCh4.boxDelay.value()
            self.widCh3.boxDelay.setValue(v3+d)
            self.widCh4.boxDelay.setValue(v4+d)
            mess=':PULSE3:DELAY '+str(round(float(v3+d),9))
            self.bnc.write(mess)
            mess=':PULSE4:DELAY '+str(round(float(v4+d),9))
            self.bnc.write(mess)
            self.bnc.query(":DISP:UPDATE")
        else:
            self.OneHzTriggButton.setStyleSheet("background-color: transparent")
            self.widCh1.valueIni()
            time.sleep(0.1)
            self.widCh2.valueIni()
            time.sleep(0.1)
            self.widCh3.valueIni()
            time.sleep(0.1)
            self.widCh4.valueIni()
            time.sleep(0.1)
            self.RUN()
            self.onehzIsRunning=False


    def SOFT(self):
            if self.isrunnig==False:
                self.RUN() 
                time.sleep(0.1)
                self.bnc.write('*TRG')
                time.sleep(0.1)
                self.isrunnig = True
                self.RUN()
            else : 
                self.bnc.write('*TRG')
        
    def iniValue(self):
        
        if self.confBNC.value("T0/trig")=='TRIG':
            self.trig.setCurrentIndex(0)
        if self.confBNC.value("T0/trig")=='GATE':
            self.trig.setCurrentIndex(1)
        if self.confBNC.value("T0/trig")=='DIS':
            self.trig.setCurrentIndex(2)
        self.TRIG()
        
        if self.confBNC.value("T0/mode")=='NORM':
            self.mode.setCurrentIndex(0)
        if self.confBNC.value("T0/mode")=='DCYC':
            self.mode.setCurrentIndex(1)
        if self.confBNC.value("T0/mode")=='BURS':
            self.mode.setCurrentIndex(2)
        if self.confBNC.value("T0/mode")=='SING':
            self.mode.setCurrentIndex(3)
        self.MODE()
        self.bnc.query(":DISP:UPDATE")
        self.hzDelay.setValue(float(self.confBNC.value("T0/delayHz")))
        self.delayHz=self.hzDelay.value()

    def DELAYHZ(self):
        self.delayHz=self.hzDelay.value()
        self.confBNC.setValue("T0/delayHz",self.delayHz)

    def closeEvent(self,event):
        ''' closing window event (cross button) '''
        self.bnc.write(":PULSE0:STAT OFF") # not running 
        time.sleep(0.1)  
    
class WIDGETBNC(QWidget):
    #widget for 1 channel mode sate delay witdth
    def __init__(self,channel='PULSE1',conf=None,color='white',parent=None):
        
        super(WIDGETBNC, self).__init__(parent)
        
        self.isWinOpen=False
        self.channel=channel
        self.color=color
        self.parent=parent
        self.bnc=self.parent.bnc
        self.confBNC=conf
        self.setup()
        self.valueIni()
        self.actionButton()
        
    def setup(self):

        vbox1=QVBoxLayout()
        hbox=QHBoxLayout()
        hbox1=QHBoxLayout()

        self.name=QLabel(self.channel)
        self.name.setStyleSheet('font: bold 18px')
        #self.name.setStyleSheet('border-width: 2px;border-style: solid;border-color: white')
        self.name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        hbox.addWidget(self.name)
        self.state=QComboBox(self)
        self.state.addItem('Enable')
        self.state.addItem('Disable')
        hbox.addWidget(self.state)
        self.mode=QComboBox(self)
        self.mode.addItem('Normal')
        self.mode.addItem('Duty circle')
        self.mode.addItem('Burst')
        self.mode.addItem('Single Shot')
        hbox.addWidget(self.mode)
        vbox1.addLayout(hbox)

        lab1=QLabel('Delay')
        self.boxDelay=QDoubleSpinBox()
        self.boxDelay.setDecimals(9)
        self.boxDelay.setMaximum(1)
        self.boxDelay.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        hbox1.addWidget(lab1)
        hbox1.addWidget(self.boxDelay)

        lab2=QLabel('Width')
        self.boxWidth=QDoubleSpinBox()
        self.boxWidth.setDecimals(9)
        self.boxWidth.setMaximum(1)
        self.boxWidth.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        hbox1.addWidget(lab2)
        hbox1.addWidget(self.boxWidth)

        vbox1.addLayout(hbox1)
       
        
        widget=QWidget()
        
        widget.setLayout(vbox1)
        widget.setObjectName("colorWidget")
        #border-width: 2px;border-style: solid;border-color: white
        widget.setStyleSheet('QWidget#colorWidget{ border-width: 1px;border-style: solid;border-color: white}')
        vbox2=QVBoxLayout()
        vbox2.addWidget(widget)
        self.setLayout(vbox2)
        
    def actionButton(self):
         self.state.currentIndexChanged.connect(self.STATE)
         self.mode.currentIndexChanged.connect(self.MODE)
         self.boxDelay.editingFinished.connect(self.DELAY)
         self.boxWidth.editingFinished.connect(self.WIDTH)


    def STATE(self):

        if self.state.currentIndex()==0:
            
            mess=':'+str(self.channel)+':STATE ON '
            if self.parent.onehzIsRunning==False :
                self.confBNC.setValue(self.channel+'/state','ON')
            self.bnc.write(mess)
            # print(self.channel,mess)
        else :
            mess=':'+str(self.channel)+':STATE OFF '
            if self.parent.onehzIsRunning==False :
                self.confBNC.setValue(self.channel+'/state','OFF')
            self.bnc.write(mess)
        self.bnc.query(":DISP:UPDATE")
    
    def DELAY(self):
        val=self.boxDelay.value()
        mess=':'+str(self.channel)+':DELAY '+str(val)
        self.bnc.write(mess)
        if self.parent.onehzIsRunning==False :
            self.confBNC.setValue(self.channel+'/delay',val)
        self.bnc.query(":DISP:UPDATE")

    def WIDTH(self):
        val=self.boxWidth.value()
        mess=':'+str(self.channel)+':WIDT '+str(val)
        self.bnc.write(mess)
        if self.parent.onehzIsRunning==False :
            self.confBNC.setValue(self.channel+'/width',val)
        self.bnc.query(":DISP:UPDATE")

    def MODE(self):
        if self.mode.currentIndex()==0:
            mess=':' +str(self.channel)+':CMOD NORMal'
            self.bnc.write(mess)
            if self.parent.onehzIsRunning==False :
                self.confBNC.setValue(self.channel+'/mode','NORMal')
        if self.mode.currentIndex()==1:
            mess=':' +str(self.channel)+':CMOD DCYClE'
            if self.parent.onehzIsRunning==False :
                self.confBNC.setValue(self.channel+'/mode','DCYClE')
            self.bnc.write(mess)
        if self.mode.currentIndex()==2:
            mess=':' +str(self.channel)+':CMOD BURS'
            self.bnc.write(mess)
            if self.parent.onehzIsRunning==False :
                self.confBNC.setValue(self.channel+'/mode','BURST')
        if self.mode.currentIndex()==3:
            mess=':' +str(self.channel)+':CMOD SING'
            self.bnc.write(mess)
            if self.parent.onehzIsRunning==False :
                self.confBNC.setValue(self.channel+'/mode','SINGle')
        self.bnc.query(":DISP:UPDATE")

    def valueIni(self):
        # write initial value on the widget and send to the controler
        self.bnc.write(":"+self.channel+":SYNC T0")
        time.sleep(0.01)
        self.bnc.write(":"+self.channel+":OUTPut:AMPL 5.0")
        time.sleep(0.01)
        self.bnc.write(":"+"self.channel"+":EDGe RISing")
        time.sleep(0.01)
        self.bnc.write(":"+"self.channel"+":POLarity NORMal")
        time.sleep(0.01)
        if self.confBNC.value(self.channel+'/mode')=='NORMal':
            self.mode.setCurrentIndex(0)
        if self.confBNC.value(self.channel+'/mode')=='DCYClE':
            self.mode.setCurrentIndex(1)
        if self.confBNC.value(self.channel+'/mode')=='BURST':
            self.mode.setCurrentIndex(2)
        if self.confBNC.value(self.channel+'/mode')=='SINGle':
            self.mode.setCurrentIndex(3)
        self.MODE()
        time.sleep(0.01)
        
        d=self.confBNC.value(self.channel+'/delay')
        self.boxDelay.setValue(round(float(d),9))
        mess=':'+str(self.channel)+':DELAY '+str(round(float(d),9))
        
        self.bnc.write(mess)
        time.sleep(0.05)

        w=self.confBNC.value(self.channel+'/width')
        self.boxWidth.setValue(round(float(w),9))
        mess=':'+str(self.channel)+':WIDTH '+str(round(float(w),9))
        self.bnc.write(mess)
        time.sleep(0.05)

        if self.confBNC.value(self.channel+"/state")=='ON':
            self.state.setCurrentIndex(0)
        if self.confBNC.value(self.channel+"/state")=='OFF':
            self.state.setCurrentIndex(1)
        self.STATE()
        time.sleep(0.05)
        self.bnc.query(":DISP:UPDATE")
        
class THREADONEHZ(QtCore.QThread):
    '''Second thread for controling one HZ
    '''
    def __init__(self, parent):
        super(THREADONEHZ,self).__init__()
        self.parent=parent
        self.bnc = self.parent.bnc
        self.stopRun=False
    
   
    
    
    def run(self):
        i=0
        while True:
            if self.stopRun==True:
                break
            self.bnc.write('*TRG')
            i=i+1
            
            time.sleep(1)
       
    def stopThreadOneHz(self):
        
        self.stopRun=True

if __name__ =='__main__':
    appli=QApplication(sys.argv)
    tt=BNCBOX()
    tt.show()
    appli.exec()