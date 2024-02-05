# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
import numpy as np
import math

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
    

    def bomberManCoords(self, world):
        bombMan = []
        for x in range(world.width()):
            for y in range(world.height()):
                if world.characters_at(x,y):
                    bombMan = [x, y]

        return bombMan
    
    def exitCoords(self, world):
        exitC = []
        for x in range(world.width()):
            for y in range(world.height()):
                if world.exit_at(x,y):
                    exitC = [x, y]

        return exitC 



    def evalState(self, world): #this will return a "score" which will tell you how desireable the state is
        stateScore = 0  #return score
        #stateProb = 0
        #return [stateScore, stateProb]
        coordsBM = self.bomberManCoords(world) #coords for BomberMan
        monsterLocs = self.getMonCoords(world) # coords for the monter
        exitLoc = self.exitCoords(world) # coords for exit
        worldScore = world.scores[self] #is a dictionary { character_name : score } that contains the score of every character in this case getting the score of the character and intergrating it to the function
        
        #weights for score change based on values :)
        monsterDistWeight = -0.2
        exitDisWeight = -0.1

        #getting score for monsters
        for monsterLoc in monsterLocs:
            #calculating the Euclidean between the monster and BM
            disMonToBMan = math.sqrt((monsterLoc[0]- coordsBM[0])**2 + (monsterLoc[1]- coordsBM[1])**2 ) #distance from BM to Monster
            stateScore += disMonToBMan * monsterDistWeight

        #getting score from BM to exit (#calculating the Euclidean between the exit and BM)
        exitToBM =  math.sqrt((exitLoc[0]- coordsBM[0])**2 + (exitLoc[1]- coordsBM[1])**2 )
        stateScore += exitToBM * exitDisWeight

        #will add score for bombs later.............

        return stateScore

    
    def calcMoveProb(self, world):
        prob = 0
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
