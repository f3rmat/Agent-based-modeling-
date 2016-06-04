import pygame, sys
from pygame.locals import *
import random

pygame.init()
global displaysurf
black = (0,0,0)
white = (255,255,255)
grey = (40,40,40)
green = (0,255,0)
FPS = 15

window_width = 640
window_height = 480
cell_size = 10

cell_width = window_width/cell_size #important
cell_height = window_height/cell_size #important


assert window_width % cell_size == 0, "Window width must be a multiple of cell size"
assert window_height % cell_size == 0, "Window height must be a multiple of cell size"


displaysurf = pygame.display.set_mode((window_width,window_height))
pygame.display.set_caption('Game Of Life')
icon = pygame.image.load('glider.png')
pygame.display.set_icon(icon)

def draw_grid():
    for x in range(0, window_width, cell_size): # draw vertical lines
        pygame.draw.line(displaysurf, grey, (x,0),(x,window_height))
    for y in range(0, window_height, cell_size): # draw horizontal lines
        pygame.draw.line(displaysurf, grey, (0,y),(window_width,y))


def blank_grid():
    grid_dict = {}
    for y in range (int(cell_height)):
        for x in range (int(cell_width)):
            grid_dict[x,y] = 0

    return grid_dict


def starting_grid_random(life_dict):
    for item in life_dict:
        life_dict[item] = random.randint(0,1)
    return life_dict

def colour_grid(item, life_dict):
    x = item[0]
    y = item[1]
    y = y * cell_size 
    x = x * cell_size 
    if life_dict[item] == 0:
        pygame.draw.rect(displaysurf, white, (x, y, cell_size, cell_size))
    if life_dict[item] == 1:
        pygame.draw.rect(displaysurf, green, (x, y, cell_size, cell_size))


def getNeighbours(item,life_dict):
    neighbours = 0
    for x in range (-1,2):
        for y in range (-1,2):
            checkCell = (item[0]+x,item[1]+y)
            if checkCell[0] < cell_width  and checkCell[0] >=0:
                if checkCell [1] < cell_height and checkCell[1]>= 0:
                    if life_dict[checkCell] == 1:
                        if x == 0 and y == 0: 
                            neighbours += 0
                        else:
                            neighbours += 1
    return neighbours


def tick(life_dict):
    newTick = {}
    for item in life_dict:
        numberNeighbours = getNeighbours(item, life_dict)
        if life_dict[item] == 1: # For those cells already alive
            if numberNeighbours < 2: # kill under-population
                newTick[item] = 0
            elif numberNeighbours > 3: #kill over-population
                newTick[item] = 0
            else:
                newTick[item] = 1 # keep status quo (life)
        elif life_dict[item] == 0:
            if numberNeighbours == 3: # cell reproduces
                newTick[item] = 1
            else:
                newTick[item] = 0 # keep status quo (death)
    return newTick
    

def main():
    displaysurf.fill(white)
    life_dict = blank_grid()
    life_dict = starting_grid_random(life_dict)
    pygame.display.update()
    FPSCLOCK = pygame.time.Clock()
    while True: 
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        life_dict = tick(life_dict)
        for item in life_dict:
            colour_grid(item, life_dict)

        draw_grid()
        pygame.display.update()    
        FPSCLOCK.tick(FPS)

main()


