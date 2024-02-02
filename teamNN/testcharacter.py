# This is necessary to find the main code
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

    def evalState(self, world):
        stateScore = 0
        stateProb = 0
        return [stateScore, stateProb]

    def calcMoveProb(self, world):
        prob = 0
        return prob

    def validActions(self, world):
        prob = np.zeros((10,1))
        pass

    def getMonCoords(self, world):
        pass

    def getMonActions(self, world):
        prob = numMonsters*np.zeros((9,9))
        pass

    def doAct(self, world, act):
        pass

    def do(self, world):
        # Your code here
        sensedWorld = world.from_world(world)
        actions = self.validActions(world)
        allMonActions = self.getMonActions(world)
        maxActEval = 0
        bestAct = 0

        for act in actions:
            actEval = 0
            for monActs in allMonActions:
                sensedWorldTemp = world.from_world(sensedWorld)
                self.doAct(sensedWorldTemp, act)
                for monAct in monActs:
                    self.doAct(sensedWorldTemp, monAct)
                eval = self.evalState(sensedWorldTemp)
                prob = self.calcMoveProb(sensedWorldTemp, monActs)
                actEval += eval*prob
            if actEval > maxActEval:
                maxActEval = actEval
                bestAct = act
        
        self.doAct(world, bestAct)
