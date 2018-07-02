# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 17:55:33 2018

@author: joell
"""

from termcolor import colored


from PyQt4 import QtCore, QtGui, uic  # Import the PyQt4 module we'll need
from PyQt4.QtCore import *
import random
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np

play_space = np.zeros(1, order='F')

empty_num = 0
empty_tex = " "

wall_num = 1
wall_tex = "X"

food_num = 2
food_tex = "F"

head_num = 3
head_tex = "H"

body_num = 4
body_tex = "B"

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

class MainScreen(QtGui.QMainWindow):
    def __init__(self):
        global play_space
        '''
        This is the main screen that the user interacts with.

        '''
        super(self.__class__, self).__init__()
        uic.loadUi('test.ui', self)
        self.tableWidget.cellDoubleClicked.connect(self.cellClicked_callback)
        self.pushButton.clicked.connect(self.setSize_callback)
        self.pushButton_4.clicked.connect(self.randomWall_callback)
        self.pushButton_3.clicked.connect(self.randomFood_callback)
        self.snake_button.clicked.connect(self.randomSnake_callback)
        self.n = 0
        self.snake_body = []
        self.snake_direction = "North"

    def setSize_callback(self):
        print "pressed the button"
        self.n = self.spinBox.value()
        self.tableWidget.setRowCount(self.n)
        self.tableWidget.setColumnCount(self.n)
        play_space.resize((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                local_text = self.tableWidget.item(i, j)
                if(local_text is None):
                    local_text = empty_tex
                else:
                    local_text = local_text.text()
                if(local_text == wall_tex):
                    play_space[i, j] = wall_num
                elif(local_text == food_tex):
                    play_space[i, j] = food_num
                elif(local_text == empty_tex):
                    play_space[i, j] = empty_num

    def cellClicked_callback(self, row, col):
        if(self.tableWidget.item(row, col) != None and self.tableWidget.item(row, col).text() == wall_tex):
            self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(food_tex))
            play_space[row, col] = food_num
        elif(self.tableWidget.item(row, col) != None and self.tableWidget.item(row, col).text() == food_tex):
            self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(empty_tex))
            play_space[row, col] = empty_num
        else:
            self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(wall_tex))
            play_space[row, col] = wall_num
        print play_space

    def randomWall_callback(self):
        wall_n = self.wall_spinner.value()*100
        for i in range(self.n):
            for j in range(self.n):
                if(self.tableWidget.item(i, j) is None):
                    self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(empty_tex))
                if(self.tableWidget.item(i, j).text() == wall_tex):
                    self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(empty_tex))
                    play_space[i, j] = empty_num
                if(random.randrange(0,101,1) < wall_n and self.tableWidget.item(i, j).text() == empty_tex):
                     self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(wall_tex))
                     play_space[i, j] = wall_num

    def randomFood_callback(self):
        food_n = self.food_spinner.value()*100
        for i in range(self.n):
            for j in range(self.n):
                if(self.tableWidget.item(i, j) is None):
                    self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(empty_tex))
                if(self.tableWidget.item(i, j).text() == food_tex):
                    self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(empty_tex))
                    play_space[i, j] = empty_num
                if(random.randrange(0,101,1) < food_n and self.tableWidget.item(i, j).text() == empty_tex):
                     self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(food_tex))
                     play_space[i, j] = food_num

    def isEmpty(self, row, col):
        return self.tableWidget.item(row, col) is None or self.tableWidget.item(row, col).text() == empty_tex

    def getDirection(self, random_head_row, random_head_col, direction):
        row = -1
        col = -1
        #direction  = direction[0]
        if(direction == "North"):
            row = random_head_row-1
            col = random_head_col
        elif(direction == "South"):
            row = random_head_row+1
            col = random_head_col
        elif(direction == "East"):
            row = random_head_row
            col = random_head_col+1
        elif(direction == "West"):
            row = random_head_row
            col = random_head_col-1
        else:
            print "I GOT A WEIRD DIRECTION which is {}".format(direction)
            print "South : {}, North: {}, East: {}, West : {}".format(  direction == "South",
                                                                        direction == "North",
                                                                        direction == "East",
                                                                        direction == "West")
            sys.exit(1)
        if(row>0 and col > 0 and row < self.n and col < self.n and self.isEmpty(row,col)):
            return [row, col]
        return None

    def getOppositeDirection(self, direction):
        if(direction == "North"):
            return "South"
        elif(direction == "South"):
            return "North"
        elif(direction == "East"):
            return "West"
        elif(direction == "West"):
            return "East"


    def randomSnake_callback(self):
        snake_n = self.Snake_spinner.value()
        self.snake_body = []
        for i in range(self.n):
            for j in range(self.n):
                if(self.tableWidget.item(i, j) is None):
                    self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(empty_tex))
                if(self.tableWidget.item(i, j).text() == head_tex or self.tableWidget.item(i, j).text() == body_tex):
                    self.tableWidget.setItem(i, j, QtGui.QTableWidgetItem(empty_tex))
                    play_space[i, j] = empty_num

        while (True):
            random_head_row = random.randrange(0, self.n,1)
            random_head_col = random.randrange(0, self.n,1)
            local_item = self.tableWidget.item(random_head_row, random_head_col)
            if(local_item is None or local_item.text() == empty_tex):
                self.tableWidget.setItem(random_head_row, random_head_col, QtGui.QTableWidgetItem(head_tex))
                play_space[random_head_row, random_head_col] = head_num
                self.snake_body = [[random_head_row, random_head_col]]
                break

        direction = ['North', 'South', 'East', 'West']
        first_body = True
        for i in range(self.Snake_spinner.value()):
            cell = None
            random.shuffle(direction)
            for dire in  direction:
                 # add body peices around the head
                cell = self.getDirection(random_head_row,random_head_col, dire)
                if(cell is not None):
                    if first_body:
                        self.snake_direction = self.getOppositeDirection(dire)
                        print "looking in {}".format(self.snake_direction)
                        first_body = False
                    self.tableWidget.setItem(cell[0], cell[1], QtGui.QTableWidgetItem(body_tex))
                    random_head_row = cell[0]
                    random_head_col = cell[1]
                    self.snake_body.append(cell)
                    break
                else:
                    pass
        print self.snake_body


    def closeEvent(self, event):
        self.close()
        event.accept()
        sys.exit(0)





app = QtGui.QApplication(sys.argv)
form = MainScreen()

form.show()
app.exec_()
