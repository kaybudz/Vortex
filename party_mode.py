# creating UI for practice animations
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QColor, QIcon, QPixmap, QFont
from PyQt5.QtCore import QPropertyAnimation
from io import BytesIO

class party():
    def __init__(self):
        super().__init__()


# have ufo come in from top corner of screen down to bottm center and grow as it comes down
# once it hits the ground have a blast of smoke and then have an alien appear
# have an asronaut come and greet the alien
# have the alien abduct the astronaut then fly off