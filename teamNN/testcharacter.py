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

    gamma = 0.9
    alpha = 0.01
    livingExpense = 0
    percentRandom = 0.0
    isGuided = False
    coordsBM = (0,0)

    def __init__(self, name, avatar, x, y):
        CharacterEntity.__init__(self, name, avatar, x, y)
        self.weights = np.load('weights.npy')

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
                charactersAt = world.characters_at(x,y)
                if(charactersAt != None):
                    characters += charactersAt 
        return characters 
    
    def actionToDxDy(self, action: int) -> tuple[int, int]:
        if(action == 0):#TL
            dy = -1; dx = -1
        elif(action == 1):#TM
            dy = -1; dx = 0
        elif(action == 2):#TR
            dy = -1; dx = 1
        elif(action == 3):#ML
            dy = 0; dx = -1
        elif(action == 4 or action == 9):#MC
            dy = 0; dx = 0
        elif(action == 5):#MR
            dy = 0; dx = 1
        elif(action == 6):#BL
            dy = 1; dx = -1
        elif(action == 7):#BC
            dy = 1; dx = 0
        elif(action == 8):#BR
            dy = 1; dx = 1
                
        return (dx,dy)
    
    def dxDyToAction(self, dxDy: tuple[int, int]) -> int:
        dx = dxDy[0]
        dy = dxDy[1]
        action = 0
        if(dy == -1 and dx == -1):#TL
            action = 0
        elif(dy == -1 and dx == 0):#TM     
            action = 1
        elif(dy == -1 and dx == 1):#TR
            action = 2
        elif(dy == 0 and dx == -1):#MR
            action = 3
        elif(dy == 0 and dx == 0):#MC
            action = 4        
        elif(dy == 0 and dx == 1):#MR
            action = 5       
        elif(dy == 1 and dx == -1):#BL
            action = 6
        elif(dy == 1 and dx == 0):#BC
            action = 7        
        elif(dy == 1 and dx == 1):#BR
            action = 8   
        return (action)
    
    def validPlayerMove(self, s, a):
        if self.coordsBM == (None, None):
            return False
        newCoord = tuple(np.array(self.actionToDxDy(a)) + np.array(self.coordsBM))
        if newCoord in self.walkableNeighbors(s, self.coordsBM) or a == 4 or (a == 9 and self.getBomb(s) == None):
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
        explodeCoords = []
        explosions = self.getBombExplosions(world)
        for explosion in explosions:
            explosionXY = (explosion.x, explosion.y)
            explodeCoords.append(explosionXY)
        return explodeCoords
    
    def getExplodeFutureCoords(self, world):
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
                    if (world.wall_at(checkCoord[0], checkCoord[1])):
                        break
        return explodeCoords
    
    def explodeFutureDist(self, world):
        explodeCoords = self.getExplodeFutureCoords(world)
        minDist = self.distance((0,0),(7,10))
        for coord in explodeCoords:
            dist = self.distance(coord, self.coordsBM)
            if dist < minDist:
                minDist = dist
        return minDist
    
    def explodeDist(self, world):
        explodeCoords = self.getExplodeCoords(world)
        minDist = self.distance((0,0),(7,10))
        for coord in explodeCoords:
            dist = self.distance(coord, self.coordsBM)
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
    def getMonsters(self,wrld):
        monsters = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                monsterAt = wrld.monsters_at(x,y)
                if(monsterAt != None):
                    monsters += monsterAt
        return monsters
    
    def getBombExplosions(self,wrld):
        explosions = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                expAt = wrld.explosion_at(x,y)
                if(expAt != None):
                    explosions += [expAt]
        return explosions
    
    def getMonCoords(self, world):
        allMonsters = self.getMonsters(world)
        return [(monster.x, monster.y) for monster in allMonsters]
    

    def getNearestMonsterDistEuclidian(self, s: World):
        monsterLocs = self.getMonCoords(s)
        if len(monsterLocs) == 0:
            nearestMonster = self.distance((0,0),(7,18))

        if len(monsterLocs) == 1:
            nearestMonster = self.distance(self.coordsBM, monsterLocs[0])

        if len(monsterLocs) == 2:
            firstMonster = self.distance(self.coordsBM, monsterLocs[0])
            secondMonster = self.distance(self.coordsBM, monsterLocs[1])
            if firstMonster < secondMonster:
                nearestMonster = firstMonster
            else:
                nearestMonster = secondMonster

        return nearestMonster
    

    def findClosestCornerDist(self, s: World):
        corners = []
        for x in range(s.width()):
            for y in range(s.height()):
                #corner on the bottom left
                if (y+1 == s.height() or (y+1 < s.height() and s.wall_at(x, y+1))) and ((x-1 == -1 and y+1 == s.height()) or (y+1 < s.height() and s.wall_at(x-1, y+1))) and (x-1 == -1 or s.wall_at(x-1, y)):
                    corners.append((x,y))
                #corner on the top left
                if (x-1 == -1 or s.wall_at(x-1, y)) and ((x-1 == -1 and y-1 == -1) or s.wall_at(x-1, y-1)) and (y-1 == -1 or s.wall_at(x, y-1)):
                    corners.append((x,y))
                #corner on the bottom right
                if (y+1 == s.height() or (y+1 < s.height() and s.wall_at(x, y+1))) and ((x+1 == s.width() and y+1 == s.height()) or ((x+1 < s.width() and y+1 < s.height() and s.wall_at(x+1, y+1))) or (x+1 == s.width())) and (x+1 == s.width() or (x+1 < s.width() and s.wall_at(x+1, y))):
                    corners.append((x,y))
                #corner on the top right
                if (x+1 == s.width() or (x+1 < s.width() and s.wall_at(x+1, y))) and ((x+1 == s.width() and y-1 == -1) or (x+1 < s.width() and s.wall_at(x+1, y-1)) or (x+1 == s.width())) and (y-1 == -1 or s.wall_at(x, y-1)):
                    corners.append((x,y))

        shortestDistance = -10
        for corner in corners:
            disCornerToBman = self.distance(self.coordsBM, corner)
            if shortestDistance == -10 or disCornerToBman < shortestDistance:
                shortestDistance = disCornerToBman
            
        return shortestDistance
    
    def normalizeDistFeature(self, distance):
        return 1/(1+distance)


    #Contion of world AFTER action (Features of S')
    def features(self, s: World, a: int): # TODO

        actionMove = np.array(self.actionToDxDy(a))
        self.coordsBM = tuple(np.array(self.coordsBM) + actionMove)
        placedbomb = False
        if a == 9: 
            placedbomb = True
        feature0 = self.normalizeDistFeature(self.distance(self.coordsBM,self.exitCoords(s))) #distance from you to the exit
        feature2 = self.normalizeDistFeature(self.explodeDist(s))**(self.explodeDist(s)/2.5) #Explosion Distance
        feature4 = self.normalizeDistFeature(self.getNearestMonsterDistEuclidian(s))**(self.getNearestMonsterDistEuclidian(s)/7.5) #distance of the nearest monster to BomberMan    
        feature7 = self.normalizeDistFeature(self.findClosestCornerDist(s))**(self.findClosestCornerDist(s)/2) #finds the closest corner to BomberMan
        feature8 = placedbomb == True
        feature9 = self.normalizeDistFeature(self.explodeFutureDist(s))/((self.bombTime(s)+1))
        features = [feature0, 0, feature2, 0, feature4, 0, 0, feature7, feature8, feature9]
        self.coordsBM = self.bomberManCoords(s)

        return features

    def all_a_prime(self, s: World): # TODO
        allAPrime = []
        for a in range(10):
            if(self.validPlayerMove(s, a)):
                allAPrime.append(a)
        return allAPrime

    def reward(self, s_prime: World, events=None) -> float: # TODO
        if events != None and self.checkEvents(s_prime, events) == -1000000:
            return -2 * s_prime.time
        return s_prime.scores['me']

    #Aproximation of Evaluation/Score after action a has been performed
    def Q(self, s: World, a: int) -> float:
        qEval = 0
        for weight, feature in zip(self.weights, self.features(s,a)):
            qEval += weight*feature
        return qEval
    
    def qAct(self, s: World) -> int:
        self.coordsBM = self.bomberManCoords(s)
        maxQ = -float('inf')#0
        all_a = self.all_a_prime(s)
        bestA = all_a[0]
        for a in self.all_a_prime(s):
            qVal = self.Q(s, a)
            print("qVal:",qVal,a)
            if qVal > maxQ:
                maxQ = qVal
                bestA = a
        print("bestA:",bestA)
        return bestA
    
    def checkEvents(self, world, events):
        for event in events:
            if event.tpe == Event.CHARACTER_FOUND_EXIT:
                return world.scores['me']
            if event.tpe == Event.CHARACTER_KILLED_BY_MONSTER or event.tpe == Event.BOMB_HIT_CHARACTER:
                return -1000000
        return 0
    
    def updateWeights(self, s: World, a: int) -> None:
        (s_prime, events) = self.doAct(s,a)
        featureValues = self.features(s,a)

        bombPrev = self.getBomb(s)
        bombNext = self.getBomb(s_prime)

        #The Value from making a step
        r = self.reward(s_prime, events) - self.reward(s) - self.livingExpense

        if(bombPrev == None and bombNext != None):
            print("PLACED BOMB")
            r += 100

        all_a = self.all_a_prime(s_prime)
        if(len(all_a) == 0):
            maxQ = 0
        else:
            maxQ = -float('inf')
        for a_prime in self.all_a_prime(s_prime):
            curQ = self.Q(s_prime, a_prime)
            if curQ > maxQ:
                maxQ = curQ
        delta = (r + self.gamma * maxQ) - self.Q(s, a)
        for index in range(len(self.weights)):
            self.weights[index] += self.alpha*delta*featureValues[index]

                
    def interactive(self):
        # Commands
        dx, dy = 0, 0
        # Handle input
        for c in input("How would you like to move (w=up,a=left,s=down,d=right,b=bomb)? "):
            if 'w' == c:
                dy -= 1
            if 'a' == c:
                dx -= 1
            if 's' == c:
                dy += 1
            if 'd' == c:
                dx += 1
            if 'b' == c:
                return 9
        return self.dxDyToAction((dx,dy))


    def do(self, wrld):
        # Your code here
        # print("RUNNING DO")
        #Choose A Random Action

        if self.isGuided:
            chosenAction = self.interactive()
        elif random.uniform(0,1) < self.percentRandom:
            chosenAction = random.randint(0,9)
            print("RAND")
        else:
            chosenAction = self.qAct(wrld)  
        
        # print(f"Chosen Action: {chosenAction}")

        self.doRealAction(wrld, chosenAction)

        #Update Weights
        # self.updateWeights(wrld, chosenAction)

        print(self.weights)

        np.save('weights.npy', np.array(self.weights))
