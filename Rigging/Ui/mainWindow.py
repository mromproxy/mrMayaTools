from PySide2.QtWidgets import ( QApplication, QMainWindow, QTabWidget, QWidget, QPushButton, QLabel, QTextEdit)
#from PySide2.QtGui import *
#from PySide2.QtCore import *
#import maya.cmds as mc

try:
    import maya.cmds as mc
    externalMode= False #Engine is a poor name for it
except:
    externalMode= True
    import sys

class rigMainWindow(QMainWindow):
    def __init__(self):
        super(rigMainWindow,self).__init__()
        self.setCentralWidget(arMainWidget())
        self.setMinimumSize(400,500)
        self.setWindowTitle('Mrom Autorig')
        self.show()


class arMainWidget(QTabWidget):
    def __init__(self):
        super(arMainWidget,self).__init__()

        self.setTabShape(QTabWidget.Rounded)

        self.overviewPageWidget = rigSettingsWidget()
        self.setupPageWidget = setupWidget()
        self.advancedPageWidget = advancedWidget()
        self.settingsPageWidget = toolSettingsWidget()

        self.addTab(self.overviewPageWidget,'Rig Overview')
        self.setTabToolTip(0,'Control Systems')
        self.addTab(self.setupPageWidget,'Setup')
        self.setTabToolTip(1,'Settings for the individual elements')
        self.addTab(self.advancedPageWidget,'Advanced')
        self.setTabToolTip(2,'Rig-wide settings')
        self.addTab(self.settingsPageWidget,'Settings')
        self.setTabToolTip(3,'Overall Settings for The Current Rig')
        

class rigSettingsWidget(QWidget):
    def __init__(self):
        super(rigSettingsWidget,self).__init__()
        settings={'Name':"",'Preset':"",'Root Joint':""}


        buttons = {'New':self.__createNew,'Save':self.__save,'Load':self.__load}


    def __save(self):
        pass

    def __load(self):
        pass

    def __createNew(self):
        pass

    def __createButtons(self,data):
        for text,callback in data.items():
            pass


class setupWidget(QWidget):
    def __init__(self):
        super(setupWidget,self).__init__()


class advancedWidget(QWidget):
    def __init__(self):
        super(advancedWidget,self).__init__()


class toolSettingsWidget(QWidget):
    def __init__(self):
        super(toolSettingsWidget,self).__init__()




def run():
    global vRigMainWindow 
    vRigMainWindow = rigMainWindow()

if __name__ == '__main__':
    if externalMode:
        app = QApplication(sys.argv)
        run()
        sys.exit(app.exec_())
    else:
        run()