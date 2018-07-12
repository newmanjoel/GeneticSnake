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
saved_play_space = np.zeros(1, order='F')

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

class PathSignals(QObject):
    path = pyqtSignal(str)
    get_rank = pyqtSignal(str)

class PathScreen(QtGui.QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        uic.loadUi('path_editor.ui', self)
        self.signals = PathSignals()
        self.pushButton.clicked.connect(self.run_callback)
        self.pushButton_2.clicked.connect(self.generate_random_path)
        self.pushButton_3.clicked.connect(self.clear_graph)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.auto_run)
        self.timer.start(500)
        self.slider.valueChanged.connect(self.slider_changed)
        #.sortItems (self, int column, Qt.SortOrder order = Qt.AscendingOrder)

    def slider_changed(self):
        self.timer.stop()
        self.timer.start(self.slider.value())

    def clear_graph(self):
        self.tableWidget.clearContents()
        form.algorithm.reset()
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)

    def auto_run(self):
        if(self.checkBox.isChecked()):
            self.run_callback()

    def run_callback(self):
        self.signals.path.emit("")

    def generate_random_path(self):
        for j in range(self.spinBox_2.value()):
            empty_string = ""
            for i in range(self.spinBox.value()):
                empty_string += random.choice(["S", "R", "L"])
            self.add_path_without_rank(empty_string)
        self.itterate()

    def itterate(self):
        for i in range(self.spinBox_3.value()):
            rows = self.tableWidget.rowCount()
            if(rows>2):
                string_a = self.tableWidget.item(random.randint(0,rows-1), 2).text()
                string_b = self.tableWidget.item(random.randint(0,rows-1), 2).text()

                new_path = form.algorithm.create_new_path(string_a, string_b)
                self.add_path_without_rank(new_path)
                print "-----"

    def add_path_with_rank(self, path, rank):
        current_row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(current_row)

        self.tableWidget.setItem(current_row, 0, QtGui.QTableWidgetItem("{}".fornat(rank)))
        self.tableWidget.setItem(current_row, 2, QtGui.QTableWidgetItem("{}".format(path)))
        self.tableWidget.setItem(current_row, 1, QtGui.QTableWidgetItem("{}".format(0)))
        self.tableWidget.sortItems(0, order=Qt.DescendingOrder)


    def add_path_without_rank(self, path):
        current_row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(current_row)

        self.tableWidget.setItem(current_row, 0, QtGui.QTableWidgetItem("{}".format(form.find_rank(path))))
        self.tableWidget.setItem(current_row, 2, QtGui.QTableWidgetItem("{}".format(path)))
        self.tableWidget.setItem(current_row, 1, QtGui.QTableWidgetItem("{}".format(0)))
        self.tableWidget.sortItems(0, order=Qt.DescendingOrder)


class ManualSignals(QObject):
    straight = pyqtSignal(str)
    left = pyqtSignal(str)
    right = pyqtSignal(str)


class ManualScreen(QtGui.QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        uic.loadUi('manual_move_screen.ui', self)
        self.signals = ManualSignals()
        self.pushButton.clicked.connect(self.straight_callback)
        self.pushButton_3.clicked.connect(self.right_callback)
        self.pushButton_4.clicked.connect(self.left_callback)

    def straight_callback(self):
        self.signals.straight.emit("S")

    def right_callback(self):
        self.signals.right.emit("R")

    def left_callback(self):
        self.signals.left.emit("L")

class genetic_algorithm():
    def __init__(self):
        self.best_path = ""
        self.second_best_path = ""
        self.best_fitness = 0
        self.second_best_fitness = 0
        self.random_percent = 2 # 2% chance of mutation
        self.parent_a_percent = 50 - self.random_percent/2
        self.parent_b_percent = 100 - self.parent_a_percent - self.random_percent/2
        self.choices = ["S", "L", "R"]
        self.last_day = 0

    def reset(self):
        self.best_fitness = -1
        self.second_best_fitness = -1
        self.best_path =""
        self.second_best_path = ""
        self.last_day = form.turns_alive

    def fitness(self, path, days, food):
        local_day = days - self.last_day
        try:
            local_fitness = float(food+local_day*3)/float(local_day)
        except:
            local_fitness = 0
        print "days:{}, food:{}, fitness:{}".format(local_day, food, local_fitness)
        if local_fitness > self.best_fitness:
            self.second_best_fitness = self.best_fitness
            self.best_fitness = local_fitness
            self.second_best_path = self.best_path
            self.best_path = path
        elif local_fitness > self.second_best_fitness:
            self.second_best_fitness = local_fitness
            self.second_best_path = path
        return local_fitness

    def create_new_path(self, string_a="", string_b=""):
        if(string_a == "" ):
            string_a = self.best_path
            string_b = self.second_best_path
        new_path = ""
        # using uniform crossover
        for i in range(0, len(string_a)):
            chrome_a = string_a[i]
            chrome_b = string_b[i]
            total_choices = np.array(list([chrome_a]*self.parent_a_percent))
            total_choices = np.append(total_choices, list([chrome_b]*self.parent_b_percent))
            total_choices = np.append(total_choices, list(random.sample(self.choices, self.random_percent)))
            one_letter= "{}".format(random.choice(total_choices))
            new_path += one_letter
        return new_path

snake_body_g = []
class MainScreen(QtGui.QMainWindow):
    def __init__(self):
        global play_space
        '''
        This is the main screen that the user interacts with.

        '''
        super(self.__class__, self).__init__()
        uic.loadUi('test.ui', self)

        self.manual_screen = ManualScreen()
        self.manual_screen.signals.straight.connect(self.go_straight)
        self.manual_screen.signals.left.connect(self.go_left)
        self.manual_screen.signals.right.connect(self.go_right)

        self.path_screen = PathScreen()
        self.path_screen.signals.path.connect(self.one_turn)

        self.tableWidget.cellDoubleClicked.connect(self.cellClicked_callback)
        self.pushButton.clicked.connect(self.setSize_callback)
        self.pushButton_4.clicked.connect(self.randomWall_callback)
        self.pushButton_3.clicked.connect(self.randomFood_callback)
        self.snake_button.clicked.connect(self.randomSnake_callback)
        self.n = 0
        self.snake_body = []
        self.snake_direction = "North"
        self.saved_snake_body = []
        self.saved_snake_direction = "North"

        self.turns_alive = 0
        self.alive = 1
        self.food_amount = 0
        self.saved_turns_alive = 0
        self.saved_alive = 1
        self.saved_food_amount = 0

        self.test_mode = False


        self.algorithm = genetic_algorithm()
        #self.algorithm.best_path = "SSSSSSSSSS"
        #self.algorithm.second_best_path = "LLLLLLLLLL"

        #self.path_screen.add_path_with_rank(self.algorithm.best_path, 0.1)
        #self.path_screen.add_path_with_rank(self.algorithm.second_best_path, 0.05)
        #self.path_screen.add_path_with_rank(self.algorithm.create_new_path(), 0.01)

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')

        manual_action = QtGui.QAction("&Manual Move", self)
        manual_action.setStatusTip("Manually move snake")
        manual_action.triggered.connect(self.manual_move)

        path_action = QtGui.QAction("&Path Plan", self)
        path_action.setStatusTip("Manually plan the moves of the snake")
        path_action.triggered.connect(self.path_move)

        file_menu.addAction(manual_action)
        file_menu.addAction(path_action)

    def one_turn(self, empty):
        #print "the snake is alive {} and the saved is {}".format(self.alive == 1, self.saved_alive == 1)
        self.reset_board()
        self.run_one(self.algorithm.best_path)
        self.path_screen.clear_graph()
        self.algorithm.reset()
        self.path_screen.generate_random_path()

    def find_rank(self, path):
        self.test_mode = True
        self.save_board()
        rank = self.run_path(path)
        self.reset_board()
        self.test_mode = False
        return rank

    def reset_board(self):
        global play_space, saved_play_space
        play_space = np.copy(saved_play_space)
        self.alive = self.saved_alive
        self.food_amount = self.saved_food_amount
        self.turns_alive = self.saved_turns_alive
        self.snake_body = np.copy(self.saved_snake_body)
        self.snake_direction = self.saved_snake_direction
        self.erase_snake()
        self.draw_board()
        global snake_body_g
        snake_body_g = np.copy(self.snake_body)
        self.turn_callback(self.turns_alive)

    def save_board(self):
        global play_space, saved_play_space
        saved_play_space = np.copy(play_space)
        self.saved_alive = self.alive
        self.saved_food_amount = self.food_amount
        self.saved_turns_alive = self.turns_alive
        self.saved_snake_body = np.copy(self.snake_body)
        self.saved_snake_direction = self.snake_direction

    def path_move(self):
        self.path_screen.show()

    def manual_move(self):
        self.manual_screen.show()

    def food_callback(self):
        self.food_amount += 1
        self.label_5.setText("Food Eaten:{}".format(self.food_amount))
        food_left = 0
        while food_left == 0:
            x = play_space == food_num
            food_left = np.sum(x)
            if not self.test_mode:
                print "there is {} food left".format(food_left)

            if food_left == 1 :
                self.randomFood_callback()
                print "trying again"
            if self.food_spinner.value() == 0:
                return

    def turn_callback(self, turns_set = -1):
        if turns_set == -1:
            self.turns_alive += self.alive
        else:
            self.turns_alive = turns_set
        self.label_6.setText("Alive:{}, Turns:{}".format(self.alive == 1, self.turns_alive))

    def run_one(self, test_path):
        if len(test_path) == 0:
            test_path = random.choice(["S", "R", "L" ])
        self.run_path(test_path[0])

    def run_path(self, test_string):
        for i in test_string.upper():
            if(i == "S"):
                self.go_straight()
            elif(i == "R"):
                self.go_right()
            elif(i == "L"):
                self.go_left()
            else:
                print "invalid path of {}, should be L R or S".format(i)
        return self.algorithm.fitness(test_string, self.turns_alive, self.food_amount)

    def draw_snake(self):
        for i in self.snake_body:
            self.tableWidget.setItem(i[0],i[1] , QtGui.QTableWidgetItem(body_tex))
            play_space[i[0], i[1]] = body_num

        self.tableWidget.setItem(self.snake_body[0][0], self.snake_body[0][1], QtGui.QTableWidgetItem(head_tex))
        play_space[self.snake_body[0][0], self.snake_body[0][1]] = head_num

    def erase_snake(self):
        for i in self.snake_body:
            self.tableWidget.setItem(i[0],i[1] , QtGui.QTableWidgetItem(empty_tex))
            play_space[i[0], i[1]] = empty_num

    def draw_board(self):
        for row in range(self.n):
            for col in range(self.n):
                if (int(play_space[row, col]) == empty_num ):
                    self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(empty_tex))
                elif(int(play_space[row, col]) == food_num ):
                    self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(food_tex))
                elif(int(play_space[row, col]) == wall_num ):
                    self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(wall_tex))
                elif(int(play_space[row, col]) == body_num ):
                    self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(body_tex))
                elif(int(play_space[row, col]) == head_num ):
                    self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(head_tex))
        self.draw_snake()

    def north_safe(self):
        return (self.north_empty() or self.north_food())
    def north_empty(self):
        return play_space[self.snake_body[0][0]-1, self.snake_body[0][1]] == empty_num
    def north_food(self):
        return play_space[self.snake_body[0][0]-1, self.snake_body[0][1]] == food_num
    def north_wall(self):
        return (play_space[self.snake_body[0][0]-1, self.snake_body[0][1]] == wall_num or
                play_space[self.snake_body[0][0]-1, self.snake_body[0][1]] == body_num or
                play_space[self.snake_body[0][0]-1, self.snake_body[0][1]] == head_num )

    def south_safe(self):
        return (self.south_empty() or self.south_food())
    def south_empty(self):
        return play_space[self.snake_body[0][0]+1, self.snake_body[0][1]] == empty_num
    def south_food(self):
        return play_space[self.snake_body[0][0]+1, self.snake_body[0][1]] == food_num
    def south_wall(self):
        return (play_space[self.snake_body[0][0]+1, self.snake_body[0][1]] == wall_num or
                play_space[self.snake_body[0][0]+1, self.snake_body[0][1]] == body_num or
                play_space[self.snake_body[0][0]+1, self.snake_body[0][1]] == head_num )

    def east_safe(self):
        return (self.east_empty() or self.east_food())
    def east_empty(self):
        return play_space[self.snake_body[0][0], self.snake_body[0][1]+1] == empty_num
    def east_food(self):
        return play_space[self.snake_body[0][0], self.snake_body[0][1]+1] == food_num
    def east_wall(self):
        return (play_space[self.snake_body[0][0], self.snake_body[0][1]+1] == wall_num or
                play_space[self.snake_body[0][0], self.snake_body[0][1]+1] == body_num or
                play_space[self.snake_body[0][0], self.snake_body[0][1]+1] == head_num )

    def west_safe(self):
        return (self.west_empty() or self.west_food())
    def west_empty(self):
        return play_space[self.snake_body[0][0], self.snake_body[0][1]-1] == empty_num
    def west_food(self):
        return play_space[self.snake_body[0][0], self.snake_body[0][1]-1] == food_num
    def west_wall(self):
        return (play_space[self.snake_body[0][0], self.snake_body[0][1]-1] == wall_num or
                play_space[self.snake_body[0][0], self.snake_body[0][1]-1] == body_num or
                play_space[self.snake_body[0][0], self.snake_body[0][1]-1] == head_num )

    def go_north(self):
        #print "trying to go north"
        if(self.alive == 0):
            return
        if(self.snake_body[0][0]-1 < 0):
            if not self.test_mode:
                print "collision with north wall"
            self.alive = 0
        elif(self.north_safe()):
            self.snake_direction = "North"
            self.erase_snake()
            if (self.north_food()):
                self.food_callback()
                self.snake_body = np.append(self.snake_body, [self.snake_body[-1]], axis=0)
            self.snake_body = np.roll(self.snake_body,1,0)
            self.snake_body[0] = [self.snake_body[1][0]-1, self.snake_body[1][1]]
            self.draw_snake()
        else:
            if not self.test_mode:
                print "collision with wall at {},{}".format(self.snake_body[0][0]-1, self.snake_body[0][1])
            self.alive = 0

    def go_east(self):
        #print "trying to go east"
        if(self.alive == 0):
                return
        if(self.snake_body[0][1]+1 >= self.n ):
            if not self.test_mode:
                print "collision with east wall"
            self.alive = 0
        elif(self.east_safe()):
            self.snake_direction = "East"
            self.erase_snake()
            if (self.east_food()):
                self.food_callback()
                self.snake_body = np.append(self.snake_body, [self.snake_body[-1]], axis=0)
            self.snake_body = np.roll(self.snake_body,1,0)
            self.snake_body[0] = [self.snake_body[1][0], self.snake_body[1][1]+1]

            self.draw_snake()
        else:
            #print "collision with wall"
            if not self.test_mode:
                print "collision with wall at {},{}".format(self.snake_body[0][0], self.snake_body[0][1]+1)
            self.alive = 0

    def go_south(self):
        #print "trying to go south"
        if(self.alive == 0):
            return
        if(self.snake_body[0][0]+1 >= self.n ):
            if not self.test_mode:
                print "collision with south wall"
            self.alive = 0
        elif(self.south_safe()):
            self.snake_direction = "South"
            self.erase_snake()
            if (self.south_food()):
                self.food_callback()
                self.snake_body = np.append(self.snake_body, [self.snake_body[-1]], axis=0)
            self.snake_body = np.roll(self.snake_body,1,0)
            self.snake_body[0] = [self.snake_body[1][0]+1 , self.snake_body[1][1]]
            self.draw_snake()
        else:
            #print "collision with wall"
            if not self.test_mode:
                print "collision with wall at {},{}".format(self.snake_body[0][0]+1, self.snake_body[0][1])
            self.alive = 0

    def go_west(self):
        #print "trying to go west"
        if(self.alive == 0):
            return
        if(self.snake_body[0][1]-1 < 0):
            if not self.test_mode:
                print "collision with west wall"
            self.alive = 0
        elif(self.west_safe()):
            self.snake_direction = "West"
            self.erase_snake()
            if (self.west_food()):
                self.food_callback()
                self.snake_body = np.append(self.snake_body, [self.snake_body[-1]], axis=0)
            self.snake_body = np.roll(self.snake_body,1,0)
            self.snake_body[0] = [self.snake_body[1][0] , self.snake_body[1][1]-1]
            self.draw_snake()
        else:
            #print "collision with wall"
            if not self.test_mode:
                print "collision with wall at {},{}".format(self.snake_body[0][0], self.snake_body[0][1]-1)
            self.alive = 0

    def go_straight(self):
        #print "trying to go straight"
        if(self.snake_direction == "North"):
            self.go_north()
        elif(self.snake_direction == "East"):
            self.go_east()
        elif(self.snake_direction == "South"):
            self.go_south()
        elif(self.snake_direction == "West"):
            self.go_west()
        self.turn_callback()

    def go_left(self):
        #print "trying to go left"
        if(self.snake_direction == "North"):
            self.go_west()
        elif(self.snake_direction == "East"):
            self.go_north()
        elif(self.snake_direction == "South"):
            self.go_east()
        elif(self.snake_direction == "West"):
            self.go_south()
        self.turn_callback()

    def go_right(self):
        #print "trying to go right"
        if(self.snake_direction == "North"):
            self.go_east()
        elif(self.snake_direction == "East"):
            self.go_south()
        elif(self.snake_direction == "South"):
            self.go_west()
        elif(self.snake_direction == "West"):
            self.go_north()
        self.turn_callback()

    def setSize_callback(self):
        #print "pressed the button"
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
            #print "food at at row:{} col{}".format(row,col)
            play_space[row, col] = food_num
        elif(self.tableWidget.item(row, col) != None and self.tableWidget.item(row, col).text() == food_tex):
            self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(empty_tex))
            play_space[row, col] = empty_num
        else:
            self.tableWidget.setItem(row, col, QtGui.QTableWidgetItem(wall_tex))
            play_space[row, col] = wall_num
        #print play_space

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
        self.save_board()

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
        self.save_board()

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
                    play_space[cell[0],cell[1]] = body_num
                    random_head_row = cell[0]
                    random_head_col = cell[1]
                    self.snake_body.append(cell)
                    break
                else:
                    pass
        print self.snake_body
        self.alive = 1
        self.turns_alive = -1
        self.food_amount = 0
        self.turn_callback()
        self.save_board()



    def closeEvent(self, event):
        print "close event"
        self.close()
        event.accept()
        sys.exit(0)





app = QtGui.QApplication(sys.argv)
form = MainScreen()

form.show()
app.exec_()
