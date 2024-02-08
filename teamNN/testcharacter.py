# This is necessary to find the main code
from itertools import product
from queue import PriorityQueue
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
import numpy as np
from entity import CharacterEntity
from colorama import Fore, Back
from world import World
import math
from events import Event

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


    def evalState(self, world: World, monEvents: list[Event], playerEvents: list[Event]): #this will return a "score" which will tell you how desireable the state is
        #implement A* in the eval 
        #or control the depth 
        stateScore = 0  #return score
        #stateProb = 0
        #return [stateScore, stateProb]
        coordsBM = self.bomberManCoords(world) #coords for BomberMan
        for event in playerEvents:
            if event.tpe == Event.CHARACTER_FOUND_EXIT:
                return 1000000
            if event.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                return -1000000
        for event in monEvents:
            if event.tpe == Event.CHARACTER_FOUND_EXIT:
                return 1000000
            elif event.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                return -1000000
        # character = self.getCharacteres(world)[0]
        # coordsBM = [character.x, character.y]
        
        monsterLocs = self.getMonCoords(world) # coords for the monter
        exitLoc = self.exitCoords(world) # coords for exit
        #worldScore = world.scores[self] #is a dictionary { character_name : score } that contains the score of every character in this case getting the score of the character and intergrating it to the function
        
        #weights for score change based on values :)
        monsterDistWeight = 3
        exitDisWeight = 1
        monContribution = 0

        #getting score for monsters
        for monsterLoc in monsterLocs:
            #calculating the Euclidean between the monster and BM
            #disMonToBMan = math.sqrt((monsterLoc[0]- coordsBM[0])**2 + (monsterLoc[1]- coordsBM[1])**2) #distance from BM to Monster
            disMonToBman = len(self.aStar(self.getWorld(world), (coordsBM[1], coordsBM[0]), (monsterLoc[1], monsterLoc[0])))
            monContribution -= 10**(monsterDistWeight-disMonToBman)

        # print(f"Eval From Monsters:\t{monContribution}")

        #getting score from BM to exit (#calculating the A* length between the exit and BM)
        exitToBM = len(self.aStar(self.getWorld(world), (coordsBM[1], coordsBM[0]), (exitLoc[1], exitLoc[0])))
        
        # stateScore -= exitToBM * exitDisWeight + monContribution
        #
        exitContribution = 21 - exitToBM

        # print(f"Eval From Exit Dist:\t{exitContribution}")
        stateScore = exitContribution + monContribution
        # print(f"Total State Evaluation:\t{stateScore}")

        #will add score for bombs later.............

        return stateScore

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

    def getMonsters(self,wrld):
        monsters = []

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                #+= appends empty lists and any list given
                monsterAt = wrld.monsters_at(x,y)
                # print(monsterAt) 
                if(monsterAt != None):
                    monsters += monsterAt
        return monsters

    # def getEntities(self, world, entityName = "monster"):
        # pass

    def getCharacteres(self,wrld):
        characters = []

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                #+= appends empty lists and any list given
                charactersAt = wrld.characters_at(x,y)
                # print(monsterAt) 
                if(charactersAt != None):
                    characters += charactersAt 
        return characters 

    def getMonCoords(self, world):
        allMonsters = self.getMonsters(world)
        return [(monster.x, monster.y) for monster in allMonsters]

    def getMonActions(self, world):
        prob = numMonsters*np.zeros((9,9))
        pass

    #simulated Action 
    def doAct(self, world: World, playerAction: int) -> World:
        # print("0SHIT: ", self.bomberManCoords(world))
        characters = self.getCharacteres(world)
        if(len(characters) > 0):
            character = characters[0] 
            if(playerAction < 9):
                (dx,dy) = self.actionToDxDy(playerAction)
                # newCoords = np.array(self.bomberManCoords(world)) + np.array([dx,dy])
                # if world.wall_at(newCoords[0], newCoords[1]):
                #     (dx,dy) = (0,0)
                character.move(dx,dy)
            else:
                character.move(0,0)
                character.place_bomb()
        
        (newWorld, events) = world.next()
        # print("1SHIT: ", self.bomberManCoords(newWorld))
        return (newWorld, events) 
     
    def doMonsterActs(self, world: World, monsterActions: tuple[int]) -> World:
        # print("0SHIT: ", self.bomberManCoords(world))
        monsters = self.getMonsters(world)
        if(len(monsters) > 0):
            for i, monster in enumerate(monsters):
                if(monsterActions[i] < 9):
                    (dx,dy) = self.actionToDxDy(monsterActions[i])
                    monster.move(dx,dy)
                else:
                    monster.move(0,0)
        
        (newWorld, events) = world.next()
        # print("1SHIT: ", self.bomberManCoords(newWorld))
        return (newWorld, events) 


    def doCharacterActions(self, world: World, actions: list[list[tuple[int, int], list[tuple[int, int]]]]) -> World:
        #actions is a list of list()
        #Each inner list is an action, contains a tuple coodites of where to perform the action 
        #and a list of the dx dy movemnt for each entity at that location.
        for action in actions:
            self.doCharacterAction(self, world, action)
        
    def cancelCharacterAndMonsterMovement(self, world: World) -> World:
        for monster in self.getMonsters(world):
            monster.move(0,0)
        for character in self.getCharacteres(world):
            character.move(0,0)

        return world

    def doCharacterAction(self, world: World, action: list[tuple[int, int], list[tuple[int, int]]]) -> World:
        world = self.cancelCharacterAndMonsterMovement(world)
        
        #'''
        actionPosition = action[0]
        actionMovement = action[1]
        charactersAt = world.characters_at(actionPosition[0], actionPosition[1])
        if(charactersAt != None):
            for i, character in enumerate(charactersAt):
                if(i < len(actionMovement)):
                    #Order specified doesn't really matter, because characters on identical indexes are functionally (and in code, the same)
                    character.move(actionMovement[i][0], actionMovement[i][1])
        #'''
        

        (newWorld, events) = world.next()
        return newWorld
    
    def doMonsterAction(self, world: World, action: list[tuple[int, int], list[tuple[int, int]]]) -> World:
        world = self.cancelCharacterAndMonsterMovement(world)
        
        #'''
        actionPosition = action[0]
        actionMovement = action[1]
        monstersAt = world.monsters_at(actionPosition[0], actionPosition[1])
        if(monstersAt != None):
            for i, monster in enumerate(monstersAt):
                if(i < len(actionMovement)):
                    #Order specified doesn't really matter, because characters on identical indexes are functionally (and in code, the same)
                    # print("MV")
                    monster.move(actionMovement[i][0], actionMovement[i][1])
        #''' 

        (newWorld, events) = world.next()
        return newWorld 
    
    def doActions(self, world: World, actions: list[tuple[int, int]]) -> World:
        #Easier Version where all the movements are stored in one list, no character position, just assumed it is the first character in the index order
        #Assignes movements to all characters first then monsters based on order provided in getMonsters
        #This is one step
        world = self.cancelCharacterAndMonsterMovement(world)

        characters = self.getCharacteres(world)
        monsters = self.getMonsters(world)
        numCharacters = len(characters) 

        print(monsters)

        for i, actionMovement in enumerate(actions):
            if(i < numCharacters):
                characters[i].move(actionMovement[0], actionMovement[1])
            else:
                monsters[i - numCharacters].move(actionMovement[0], actionMovement[1])
        
        (newWorld, events) = world.next()
        return newWorld
    
    def actionToDxDy(self, action: int) -> tuple[int, int]:
        if(action == 0):
            #TL
            dy = -1; dx = -1
        elif(action == 1):
            #TM
            dy = -1; dx = 0
        elif(action == 2):
            #TR
            dy = -1; dx = 1
        elif(action == 3):
            #ML
            dy = 0; dx = -1
        elif(action == 4):
            #MC
            dy = 0; dx = 0
        elif(action == 5):
            #MR
            dy = 0; dx = 1
        elif(action == 6):
            #BL
            dy = 1; dx = -1
        elif(action == 7):
            #BC
            dy = 1; dx = 0
        elif(action == 8):
            #BR
            dy = 1; dx = 1
                
        return (dx,dy)


    def doRealAction(self, world: World, action: int):
        if(action < 9):
            (dx,dy) = self.actionToDxDy(action)
            self.move(dx,dy)
        else:
            self.move(0,0)
            self.place_bomb()
        

    def do(self, world):
        # Your code here
        copyWorld = world.from_world(world)
        # playerActions = self.validActions(world) # 0-9
        playerActions = range(10)
        # allMonActions = self.getMonActions(world) # 0-8
        allMonActions = range(9)
        numMonActions = 9
        maxActEval = -10000000
        bestAct = 0
        numMonsters = len(self.getMonsters(world))


        (monsterMovedWorld, events) = copyWorld.next()
        # monsterMovedWorld.printit()
        #After the monsters Have done their determined action
        monsterMovedWorld = self.cancelCharacterAndMonsterMovement(copyWorld)
        # (monsterMovedWorld, events) = monsterMovedWorld.next()
        # monsterMovedWorld.printit()
        for playerAct in playerActions:
            actEval = 0 # Sum total of this Chance Node
            # print("69SHIT: ", self.bomberManCoords(monsterMovedWorld))
            copyMonsterMoveWorld = monsterMovedWorld.from_world(monsterMovedWorld)
            (afterPlayerMoveWorld, playerEvents) = self.doAct(copyMonsterMoveWorld, playerAct)
            #World After we have done Characters action. 
            afterPlayerMoveWorld = self.cancelCharacterAndMonsterMovement(afterPlayerMoveWorld)

            allMoves = product(*(range(numMonActions) for _ in range(numMonsters)))
            for monMoves in allMoves:
                copyAfterPlayerMove = afterPlayerMoveWorld.from_world(afterPlayerMoveWorld)
                #World after monster has done probabailstic Action
                # print("premonmove: ", self.getMonCoords(copyAfterPlayerMove))
                (afterMonsterProbMove, monEvents) = self.doMonsterActs(copyAfterPlayerMove, monMoves)
                # print(f"Monsters Move: \t{monMoves}")
                eval = self.evalState(afterMonsterProbMove, monEvents, playerEvents)
                # print(eval, "postmonmove: ", self.getMonCoords(afterMonsterProbMove))
                prob = 1/9 # self.calcMoveProb(sensedWorldTemp, monMoves, playerCoords)
                actEval += eval*prob 
        #        
            print(f"Action: {playerAct}, Score: {actEval}, Coords: {self.bomberManCoords(afterPlayerMoveWorld)}")

            if actEval > maxActEval:
                maxActEval = actEval
                bestAct = playerAct
                
            print(f"Best Action: {bestAct}")
        # for monMoves in allMoves:
        #     #Probability Moster makes all of its 9*9 actions
        #     #do monster action
            
        #     for playerAct in playerActions:
                #do player action
                #score. 



        # self.doAct(world, bestAct)
        self.doRealAction(world, bestAct)
        monsterMovedWorld = self.cancelCharacterAndMonsterMovement(copyWorld)
