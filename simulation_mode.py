# simulation mode
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton

class sim():
    def __init__(self):
        super().__init__()
        
        self.sim_enable.clicked.connect(self.sime)
        def sime():
            sim_enable.setBackground('2')

    
