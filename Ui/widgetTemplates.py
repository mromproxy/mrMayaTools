import os,re,sys,json
from PySide2.QtCore import Qt, QSize, QRect, QPoint#, QMargins
from PySide2.QtWidgets import ( QApplication, QMainWindow, QSizePolicy,
        QWidget, QDockWidget, QTabWidget , 
        QLayout, QHBoxLayout,QVBoxLayout, 
        QPushButton, QLabel, QTextEdit ) 
#from PySide2.QtGui import *
#from PySide2.QtCore import *

class skinningMainWindow(QMainWindow):
    def __init__(self):
        super(skinningMainWindow,self).__init__()
        self.statusBar().showMessage('Loading')
        #buttonMenu=QVBoxLayout()
        #settingMenu=QVBoxLayout()
        #toolsMenu=QVBoxLayout()


class ButtonWidgetTemplate(QDockWidget):
    def __init__(self):
        super(ButtonWidgetTemplate,self).__init__()
        #display
        #[name,icon,command]


class SettingsWidgetTemplate(QDockWidget):
    def __init__(self):
        super(SettingsWidgetTemplate,self).__init__()


class CommandWidgetTemplate(QDockWidget):
    def __init__(self):
        super(CommandWidgetTemplate,self).__init__()


class FlowLayout(QLayout):
    def __init__(self):
        super().__init__()

        self._itemList = []

    def __del__(self):
        """Pop element at start until no elements remain"""
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self._itemList.append(item)

    def count(self):
        return len(self._itemList)

    def itemAt(self, index):
        if 0<= index < len(self._itemList):
            return self._itemList
        return None

    def takeAt(self, index):
        if 0<= index < len(self._itemList):
            return self._itemList.pop(index)
        return None

    def expandingDirections(self): #-> PySide2.QtCore.Qt.Orientations:
        return Qt.Orientation(0) #super().expandingDirections()

    def hasHeightForWidth(self): #-> bool:
        return True

    def heightForWidth(self, width) -> int:
        height = self._doLayout(QRect(0,0, width,0),True)
        return height

    def setGeometry(self, rect): #arg__1: PySide2.QtCore.QRect) -> None:
        super().setGeometry(rect)
        self._doLayout(rect, False)
        #return super().setGeometry(arg__1)

    def sizeHint(self): #-> PySide2.QtCore.QSize:
        return self.minimumSize() #super().sizeHint()

    def minimumSize(self) #-> PySide2.QtCore.QSize:
        size = QSize()

        #######################v
        #######################
        #######################
        #######################
        #return super().minimumSize()

    def _doLayout(self,rect,test_only):
        pass

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = skinningMainWindow()
    main_window.show()
    sys.exit(app.exec_())