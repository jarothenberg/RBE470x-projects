# This is necessary to find the main code
from itertools import product
from queue import PriorityQueue
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
import numpy as np
from entity import CharacterEntity
from colorama import Fore, Back

class TestCharacter(CharacterEntity):

    def getWorld(self, world):
        worldArray = np.array([[" " for x in range(world.width())] for y in range(world.height())])

        for y in range(world.height()):
            for x in range(world.width()):
                if world.characters_at(x,y):
                    for c in world.characters_at(x,y):
                        worldArray[y][x] = "C"
                elif world.monsters_at(x,y):
                    for m in world.monsters_at(x,y):
                        worldArray[y][x] = "M"
                elif world.exit_at(x,y):
                    worldArray[y][x] = "#"
                elif world.bomb_at(x,y):
                    worldArray[y][x] = "@"
                elif world.explosion_at(x,y):
                    worldArray[y][x] = "*"
                elif world.wall_at(x,y):
                    worldArray[y][x] = "W"
                else:
                    tile = False
                    for k,clist in world.characters.items():
                        for c in clist:
                            if c.tiles.get((x,y)):
                                worldArray[y][x] = c.tiles[(x,y)] + "."
                                tile = True
                                break
        return worldArray
    
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
    
    def cost(self, current, next):
        currentY = current[0]
        currentX = current[1]
        nextY = next[0]
        nextX = next[1]

        distance = (((nextY - currentY)**2)+(nextX - currentX)**2)**0.5
        return distance
    
    def heuristic(self, goalCoords, coords):
        coordsY = coords[0]
        coordsX = coords[1]
        goalCoordsY = goalCoords[0]
        goalCoordsX = goalCoords[1]

        distance = (((goalCoordsY - coordsY)**2)+(goalCoordsX - coordsX)**2)**0.5
        return distance
    
    def aStar(self, worldArray, startCoords, goalCoords):
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
                new_cost = cost_so_far[current] + self.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goalCoords, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        step = goalCoords
        finalPath = [step]
        while finalPath[0] != startCoords:
            finalPath.insert(0, came_from[step])
            step = came_from[step]
        return finalPath

    def evalState(self, world):
        stateScore = 0
        stateProb = 0
        return [stateScore, stateProb]

    def calcMoveProb(self, world, monCoords, playerCoords):
        towardsPlayer = 0.2 # 3 cells facing player = 60%
        awayFromPlayer = 0.05 # 3 cells away from player = 15%
        sideFromPlayer = 0.1 # 2 cells side to player = 20%
        noMove = 0.05 # 1 cell no moving = 5%
        path = self.aStar(world, monCoords, playerCoords)
        dy = path[1][0] - path[0][0]
        dx = path[1][1] - path[0][1]
        prob = np.zeros((9,9))

        prob[1][1] = noMove
        if dy == -1:
            prob[0][1] = towardsPlayer
            if dx == 1:
                prob[0][2] = towardsPlayer
                prob[1][2] = towardsPlayer
                prob[0][0] = sideFromPlayer
                prob[2][2] = sideFromPlayer
                prob[1][0] = awayFromPlayer
                prob[2][0] = awayFromPlayer
                prob[2][1] = awayFromPlayer
            elif dx == -1:
                prob[0][0] = towardsPlayer
                prob[1][0] = towardsPlayer
                prob[0][2] = sideFromPlayer
                prob[2][0] = sideFromPlayer
                prob[2][1] = awayFromPlayer
                prob[2][2] = awayFromPlayer
                prob[1][2] = awayFromPlayer
            else:
                prob[0][:] = towardsPlayer
                prob[1][0] = sideFromPlayer
                prob[1][2] = sideFromPlayer
                prob[2][:] = awayFromPlayer
        elif dy == 1:
            prob[2][1] = towardsPlayer
            if dx == 1:
                prob[2][2] = towardsPlayer
                prob[1][2] = towardsPlayer
                prob[0][2] = sideFromPlayer
                prob[2][0] = sideFromPlayer
                prob[0][0] = awayFromPlayer
                prob[1][0] = awayFromPlayer
                prob[0][1] = awayFromPlayer
            elif dx == -1:
                prob[2][0] = towardsPlayer
                prob[1][0] = towardsPlayer
                prob[0][0] = sideFromPlayer
                prob[2][2] = sideFromPlayer
                prob[0][1] = awayFromPlayer
                prob[0][2] = awayFromPlayer
                prob[1][2] = awayFromPlayer
            else:
                prob[2][:] = towardsPlayer
                prob[1][0] = sideFromPlayer
                prob[1][2] = sideFromPlayer
                prob[0][:] = awayFromPlayer
        else:
            prob[0][1] = sideFromPlayer
            prob[2][1] = sideFromPlayer
            if dx == 1:
                prob[:][2] = towardsPlayer
                prob[:][0] = awayFromPlayer
            elif dx == -1:
                prob[:][0] = towardsPlayer
                prob[:][2] = awayFromPlayer
            else:
                #don't think this is possible
                pass

        return prob

    def validActions(self, world):
        prob = np.zeros((10,1))
        pass

    def findMonsters(self,wrld):
        monsters = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                #+= appends empty lists and any list given
                monsterAt = wrld.monsters_at(x,y)
                # print(monsterAt) 
                if(monsterAt != None):
                    monsters += monsterAt
        return monsters

    def getMonCoords(self, world):
        allMonsters = self.findMonsters(world)
        return [(monster.x, monster.y) for monster in allMonsters]

    def getMonActions(self, world):
        prob = numMonsters*np.zeros((9,9))
        pass

    def doAct(self, world, act):
        pass

    def do(self, world):
        # Your code here
        sensedWorld = world.from_world(world)
        playerActions = self.validActions(world)
        allMonActions = self.getMonActions(world)
        numMonActions = 9
        maxActEval = 0
        bestAct = 0
        numMonsters = 2
        for playerAct in playerActions:
            actEval = 0
            allMoves = product(*(range(numMonActions) for _ in range(numMonsters)))
            for monMoves in allMoves:
                # print(combination)
                sensedWorldTemp = world.from_world(sensedWorld)
                self.doAct(sensedWorldTemp, playerAct, monMoves)
                eval = self.evalState(sensedWorldTemp)
                prob = self.calcMoveProb(sensedWorldTemp, monMoves)
                actEval += eval*prob
            if actEval > maxActEval:
                maxActEval = actEval
                bestAct = playerAct
        
        self.doAct(world, bestAct)
