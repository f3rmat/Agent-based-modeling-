import pygame, sys
from pygame.locals import *
import random
import math
import time

pygame.init()
global displaysurf
black = (0,0,0)
white = (255,255,255)
grey = (40,40,40)
green = (0,255,0)
red = (255,0,0)
FPS = 50

window_width = 640
window_height = 480
cell_size = 10

number_merchants = 30
number_orders = 72
number_runners = 30
dispatch_radius = 10
duration_game = 10800

map1 = {} #maps locations on grid to merchant ID
map2 = {} #present active merchants are set to true
map3 = {} #returns true if there is a merchant at (x,y) else false

runners_distance = [0]*(number_merchants + 1)
orders_checklist = [0]*(number_orders + 1)

cell_width = window_width/cell_size #important
cell_height = window_height/cell_size #important


assert window_width % cell_size == 0, "Window width must be a multiple of cell size"
assert window_height % cell_size == 0, "Window height must be a multiple of cell size"


displaysurf = pygame.display.set_mode((window_width,window_height))
pygame.display.set_caption('Runner-simulation-2')
icon = pygame.image.load('glider.png')
pygame.display.set_icon(icon)


class merchant:

    count = 0

    def __init__(self, name):
        self.name = name

    def x_coord(self, x):
        self.xcoord = x

    def y_coord(self, y):
        self.ycoord = y

    def region(self, y):
        self.reg = y

    def increment_count(self):
        self.count = self.count + 1


class order:

    def __init__(self, name):
        self.name = name

    def assign(self, name):
        self.ass = name

    def set_time(self, time):
        self.time = time

class runner:
    def __init__(self, name):
        self.name = name
        self.busy = 0
        self.orders_taken = 0
        self.distance_to_travel = 0
        self.order = 0
        self.xcoord = 0
        self.ycoord = 0

    def x_coord(self, x):
        self.xcoord = x

    def y_coord(self, y):
        self.ycoord = y

    def set_busy(self,x):
        self.busy = x

    def set_distance_to_travel(self, distance):
        self.distance_to_travel = distance

    def set_order(self, order):
        self.order = order


def draw_grid():
    for x in range(0, window_width, cell_size): # draw vertical lines
        pygame.draw.line(displaysurf, grey, (x,0),(x,window_height))
    for y in range(0, window_height, cell_size): # draw horizontal lines
        pygame.draw.line(displaysurf, grey, (0,y),(window_width,y))


def colour_grid(life_dict, runners):
   for y in range (int(cell_height)):
        for x in range (int(cell_width)):
            a = y * cell_size
            b = x * cell_size
            for i in range(1,number_runners + 1):
                if runners[i].xcoord == x and runners[i].ycoord == y:
                    if runners[i].busy == 1:
                        pygame.draw.rect(displaysurf, white, (b, a, cell_size, cell_size))

                    elif runners[i].busy ==  0:
                        pygame.draw.rect(displaysurf, green, (b, a, cell_size, cell_size))


            if life_dict[x,y] == 0:
                pygame.draw.rect(displaysurf, white, (b, a, cell_size, cell_size))
            elif life_dict[x,y] == 1:
                pygame.draw.rect(displaysurf, grey, (b, a, cell_size, cell_size))
            elif life_dict[x,y] >= 2:
                pygame.draw.rect(displaysurf, red, (b, a, cell_size, cell_size))



def blank_grid():
    grid_dict = {}
    for y in range (int(cell_height)):
        for x in range (int(cell_width)):
            grid_dict[x,y] = 0

    return grid_dict

def starting_orders_random(orders):

    x = random.randint(1,100)

    orders[1].set_time(x)

    lambda1 = 150

    for i in range(2,number_orders+1):

        z = random.uniform(0,1)

        alpha = (-1*lambda1)*math.log(1-z)

        s = orders[i-1].time + alpha

        orders[i].set_time((int)(s))

    return orders

def initialise_arrays(merchants, orders, runners):
    for i in range(1,number_merchants+1):
        merchants[i] = merchant(i)
    for i in range(1,number_orders+1):
        orders[i] = order(i)
    for i in range(1,number_runners+1):
        runners[i] = runner(i)

    return merchants, orders, runners

def initialise_coordinates(merchants, life_dict, runners):
    for y in range (int(cell_height)):
        for x in range (int(cell_width)):
            map3[x,y] = 0

    for i in range(1,number_merchants+1):
        x = random.randint(0,1000)%((int)(cell_width))
        y = random.randint(0,1000)%((int)(cell_height))
        merchants[i].x_coord(x)
        merchants[i].y_coord(y)
        life_dict[x,y] = 1
        map1[x,y] = i
        map3[x,y] = 1

    for i in range(1,number_runners+1):
        x = random.randint(0,1000)%((int)(cell_width))
        y = random.randint(0,1000)%((int)(cell_height))
        runners[i].xcoord = x
        runners[i].ycoord = y

        while life_dict[x,y] != 0:
            x = random.randint(0,1000)%((int)(cell_width))
            y = random.randint(0,1000)%((int)(cell_height))
            runners[i].xcoord = x
            runners[i].ycoord = y
        life_dict[x,y] = -1

    return merchants, life_dict, runners




def check(merchants,life_dict,runners):
    map2 = finding_active_merchants(merchants,life_dict)
    for i in range (1,number_merchants+1):
        if map2[i] == 1:
            minimum = 100000
            temp = 0
            for k in range(1,number_runners+1):
                if abs(runners[k].xcoord-merchants[i].xcoord) + abs(runners[k].ycoord-merchants[i].ycoord) < minimum and runners[k].busy==0:
                    minimum = abs(runners[k].xcoord-merchants[i].xcoord) + abs(runners[k].ycoord-merchants[i].ycoord)
                    temp = k
            if minimum <= dispatch_radius:
                runners[temp].busy = 1
                life_dict[merchants[i].xcoord,merchants[i].ycoord] -= 1

                if map3[runners[temp].xcoord, runners[temp].ycoord]==0:
                    life_dict[runners[temp].xcoord, runners[temp].ycoord] = 0
                elif map3[runners[temp].xcoord, runners[temp].ycoord]==1:
                    life_dict[runners[temp].xcoord, runners[temp].ycoord] = 1

                x = random.randint(0,1000)%((int)(cell_width))
                y = random.randint(0,1000)%((int)(cell_height))
                while(life_dict[x,y]!=0):
                    x = random.randint(0,1000)%((int)(cell_width))
                    y = random.randint(0,1000)%((int)(cell_height))
                runners[temp].distance_to_travel = abs(runners[temp].xcoord- x) + abs(runners[temp].ycoord - y)
                runners_distance[temp] += abs(runners[temp].xcoord - x) +abs(runners[temp].ycoord - y)
                runners[temp].xcoord = x
                runners[temp].ycoord = y
                print("runner number " + str(temp))
                runners[temp].orders_taken+=1




def finding_active_merchants(merchants,life_dict):
    for i in range(1,number_merchants+1):
        map2[i] = 0

    for i in range(1,number_merchants+1):
        if life_dict[merchants[i].xcoord,merchants[i].ycoord] >= 2:
            map2[i] = life_dict[merchants[i].xcoord,merchants[i].ycoord] - 1

    return map2



def main():
    start_time = time.time()

    displaysurf.fill(white)

    life_dict = blank_grid()

    orders_lost = 0

    merchants = [0]*(number_merchants+1)

    orders = [0]*(number_orders+1)

    loc_dec = [0]*(number_orders + 1)

    locs = [0]*(number_merchants+1)

    runners = [0]*(number_runners+1)

    merchants, orders, runners = initialise_arrays(merchants, orders, runners)

    orders = starting_orders_random(orders)

    while not(orders[number_orders].time > 10000 and orders[number_orders].time < 10600):
        orders = starting_orders_random(orders)

    merchants, life_dict, runners = initialise_coordinates(merchants, life_dict, runners)

    for i in range(1,number_merchants+1):
        locs[i] = random.uniform(0,1)

    locs.sort()

    for i in range(1,number_merchants+1):
        merchants[i].region(locs[i])

    merchants[number_merchants].reg = 1

    print("slabs for merchants: ")
    for i in range(1,number_merchants+1):
        print(merchants[i].reg)

    for i in range(1,number_orders+1):
        loc_dec[i] = random.uniform(0,1)

    print("values to be put in the slabs: ")

    for i in range(1,number_orders+1):
        print(loc_dec[i])

    for i in range(1,number_orders+1):
        flag = 1
        for j in range(1,number_merchants+1):
            if j==1 and merchants[j].reg > loc_dec[i]:
                #print("an assignment done")
                #print(j,i)
                orders[i].assign(j)
                merchants[j].increment_count()
                flag = 0
                break
            elif merchants[j].reg > loc_dec[i] and loc_dec[i] >=merchants[j-1].reg:
                #print("an assignment done")
                #print(j,i)
                orders[i].assign(j)
                merchants[j].increment_count()
                flag = 0
                break
        if flag == 1:
            #print("an assignment done")
            #print(number_merchants,i)
            orders[i].assign(number_merchants)
            merchants[number_merchants].increment_count()


    pygame.display.update()

    FPSCLOCK = pygame.time.Clock()

    for i in range(1,duration_game+1):
       
##        colour_grid(life_dict,runners)
##        draw_grid()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

                
        for j in range(1,number_orders+1):
            if orders[j].time == i:
                x = orders[j].ass
                if life_dict[merchants[x].xcoord,merchants[x].ycoord] == -1:
                    life_dict[merchants[x].xcoord,merchants[x].ycoord] = 2
                else:
                    life_dict[merchants[x].xcoord,merchants[x].ycoord] += 1
                
                print("order arrival "+(str)(j) + " life dict value " + str(life_dict[merchants[x].xcoord,merchants[x].ycoord]) + " merchant no: " + str(map1[merchants[x].xcoord,merchants[x].ycoord]) )
##                if life_dict[merchants[x].xcoord,merchants[x].ycoord] >2:
##                    print("hahhhhhhhhdaghgbjgagygyhhhhahahahhaah" + str(j))

        for j in range(1,number_orders+1):
            if orders[j].time+50 == i and life_dict[merchants[orders[j].ass].xcoord,merchants[orders[j].ass].ycoord]>=2:
                x = orders[j].ass
                print("order lost " + str(j) + " life dict value " + str(life_dict[merchants[x].xcoord,merchants[x].ycoord]) +" at merchant " + str(map1[merchants[x].xcoord,merchants[x].ycoord]))
                life_dict[merchants[x].xcoord,merchants[x].ycoord] -= 1
                orders_lost+=1

        check(merchants,life_dict,runners)

        for e in range(1,number_runners+1):
            if runners[e].busy == 1:
                runners[e].distance_to_travel-=1
                if runners[e].distance_to_travel==0:
                    runners[e].busy = 0


##        colour_grid(life_dict,runners)
##        draw_grid()
##        pygame.display.update()
##        FPSCLOCK.tick(FPS)

    elapsed_time = time.time() - start_time
    print("elapsed time is: ",elapsed_time)


    sum123 = 0
    for i in range(1,number_runners+1):
        if runners[i].busy == 1:
            print("Busy Runners:", i)
        print("Runner Number: "+str(i)+" distance traveled: "+str(runners_distance[i]) + " orders taken " +str(runners[i].orders_taken))
        sum123 +=runners[i].orders_taken


    for i in range(1,number_orders+1):
        print("order number " + str(i) +" has time " +str(orders[i].time))
        
    print("orders lost: "+str(orders_lost))
    print("orders picked: "+str(sum123))


main()
