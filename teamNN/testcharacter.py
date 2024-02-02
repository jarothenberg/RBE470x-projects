# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

class TestCharacter(CharacterEntity):

    counter = 0

    def findMonstersExp(self, wrld):
        monsters = []
        for index, monstersOnSquare in wrld.monsters.items():
           monsters += monstersOnSquare 
        return monsters
    
    def findMonsterSquaresExp(self, wrld):
        return wrld.monsters.items()
    
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

    def do(self, wrld):
        # Your code here
        print(self.counter)

        # for index, monsterlist in wrld.monsters.items():

        mlist = self.findMonstersExp(wrld)
        print(mlist)
        mlist2 = self.findMonsters(wrld)
        print(mlist2)
            # for m in mlist:
                # print(f"Name: {m.name} at ({m.x},{m.y})")
        
        if(self.counter % 2 == 0):
            # self.move(1,0)
            # self.dx = 6
            # self.dy = 17
            self.dx = 2 
            self.dy = -1

        else:
            pass
            self.dx = 0
            self.dy = 0
            # self.move(-1,1)


        self.counter += 1
        
        
