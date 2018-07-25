# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 18:52:18 2018

@author: joell
"""

import random
import copy
from collections import deque

class WorldError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BodySizeToSmall(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SnakeDeath(Exception):
    def __init__(self, text, alive, food, path):
        self.text = text
        self.alive = alive
        self.food = food
        self.path = path

    def __str__(self):
        return "Snake {}, eaten: {}, alive: {} turns, path: {}".format(self.text, self.food, self.alive, self.path)


class Brain():
    def __init__(self):
        self.n = 50
        self.path = ""
        self.mutate_rate = 1  # 1 % mutation rate
        self.random_path()

    def random_path(self):
        self.path = ""
        for i in range(self.n):
            self.path += random.choice(["S", "L", "R"])
        self.path = list(self.path)

    def clone(self):
        return self.path

    def mutate(self):
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
        self.wal = []

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
            raise WorldError("Failed in north_of with {} and {}".format(test_row, test_col))

    def south_of(self, test_row, test_col):
        if(test_row >= 0 and test_row+1 < self.n and test_col >= 0 and test_col < self.n):
            return self.play_space[test_row+1][test_col]
        else:
            #print "failed in a north of {},{}".format(test_row+1, test_col)
            return self.wall
            raise WorldError("Failed in south_of with {} and {}".format(test_row, test_col))

    def west_of(self, test_row, test_col):
        if(test_row >= 0 and test_row < self.n and test_col-1 >= 0 and test_col < self.n):
            return self.play_space[test_row][test_col - 1]
        else:
            #print "failed in a north of {},{}".format(test_row, test_col-1)
            return self.wall
            raise WorldError("Failed in west_of with {} and {}".format(test_row, test_col))

    def east_of(self, test_row, test_col):
        if(test_row >= 0 and test_row < self.n and test_col >= 0 and test_col + 1 < self.n):
            return self.play_space[test_row][test_col + 1]
        else:
            #print "failed in a north of {},{}".format(test_row, test_col+1)
            return self.wall
            raise WorldError("Failed in east_of with {} and {} while n is " .format(test_row, test_col, self.n))

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
                    if self.play_space[row][col] == self.empty and random.randint(0, 100)<=percent:
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

        self.name = ""

    def get_snake(self):
        return self.body

    def is_dead(self):
        return self.alive != 1

    def have_child(self):
        child = Snake()
        child.brain.path = self.brain.path
        child.body = copy.deepcopy(self.body)
        child.direction = copy.deepcopy(self.direction)
        return child

    def roll(self, array_to_roll):
        if(len(array_to_roll) < 1):
            raise BodySizeToSmall("Tried to roll a body that was less than 1")
        x = deque(array_to_roll)
        x.rotate(1)
        return list(x)

    def ate_food(self, add_food=1):
        self.food += 1
        self.body.append(self.body[-1])
        self.calculate_fitness()

    def redraw(self):
        self.world.clear_board()
        self.world.draw_snake(self.body)
        self.world.draw_walls()
        self.world.draw_foods()

    def turn_callback(self):
        if(self.alive == 1):
            self.turns_alive += 1

    def calculate_fitness(self):
        if(self.turns_alive != 0):
            self.fitness += (1.0/self.turns_alive)*self.food**3 #  incremental update of fitness?
        #self.fitness = 0.1*self.turns_alive**2+self.food**3 +0.000001


    def north_safe(self):
        return (self.north_empty() or self.north_food())
    def north_empty(self):
        return self.world.north_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def north_food(self):
        return self.world.north_of(self.body[0][0], self.body[0][1]) == self.world.food
    def north_wall(self):
        return (self.world.north_of(self.body[0][0], self.body[0][1]) == self.world.wall or
                self.world.north_of(self.body[0][0], self.body[0][1]) == self.world.body or
                self.world.north_of(self.body[0][0], self.body[0][1]) == self.world.head)

    def south_safe(self):
        return (self.south_empty() or self.south_food())
    def south_empty(self):
        return self.world.south_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def south_food(self):
        return self.world.south_of(self.body[0][0], self.body[0][1]) == self.world.food
    def south_wall(self):
        return (self.world.south_of(self.body[0][0], self.body[0][1]) == self.world.wall or
                self.world.south_of(self.body[0][0], self.body[0][1]) == self.world.body or
                self.world.south_of(self.body[0][0], self.body[0][1]) == self.world.head)

    def east_safe(self):
        return (self.east_empty() or self.east_food())
    def east_empty(self):
        return self.world.east_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def east_food(self):
        return self.world.east_of(self.body[0][0], self.body[0][1]) == self.world.food
    def east_wall(self):
        return (self.world.east_of(self.body[0][0], self.body[0][1]) == self.world.wall or
                self.world.east_of(self.body[0][0], self.body[0][1]) == self.world.body or
                self.world.east_of(self.body[0][0], self.body[0][1]) == self.world.head)

    def west_safe(self):
        return (self.west_empty() or self.west_food())
    def west_empty(self):
        return self.world.west_of(self.body[0][0], self.body[0][1]) == self.world.empty
    def west_food(self):
        return self.world.west_of(self.body[0][0], self.body[0][1]) == self.world.food
    def west_wall(self):
        return (self.world.west_of(self.body[0][0], self.body[0][1]) == self.world.wall or
                self.world.west_of(self.body[0][0], self.body[0][1]) == self.world.body or
                self.world.west_of(self.body[0][0], self.body[0][1]) == self.world.head)

    def a_valid_path(self, row, col):
        return (self.world.north_of(row, col) < 2 or
                self.world.south_of(row, col) < 2 or
                self.world.east_of(row, col) < 2 or
                self.world.west_of(row, col) < 2)

    def move_north(self):
        #print "orignal"
        #print self.body
        self.body = self.roll(self.body)
        #print "rolled"
        #print self.body
        self.body[0] = [self.body[1][0]-1, self.body[1][1]]
        #print "moved head up 1"
        #print self.body
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
        if(self.alive == 0):
            raise SnakeDeath("the snake is already dead", self.turns_alive, self.food, self.brain.path)
        if(self.north_safe()):
            self.direction = "North"
            if (self.north_food()):
                #print "n: {} ,s: {}, f: {}".format(self.name, [self.body[0][0]-1, self.body[0][1]],self.world.foods)
                if([self.body[0][0]-1, self.body[0][1]] in self.world.foods):
                    self.world.foods.remove([self.body[0][0]-1, self.body[0][1]])
                else:
                    print "Theres a food issue north"
                    print "n: {} ,s: {}, f: {}".format(self.name, [self.body[0][0]-1, self.body[0][1]],self.world.foods)
                self.ate_food()

            self.move_north()
        else:
            #print "collision with wall at {},{}".format(self.body[0][0]-1, self.body[0][1])
            self.alive = 0
            raise SnakeDeath("died at {},{}".format(self.body[0][0]-1, self.body[0][1]), self.turns_alive, self.food, self.brain.path)

    def go_east(self):
        if(self.alive == 0):
            raise SnakeDeath("the snake is already dead", self.turns_alive, self.food, self.brain.path)
        if(self.east_safe()):
            self.direction = "East"
            if (self.east_food()):
                self.ate_food()
                if ([self.body[0][0], self.body[0][1]+1] in self.world.foods):
                    self.world.foods.remove([self.body[0][0], self.body[0][1]+1])
                else:
                    print "Theres a food issue east"
            self.move_east()
        else:
            #print "collision with wall at {},{}".format(self.body[0][0], self.body[0][1]+1)
            self.alive = 0
            raise SnakeDeath("died at {},{}".format(self.body[0][0], self.body[0][1]+1), self.turns_alive, self.food, self.brain.path)

    def go_south(self):
        if(self.alive == 0):
            raise SnakeDeath("the snake is already dead", self.turns_alive, self.food, self.brain.path)
        if(self.south_safe()):
            self.direction = "South"
            if (self.south_food()):
                self.ate_food()
                if ([self.body[0][0]+1, self.body[0][1]] in self.world.foods):
                    self.world.foods.remove([self.body[0][0]+1, self.body[0][1]])
                else:
                    print "Theres a food issue south"
            self.move_south()
        else:
            #print "collision with wall at {},{}".format(self.body[0][0]+1, self.body[0][1])
            self.alive = 0
            raise SnakeDeath("died at {},{}".format(self.body[0][0]+1, self.body[0][1]), self.turns_alive, self.food, self.brain.path)

    def go_west(self):
        if(self.alive == 0):
            raise SnakeDeath("the snake is already dead", self.turns_alive, self.food, self.brain.path)
        if(self.west_safe()):
            self.direction = "West"
            if (self.west_food()):
                self.ate_food()
                if ([self.body[0][0], self.body[0][1]-1] in self.world.foods):
                    self.world.foods.remove([self.body[0][0], self.body[0][1]-1])
                else:
                    print "Theres a food issue south"
            self.move_west()
        else:
            #print "collision with wall at {},{}".format(self.body[0][0], self.body[0][1]-1)
            self.alive = 0
            raise SnakeDeath("died at {},{}".format(self.body[0][0], self.body[0][1]-1), self.turns_alive, self.food, self.brain.path)

    def go_straight(self):
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
        if(self.alive == 1):
            self.run_path(self.brain.path[self.turns_alive])

        if(self.turns_alive == self.brain.n):
            self.alive = 0

    def run_path(self, test_string):
        try:
            for i in test_string.upper():
                if(i == "S"):
                    self.go_straight()
                elif(i == "R"):
                    self.go_right()
                elif(i == "L"):
                    self.go_left()
                else:
                    print "invalid path of {}, should be L R or S".format(i)
        except SnakeDeath as snake_ded:
            pass
            #return self.algorithm.fitness(snake_ded.path, snake_ded.alive, snake_ded.food)
        #return self.algorithm.fitness(self.brain.path, self.turns_alive, self.food)

    def generate_random_body(self):
        length = 2  # this is the length of the random generated snake
        row = random.randint(0, self.world.n - 1)
        col = random.randint(0, self.world.n - 1)
        self.body.append([row, col])
        length -= 1
        for i in range(length):
            if self.a_valid_path(row, col):
                if(self.north_safe()):
                    self.ate_food(0)
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0]-1, self.body[1][1]]
                elif(self.south_safe()):
                    self.ate_food(0)
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0]+1, self.body[1][1]]
                elif(self.east_safe()):
                    self.ate_food(0)
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0], self.body[1][1]+1]
                elif(self.south_safe()):
                    self.ate_food(0)
                    self.body = self.roll(self.body)
                    self.body[0] = [self.body[1][0], self.body[1][1]-1]





class Population():
    def __init__(self, pop_num):
        self.n = pop_num
        self.snakes = []
        for i in range(self.n):
            self.snakes.append(Snake())
            self.snakes[i].name = "SNAKE {}, GEN {}".format(i,0)

        self.generation = 0
        self.max_snake = Snake()
        self.max_fitness = 0

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
        for i in range(self.n):
            if(self.snakes[i].fitness >= self.max_fitness):
                self.max_fitness = self.snakes[i].fitness
                self.max_snake = copy.deepcopy(self.snakes[i])
                self.snakes[i].best_snake = True
        #print self.max_snake.world.fancy_print_world()

    def natural_selection(self):
        self.babies = []
        for i in range(self.n):
            self.babies.append(Snake())

        for i in range(self.n):
            parent = self.select_parent()

            self.babies[i] = copy.deepcopy(parent.have_child())
        self.snakes = copy.deepcopy(self.babies);
        self.babies = []

        self.generation += 1

    def mutate_babies(self):
        for i in range(self.n):
            self.snakes[i].brain.mutate()
            self.snakes[i].name = "SNAKE {}, GEN {}".format(i,self.generation)


    def select_parent(self):
        random_point = random.randint(0, int(self.get_fitness_sum()))
        result = 0
        for i in range(self.n):
            result += self.snakes[i].fitness
            if(result >= random_point):
                # this is the parent
                return self.snakes[i]
        print "the random point was {} and the fitness sum was {}".format(random_point, self.get_fitness_sum())
        raise ValueError("I should never have sorted the snakes!")


    def get_fitness_sum(self):
        result = 0
        for i in range(self.n):
            result += self.snakes[i].fitness
        return result



s = "S"
l = "L"
r = "R"
if(__name__ == "__main__"):
    snake1 = Snake()
    snake1.generate_random_body()
    snake1.world.draw_snake(snake1.body)
    snake1.world.random_generator(10, snake1.world.food)
    print snake1.world.fancy_print_world()

    for turn in range(50):
        print "TURN {}".format(turn)
        test = Population(100)
        test.set_all_snake_bodies(copy.deepcopy(snake1.body),copy.deepcopy(snake1.direction))
        test.set_all_snake_world(copy.deepcopy(snake1.world.play_space),
                                 copy.deepcopy(snake1.world.foods),
                                 copy.deepcopy(snake1.world.walls))


        while(test.generation <= 50):
            if(not test.all_snakes_dead()):
                test.update()
            else:
                #test.calculate_fitness()
                test.best_snake()
                test.natural_selection()
                test.set_all_snake_bodies(copy.deepcopy(snake1.body), copy.deepcopy(snake1.direction))
                test.set_all_snake_world(copy.deepcopy(snake1.world.play_space),
                                         copy.deepcopy(snake1.world.foods),
                                         copy.deepcopy(snake1.world.walls))

                test.mutate_babies()
                if(test.generation % 10 == 0):
                    print "generation: {}, fitness: {}, turns: {}, food: {}, path: {}".format(
                                                                    test.generation,
                                                                    test.max_snake.fitness,
                                                                    test.max_snake.turns_alive,
                                                                    test.max_snake.food,
                                                                    test.max_snake.brain.path[0:5])
                    print test.max_snake.world.fancy_print_world()

        print "MY SNEK"
        print "GOING {}".format(test.max_snake.brain.path[0])
        snake1.run_path(test.max_snake.brain.path[0])
        print snake1.world.fancy_print_world()
        if len(snake1.world.foods) == 0:
            snake1.world.random_generator(10, snake1.world.food)
        if snake1.alive == 0:
            break


    print "done"
    print snake1.world.fancy_print_world()
    print "fitness: {}, turns: {}, food: {}".format(
                                                    snake1.fitness,
                                                    snake1.turns_alive,
                                                    snake1.food)







