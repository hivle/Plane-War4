from pygame import *
import os
from random import *

#load the screen
size=(width, height)= (450, 700)
screen = display.set_mode(size)
screen.fill((255,255,255))


#Font for energy and health bar and others
font.init()
arcadefont=font.Font('resources\Fonts\ka1.ttf',10)
arcadefont2=font.Font('resources\Fonts\ka1.ttf',50)
arcadefont3=font.Font('resources\Fonts\ka1.ttf',30)

noenergy = arcadefont.render(("No Energy!!!"), True,(255,0,0))
speedboost = arcadefont.render(("Speed Boost!"),True,(255,255,255))
energyfull = arcadefont.render(("Energy Full"),True,(255,255,255))
regenerate = arcadefont.render(("Resting..."),True,(0,255,0))
healthword = arcadefont.render(("Health"),True,(255,255,255))


clickb=Rect(175,400,120,30)
click = arcadefont3.render(("PLAY"),True,(255,255,255))
click2 = arcadefont3.render(("PLAY"),True,(100,100,100))

exitb=Rect(180,600,120,30)
exit1 = arcadefont3.render(("EXIT"),True,(255,255,255))
exit2 = arcadefont3.render(("EXIT"),True,(100,100,100))

instb=Rect(90,450,300,30)
inst1 = arcadefont3.render(("INSTRUCTIONS"),True,(255,255,255))
inst2 = arcadefont3.render(("INSTRUCTIONS"),True,(100,100,100))

setb=Rect(140,500,180,30)
set1 = arcadefont3.render(("SETTING"),True,(255,255,255))
set2 = arcadefont3.render(("SETTING"),True,(100,100,100))

creditb=Rect(140,550,180,30)
credit1 = arcadefont3.render(("CREDITS"),True,(255,255,255))
credit2 = arcadefont3.render(("CREDITS"),True,(100,100,100))

start=arcadefont.render(("PRESS ARROW KEYS TO MOVE!"),True,(255,255,255))

title= arcadefont2.render(("PLANE"), True,(255,255,255))
title2= arcadefont2.render(("WAR!"), True,(255,255,255))


#Load the background
background=image.load(os.path.join('resources','background.jpg'))
screen.blit(background,(0,0))

bull=image.load(os.path.join('resources','sprites','b7.png'))
bull=transform.scale(bull,(15,15))

#Load the plane
planepic=image.load(os.path.join('resources','plane.png')) 


#load music
mixer.init()
music=mixer.music.load('resources\sound\Street Fighter - Guile Stage.mp3')
mixer.music.play(-1,0)

#The energy and health variable
energy=100
health=100

#Plane speed and bullet speed
speed=2
bspeed=2

learn=0

#Load the menu picture
menupic=image.load(os.path.join('resources','menupicture.jpg'))

planewidth=50
planeheight=50


class plane:
    def __init__ (self, x, y):
        self.x = x
        self.y = y
        self.dir="up"
    def draw(self):
        screen.blit(planepic,(self.x, self.y))
    def move(self, keys):
        if keys[K_w]:
            self.y -= speed
            
        if keys[K_a]:
            self.x -= speed
          
        if keys[K_s]:
            self.y += speed
           
        if keys[K_d]:
            self.x += speed
           
        #Make the plane stay on the screen
        if self.y>650:
            self.y=650
        if self.y<0:
            self.y=0
        if self.x>=405:
            self.x=405
        if self.x<0:
            self.x=0
            
            
            

class bullet:
    def __init__(self, plane):
        self.x = plane.x
        self.y = plane.y
        self.dir = plane.dir
        
    def shoot(self):
        if self.dir=="up":
            self.y -=bspeed
            screen.blit(bull,(self.x+17, self.y-5))
        

#two map positions, everytime the while loop runs both map position add one
mappos1=-68
mappos2=-68


#The while loop for the menu
running=True
run=True
instructions=True
while run:
    for e in event.get():       
        if e.type == QUIT:      
            run=False
            running=False
            instructions=False
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()
    #All the buttons for the menu
    screen.blit(menupic,(0,0))
    screen.blit(title,(120,30))
    screen.blit(title2,(150,110))
    screen.blit(click,(175,400))
    screen.blit(exit1,(180,600))
    screen.blit(inst1,(90,450))
    screen.blit(set1,(140,500))
    screen.blit(credit1,(140,550))
    if clickb.collidepoint(mx,my):
        screen.blit(click2,(175,400))
    if exitb.collidepoint(mx,my):
        screen.blit(exit2,(180,600))
    if instb.collidepoint(mx,my):
        screen.blit(inst2,(90,450))
    if setb.collidepoint(mx,my):
        screen.blit(set2,(140,500))
    if creditb.collidepoint(mx,my):
        screen.blit(credit2,(140,550))
    display.flip()
    #Do stuff after pressing button
    if clickb.collidepoint(mx,my) and mb[0]==1:
            break
    if exitb.collidepoint(mx,my) and mb[0]==1:
            run=False
            running=False
            instructions=False
    if instb.collidepoint(mx,my) and mb[0]==1:
            run=False
            running=False


while instructions:
    for e in event.get():       
        if e.type == QUIT:      
            run=False
            running=False
            instructions=False
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()
    break#################


        
count=0
plane1=plane(195,600)
bullets=[]


while running:
    for e in event.get():       
        if e.type == QUIT:      
            running=False
            
    keys = key.get_pressed()
    mb = mouse.get_pressed()

    
    #Make the map run forever
    if mappos1==0:
        mappos1=-768
    if mappos2==768:
        mappos2=0
    mappos1 +=1
    mappos2 +=1
    screen.blit(background,(0,mappos1))
    screen.blit(background,(0,mappos2))

 
        
    count+=1

    plane1.move(keys)
    plane1.draw()

    speed=2
    bspeed=2


    

    #Draw the energy bar and health bar
    draw.rect(screen,(0,0,255),(20,670,energy,20))
    draw.rect(screen,(0,0,0),(18,668,102,22),2)

    draw.rect(screen,(255,0,0),(340,670,health,20))
    draw.rect(screen,(0,0,0),(338,668,102,22),2)

    #Blit the word "Health"
    screen.blit(healthword,(362,672))


    #make the bullet move faster when moving up so it dosnt look weired
    if keys[K_w]:
        bspeed +=speed
        
    if energy>0:
        if (keys[K_RSHIFT]or keys[K_LSHIFT]) and (keys[K_w]or keys[K_s] or keys[K_d] or keys[K_a]):
            speed +=3
            energy -=1/2
            if keys[K_w]:
                bspeed +=5
    if energy<100:
        energy +=1/8
    if energy==100:
        screen.blit(energyfull,(24,672))
    if 1<energy<100:
        if (keys[K_RSHIFT]or keys[K_LSHIFT]) and(keys[K_w]or keys[K_s] or keys[K_d] or keys[K_a]):
            screen.blit(speedboost,(21,672))
        else:
            screen.blit(regenerate,(26,672))
    
    if energy<=0:
        screen.blit(noenergy,(24,672))


    if keys[K_w]:
        planeheight=45
        learn=1
    if keys[K_a]:
        planewidth=43
        learn=1
    if keys[K_s]:
        planeheight=45
        learn=1
    if keys[K_d]:
        planewidth=43
        learn=1

    planepic=image.load(os.path.join('resources','plane.png')) 
    planepic=transform.scale(planepic,(planewidth,planeheight))

    planewidth=50
    planeheight=50
    
    
    if  count == 1:
        bullets.append(bullet(plane1))
    for b in bullets:
        b.shoot()
    if count == 30:
        count = 0

    #Learn
    if learn==0:
        screen.blit(start,(125,550)) 
        
    

  
    display.flip()
quit()
