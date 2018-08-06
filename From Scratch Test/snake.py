# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 18:52:18 2018

@author: joell
"""

import random
import copy
from collections import deque
import operator

import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.lines as lines
#import matplotlib.transforms as mtransforms
#import matplotlib.text as mtext
#from matplotlib.animation import FuncAnimation


class Brain():
    def __init__(self):
        ''' The default parameters of the brain '''
        self.n = 100
        self.path = ""
        self.mutate_rate = 5  # 2 % mutation rate
        self.random_path()
        self.chromo_length = 3

    def random_path(self):
        ''' Generate a random path '''
        self.path = ""
        for i in range(self.n):
            self.path += random.choice(["S", "L", "R"])
        self.path = list(self.path)

    def clone(self):
        ''' copies the path that the brain had'''
        return self.path

    def mix(self, parentB):
        '''
        This mixes parentA (this) and parentB to create a hybrid child
        this is a 50/50 mix for each parent with no mutation
        '''
        half = self.n/2
        result = []
        for i in range(0,self.n, self.chromo_length):
            random_num = random.randint(0,self.n)  # this is assuming that it uses both endpoints (inclusive on both sizes) otherwise it will slightly favor parent A
            if random_num > half:
                chromo = self.path[i:i+self.chromo_length]
                for gene in chromo:
                    result.append(gene)
            else:
                chromo = parentB.brain.path[i:i+self.chromo_length]
                for gene in chromo:
                    result.append(gene)
        return result

    def mutate(self):
        ''' this is the main mutation function '''
        for i in range(self.n):
            rand = random.randint(0, 100)
            if rand < self.mutate_rate:
                # print "mutating something"
                self.path[i] = random.choice(["S", "L", "R"])


class Board():
    def __init__(self):
        self.n = 10
        self.empty = 0
        self.food = 1
        self.wall = 2
        self.head = 3
        self.body = 4
        self.play_space = []
        self.resize_board(self.n)

        self.foods = []
        self.walls = []

    def resize_board(self, size):
        self.play_space = [[self.empty for col in range(size)] for row in range(size)]

    def clear_board(self):
        self.resize_board(self.n)

    def clear_food(self):
        for fud in self.foods:
            self.play_space[fud[0]][fud[1]] = self.empty
        self.foods = []

    def clear_wall(self):
        for wal in self.walls:
            self.play_space[wal[0]][wal[1]] = self.empty
        self.wall = []

    def draw_head(self, row, col):
        #if(row<self.n and row>=0 and col<self.n and col>= 0):
            #print "trying to draw a head at {},{}".format(row, col)
        try:
            self.play_space[row][col] = self.head
        except IndexError as e:
            print "Error : {}".format(e.message)
            print "The numbers I failed on were {},{} and n is {}".format(row,col, self.n)
            raise(e)

    def draw_body(self, row, col):
        self.play_space[row][col] = self.body

    def draw_snake(self, local_snake):
        First = True
        for body in local_snake:
            if(First):
                self.draw_head(body[0], body[1])
                First = False
            else:
                self.draw_body(body[0], body[1])

    def draw_foods(self):
        for fud in self.foods:
            self.play_space[fud[0]][fud[1]] = self.food

    def draw_walls(self):
        for wa in self.walls:
            self.play_space[wa[0]][wa[1]] = self.wall

    def north_of(self, test_row, test_col):
        if(test_row-1 >= 0 and test_row < self.n and test_col >= 0 and test_col < self.n):
            #print "{},{} are the types {},{}".format(test_row-1, test_col, type(test_row-1), type(test_col))
            return self.play_space[test_row-1][ test_col]
        else:
            #print "failed in a north of {},{}".format(test_row-1, test_col)
            return self.wall

    def south_of(self, test_row, test_col):
        if(test_row >= 0 and test_row+1 < self.n and test_col >= 0 and test_col < self.n):
            return self.play_space[test_row+1][test_col]
        else:
            #print "failed in a north of {},{}".format(test_row+1, test_col)
            return self.wall

    def west_of(self, test_row, test_col):
        if(test_row >= 0 and test_row < self.n and test_col-1 >= 0 and test_col < self.n):
            return self.play_space[test_row][test_col - 1]
        else:
            #print "failed in a north of {},{}".format(test_row, test_col-1)
            return self.wall

    def east_of(self, test_row, test_col):
        if(test_row >= 0 and test_row < self.n and test_col >= 0 and test_col + 1 < self.n):
            return self.play_space[test_row][test_col + 1]
        else:
            #print "failed in a north of {},{}".format(test_row, test_col+1)
            return self.wall

    def random_generator(self, percent, fill_with):
        placed = 0
        if fill_with == self.food:
            self.clear_food()
        elif fill_with == self.wall:
            self.clear_wall()
        else:
            raise TypeError("fill_width must be a food or a wall")

        while placed == 0:
            for row in range(self.n):
                for col in range(self.n):
                    if self.play_space[row][col] == self.empty and random.randint(0, 100) <= percent:
                        placed += 1
                        if fill_with == self.food:
                            self.play_space[row][col] = self.food
                            self.foods.append([row, col])
                        elif fill_with == self.wall:
                            self.play_space[row][col] = self.wall
                            self.walls.append([row, col])

    def world_num_to_text(self, num):
        if num == self.empty:
            return " "
        elif num == self.food:
            return "+"
        elif num == self.wall:
            return "#"
        elif num == self.body:
            return "-"
        elif num == self.head:
            return "s"

    def fancy_print_world(self):
        string_to_print = ""
        for row in range(self.n):
            string_to_print += "| "
            for col in range(self.n):
                string_to_print += "{} ".format(self.world_num_to_text(self.play_space[row][col]))
            string_to_print += "|\n"
        return string_to_print


class Snake():
    def __init__(self):
        self.body = []
        self.direction = "North"
        self.alive = 1
        self.turns_alive = 0
        self.food = 0
        self.world = Board()
        self.brain = Brain()
        self.fitness = 0
        self.best_snake = False
        self.died_by = 0
        self.last_food = 0
        self.name = ""

    def get_snake(self):
        return self.body

    def is_dead(self):
        return self.alive != 1

    def is_alive(self):
        return self.alive == 1

    def have_child(self, parentB):
        ''' Only thing that matters is the path, everything else if set later '''
        child = Snake()
        child.brain.path = copy.deepcopy(self.brain.mix(parentB))
        return child

    @classmethod
    def roll(self, array_to_roll):
        ''' see https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.roll.html'''
        x = deque(array_to_roll)
        x.rotate(1)
        return list(x)

    def ate_food(self):
        ''' this is called every time food is eaten '''
        self.food += 1
        self.body.append(self.body[-1])
        self.last_food = self.turns_alive

    def redraw(self):
        self.world.clear_board()
        self.world.draw_snake(self.body)
        self.world.draw_walls()
        self.world.draw_foods()

    def turn_callback(self):
        if(self.alive == 1):
            self.turns_alive += 1
            if(len(self.world.foods) == 0):
                self.alive = 0
                self.died_by = self.world.food

    def calculate_fitness(self):
        ''' main fitness function '''
        turn_fitness = 0
        if(self.died_by == self.world.food):
            # reward eating all the food in the shortest amount of time
            turn_fitness = float(self.brain.n)/self.turns_alive
        elif(self.died_by == self.world.wall):
            # penalize wall hitting, this will be a small number but still want this to increase as time goes on to avoid hitting a wall
            turn_fitness = float(self.turns_alive)/self.brain.n
        if (self.last_food != 0):
            turn_fitness = float(self.food)/self.last_food
        else:
            turn_fitness = 0
        food_fitness = (float(self.food)/(len(self.world.foods)+self.food))*100  # this creates a ratio of food eaten, then scaled up by a number
        self.fitness = food_fitness + turn_fitness
        # take the turn and multiply it by the food, this punishes long living snakes that have no food and rewards snakes that eat food quickly


    def north_safe(self):
        return (self.north_empty() or self.north_food())
    def north_empty(self):
        return self.world.north_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def north_food(self):
        return self.world.north_of(self.body[0][0], self.body[0][1]) == self.world.food

    def south_safe(self):
        return (self.south_empty() or self.south_food())
    def south_empty(self):
        return self.world.south_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def south_food(self):
        return self.world.south_of(self.body[0][0], self.body[0][1]) == self.world.food

    def east_safe(self):
        return (self.east_empty() or self.east_food())
    def east_empty(self):
        return self.world.east_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def east_food(self):
        return self.world.east_of(self.body[0][0], self.body[0][1]) == self.world.food

    def west_safe(self):
        return (self.west_empty() or self.west_food())
    def west_empty(self):
        return self.world.west_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def west_food(self):
        return self.world.west_of(self.body[0][0], self.body[0][1]) == self.world.food

    def a_valid_path(self, row, col):
        return (self.world.north_of(row, col) < 2 or
                self.world.south_of(row, col) < 2 or
                self.world.east_of(row, col) < 2 or
                self.world.west_of(row, col) < 2)

    def move_north(self):
        self.body = self.roll(self.body)
        self.body[0] = [self.body[1][0]-1, self.body[1][1]]
        self.redraw()

    def move_south(self):
        self.body = self.roll(self.body)
        self.body[0] = [self.body[1][0]+1, self.body[1][1]]
        self.redraw()

    def move_east(self):
        self.body = self.roll(self.body)
        self.body[0] = [self.body[1][0], self.body[1][1]+1]
        self.redraw()

    def move_west(self):
        self.body = self.roll(self.body)
        self.body[0] = [self.body[1][0], self.body[1][1]-1]
        self.redraw()

    def go_north(self):
        ''' make the snake go absolute noth '''
        if(self.north_safe()):
            self.direction = "North"
            if (self.north_food()):
                if([self.body[0][0]-1, self.body[0][1]] in self.world.foods):
                    self.world.foods.remove([self.body[0][0]-1, self.body[0][1]])
                self.ate_food()
            self.move_north()
        else:
            self.alive = 0
            self.died_by = self.world.wall

    def go_east(self):
        ''' make the snake go absolute east '''
        if(self.east_safe()):
            self.direction = "East"
            if (self.east_food()):
                self.ate_food()
                if ([self.body[0][0], self.body[0][1]+1] in self.world.foods):
                    self.world.foods.remove([self.body[0][0], self.body[0][1]+1])
            self.move_east()
        else:
            self.alive = 0
            self.died_by = self.world.wall

    def go_south(self):
        ''' make the snake go absolute south '''
        if(self.south_safe()):
            self.direction = "South"
            if (self.south_food()):
                self.ate_food()
                if ([self.body[0][0]+1, self.body[0][1]] in self.world.foods):
                    self.world.foods.remove([self.body[0][0]+1, self.body[0][1]])
            self.move_south()
        else:
            self.alive = 0
            self.died_by = self.world.wall

    def go_west(self):
        ''' make the snake go absolute west '''
        if(self.west_safe()):
            self.direction = "West"
            if (self.west_food()):
                self.ate_food()
                if ([self.body[0][0], self.body[0][1]-1] in self.world.foods):
                    self.world.foods.remove([self.body[0][0], self.body[0][1]-1])
            self.move_west()
        else:
            self.alive = 0
            self.died_by = self.world.wall

    def go_straight(self):
        ''' make the snake go straight '''
        if(self.direction == "North"):
            self.go_north()
        elif(self.direction == "East"):
            self.go_east()
        elif(self.direction == "South"):
            self.go_south()
        elif(self.direction == "West"):
            self.go_west()
        self.turn_callback()

    def go_left(self):
        ''' make the snake turn left '''
        if(self.direction == "North"):
            self.go_west()
        elif(self.direction == "East"):
            self.go_north()
        elif(self.direction == "South"):
            self.go_east()
        elif(self.direction == "West"):
            self.go_south()
        self.turn_callback()

    def go_right(self):
        ''' make the snake turn right '''
        if(self.direction == "North"):
            self.go_east()
        elif(self.direction == "East"):
            self.go_south()
        elif(self.direction == "South"):
            self.go_west()
        elif(self.direction == "West"):
            self.go_north()
        self.turn_callback()

    def update(self):
        ''' if the snake is alive, run one turn '''
        if(self.alive == 1):
            self.run_one()

        if(self.turns_alive == self.brain.n):
            self.alive = 0
            self.died_by = self.world.wall
            # this means that we have a snake that lived its entire life
            # just used for makeing sure everything ends on time

    def run_one(self):
        ''' run one turn '''
        current_path = self.brain.path[self.turns_alive]
        self.run_path(current_path)

    def run_path(self, test_string):
        ''' move the snake along a specic path '''
        for i in test_string.upper():
            if(i == "S"):
                self.go_straight()
            elif(i == "R"):
                self.go_right()
            elif(i == "L"):
                self.go_left()
            else:
                print "invalid path of {}, should be L R or S".format(i)

    def generate_random_body(self):
        ''' generate a random snake, this is only done on a empty world '''
        length = 2  # this is the length of the random generated snake
        row = random.randint(0, self.world.n - 1)
        col = random.randint(0, self.world.n - 1)
        self.body.append([row, col])
        length -= 1
        for i in range(length):
            if self.a_valid_path(row, col):
                if(self.north_safe()):
                    self.ate_food()
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0]-1, self.body[1][1]]
                elif(self.south_safe()):
                    self.ate_food()
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0]+1, self.body[1][1]]
                elif(self.east_safe()):
                    self.ate_food()
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0], self.body[1][1]+1]
                elif(self.south_safe()):
                    self.ate_food()
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0], self.body[1][1]-1]


class Population():
    def __init__(self, pop_num):
        self.n = pop_num
        self.snakes = []
        self.babies = []
        for i in range(self.n):
            self.snakes.append(Snake())
            self.snakes[i].name = "SNAKE {}, GEN {}".format(i,0)

        self.generation = 0
        self.max_snake = Snake()
        self.max_fitness = 0
        self.best_samples = int(self.n*0.1)  # take 10% from the best everything else is random
        self.average_fitness = 0
        self.sorted_population = {}

    def update(self):
        for i in range(self.n):
            self.snakes[i].update()

    def calculate_fitness(self):
        for i in range(self.n):
            self.snakes[i].calculate_fitness()

    def all_snakes_dead(self):
        for i in range(self.n):
            if(not self.snakes[i].is_dead()):
                return False
        return True

    def set_all_snake_bodies(self, body, dire):
        for i in range(self.n):
            self.snakes[i].body = copy.deepcopy(body)
            self.snakes[i].direction = copy.deepcopy(dire)

    def set_all_snake_world(self, world, food, wall):
        for i in range(self.n):
            self.snakes[i].world.play_space = copy.deepcopy(world)
            self.snakes[i].world.foods = copy.deepcopy(food)
            self.snakes[i].world.walls = copy.deepcopy(wall)

    def best_snake(self):
        local_max = 0
        for i in range(self.n):
            if(self.snakes[i].fitness >= self.max_fitness):
                self.max_fitness = self.snakes[i].fitness
                self.max_snake = copy.deepcopy(self.snakes[i])
                self.snakes[i].best_snake = True
            local_max = max(self.snakes[i].fitness, local_max)
        return local_max

    def set_all_properties(self, master_snake):
        self.set_all_snake_bodies(copy.deepcopy(master_snake.body),copy.deepcopy(master_snake.direction))
        self.set_all_snake_world(copy.deepcopy(master_snake.world.play_space),
                                 copy.deepcopy(master_snake.world.foods),
                                 copy.deepcopy(master_snake.world.walls))

    def natural_selection(self):
        self.babies = []
        for i in range(self.n):
            self.babies.append(Snake())
        self.sorted_population = {}
        self.rank_parents()

        for i in range(self.n):
            parentA = self.select_parent(i)
            parentB = self.select_parent(i)
            self.babies[i] = copy.deepcopy(parentA.have_child(parentB))
        self.babies[-1].brain.path = self.max_snake.brain.path #this ensures that the best always makes it
        self.snakes = copy.deepcopy(self.babies)
        self.generation += 1

    def mutate_babies(self):
        for i in range(self.n):
            self.snakes[i].brain.mutate()
            self.snakes[i].name = "SNAKE {}, GEN {}".format(i,self.generation)

    def rank_parents(self):
        self.sorted_population = {}
        for i in range(self.n):
            self.sorted_population[i] = self.snakes[i].fitness
        self.sorted_population = sorted(self.sorted_population.items(), key=operator.itemgetter(1), reverse = False)
        # the operator.itemgetter(1) just says that it is looking at the second object in the item as the item (key, fitness)

    def select_parent(self, i):
        '''
        picks from the best X% and all others are from a random location
        It IS possbile to randomly choose to breed with a 'good' snake
        '''
        if i < self.best_samples:
            random_good_parent = random.randint(0, self.best_samples)
            return self.snakes[self.sorted_population[random_good_parent][0]]
        random_point = random.randint(0, int(self.get_fitness_sum()))
        result = 0
        for i in range(self.n):
            result += self.snakes[i].fitness
            if(result >= random_point):
                return self.snakes[i]

    def get_fitness_sum(self):
        result = 0
        for i in range(self.n):
            result += self.snakes[i].fitness
        self.average_fitness = float(result)/self.n
        return result

def display_best_snake_moving(snek, run_once = False):
    ''' snek is a snake object that was the orignal with the path from the best '''
    plt.subplot(212)
    while snek.is_alive():
        if not run_once:
            snek.run_one()
        plt.cla()
        plt.xlim(-1, 10)
        plt.ylim(10, -1)
        xdata, ydata = [], []

        for bod in snek.body:
            # bod is [row, col] which translates to [y,x]
            xdata.append(bod[1])
            ydata.append(bod[0])
        # plot the body and the head
        plt.plot(xdata, ydata, linewidth=5.0)
        plt.scatter(xdata[0],ydata[0], s=60, c='cyan')

        for fud in snek.world.foods:
            # fud is [row, col] which translates to [y,x]
            plt.scatter(fud[1], fud[0], s=60, c='red')

        for wal in snek.world.walls:
            # wal is [row, col] which translates to [y,x]
            plt.scatter(wal[1], wal[0], s=60, c='black')

        plt.plot([0, 0, 9, 9, 0], [0, 9, 9, 0, 0], c='black')

        plt.xticks(range(-1, 11, 1))
        plt.yticks(range(-1, 11, 1))
        plt.grid(which = 'both')
        plt.title("Turn: {}, Food: {}, Food Left: {}".format(snek.turns_alive, snek.food, len(snek.world.foods)))
        plt.show()
        plt.pause(0.2)
        if run_once:
            break





if(__name__ == "__main__"):
    snake1 = Snake()
    snake1.body.append([5,5])
    snake1.body.append([5,4])
    #snake1.generate_random_body()
    snake1.world.draw_snake(snake1.body)
    snake1.world.foods = [[2, 6], [2, 1], [7, 3], [7, 5], [2, 8]]
    snake1.redraw()
    #snake1.world.random_generator(10, snake1.world.food)
    #snake1.world.random_generator(1, snake1.world.wall)
    print snake1.world.fancy_print_world()
    fitnesses = []
    local_fitness = []
    rolling_average = []
    bodies = []

    population_limit = 100
    population_generations = 200


    test = Population(population_limit)
    test.set_all_properties(snake1)

    display_best_snake_moving(snake1, True)

    plt.subplot(211)
    title = ''
    while(test.generation < population_generations):
        if(not test.all_snakes_dead()):
            test.update()
        else:
            test.calculate_fitness()
            local_fitness.append(test.best_snake())

            rolling_average.append(test.average_fitness)

            test.natural_selection()
            test.set_all_properties(snake1)
            test.mutate_babies()
            fitnesses.append(test.max_snake.fitness)

            #if(test.generation % 10 == 0):
            title =  "population: {}, fitness: {:.2f}, turns: {}, food: {}, food left: {}, path size: {}, mutation rate: {}, gene: {}".format(
                                                                population_limit,
                                                                test.max_snake.fitness,
                                                                test.max_snake.last_food,
                                                                test.max_snake.food,
                                                                len(test.max_snake.world.foods),
                                                                test.max_snake.brain.n,
                                                                test.max_snake.brain.mutate_rate,
                                                                test.max_snake.brain.chromo_length)
            print title

            plt.cla()
            #plt.plot(fitnesses)
            plt.plot(local_fitness)
            plt.plot(rolling_average)
            plt.title(title)
            plt.legend(['Best Snake per generation', 'Average Snake per generation'], loc=2 )
            plt.show()
            plt.pause(0.000000001)

    print "done"
    print snake1.world.fancy_print_world()

    snake1.brain.path = test.max_snake.brain.path
    display_best_snake_moving(snake1)

