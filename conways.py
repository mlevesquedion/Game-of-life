import os
import pygame
import shelve
import sys
from copy import deepcopy
from pygame.locals import *

pygame.init()

# Game dimensions
cellSize = 10
cellsInWidth = 100
cellsInHeight = 60
screenWidth = cellSize * cellsInWidth
cellArrayHeight = cellSize * cellsInHeight
buttonSize = 50
buttonBarHeight = buttonSize
screenHeight = cellArrayHeight + buttonBarHeight
screen = pygame.display.set_mode((screenWidth, screenHeight))

array = [[False for _ in range(cellsInHeight)] for _ in range(cellsInWidth)]
shouldSwitchStates = [[False for _ in range(cellsInHeight)] for _ in range(cellsInWidth)]
stack = []

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

FPSclock = pygame.time.Clock()
FPS = 10

positions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

buttons = [pygame.image.load(file + '.png') for file in ('play', 'pause', 'undo', 'step', 'plus', 'minus', 'clear', 'save', 'load')]

def count_neighbors(x, y):
    numberOfNeighbors = 0
    for i, j in positions:
        try:
            if x == 0 and i == -1 or y == 0 and j == -1:
                raise IndexError
            if array[x + i][y + j]:
                numberOfNeighbors += 1
        except IndexError:
            pass
    return numberOfNeighbors

def iterate_array():
    for i, row in enumerate(array):
        for j, cell in enumerate(row):
            yield (i, row, j, cell)

def draw_grid():
    for (i, row, j, cell) in iterate_array():
        pygame.draw.rect(screen, GRAY, (i * cellSize, j * cellSize, cellSize, cellSize), 1)

def draw_array():
    for (i, row, j, cell) in iterate_array():
        color = WHITE if cell else BLACK
        pygame.draw.rect(screen, color, (i * cellSize, j * cellSize, cellSize, cellSize))

def draw_FPS():
    FPSsurface = pygame.font.SysFont('calibri', 50).render('FPS : {}'.format(FPS), True, BLACK)
    FPSrect = FPSsurface.get_rect()
    FPSrect.bottomright = (screenWidth - 10, screenHeight + 3)
    screen.blit(FPSsurface, FPSrect)

def update_shouldSwitchStates():
    for (i, row, j, cell) in iterate_array():
        numberOfNeighbors = count_neighbors(i, j)
        shouldSwitchState = False
        if cell and (numberOfNeighbors < 2 or numberOfNeighbors > 3):
            shouldSwitchState = True
        elif not cell and numberOfNeighbors == 3:
            shouldSwitchState = True
        shouldSwitchStates[i][j] = shouldSwitchState

def update_array():
    global stack
    stack.append(deepcopy(array))
    if len(stack) > 10:
        stack = stack[1:]
    for (i, row, j, cell) in iterate_array():
        if shouldSwitchStates[i][j]:
            array[i][j] = not array[i][j]


def draw_buttons():
    for i, button in enumerate(buttons):
        screen.blit(button, (i * buttonSize, cellArrayHeight, 50, 50))

elapsedTime = 0
updatePositions = False
while True: # Main game loop

    for event in pygame.event.get(): # Main event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            if mouseY in range(cellArrayHeight):
                cellX, cellY = mouseX // 10, mouseY // 10
                currentValue = array[cellX][cellY]
                array[cellX][cellY] = not currentValue
            elif mouseX in range(buttonSize * len(buttons)):
                if mouseX in range(buttonSize):
                    updatePositions = True
                elif mouseX in range(buttonSize, buttonSize * 2):
                    updatePositions = False
                elif mouseX in range(buttonSize * 2, buttonSize * 3):
                    if stack:
                        array = deepcopy(stack.pop())
                elif mouseX in range(buttonSize * 3, buttonSize * 4):
                    update_shouldSwitchStates()
                    update_array()
                elif mouseX in range(buttonSize * 4, buttonSize * 5):
                    FPS += 1
                elif mouseX in range(buttonSize * 5, buttonSize * 6):
                    FPS -= 1
                    if FPS == 0:
                        FPS = 1
                elif mouseX in range(buttonSize * 6, buttonSize * 7):
                    array = [[False for _ in range(cellsInHeight)] for _ in range(cellsInWidth)]
                elif mouseX in range(buttonSize * 7, buttonSize * 8):
                    shelf = shelve.open('savestate')
                    shelf['array'] = array
                    shelf.close()
                elif mouseX in range(buttonSize * 8, buttonSize * 9):
                    shelf = shelve.open('savestate')
                    array = shelf['array']
                    shelf.close()
                    
    screen.fill(WHITE)

    draw_array()
    draw_buttons()
    draw_grid()
    draw_FPS()

    if updatePositions and elapsedTime > (1000 / FPS):
        update_shouldSwitchStates()
        update_array()
        elapsedTime = 0
    
    pygame.display.update()
    elapsedTime += FPSclock.tick()
