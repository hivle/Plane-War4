from pygame import *
from math import *
from random import *
import os
size=(width, height)= (450, 700)
screen = display.set_mode(size)


enemy=image.load(os.path.join('resources','HENRY.png'))
enemy=transform.scale(enemy,(50,50))


class npc:
    def __init__ (self, x, y):
        self.x = x
        self.y = y
    def draw(self):
        screen.fill((0,0,0))
        screen.blit(enemy,(self.x,self.y))
        
    def move(self):
        self.y +=1/8
        

count=0
a=randint(0,400)
npc1=npc(a,-50)
n=[]
running=True
while running:

    for e in event.get():       
        if e.type == QUIT:      
            running = False
    for i in range(3):
         n.append(npc1)
    count +=1
    if count==6000:
        a=randint(0,400)
        npc1=npc(a,-50)
        count=1
    npc1.move()
    npc1.draw()
   
    display.flip()

        
