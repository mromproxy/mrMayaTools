import re,os
from PySide2.QtWidgets import ( QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSlider, QLineEdit, QRadioButton, 
QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QDockWidget )
from PySide2.QtCore import Qt


class QSliderGroup(QWidget):
    def __init__(self,label='',minValue=0,maxValue=1,sliderPrecision=.01,
                    orientation=Qt.Horizontal,alignment=Qt.AlignLeft,spinBoxArrows=0):
        super(QSliderGroup,self).__init__()
        
        #Input House
        if sliderPrecision == 0:
            self.sliderPrecision = 1
        else:
            self.sliderPrecision = sliderPrecision
        
        #Create Widgets
        self.label = QLabel(label)
        self.label.adjustSize()
        self.slider = QSlider(orientation)
        self.spinBox = QDoubleSpinBox()

        #Adjust Spinbox
        if not spinBoxArrows:
            self.spinBox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.spinBox.setAlignment(alignment)

        #Set Max/Min
        if maxValue:
            self.spinBox.setMaximum(maxValue)
            self.slider.setMaximum(maxValue / sliderPrecision)
        if minValue:
            self.spinBox.setMaximum(minValue)
            self.slider.setMaximum(minValue / sliderPrecision)

        #connect slider and spinbox
        self.slider.valueChanged.connect(self.sliderUpdated)
        self.spinBox.valueChanged.connect(self.spinnerUpdated)

        #Create Layout, add widgets
        if orientation == Qt.Horizontal:
            self.setLayout(QHBoxLayout())
            self.label.setAlignment(Qt.AlignVCenter | alignment)
            if label:
                self.layout().addWidget(self.label)
            self.layout().addWidget(self.slider)
            self.layout().addWidget(self.spinBox)
        else:
            self.setLayout(QVBoxLayout())
            self.label.setAlignment(Qt.AlignHCenter | alignment)
            self.layout().addWidget(self.slider, alignment=Qt.AlignHCenter)
            self.layout().addWidget(self.spinBox)
            if label:
                self.layout().addWidget(self.label)


    def sliderUpdated(self,value):
        self.spinBox.setValue(value * self.sliderPrecision)


    def spinnerUpdated(self,value):
        self.slider.setValue(value / self.sliderPrecision)

class QFileDialogGroup(QWidget):
    def __int__(self,label='',buttonText='',lineEditPlaceholder='',
                alignment=Qt.AlignLeft,**kwargs):
        super(QFileDialogGroup,self).__init__()

        self.setLayout(QHBoxLayout())
        self.label = QLabel(label)
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText(lineEditPlaceholder)
        self.button = QPushButton(buttonText)
        self.button.clicked.connect(self.__buttonPressed)

        for widget in [self.label,self.lineEdit,self.button]:
            self.layout().addWidget(widget,alignment=alignment)


    def __buttonPressed(self):
        pass