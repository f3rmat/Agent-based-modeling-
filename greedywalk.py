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
dispatch_radius = 5
duration_game = 10800
#w = 0.9


map1 = {} #maps locations on grid to merchant ID
map2 = {} #present active merchants are set to true
map3 = {} #returns true if there is a merchant at (x,y) else false



runners_distance = [0]*(number_runners + 1)
last_decision = [0]*(number_runners+1) #holds time stamp 
last_decision_location = [0]*(number_runners+1)
w = [0]*(number_runners+1)
orders_taken = [0]*(number_runners+1)

for i in range(1,number_runners+1):
    w[i] = 0.2

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

    def w_x_coord(self, x):
        self.wxcoord = x

    def w_y_coord(self, y):
        self.wycoord = y



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
            if life_dict[x,y] == 0:
                pygame.draw.rect(displaysurf, white, (b, a, cell_size, cell_size))
            elif life_dict[x,y] == 1:
                pygame.draw.rect(displaysurf, grey, (b, a, cell_size, cell_size))
            elif life_dict[x,y] >= 2:
                pygame.draw.rect(displaysurf, red, (b, a, cell_size, cell_size))

            for i in range(1,number_runners + 1):
                if runners[i].xcoord == x and runners[i].ycoord == y:
                    if runners[i].busy == 1:
                        pygame.draw.rect(displaysurf, white, (b, a, cell_size, cell_size))

                    elif runners[i].busy ==  0:
                        pygame.draw.rect(displaysurf, green, (b, a, cell_size, cell_size))



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

    for i in range(1,number_merchants+1):
        flag = 1
        while True:
            start = random.randint(0,3)
            if start==0 and merchants[i].xcoord-dispatch_radius >= 0 and life_dict[merchants[i].xcoord-dispatch_radius,merchants[i].ycoord]==0:
                merchants[i].wxcoord = (merchants[i].xcoord-dispatch_radius)
                merchants[i].wycoord = (merchants[i].ycoord)
                flag = 0
            elif start==0 and merchants[i].xcoord-dispatch_radius < 0 and life_dict[merchants[i].xcoord+dispatch_radius,merchants[i].ycoord]==0:
                merchants[i].wxcoord = (merchants[i].xcoord+dispatch_radius)
                merchants[i].wycoord = (merchants[i].ycoord)
                flag = 0

            elif start==1 and merchants[i].ycoord-dispatch_radius >= 0 and life_dict[merchants[i].xcoord,merchants[i].ycoord-dispatch_radius]==0:
                merchants[i].wycoord = (merchants[i].ycoord-dispatch_radius)
                merchants[i].wxcoord = (merchants[i].xcoord)
                flag = 0
            elif start==1 and merchants[i].ycoord-dispatch_radius < 0 and life_dict[merchants[i].xcoord,merchants[i].ycoord+dispatch_radius]==0:
                merchants[i].wycoord = (merchants[i].ycoord+dispatch_radius)
                merchants[i].wxcoord = (merchants[i].xcoord)
                flag = 0
            
            elif start==2 and merchants[i].xcoord+dispatch_radius < cell_width and life_dict[merchants[i].xcoord+dispatch_radius,merchants[i].ycoord]==0:
                merchants[i].wxcoord = (merchants[i].xcoord+dispatch_radius)
                merchants[i].wycoord = (merchants[i].ycoord)
                flag = 0
            elif start==2 and merchants[i].xcoord+dispatch_radius >= cell_width and life_dict[merchants[i].xcoord-dispatch_radius,merchants[i].ycoord]==0:
                merchants[i].wxcoord = (merchants[i].xcoord-dispatch_radius)
                merchants[i].wycoord = (merchants[i].ycoord)
                flag = 0

            elif start==1 and merchants[i].ycoord+dispatch_radius < cell_height and life_dict[merchants[i].xcoord,merchants[i].ycoord+dispatch_radius]==0:
                merchants[i].wycoord = (merchants[i].ycoord+dispatch_radius)
                merchants[i].wxcoord = (merchants[i].xcoord)
                flag = 0
                
            elif start==1 and merchants[i].ycoord+dispatch_radius >= cell_height and life_dict[merchants[i].xcoord,merchants[i].ycoord-dispatch_radius]==0:
                merchants[i].wycoord = (merchants[i].ycoord-dispatch_radius)
                merchants[i].wxcoord = (merchants[i].xcoord)
                flag = 0
                
            if flag == 0:
                break
            

    for i in range(1,number_merchants+1):
        print("merchant number " + str(i) + " coord " + str(merchants[i].xcoord) + " " + str(merchants[i].ycoord) + " wcoord " +
              str(merchants[i].wxcoord) + " " + str(merchants[i].wycoord))

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

    for j in range(1,number_runners+1):
        maxi = 0
        maxi_index = 0

        for k in range(1,number_merchants+1):
            dist = 1.0/(abs(runners[j].xcoord - merchants[k].xcoord) + abs(runners[j].ycoord - merchants[k].ycoord))
            frequency = merchants[k].count/72.0
            if w[j]*dist + (1-w[j])*frequency > maxi:
                maxi = w[j]*dist + (1-w[j])*frequency
                maxi_index = k

        last_decision[j] = 0
        last_decision_location[j] = maxi_index
        runners[j].busy = 0
        runners_distance[j]  += ((abs(runners[j].xcoord - merchants[maxi_index].wxcoord) +
                                  abs(runners[j].ycoord - merchants[maxi_index].wycoord)))
        runners[j].xcoord = merchants[maxi_index].wxcoord
        runners[j].ycoord = merchants[maxi_index].wycoord
        print("runner number "+str(j)+" "+str(runners[j].xcoord)+" "+str(runners[j].ycoord) + "  index " + str(maxi_index))

    return merchants, life_dict, runners

##def check(merchants,life_dict,runners):
##    map2 = finding_active_merchants(merchants,life_dict)
##    for i in range (1,number_merchants+1):
##        if map2[i] != 0:
##            for j in range(1,number_runners+1):
##                if runners[j].busy == 0 and runners[j].xcoord == merchants[i].wxcoord and runners[j].ycoord == merchants[i].wycoord:
##                    x = random.randint(0,1000)%((int)(cell_width))
##                    y = random.randint(0,1000)%((int)(cell_height))
##                    while life_dict[x,y]!=0:
##                        x = random.randint(0,1000)%((int)(cell_width))
##                        y = random.randint(0,1000)%((int)(cell_height))
##                    print("runner number "+str(j) + " at merchant " + str(i))
##                    runners[j].distance_to_travel = abs(merchants[i].wxcoord - x) + abs(merchants[i].wycoord - y)
##                    runners[j].xcoord = x
##                    runners[j].ycoord = y
##                    runners[j].busy = 1
##                    runners_distance[j]+=runners[j].distance_to_travel
##                    life_dict[merchants[i].xcoord,merchants[i].ycoord]-=1
##                    if life_dict[merchants[i].xcoord,merchants[i].ycoord]==1:  
##                        break

def check(merchants, life_dict, runners):
    map2 = finding_active_merchants(merchants,life_dict)
    for i in range (1,number_merchants+1):

        if map2[i] ==1 :
            
            count = 1
            
            temp_ar = [0]*(number_runners+1)
            for j in range(1,number_runners+1):
                if runners[j].busy == 0 and runners[j].xcoord == merchants[i].wxcoord and runners[j].ycoord == merchants[i].wycoord:
                    temp_ar[count] = j
                    count+=1

            if count>2:
                random_index = random.randint(1,count-1)
                
            elif count==2:
                random_index = 1

            elif count == 1:
                continue

            x = random.randint(0,1000)%((int)(cell_width))
            y = random.randint(0,1000)%((int)(cell_height))
            while life_dict[x,y]!=0:
                x = random.randint(0,1000)%((int)(cell_width))
                y = random.randint(0,1000)%((int)(cell_height))
            runners[temp_ar[random_index]].distance_to_travel = abs(merchants[i].wxcoord - x) + abs(merchants[i].wycoord - y)
            runners[temp_ar[random_index]].xcoord = x
            runners[temp_ar[random_index]].ycoord = y
            runners[temp_ar[random_index]].busy = 1
            orders_taken[temp_ar[random_index]] += 1
            print("runner number " + str(temp_ar[random_index]) +  " at merchant " + str(i) + " orders taken " + str(orders_taken[temp_ar[random_index]]))

            runners_distance[temp_ar[random_index]]+=runners[temp_ar[random_index]].distance_to_travel
            life_dict[merchants[i].xcoord,merchants[i].ycoord]-=1
            



        elif map2[i]==2:
            count = 1
            temp_ar = [0]*(number_runners+1)
            for j in range(1,number_runners+1):
                if runners[j].busy == 0 and runners[j].xcoord == merchants[i].wxcoord and runners[j].ycoord == merchants[i].wycoord:
                    temp_ar[count] = j
                    count+=1

            if count==1:
                continue
            
            elif count==3:
                random_index1 = random.randint(1,count-1)
                random_index2 = random.randint(1,count-1)
                while random_index2 == random_index1:
                    random_index2 = random.randint(1,count-1)
                    
                x = random.randint(0,1000)%((int)(cell_width))
                y = random.randint(0,1000)%((int)(cell_height))
                while life_dict[x,y]!=0:
                    x = random.randint(0,1000)%((int)(cell_width))
                    y = random.randint(0,1000)%((int)(cell_height))
                runners[temp_ar[random_index1]].distance_to_travel = abs(merchants[i].wxcoord - x) + abs(merchants[i].wycoord - y)
                runners[temp_ar[random_index1]].xcoord = x
                runners[temp_ar[random_index1]].ycoord = y
                runners[temp_ar[random_index1]].busy = 1
                orders_taken[temp_ar[random_index1]] += 1
                print("runner number " + str(temp_ar[random_index]) +  " at merchant " + str(i) + " orders taken " + str(orders_taken[temp_ar[random_index1]]) )

                runners_distance[temp_ar[random_index1]]+=runners[temp_ar[random_index1]].distance_to_travel
                life_dict[merchants[i].xcoord,merchants[i].ycoord]-=1

                x = random.randint(0,1000)%((int)(cell_width))
                y = random.randint(0,1000)%((int)(cell_height))
                while life_dict[x,y]!=0:
                    x = random.randint(0,1000)%((int)(cell_width))
                    y = random.randint(0,1000)%((int)(cell_height))
                runners[temp_ar[random_index2]].distance_to_travel = abs(merchants[i].wxcoord - x) + abs(merchants[i].wycoord - y)
                runners[temp_ar[random_index2]].xcoord = x
                runners[temp_ar[random_index2]].ycoord = y
                runners[temp_ar[random_index2]].busy = 1
                orders_taken[temp_ar[random_index2]] += 1
                print("runner number " + str(temp_ar[random_index]) +  " at merchant " + str(i) + " orders taken " + str(orders+taken[temp_ar[random_index2]]) )

                runners_distance[temp_ar[random_index2]]+=runners[temp_ar[random_index2]].distance_to_travel
                life_dict[merchants[i].xcoord,merchants[i].ycoord]-=1

            elif count==2:
                random_index = 1#random.randint(1,count-1)
                x = random.randint(0,1000)%((int)(cell_width))
                y = random.randint(0,1000)%((int)(cell_height))
                while life_dict[x,y]!=0:
                    x = random.randint(0,1000)%((int)(cell_width))
                    y = random.randint(0,1000)%((int)(cell_height))
                runners[temp_ar[random_index]].distance_to_travel = abs(merchants[i].wxcoord - x) + abs(merchants[i].wycoord - y)
                runners[temp_ar[random_index]].xcoord = x
                runners[temp_ar[random_index]].ycoord = y
                runners[temp_ar[random_index]].busy = 1
                orders_taken[temp_ar[random_index]]+=1
                print("runner number " + str(temp_ar[random_index]) +  " at merchant " + str(i) + " orders taken " + str(orders_taken[temp_ar[random_index]]) )

                runners_distance[temp_ar[random_index]]+=runners[temp_ar[random_index]].distance_to_travel
                life_dict[merchants[i].xcoord,merchants[i].ycoord]-=1

            elif count>3:
                while True:
                    print("alert count exceed 3 in check")

                

            


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

    for i in range(1,number_orders+1):
        loc_dec[i] = random.uniform(0,1)

    for i in range(1,number_orders+1):
        flag = 1
        for j in range(1,number_merchants+1):
            if j==1 and merchants[j].reg > loc_dec[i]:
                orders[i].assign(j)
                merchants[j].increment_count()
                flag = 0
                break
            elif merchants[j].reg > loc_dec[i] and loc_dec[i] >=merchants[j-1].reg:
                orders[i].assign(j)
                merchants[j].increment_count()
                flag = 0
                break
        if flag == 1:
            orders[i].assign(number_merchants)
            merchants[number_merchants].increment_count()

    pygame.display.update()
    FPSCLOCK = pygame.time.Clock()

    for i in range(1,number_merchants+1):
        print("merchant number: " + str(i) + " and count: " + str(merchants[i].count))

    for i in range(1,duration_game+1):
##       
##        colour_grid(life_dict,runners)
##        draw_grid()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

                
        for j in range(1,number_orders+1):
            if orders[j].time == i:
                x = orders[j].ass
                life_dict[merchants[x].xcoord,merchants[x].ycoord] += 1 
                print("order arrival "+(str)(j) + " life dict value " + str(life_dict[merchants[x].xcoord,merchants[x].ycoord])
                      + " merchant no: " + str(map1[merchants[x].xcoord,merchants[x].ycoord]) )


        for j in range(1,number_orders+1):
            if orders[j].time+50 == i and life_dict[merchants[orders[j].ass].xcoord,merchants[orders[j].ass].ycoord]>=2:
                x = orders[j].ass
                print("order lost " + str(j) + " life dict value " + str(life_dict[merchants[x].xcoord,merchants[x].ycoord]) +" at merchant " + str(map1[merchants[x].xcoord,merchants[x].ycoord]))
                life_dict[merchants[x].xcoord,merchants[x].ycoord] -= 1
                orders_lost+=1


        check(merchants,life_dict,runners)


        for j in range(1,number_merchants+1):
            if life_dict[merchants[j].xcoord,merchants[j].ycoord] == 0:
                life_dict[merchants[j].xcoord,merchants[j].ycoord] = 1
        
        for j in range(1,number_runners+1):
            if last_decision[j]+100==i and runners[j].busy == 0:
                maxi = 0
                maxi_index = 0
                for k in range(1,number_merchants+1):
                    if k!=last_decision_location[j]:
                        if runners[j].xcoord == merchants[k].xcoord and runners[j].ycoord == merchants[k].ycoord:
                            print("runner number "+str(j)+" merchant number" +str(k)+" coord "+str(runners[j].xcoord)+" "+str(runners[j].ycoord))
                        dist = 1.0/(abs(runners[j].xcoord - merchants[k].xcoord) + abs(runners[j].ycoord - merchants[k].ycoord))
                        frequency = merchants[k].count/72.0
                        if w[j]*dist + (1-w[j])*frequency > maxi:
                            maxi = w[j]*dist + (1-w[j])*frequency
                            maxi_index = k

                runners_distance[j] += abs(merchants[maxi_index].wxcoord - merchants[last_decision_location[j]].wxcoord) + abs(merchants[maxi_index].wycoord - merchants[last_decision_location[j]].wycoord)
                life_dict[runners[j].xcoord, runners[j].ycoord] = 0
                last_decision[j] = i
                last_decision_location[j] = maxi_index
                runners[j].xcoord = merchants[maxi_index].wxcoord
                runners[j].ycoord = merchants[maxi_index].wycoord





        

        for e in range(1,number_runners+1):
            if runners[e].busy == 1:
                runners[e].distance_to_travel-=1
                
                if runners[e].distance_to_travel == 0 and last_decision_location[e] < 0:
                    runners[e].busy = 0
                    last_decision_location[e] = -1*last_decision_location[e]
                    last_decision[e] = i
                    print("runner reappeared " + str(e) + " " + str(runners[e].xcoord) + " " + str(runners[e].ycoord));

                                    
                elif runners[e].distance_to_travel==0:               
                    #runners[e].busy = 0
                    print("runner reached destination ",e);
                    #runners[e].orders_taken+=1
                    maxi = 0
                    maxi_index = 0

                    for k in range(1,number_merchants+1):
                        dist = 1.0/(abs(runners[e].xcoord - merchants[k].xcoord) + abs(runners[e].ycoord - merchants[k].ycoord))
                        frequency = merchants[k].count/72.0
                        if w[e]*dist + (1-w[e])*frequency > maxi:
                            maxi = w[e]*dist + (1-w[e])*frequency
                            maxi_index = k
                    
                    runners_distance[e] += abs(merchants[maxi_index].wxcoord - runners[e].xcoord) + abs(merchants[maxi_index].wycoord - runners[e].ycoord)
                    #last_decision[e] = i
                    last_decision_location[e] = -1*maxi_index
                    runners[e].distance_to_travel  = abs(merchants[maxi_index].wxcoord - runners[e].xcoord) + abs(merchants[maxi_index].wycoord - runners[e].ycoord)
                    runners[e].xcoord = merchants[maxi_index].wxcoord
                    runners[e].ycoord = merchants[maxi_index].wycoord



                    
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
        print("Runner Number: "+str(i)+" distance traveled: "+str(runners_distance[i]) + " orders taken " +str(orders_taken[i]))
        sum123 +=orders_taken[i]


    for i in range(1,number_orders+1):
        print("order number " + str(i) +" has time " +str(orders[i].time))
        
    print("orders lost: "+str(orders_lost))
    print("orders picked: "+str(sum123))


main()
