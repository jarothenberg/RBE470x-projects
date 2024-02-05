# This is necessary to find the main code
import sys

sys.path.insert(0, '../bomberman')
# Import necessary stuff
import numpy as np
from entity import CharacterEntity
from colorama import Fore, Back
from game import Game
from world import World 

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
        allMonsters = self.findMonsters(world)
        return [(monster.x, monster.y) for monster in allMonsters]

    def getMonActions(self, world):
        prob = numMonsters*np.zeros((9,9))
        pass


    def scheduelMoveEntity(self, index, movement) -> None:
        
        pass

    def doAct(self, world, act): #-> World:
        pass

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

            
    def do(self, world):
        # Your code here

        print("Test")

        # sensedWorld = world.from_world(world)
        
        # sensedWorld.printit()        
        # self.move(1,1)

        chars = self.getCharacteres(world)
        # print(chars)
        character = chars[0]

        print(character,self)
        # character.dx = 5
        # character.dy = 5

        # actions = [()]   

        monsters = self.getMonsters(world)
        monster = monsters[0] 

        # newWorld = self.doCharacterAction(world,  [(character.x, character.y), [(1,1)]])
        # newWorld = self.doMonsterAction(newWorld, [(monster.x  , monster.y), [(-1,-1)]])

        newWorld = self.doActions(world, [(1,1) , (1,-1)])    
        newWorld = self.doActions(newWorld, [(0,0) , (1,-1)])    


        print("SW: ")
        # print(world)
        newWorld.printit()
        print("ENd SW")
        # print(events)


        # monsterList = self.getMonsters(world)
        # for monster in monsterList:
        #     print(monster.dx, monster.dy)
        #     monster.dx = 0
        #     monster.dy = 0
        #     print(monster.dx, monster.dy)

        '''
        characters = self.getCharacteres(sensedWorld)
        print(characters)

        # player = characters[0]
        # player.move(1,0)

        monsterList = self.getMonsters(sensedWorld)

        monsterMoves = [(monster.dx, monster.dy) for monster in monsterList]
        print(monsterMoves)

        (newWorld, events) = sensedWorld.next()
        print("SW: ")
        # print(world)
        newWorld.printit()
        print("ENd SW")
        print(events)
        #'''


        # monsterCords = self.getMonCoords(sensedWorld)#self.findMonsters(sensedWorld)
        # monCord2 = self.getMonCoords(world)
        
        # print(monsterCords,monCord2)


        # sensedWorld = world.from_world(world)
        # actions = self.validActions(world)
        # allMonActions = self.getMonActions(world)
        # maxActEval = 0
        # bestAct = 0

        # for act in actions:
        #     actEval = 0
        #     for monActs in allMonActions:
        #         sensedWorldTemp = world.from_world(sensedWorld)
        #         self.doAct(sensedWorldTemp, act)
        #         for monAct in monActs:
        #             self.doAct(sensedWorldTemp, monAct)
        #         eval = self.evalState(sensedWorldTemp)
        #         prob = self.calcMoveProb(sensedWorldTemp, monActs)
        #         actEval += eval*prob
        #     if actEval > maxActEval:
        #         maxActEval = actEval
        #         bestAct = act
        
        # self.doAct(world, bestAct)
