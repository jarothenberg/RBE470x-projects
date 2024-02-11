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
import time
from sensed_world import SensedWorld

class TestCharacter(CharacterEntity):

    astarwoopie = 0
    depth = 0

    def walkableNeighbors(self, world: World, coords):
        x = coords[0]
        y = coords[1]
        neighbors = []
        if y+1 < world.height():
            if not world.wall_at(x,y+1):
                neighbors.append((x,y+1))
            if x+1 < world.width() and not world.wall_at(x+1,y+1):
                neighbors.append((x+1,y+1))
            if x-1 >= 0 and not world.wall_at(x-1, y+1):
                neighbors.append((x-1, y+1))
        if y-1 >= 0:
            if not world.wall_at(x,y-1):
                neighbors.append((x,y-1))
            if x+1 < world.width() and not world.wall_at(x+1, y-1):
                neighbors.append((x+1, y-1))
            if x-1 >= 0 and not world.wall_at(x-1, y-1):
                neighbors.append((x-1, y-1))
        if x+1 < world.width() and not world.wall_at(x+1, y):
            neighbors.append((x+1, y)) 
        if x-1 >= 0 and not world.wall_at(x-1,y):
            neighbors.append((x-1,y))
        return neighbors
    
    def cost(self, current, next):
        currentX = current[0]
        currentY = current[1]
        nextX = next[0]
        nextY = next[1]

        #distance = (((nextY - currentY)**2)+(nextX - currentX)**2)**0.5
        distance = 1
        return distance
    
    def heuristic(self, goalCoords, coords):
        coordsX = coords[0]
        coordsY = coords[1]
        goalCoordsX = goalCoords[0]
        goalCoordsY = goalCoords[1]

        distance = (((goalCoordsY - coordsY)**2)+(goalCoordsX - coordsX)**2)**0.5
        #distance = 1
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

    def aStar(self, world: World, startCoords, goalCoords):
        startTime = time.time()
        frontier = PriorityQueue()
        #frontier.put(startCoords, 0)

        frontier.put((0,startCoords))

        came_from = {}
        cost_so_far = {}
        came_from[startCoords] = None
        cost_so_far[startCoords] = 0

        while not frontier.empty():
            current = frontier.get()[1]


            if current == goalCoords:
                break
            
            for next in self.walkableNeighbors(world, current):
                new_cost = cost_so_far[current] + self.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goalCoords, next)
                    frontier.put((priority, next))

                    came_from[next] = current

        step = goalCoords
        finalPath = [step]
        while finalPath[0] != startCoords:
            finalPath.insert(0, came_from[step])
            step = came_from[step]
        self.astarwoopie += time.time() - startTime
        #print(len(finalPath))
        return finalPath
    
    def checkEvents(self, world, events):
        for event in events:
            if event.tpe == Event.CHARACTER_FOUND_EXIT:
                return world.scores['me']
            if event.tpe == Event.CHARACTER_KILLED_BY_MONSTER or event.tpe == Event.BOMB_HIT_CHARACTER:
                return -1000000
        return 0

    #3 A*
    def evalState(self, world: World, events: list[Event]): #this will return a "score" which will tell you how desireable the state is
        stateScore = 0#-world.scores['me']  #return score
        # print("checking state score")

        eventScore = self.checkEvents(world, events)
        if(eventScore != 0):
            return eventScore + stateScore

        coordsBM = self.bomberManCoords(world) #coords for BomberMan
        # print(coordsBM)
        exitLoc = self.exitCoords(world) # coords for exit   
        exitToBM = len(self.aStar(world, (coordsBM[0], coordsBM[1]), (exitLoc[0], exitLoc[1])))
        monsterLocs = self.getMonCoords(world) # coords for the monter

        #weights for score change based on values :)
        monsterDistWeight = 2
        exitDisWeight = 1
        monContribution = 0

        #getting score for monsters
        for monsterLoc in monsterLocs:
            disMonToBman = len(self.aStar(world, (coordsBM[0], coordsBM[1]), (monsterLoc[0], monsterLoc[1])))
            monContribution -= 10**(monsterDistWeight-disMonToBman)
            monContribution = 0
            #print(disMonToBman)
            if disMonToBman <= 2:
                # print("HI?")
                return -1000000

        exitContribution = 21 - exitToBM

        # print(f"Eval From Exit Dist:\t{exitContribution}")
        stateScore = exitContribution + monContribution
        # print(f"Total State Evaluation:\t{stateScore}")

        #will add score for bombs later.............

        # print(f"STATE SCORE {stateScore}")

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

    #Currently not being used. Maybe delete later
    def validActions(self, world):
        prob = np.zeros((10,1))
        pass

    def getMonsters(self,world):
        monsters = []
        for x in range(world.width()):
            for y in range(world.height()):
                #+= appends empty lists and any list given
                monsterAt = world.monsters_at(x,y)
                # print(monsterAt) 
                if(monsterAt != None):
                    monsters += monsterAt
        return monsters

    def getCharacteres(self,world):
        characters = []
        for x in range(world.width()):
            for y in range(world.height()):
                #+= appends empty lists and any list given
                charactersAt = world.characters_at(x,y)
                # print(monsterAt) 
                if(charactersAt != None):
                    characters += charactersAt 
        return characters 

    def getMonCoords(self, world):
        allMonsters = self.getMonsters(world)
        return [(monster.x, monster.y) for monster in allMonsters]

    #currently not being used maybe delete later?
    def getMonActions(self, world):
        prob = numMonsters*np.zeros((9,9))
        pass

    #simulated Action 
    def doAct(self, world: World, playerAction: int) -> World:
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
        return (newWorld, events) 
     
    def doMonsterActs(self, world: World, monsterActions: tuple[int]) -> World:
        monsters = self.getMonsters(world)
        if(len(monsters) > 0):
            for i, monster in enumerate(monsters):
                if(monsterActions[i] < 9):
                    (dx,dy) = self.actionToDxDy(monsterActions[i])
                    monster.move(dx,dy)
                else:
                    monster.move(0,0)
        
        (newWorld, events) = world.next()
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

    def cancelCharacterMovement(self, world: World) -> World:
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

        #print(monsters)

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
        elif(action == 4 or action == 9):
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
    
    def dxDyToAction(self, dxDy: tuple[int, int]) -> int:
        dx = dxDy[0]
        dy = dxDy[1]
        action = 0
        if(dy == -1 and dx == -1):
            #TL
            action = 0
        elif(dy == -1 and dx == 0):
            #TM     
            action = 1
        elif(dy == -1 and dx == 1):
            #TR
            action = 2
        elif(dy == 0 and dx == -1):
            #MR
            action = 3
        elif(dy == 0 and dx == 0):
            #MC
            action = 4        
        elif(dy == 0 and dx == 1):
            #MR
            action = 5       
        elif(dy == 1 and dx == -1):
            #BL
            action = 6
        elif(dy == 1 and dx == 0):
            #BC
            action = 7        
        elif(dy == 1 and dx == 1):
            #BR
            action = 8   
            
        return (action)


    def doRealAction(self, world: World, action: int):
        if(action < 9):
            (dx,dy) = self.actionToDxDy(action)
            self.move(dx,dy)
        else:
            self.move(0,0)
            self.place_bomb()
        

    def validPlayerMove(self, act, state):
        bmCoords = self.bomberManCoords(state)
        newCoord = tuple(np.array(self.actionToDxDy(act)) + np.array(bmCoords))
        if newCoord in self.walkableNeighbors(state, bmCoords) or act == 4 or act == 9:
            return True
        else:
            return False
        
    def validMonMove(self, acts, state):
        monCoords = self.getMonCoords(state)  
        for monNum, monAct in enumerate(acts):
            monCoord = monCoords[monNum]
            newCoord = tuple(np.array(self.actionToDxDy(monAct)) + np.array(monCoord))
            if newCoord not in self.walkableNeighbors(state, monCoord) or monAct == 4:
                return False
        return True

    def expectimaxSearch(self, state: World, depth) -> int: #This returns and action, Which in our case is a number between 0-9
        #For All Actions
        #Return Action with Greatest Expected value
        
        playerActions = [8, 6, 2, 0, 7, 5, 3, 1, 4, 9]
        bestAction = 0
        maxEval = -1000000
        for playerAction in playerActions:
            if not self.validPlayerMove(playerAction, state):
                continue

            (worldAfterPlayerAction, events) = self.doAct(state, playerAction)

            worldAfterPlayerAction = self.cancelCharacterAndMonsterMovement(worldAfterPlayerAction)

            actionExpectedValue = self.expValue(worldAfterPlayerAction, events, depth - 1)

            if(actionExpectedValue > maxEval):
                maxEval = actionExpectedValue
                bestAction = playerAction 

            print(f"Action: {playerAction}, Score: {actionExpectedValue}")
            print(f"Best Action: {bestAction}")

        return bestAction

    
    
    def maxValue(self, state: World, events, depthRemaining: int) -> float: #Returns the Value Of the world
        #If Terminal State, Then Rerturn Utility
        eventScore = self.checkEvents(state, events)
        if(eventScore != 0):
            return eventScore

        if(depthRemaining == 0):
            # print("max value evalstate")
            eval = self.evalState(state, events)
            # print(f"Max EVAL: {eval}")
            return eval

        playerActions = [8, 6, 2, 0, 7, 5, 3, 1, 4, 9]
        #V = -inf
        maxEval = -1000000000
        for playerAction in playerActions:
            if not self.validPlayerMove(playerAction, state):
                continue

            (worldAfterPlayerAction, newEvents) = self.doAct(state, playerAction)

            worldAfterPlayerAction = self.cancelCharacterAndMonsterMovement(worldAfterPlayerAction)

            #V = Max(Expected Values)
            actionExpectedValue = self.expValue(worldAfterPlayerAction, newEvents, depthRemaining - 1)

            if(actionExpectedValue > maxEval):  
                maxEval = actionExpectedValue

        return maxEval 
    
    def sign(self, num: float) -> int:
        if(num == 0):
            return 0
        else:
            return int(num/abs(num))

    def monsterStraightTowards(self, characterPos: tuple[int, int], monCoords: tuple[int, int]) -> int: #int Action To take

        diffTuple = [0,0]
        diffTuple[0] = characterPos[0] - monCoords[0]
        diffTuple[1] = characterPos[1] - monCoords[1]
        
        #DX,DY
        diffTuple[0] = self.sign(diffTuple[0])
        diffTuple[1] = self.sign(diffTuple[1])

        return self.dxDyToAction(tuple(diffTuple))


    def probabiltyMonsterAction(self, actions: tuple, state: World) -> float: #Probabilty of the monster making the action
        
        #Old Code
        '''
        numMonsters = len(self.getMonsters(state))
        numMonActions = 9
        return 1/(numMonActions**numMonsters)
        '''

        #Ryan
        
        # numMonsters = len(actions)
        # monCoords = self.getMonCoords(state)
        # character = self.getCharacteres(state)[0]
        # characterPos = (character.x, character.y)

        # idealActions = ()
        # for i in range(numMonsters):
        #     monsterStraightMove = self.monsterStraightTowards(characterPos, monCoords[i])
        #     idealActions += (monsterStraightMove,)

        # if(actions == idealActions):
        #     return 1
        # else:
        #     return 0

        #'''

        # JACK CODE
        numMonsters = len(self.getMonsters(state))
        monCoords = self.getMonCoords(state)
        idealActions = [0] * numMonsters
        bmCoord = self.bomberManCoords(state)
        idealMovesDxDy = [0,0] * numMonsters
        numMonActions = 9
        for monNum, monCoord in enumerate(monCoords):
            monPath = self.aStar(state, monCoord, tuple(bmCoord))
            nextMonMove = monPath[1]
            idealMovesDxDy[monNum] = tuple(np.array(nextMonMove) - np.array(monCoord))
            idealActions[monNum] = self.dxDyToAction(tuple(idealMovesDxDy))
        # print(idealActions, np.array(actions))
        monTowards = 0
        idealMonTowards = 0
        for idealMondxdy, mondxdy in zip(idealActions, actions):
            idealdx, idealdy = self.actionToDxDy(idealMondxdy)
            mondx, mondy = self.actionToDxDy(mondxdy)
            # if mondx == idealdx and mondy == idealdy:
            #     return 1 / (1/9 * numMonActions**numMonsters)
            # else:
            #     return 0
            if (mondx == idealdx and mondy != -idealdy) or (mondy == idealdy and mondx != -idealdx):
                monTowards += 1
            if (mondx == idealdx and mondy == idealdy):
                idealMonTowards += 1

        if self.depth >= 4:
            if idealMonTowards == numMonsters:
                return 1
            else:
                return 0
        else:
            if monTowards == 0:
                return (0.25) / (6/9 * numMonActions**numMonsters)
            else:
                return (0.75 * monTowards/numMonsters) / (3/9 * numMonActions**numMonsters)
        

    def expValue(self, state: World, events, depthRemaining: int) -> float: #Returns the Utlity Value of the world
        # print(f"EXP: Depth Remaining{depthRemaining}")
        eventScore = self.checkEvents(state, events)
        if(eventScore != 0):
            return eventScore

        if(depthRemaining == 0):
            # print("expval evalstate depth")
            eval = self.evalState(state, events)
            # print(f"EVAL: {eval}")
            return eval

        #V = 0
        sumVal = 0

        # monsterActions = range(9)
        numMonActions = 9
        numMonsters = len(self.getMonsters(state))

        if(numMonsters == 0):
            # print("expval evalstate mons")
            return self.evalState(state, events)

        else:
            allMoves = product(*(range(numMonActions) for _ in range(numMonsters)))
            #9*9=81 Runs

            for monMoves in allMoves:
                if not self.validMonMove(monMoves, state):
                    continue

                probAction = self.probabiltyMonsterAction(monMoves, state)
                # print("probaction: ", probAction)
                if(probAction == 0):
                    continue

                (worldAfterMonsterAction, newEvents) = self.doMonsterActs(state, monMoves)
                
                worldAfterMonsterAction = self.cancelCharacterAndMonsterMovement(worldAfterMonsterAction)
                maxVal = self.maxValue(worldAfterMonsterAction, newEvents, depthRemaining - 1)
                # print(f"MV: {maxVal}")
                sumVal += probAction * maxVal
            return sumVal

    def distance(self, tuple1, tuple2):
        x1 = tuple1[0]
        y1 = tuple1[1]
        x2 = tuple2[0]
        y2 = tuple2[1]

        distance = (((y2 - y1)**2)+(x2 - x1)**2)**0.5
        return distance
    
    def nearestMonsterDistance(self, world: World):
        bmCoords = self.bomberManCoords(world)
        monsterCoords = self.getMonCoords(world)

        smallestDistance = 1000

        for monsterCoord in monsterCoords:
            # dist = self.distance(characterPos, monsterPos)
            dist = len(self.aStar(world, (monsterCoord[0], monsterCoord[1]), (bmCoords[0], bmCoords[1])))
            # print(dist)
            if(dist < smallestDistance):
                smallestDistance = dist

        return smallestDistance

    def distToDepth(self, nearestDist):
        if(nearestDist < 3):
            return 4
        else:
            return 2           

    def do(self, world):
        world = self.cancelCharacterMovement(world) # idk why but this let us move
        # world = SensedWorld.from_world(world)

        (monsterMovedWorld, events) = world.next()
        # monsterMovedWorld.printit()
        #After the monsters Have done their determined action
        monsterMovedWorld = self.cancelCharacterAndMonsterMovement(monsterMovedWorld)
        if self.checkEvents(monsterMovedWorld, events) == 0:
        #'''
            nearDist = self.nearestMonsterDistance(monsterMovedWorld)
        # print(f"ND {nearDist}")

            self.depth = self.distToDepth(nearDist)

            bestAction = self.expectimaxSearch(monsterMovedWorld, self.depth)
            self.doRealAction(world, bestAction)

        # '''

        # bestAction = self.expectimaxSearch(monsterMovedWorld, 4)


        # self.doAct(world, bestAct)
        #'''
        # self.cancelCharacterAndMonsterMovement(world)
