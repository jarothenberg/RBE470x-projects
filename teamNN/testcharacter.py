# This is necessary to find the main code
from queue import PriorityQueue
import sys
from typing import Any

import numpy as np
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

global interceptable
interceptable = True

class TestCharacter(CharacterEntity):

    def getWorld(self, wrld):
        wrldArray = np.array([[" " for x in range(wrld.width())] for y in range(wrld.height())])

        for y in range(wrld.height()):
            for x in range(wrld.width()):
                if wrld.characters_at(x,y):
                    for c in wrld.characters_at(x,y):
                        wrldArray[y][x] = "C"
                elif wrld.monsters_at(x,y):
                    for m in wrld.monsters_at(x,y):
                        wrldArray[y][x] = "M"
                elif wrld.exit_at(x,y):
                    wrldArray[y][x] = "#"
                elif wrld.bomb_at(x,y):
                    wrldArray[y][x] = "@"
                elif wrld.explosion_at(x,y):
                    wrldArray[y][x] = "*"
                elif wrld.wall_at(x,y):
                    wrldArray[y][x] = "W"
                else:
                    tile = False
                    for k,clist in wrld.characters.items():
                        for c in clist:
                            if c.tiles.get((x,y)):
                                wrldArray[y][x] = c.tiles[(x,y)] + "."
                                tile = True
                                break
        return wrldArray
    
    def isCellWalkable(self, worldArray, coords):
        y = coords[0]
        x = coords[1]
        if worldArray[y][x] == "W":
            return False
        return True
    
    def walkableNeighbors(self, worldArray, coords):
        y = coords[0]
        x = coords[1]
        neighbors = []
        if y+1 < len(worldArray):
            if self.isCellWalkable(worldArray, (y+1, x)):
                neighbors.append((y+1, x))
            if x+1 < len(worldArray[0]) and self.isCellWalkable(worldArray, (y+1, x+1)):
                neighbors.append((y+1, x+1))
            if x-1 >= 0 and self.isCellWalkable(worldArray, (y+1, x-1)):
                neighbors.append((y+1, x-1))
        if y-1 >= 0:
            if self.isCellWalkable(worldArray, (y-1, x)):
                neighbors.append((y-1, x))
            if x+1 < len(worldArray[0]) and self.isCellWalkable(worldArray, (y-1, x+1)):
                neighbors.append((y-1, x+1))
            if x-1 >= 0 and self.isCellWalkable(worldArray, (y-1, x-1)):
                neighbors.append((y-1, x-1))
        if x+1 < len(worldArray[0]) and self.isCellWalkable(worldArray, (y, x+1)):
            neighbors.append((y, x+1))
        if x-1 >= 0 and self.isCellWalkable(worldArray, (y, x-1)):
            neighbors.append((y, x-1))
        return neighbors
    
    def cost(self, current, next, monsterCoords):
        global interceptable
        currentY = current[0]
        currentX = current[1]
        nextY = next[0]
        nextX = next[1]
        distance = (((nextY - currentY)**2)+(nextX - currentX)**2)**0.5
        # print("HELP ME: ", monsterCoords)
        cautiousness = 15
        monsterCloseMod = 0
        # print("GO AROUND")
        if monsterCoords != (None, None):
            for coords in monsterCoords:
                # print(coords)
                monsterCoordsY = coords[0]
                monsterCoordsX = coords[1]
                monsterDist = (((monsterCoordsY - nextY)**2)+(monsterCoordsX - nextX)**2)**0.5
                monsterCloseMod += 10**(cautiousness-monsterDist)
        return distance+monsterCloseMod*interceptable
    
    def heuristic(self, goalCoords, coords, monsterCoords):
        global interceptable
        coordsY = coords[0]
        coordsX = coords[1]
        goalCoordsY = goalCoords[0]
        goalCoordsX = goalCoords[1]

        goalDist = (((goalCoordsY - coordsY)**2)+(goalCoordsX - coordsX)**2)**0.5
        goalHeuristic = goalDist

        monsterDistSum = 0

        if monsterCoords != (None, None):
            for coords in monsterCoords:
                monsterCoordsY = coords[0]
                monsterCoordsX = coords[1]
                monsterDistSum += (((monsterCoordsY - coordsY)**2)+(monsterCoordsX - coordsX)**2)**0.5

        monsterHeuristic = monsterDistSum
        return goalHeuristic - monsterHeuristic*interceptable

    
    def canIntercept(self, worldArray, startCoords, goalCoords, monsterCoords):
        global interceptable

        if interceptable:

            interceptable = False
            bestPath = self.aStar(worldArray, startCoords, goalCoords, monsterCoords, False)
            interceptable = True

            stepNum = 0
            for step in bestPath:
                for monsterCoord in monsterCoords:
                    monsterCoord = (monsterCoord[0], monsterCoord[1])
                    curMonsterDist = len(self.aStar(worldArray, monsterCoord, step, (None, None), True))
                    if curMonsterDist-2 <= stepNum:
                        interceptable = True
                        return True
                stepNum += 1
            print("SLICK")
            interceptable = False
            return False
        else:
            print("SLICK")
            interceptable = False
            return False

    def aStar(self, worldArray, startCoords, goalCoords, monsterCoords, isMonster):
        frontier = PriorityQueue()
        frontier.put(startCoords, 0)
        came_from = {}
        cost_so_far = {}
        came_from[startCoords] = None
        cost_so_far[startCoords] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goalCoords:
                break
            
            for next in self.walkableNeighbors(worldArray, current):
                new_cost = cost_so_far[current] + self.cost(current, next, monsterCoords)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goalCoords, next, monsterCoords)
                    frontier.put(next, priority)
                    came_from[next] = current

        step = goalCoords
        finalPath = [step]
        while finalPath[0] != startCoords:
            finalPath.insert(0, came_from[step])
            step = came_from[step]
        return finalPath
    

    def do(self, wrld):
        global interceptable
        # print("HI")
        # print(wrld)
                # Commands
        worldArray = self.getWorld(wrld)
        startWhere = np.where(worldArray == 'C')
        startCoords = (startWhere[0][0], startWhere[1][0])
        goalWhere = np.where(worldArray == '#')
        goalCoords = (goalWhere[0][0], goalWhere[1][0])
        monsterWhere = np.argwhere(worldArray == "M")
        if ((len(monsterWhere) > 0)):
            monsterCoords = [coord.tolist() for coord in monsterWhere]
        else:
            monsterCoords = (None, None)
            interceptable = False
        path = self.aStar(worldArray, startCoords, goalCoords, monsterCoords, False)
        self.canIntercept(worldArray, startCoords, goalCoords, monsterCoords)
        dy = path[1][0] - path[0][0]
        dx = path[1][1] - path[0][1]
        # Execute commands
        print(dy, dx)
        self.move(dx, dy)
        
        # implement a version of a* that uses a heuristic to get optimal path to target
