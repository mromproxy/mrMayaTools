"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Skinning

Description: In Development
    Main Window for skinning related tools

"""
import os
import re
import sys
import json

from PySide2.QtWidgets import ( QApplication, QMainWindow, QSizePolicy, QAction,
        QWidget, QDockWidget, QTabWidget , 
        QLayout, QHBoxLayout,QVBoxLayout, 
        QPushButton, QLabel, QTextEdit, QGroupBox, QDoubleSpinBox ) 
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt, QObject

class skinningMainWindow(QMainWindow):
    def __init__(self):
        super(skinningMainWindow,self).__init__()
        self.statusBar().showMessage('Loading')
        testKeySequence = QKeySequence()
        print( QKeySequence.fromString("Ctrl+[") )
        
        changePaintSkinValueWidget = changePaintSkinValueGroup()
        self.setCentralWidget(changePaintSkinValueWidget)
        #settingsWidget = settingsDockWidget()
        #buttonMenu=QVBoxLayout()
        #settingMenu=QVBoxLayout()
        #toolsMenu=QVBoxLayout()


class buttonDockWidget(QDockWidget):
    def __init__(self):
        super(buttonDockWidget,self).__init__()
        #display
        #[name,icon,command]


class settingsDockWidget(QDockWidget):
    def __init__(self):
        super(settingsDockWidget,self).__init__()
        

class changePaintSkinValueGroup(QGroupBox):
    def __init__(self):
        super(changePaintSkinValueGroup,self).__init__()
        #paintSkinSettingsWidget = QGroupBox()
        #self.setObjectName('Paint Skin Weights')
        self.setTitle( 'Paint Skin Weights' )
        
        
        #Step Increment Segment
        paintSkinValueLayout = QHBoxLayout()
        paintSkinValueLayout.setAlignment(Qt.AlignRight)
        paintSkinValueLabel = QLabel("Step Increment: ")
        paintSkinValueDoubleSpinBox = QDoubleSpinBox()
        paintSkinValueDoubleSpinBox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        paintSkinValueDoubleSpinBox.setValue(0.05)
        paintSkinValueLayout.addWidget(paintSkinValueLabel)
        paintSkinValueLayout.addWidget(paintSkinValueDoubleSpinBox)

        paintSkinValueChangeHotkeyLabel = QLabel("Step Value Hotkey: ")
        self.paintSkinValueChangeValueDownLabel = QLabel('Ctrl + [')
        self.changePaintSkinValueDownAction = QAction()
        
        self.paintSkinValueChangeValueDownLabel.addAction(self.changePaintSkinValueDownAction)
        self.paintSkinValueChangeValueUpLabel = QLabel('Ctrl + ]')
        self.paintSkinValueChangeValueUpLabel.addAction(QAction())
        self.updateChangeValueHotkeys()
        
        self.setLayout(paintSkinValueLayout)
        #paintSkinValueChangeDownHotkey = QKeySequence(Qt.CTRL + Qt.Key_BracketLeft)
        #paintSkinValueChangeUpHotkey = QKeySequence(Qt.CTRL + Qt.Key_BracketRight)
        
        #paintSkinValueChangeValueDownLabel= QLabel( QKeySequence.toString(paintSkinValueChangeDownHotkey) )
        #paintSkinValueChangeValueUpLabel= QLabel( QKeySequence.toString(paintSkinValueChangeUpHotkey) )
        #paintSkinValueChangeValueDownLabel.addAction() addAction
        #print(QKeySequence.toString(paintSkinValueChangeDownHotkey))
        #print(paintSkinValueChangeDownHotkey)
        #print( QKeySequence(QObject.tr("Ctrl+[")) )


    def updateChangeValueHotkeys(self):
        valueDownKeySequence = QKeySequence.fromString( self.paintSkinValueChangeValueDownLabel.text() )
        print( self.paintSkinValueChangeValueDownLabel.actions() ) #[0].setShortcut(valueDownKeySequence)
        self.changePaintSkinValueDownAction.setShortcut(valueDownKeySequence)
        # valueUpKeySequence = QKeySequence.fromString( self.paintSkinValueChangeValueUpLabel.text() )
        # self.paintSkinValueChangeValueUpLabel.actions()[0].setShortcut(valueUpKeySequence)

class commandDockWidget(QDockWidget):
    def __init__(self):
        super(commandDockWidget,self).__init__()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = skinningMainWindow()
    main_window.show()
    sys.exit(app.exec_())

"""
print( mc.artAttrSkinPaintCtx('artAttrSkinContext', e=1, value=.01) )
print( mc.artAttrSkinPaintCtx('artAttrSkinContext', q=1, value=1) )

print( mc.currentCtx() )


"""