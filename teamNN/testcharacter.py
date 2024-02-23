# This is necessary to find the main code
import sys

import numpy as np
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from world import World
from events import Event
import random
import time
from queue import PriorityQueue


class TestCharacter(CharacterEntity):

    gamma = 1
    alpha = 0.01
    weights = [0.0, 0.0, 0.0]
    # np.save('weights.npy',weights)
    def __init__(self, name, avatar, x, y):
        CharacterEntity.__init__(self, name, avatar, x, y)
        self.weights = np.load('weights.npy')

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
                step = goalCoords
                finalPath = [step]
                while finalPath[0] != startCoords:
                    finalPath.insert(0, came_from[step])
                    step = came_from[step]
                #print(len(finalPath))
                return finalPath
            
            for next in self.walkableNeighbors(world, current):
                new_cost = cost_so_far[current] + self.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goalCoords, next)
                    frontier.put((priority, next))

                    came_from[next] = current

        return []   

    def doAct(self, world: World, playerAction: int) -> World:
        characters = self.getCharacteres(world)
        if(len(characters) > 0):
            character = characters[0] 
            if(playerAction < 9):
                (dx,dy) = self.actionToDxDy(playerAction)
                character.move(dx,dy)
            else:
                character.move(0,0)
                character.place_bomb()
        
        (newWorld, events) = world.next()
        return (newWorld, events) 

    def getCharacteres(self,world: World) -> list[CharacterEntity]:
        characters = []
        for x in range(world.width()):
            for y in range(world.height()):
                #+= appends empty lists and any list given
                charactersAt = world.characters_at(x,y)
                # print(monsterAt) 
                if(charactersAt != None):
                    characters += charactersAt 
        return characters 
    
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
    
    def validPlayerMove(self, s, a):
        bmCoords = self.bomberManCoords(s)
        newCoord = tuple(np.array(self.actionToDxDy(a)) + np.array(bmCoords))
        if newCoord in self.walkableNeighbors(s, bmCoords) or a == 4 or a == 9:
            return True
        else:
            return False
  
    def bomberManCoords(self, world):
        bombMan = (None, None)
        for x in range(world.width()):
            for y in range(world.height()):
                if world.characters_at(x,y):
                    bombMan = (x, y)
        return bombMan
    
    def exitCoords(self, world):
        for x in range(world.width()):
            for y in range(world.height()):
                if world.exit_at(x,y):
                    exitC = (x, y)
        return exitC 
    

    def getBomb(self, world: World):
        for x in range(world.width()):
            for y in range(world.height()):
                bombAt = world.bomb_at(x,y)
                if(bombAt != None):
                    return bombAt
        return None 
    
    def bombCoords(self, world):
        bomb = self.getBomb(world)
        if bomb != None:
            return (bomb.x, bomb.y)
        else:
            return (None, None)

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
    
    def doRealAction(self, world: World, action: int):
        if(action < 9):
            (dx,dy) = self.actionToDxDy(action)
            self.move(dx,dy)
        else:
            self.move(0,0)
            self.place_bomb()

    def bombTime(self, world):
        bomb = self.getBomb(world)
        maxBombTime = 10
        if bomb != None:
            return bomb.timer
        else:
            return maxBombTime
        

    def getExplodeCoords(self, world):
        bombCoord = self.bombCoords(world)
        explodeCoords = [bombCoord]
        bombRange = 4
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        if bombCoord == (None, None):
            return []
        for explodeDir in directions:
            for explodeDist in range(1,bombRange+1):
                checkCoord = tuple(np.array(explodeDir)*explodeDist + np.array(bombCoord))
                if (checkCoord[0] >= 0 and checkCoord[0] < world.width()) and (checkCoord[1] >= 0 and checkCoord[1] < world.height()):
                    explodeCoords.append(checkCoord)
                    # print(checkCoord)
                    if (world.wall_at(checkCoord[0], checkCoord[1])):
                        break
        return explodeCoords
    
    def explodeDist(self, world):
        explodeCoords = self.getExplodeCoords(world)
        minDist = 15
        for coord in explodeCoords:
            dist = self.distance(coord, self.bomberManCoords(world))
            if dist < minDist:
                minDist = dist
        return minDist
    
            
    def distance(self, tuple1, tuple2):
        x1 = tuple1[0]
        y1 = tuple1[1]
        x2 = tuple2[0]
        y2 = tuple2[1]

        distance = (((y2 - y1)**2)+(x2 - x1)**2)**0.5
        return distance
    

    #Contion of world AFTER action (Features of S')
    def features(self, s: World, a: int): # TODO
        # print("UPDATING FEATURES")
        (s_prime, events) = self.doAct(s,a)
        # feature0 = len(self.aStar(s, self.bomberManCoords(s), self.exitCoords(s)))

        eventScore = self.checkEvents(s_prime, events)
        if(eventScore != 0):
            return [0] * len(self.weights)
        
        # print("HELP:",[event.tpe for event in events])
        # print(self.explodeDist(s_prime))
        feature0 = self.distance(self.bomberManCoords(s_prime),self.exitCoords(s))
        feature1 = self.bombTime(s_prime)
        feature2 = self.explodeDist(s_prime)
        features = [feature0, feature1, feature2]
        return features

    def all_a_prime(self, s: World): # TODO
        allAPrime = []
        for a in range(10):
            if(self.validPlayerMove(s, a)):
                allAPrime.append(a)
        return allAPrime

    def reward(self, s_prime: World) -> float: # TODO
        return s_prime.scores['me']

    #Aproximation of Evaluation/Score after action a has been performed
    def Q(self, s: World, a: int) -> float:
        qEval = 0
        for weight, feature in zip(self.weights, self.features(s,a)):
            qEval += weight*feature
        return qEval
    
    def checkEvents(self, world, events):
        for event in events:
            if event.tpe == Event.CHARACTER_FOUND_EXIT:
                return world.scores['me']
            if event.tpe == Event.CHARACTER_KILLED_BY_MONSTER or event.tpe == Event.BOMB_HIT_CHARACTER:
                return -1000000
        return 0
    
    def updateWeights(self, s: World, a: int) -> None:
        (s_prime, events) = self.doAct(s,a)

        eventScore = self.checkEvents(s_prime, events)
        if(eventScore != 0):
            return

        #The Value from making a step
        r = self.reward(s_prime) - self.reward(s)
        print("R:",r)
        maxQ = 0
        for a_prime in self.all_a_prime(s_prime):
            curQ = self.Q(s_prime, a_prime)
            if curQ > maxQ:
                maxQ = curQ
        delta = (r + self.gamma * maxQ) - self.Q(s, a)
        # print(delta, r)
        featureValues = self.features(s,a)
        # print("updating weights")
        for index in range(len(self.weights)):
            # print("Weight before:",self.weights[index], self.alpha*delta*featureValues[index])
            self.weights[index] += self.alpha*delta*featureValues[index]
            # print("Weight after:",self.weights[index])

    def do(self, wrld):
        # Your code here
        print("RUNNING DO")
        
        #Choose A Random Action
        chosenAction = random.randint(0,9)

        print(f"Chosen Action: {chosenAction}")

        self.doRealAction(wrld, chosenAction)

        #Update Weights
        self.updateWeights(wrld, chosenAction)

        print(self.weights)

        np.save('weights.npy', np.array(self.weights))
