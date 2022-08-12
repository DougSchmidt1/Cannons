## Initial Cannon Game Attempt ##
# ALL VALUES IN METRIC
#----CRITICAL ADJUSTMENT TO THE FOLLOWING VARIABLE-------#
'''
    4) Run from icon (executable)
'''
#8/(rho_b*(V_muzz**2)*np.pi*(R_b**4))
#https://en.wikipedia.org/wiki/Ballistic_coefficient#Ballistics
#import pandas as pd
import pygame as pg
import numpy as np
import sys
from pygame import mixer

#Colors for pygame
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
TEAL =  (  0, 100, 255)
GREEN = (  0, 255,   0)
GUN   = ( 73,  87,  42)
RED =   (255,   0,   0)
ORANGE = (255, 185,  110)
GREY = (200,  200, 200)
COLORS = [BLACK,WHITE,BLUE,ORANGE,RED,GREY,TEAL]
pg.init()

# IMAGES
#bgraw = pg.image.load(r"C:\Users\dougi\Documents\Python\Cannons\background.bmp")
bgraw = pg.image.load("background.bmp")
CANNONS = pg.image.load('CANNONS2.bmp')
controls = pg.image.load('controls.bmp')
Ltank = pg.image.load('LeftTank.png')
Rtank = pg.image.load('RightTank.png')
bomb = pg.image.load('bomb.bmp')
hellfire = pg.image.load('hellfiredrop.bmp')
hellfire_drop = pg.image.load('hellfire.bmp')
bullet = pg.image.load('bullet.bmp')
SAAM = pg.image.load('SAAM.bmp')
explode = pg.image.load('explosion.png')
gunblast = pg.image.load('gunblast.bmp')
B2 = pg.image.load('B2.bmp')
F16a = pg.image.load('f16_scaled.bmp')
A10 = pg.image.load('A-10.bmp')
F22 = pg.image.load('F22.bmp')
F35 = pg.image.load('F35.bmp')
F16abombed = pg.image.load('f16_bombed.bmp')
F22bombed = pg.image.load('F22bombed.bmp')
A10bombed = pg.image.load('A-10bombed.bmp')
B2bombed = pg.image.load('B2bombed.bmp')
F35bombed = pg.image.load('F35bombed.bmp')
menutank = pg.image.load('Tank.bmp')
smokepuff = pg.image.load('smoke.bmp')
GroundExp1 = pg.image.load('groundExp.bmp')
GroundExp2 = pg.image.load('groundExp2.bmp')
AirExp1 = pg.image.load('exp2.bmp')
AirExp2 = pg.image.load('airexp.bmp')
[twidth,theight] = Ltank.get_rect()[2:]
a = theight//2
b = twidth//2

class Env:
    class Proj:
        def __init__(self):
            self.Dcoef = 500.0
            R_b = 0.060 #m
            M_b = 10 #kg4
            self.partial = 0.5 * (self.Dcoef*np.pi*(R_b**2))/M_b*Env().tstep
            self.Vorig = self.V_muzz = 1670  #m/s, see M829 armor piercing round https://en.wikipedia.org/wiki/M829
            self.V_scale = 1.0 #adjust via window dimensions
            #self.vol_num = 3
    def __init__(self,Gmult=1,bg = bgraw):
        #1 - 10 difficulty level
        Gshift = [2,5,10,20,35,50]
        M_e = 5.9722E24 #kg
        R_e = 6.375E6 #m  (Range from Polar 6.351E6 to 6.378E6
        G = 6.67408E-11 #m^3/(kg*s^2), #Fg = GMm/R^2
        
        FPS = 90
        
        rho_b = (11343 + 7700)/2 #average of lead and steel densities
        self.threat_names = ['F16a','A10','B2','F35','F22']
        self.gamestate = 'MainMenu'
        self.gamediff = 1
        self.threat_list      = []
        self.bomb_list        = []
        self.agm_list         = []
        self.bullet_list      = []
        self.groundexplosions = []
        self.airexplosions    = []
        self.nukes            = []
        self.cloud_list       = []
        self.ground = 0.856327
        self.text_effects = 50
        self.controls = False
        self.pause = False
        self.tstep=1/FPS 
        self.g = G*M_e/(R_e**2) #m/s^2
        self.Gshift = [Gmult*k for k in Gshift]
        self.Gspec = Gshift[3]
        self.ang_step = 2/FPS
        self.dmg_limit = 500
        self.hit_damage = self.dmg_limit // 3
        self.hitrad = 2
        self.fire_spacing = 60
        self.screen_width = self.max_width = bgraw.get_width()
        self.screen_height = self.max_height = bgraw.get_height()        
        #Natural Values
    def statechange(self,statename):
        if statename.lower() == self.gamestate.lower():
            return -1
        else:
            self.gamestate = statename
            if statename == "NewGame":
                self.buildthreats()
            elif statename == "MainMenu":
                self.threat_list.clear()
                self.bomb_list.clear()
            elif statename == "ResumeGame":
                print('placeholder')
            return 1
    def buildthreats(self):
        self.Gspec = self.Gshift[round(self.gamediff // 2)]
        self.hit_damage = int(self.dmg_limit / (10-self.gamediff))
        for i in range(self.gamediff):
            name = self.threat_names[np.random.randint(0,len(self.threat_names))]
            inLib = {'name':           name,
                     'seedheight':     np.random.randint(100,400),
                     'speed':          [6,4,3,7,9][self.threat_names.index(name)],
                     'points':         [300,400,500,600,800][self.threat_names.index(name)],
                     'direct':         ['left','right'][np.random.randint(0,2)],
                     'timeout':        (5E3)//self.gamediff}
                     
            thr = Threat(
                eval(inLib['name']),inLib['seedheight'],inLib['speed'],inLib['points'],EXPimg = eval('%sbombed' % inLib['name']),direction = inLib['direct'],timeout=inLib['timeout'])
            self.threat_list.append(thr)
    def delete_all(self):
        self.threat_list       = []
        self.bomb_list         = []
        self.bullet_list       = []
        self.agm_list          = [] 
        self.groundexplosions  = []
        self.airexplosions     = []
        self.nukes              = []
        self.cloud_list        = []
        

env = Env()
env.screen_width = int(bgraw.get_width())
env.screen_height = int(bgraw.get_height())
#rho_data = np.array(pd.read_excel(r'C:\Users\dougi\Downloads\cannons\Python\air_density_table.xlsx','Reduced',2))

class Cloud:
    def __init__(self):
        self.image = pg.image.load('cloud%d.bmp' % np.random.randint(1,5))
        self.xspeed = np.random.randint(1,3)
        env.cloud_list.append(self)
        self.pos = self.image.get_rect()
        self.pos.left = -self.image.get_width()
        self.pos.bottom = np.random.randint(env.screen_height)*0.3
    def move(self):
        self.pos.left += self.xspeed
        if self.pos.left > env.screen_width:
            self.pos.left = -self.image.get_width()
            self.xspeed = np.random.randint(3,5)
        elif self.pos.left < -self.image.get_width():
            self.pos.left = env.screen_width
            self.xspeed = np.random.randint(3,5)
    def update(self):
        self.move()
        screen.blit(self.image,(self.pos.centerx,self.pos.centery))
        
class Tank:
    def __init__(self, xpos = Env().screen_width/2, ypos = .825*Env().screen_height, can_ang=np.pi/3, proj = Env().Proj()): #xpos=env.screen_width//2,ypos=env.screen_height-100):
        self.Vadj = proj.V_scale
        self.dmg_limit = 400
        self.score = 0
        self.xspeed = 2
        self.state = self.damage =  0    
        self.Vorig = self.V_muzz = 1670  #m/s, see M829 armor piercing round https://en.wikipedia.org/wiki/M829
        self.xlast = self.xpos = self.loc = xpos
        self.ypos = ypos
        self.image = Rtank
        self.half = self.image.get_width()/2
        self.gunlen = 50 
        self.old_ang = self.can_ang = can_ang
        self.barreltip_y = env.screen_height - self.gunlen*np.sin(self.can_ang)
        self.barreltip_x = self.xpos + self.gunlen*np.cos(self.can_ang) #can_pos
        self.pos = self.image.get_rect() 
    def turn(self):
        self.can_ang = np.pi-self.can_ang
    def shoot(self):
        img = pg.transform.rotate(gunblast,self.can_ang)
        screen.blit(img,(int(self.barreltip_x)-b-10, int(self.barreltip_y)-26))
        Bullet(int(self.barreltip_x)-b-10, int(self.barreltip_y)-26,self.Vadj*t1.V_muzz,self.can_ang)
        screen.blit(img,(int(self.barreltip_x)-10, int(self.barreltip_y)-26))
    def update(self):
        temp = self.state
        self.loc = int(self.xpos)
        if self.xlast < self.loc:
            self.state = 0    
            self.image = Rtank
        elif self.xlast > self.loc:
            self.state = 1
            self.image = Ltank            
        if self.state != temp:
            self.turn()
        if self.state:
            if t1.can_ang < 2*np.pi/3:
                t1.can_ang = 2*np.pi/3
            elif t1.can_ang > np.pi:
                t1.can_ang = np.pi
        else:
            if t1.can_ang > np.pi/3:
                t1.can_ang = np.pi/3
            elif t1.can_ang < 0:
                t1.can_ang = 0
        self.xlast = self.loc 
    def aim_adjust(self,rat):
        self.barreltip_y = rat*env.screen_height - self.gunlen * np.sin(self.can_ang)
        self.barreltip_x = self.xpos + self.gunlen*np.cos(self.can_ang) #can_pos
    def draw(self,rat,env):
        #pg.draw.aaline(screen, GUN, [t1.loc-b, (rat*env.screen_height)+a],[barreltip_x-b, (barreltip_y)+a], 6)
        self.update()
        self.aim_adjust(rat)
        pg.draw.line(screen, GUN, [self.loc-b, (rat*env.screen_height)],[self.barreltip_x-b, (self.barreltip_y)], 4)
        pg.draw.circle(screen,GUN,[int(self.barreltip_x)-b, int(self.barreltip_y)],4)
        screen.blit(t1.image,(t1.loc - twidth, 0.782*env.screen_height))
    def reset(self,xpos = Env().screen_width/2, ypos = .825*Env().screen_height, can_ang=np.pi/3):
        #xpos=env.screen_width//2,ypos=env.screen_height-100):
        self.state = self.damage = 0
        self.xlast = self.xpos = self.loc = xpos
        self.ypos = ypos
        self.old_ang = self.can_ang = can_ang
        self.image = Rtank
        self.score = 0

class Bullet:
    def __init__(self,xpos,ypos,speed,ang,image=bullet):
        self.xpos = xpos
        self.ypos = ypos
        self.xvel = speed*np.cos(t1.can_ang) 
        self.yvel =-speed*np.sin(t1.can_ang)
        self.image = bullet
        self.half = self.image.get_width()/2
        self.ang = ang 
        self.curr_image = pg.transform.rotate(self.image,self.ang)
        self.state = 0
        play_sound('gun')
        self.pos = self.image.get_rect() 
        FPS = 120
        self.tstep=1/FPS
        Dcoef = 500.0
        R_b = 0.060 #m
        M_b = 10 #kg4
        self.partial = 0.5 * (Dcoef*np.pi*(R_b**2))/M_b*Env().tstep
        self.pos = self.image.get_rect()
        env.bullet_list.append(self)
    def freefall(self,env):
        self.yvel += env.Gspec*self.tstep
        #self.xvel -= rho_interp(self.ypos)*self.partial
        self.ang = np.rad2deg(np.arctan(self.xvel/self.yvel))
        self.curr_image = pg.transform.rotate(self.image,self.ang)
        self.xpos += self.xvel*self.tstep
        self.ypos += self.yvel*self.tstep
        if not (0 < self.xpos < env.screen_width):
            if self.xpos < 0:
                self.xpos = env.screen_width #-self.image.get_width()
            if self.xpos > env.screen_width:
                self.xpos = 0
        elif self.ypos < 0:
            self.state = 5
    def update(self,env):
        '''Update collision state to:
            1 : passive explosion, no damage
            2 : destroyed threat
            3 : hit tank
            4 : hit bomb
            5 : shot too high, left screen
            6 : hit AGM'''
        if collision_detect(self.xpos,self.ypos,env.threat_list):
            self.state = 2
            self.image = explode
            self.ypos -= self.image.get_height()
            self.xpos -= self.image.get_width()//2
            play_sound('planehit')
        elif collision_detect(self.xpos,self.ypos,env.bomb_list):
            self.state = 4
            self.image = explode
            self.ypos -= self.image.get_height()
            self.xpos -= self.image.get_width()//2
            play_sound('bulletbomb')
        elif collision_detect(self.xpos,self.ypos,env.agm_list):
            self.state = 6
            self.image = explode
            self.ypos -= self.image.get_height()
            self.xpos -= self.image.get_width()//2
            play_sound('bulletbomb')
        elif self.ypos > env.ground*env.screen_height:
            if tank_collide(self.xpos,t1):
                self.state = 3
            else:
                self.state = 1
            self.image = explode
            self.ypos -= self.image.get_height()
            self.xpos -= self.image.get_width()//2
            play_sound('tankhit')
        else: self.freefall(env)
    
############################ - ADVERSARY - #################################

class Bomb:
    def __init__(self,xpos,ypos,speed):
        self.ylast = self.xpos = xpos
        self.xlast = self.ypos = ypos
        self.xvel = 75*speed*env.tstep*20 #(avg flight mph / assigned in-game fighter speed)
        self.yvel = 0
        if self.xvel <0:
            self.image = pg.transform.flip(bomb,True,False)
        else:
            self.image = bomb
        self.half = self.image.get_width()/2
        self.halfy = self.image.get_height()/2
        self.explode = explode
        self.ang = 0
        self.curr_image = pg.transform.rotate(self.image,self.ang)
        self.state = 0
        play_sound('bombdrop')
        self.tstep= env.tstep
        Dcoef = 500.0
        R_b = 0.060 #m
        M_b = 10 #kg4
        self.partial = 0.5 * (Dcoef*np.pi*(R_b**2))/M_b*self.tstep
        self.pos = self.image.get_rect()
        env.bomb_list.append(self)
    def freefall(self,env):
        self.xlast = self.xpos
        self.ylast = self.ypos
        self.yvel += env.Gspec*self.tstep
        #self.xvel -= rho_interp(self.ypos)*self.partial
        self.ang = -np.rad2deg(np.arctan(self.yvel/self.xvel))
        self.curr_image = pg.transform.rotate(self.image,self.ang)
        self.xpos += self.xvel*self.tstep
        self.ypos += self.yvel*self.tstep
        if self.xpos > env.screen_width:
            self.xpos = -bomb.get_width()
        elif self.xpos < -bomb.get_width():
            self.xpos = env.screen_width
    def update(self,env):
        '''Check upon impact with the ground for collisions:
            state = 3: collided with tank
            state = 2: collided with bullet
            state = 1: no collision'''
        if self.ypos > env.ground*env.screen_height:
            GroundExplosion(self.xpos,self.ypos)
            if tank_collide(self.xpos,t1):
                self.state = 3
            else:
                self.state = 2
            play_sound('bulletmiss')
        else: self.freefall(env)
        
class AGM:
    def __init__(self,xpos,ypos,speed):
        self.ylast = self.xpos = xpos
        self.xlast = self.ypos = ypos
        self.ystart = ypos
        self.xvel = 75*speed*env.tstep*20  #(avg flight mph / assigned in-game fighter speed)
        self.yvel = 0
        self.ang = 0
        self.angDel = 0
        self.score = 5000
        self.area = 0
        self.state = 0 
        self.manouver_lim = 0.4 #deg/clock cycle
        self.impulse = 7.0
        self.tstep= env.tstep
        self.count= 0 
        self.halfpuff = smokepuff.get_width()//2
        # Dcoef = 500.0
        # R_b = 0.060 #m
        # M_b = 10 #kg4
        # self.partial = 0.5 * (Dcoef*np.pi*(R_b**2))/M_b*self.tstep
        if self.xvel <0:
            self.image = pg.transform.flip(hellfire,True,False)
            self.drop = pg.transform.flip(hellfire_drop,True,False)
            self.dir = -1
        else:
            self.image = hellfire
            self.drop = hellfire_drop
            self.dir = 1
        self.curr_image = pg.transform.rotate(self.image,self.ang)
        self.half = self.image.get_width()/2
        self.halfy = self.image.get_height()/2
        self.pos = self.image.get_rect()
        self.explode = explode
        self.smoketrail = []
        play_sound('bombdrop') 
        env.agm_list.append(self)
    def freefall(self,env):
        if self.ylast > (self.ystart+self.halfy*3):
            play_sound('missile')
            self.count += 1
            self.powered()
        else:
            self.xlast = self.xpos
            self.ylast = self.ypos
            self.yvel += env.Gspec*self.tstep
            #self.xvel -= rho_interp(self.ypos)*self.partial
            self.ang = -np.rad2deg(np.arctan(self.yvel/self.xvel))
            self.curr_image = pg.transform.rotate(self.image,self.ang)
            self.xpos += self.xvel*self.tstep
            self.ypos += self.yvel*self.tstep
            if self.xpos > env.screen_width:
                self.xpos = -self.image.get_width()
                self.smoketrail = []
            elif self.xpos < -self.image.get_width():
                self.xpos = env.screen_width
                self.smoketrail = []
    def powered(self):
        self.xlast = self.xpos
        self.ylast = self.ypos
        self.smokecheck()
        #self.xvel -= rho_interp(self.ypos)*self.partial        
        self.calculate()
        self.curr_image = pg.transform.rotate(self.drop,self.ang)
        if self.xpos > env.screen_width:
            self.xpos = -self.image.get_width()
            self.smoketrail = []
        elif self.xpos < -self.image.get_width():
            self.xpos = env.screen_width
            self.smoketrail = []
    def calculate(self):
        deltas = [t1.pos.centerx-self.xlast, t1.pos.centery-self.ylast]
        calcAng = -self.dir*np.rad2deg(np.arctan(deltas[1]/deltas[0]))
        last = self.angDel 
        self.angDel = calcAng-self.ang
        if abs(self.angDel) > self.manouver_lim:
            self.steer(last)
        self.xpos += self.xvel*self.tstep
        self.ypos += self.yvel*self.tstep
    def steer(self,last):
        # P = 0.5; I = 0.4; D = 0.4
        # #print(self.angDel)
        # delErr = self.angDel - last
        # self.area += (self.angDel * self.tstep)
        # adjustment = ((-P*self.angDel + I*self.area + D*delErr)) #self.manouver_lim)
        # print('Missile Angle=%d' %self.ang)
        # print('Target - missile angle = %d\n' % self.angDel)
        # print('XVEL = %d' % self.xvel)
        if self.angDel < -self.manouver_lim/2:
            self.ang -= self.manouver_lim #- I*self.area - D*delErr 
        elif self.angDel > self.manouver_lim/2: 
            self.ang += self.manouver_lim #- I*self.area - D*delErr         
        self.xvel += self.dir*self.impulse*np.cos(np.deg2rad(self.ang)) #comp[0]*self.impulse*np.cos(self.ang)        
        self.yvel += -self.dir*self.impulse*np.sin(np.deg2rad(self.ang))           #comp[1]*self.impulse*np.sin(self.ang)  + env.Gspec*self.tstep
    def smokecheck(self):
        if self.count % 4 == 0:
            self.count = 0 
            self.smoketrail.append((self.xpos-self.halfpuff*self.dir,self.ypos-self.dir*self.halfpuff))
        for i,puff in enumerate(self.smoketrail):
            puffshift = (len(self.smoketrail)-i) + 3*(-1)**i - 3*i%2
            screen.blit(smokepuff,(puff[0],puff[1]-puffshift))    
    def update(self,env):
        '''Check upon impact with the ground for collissions:
            state = 3: collided with tank
            state = 2: no collision
            state = 1: collided with bullet'''
        if self.ypos > env.ground*env.screen_height:
            GroundExplosion(self.xpos,self.ypos)
            if tank_collide(self.xpos,t1):
                self.state = 3
            else:
                self.state = 2
            play_sound('bulletmiss')
        else: self.freefall(env)      
        
class Threat:
    def __init__(self, image, height, speedseed, score = 300, EXPimg = B2bombed, direction='right', timeout=2000):
        if direction.lower() == 'right':
            self.vx = np.random.randint(speedseed-1,speedseed+1)
        else:
            self.vx = -np.random.randint(speedseed-1,speedseed+1)
            image = pg.transform.flip(image,True,False)
            EXPimg = pg.transform.flip(EXPimg,True,False)
        self.yspeed = np.random.randint(speedseed-3,speedseed-1)
        self.vy =self.yspeed 
        self.cyclecount = 0
        if timeout:
            self.timeout = np.random.randint(timeout//4,timeout)
        else:
            self.timeout = 1E15
        self.cyclemax = np.random.randint(2,5) + 1     
        self.service_floor = 0.4 + 0.25*np.random.random()
        self.service_ceil = .8 + .2*np.random.random()   
        self.image = image
        self.explode = EXPimg
        self.state = 0
        self.half = self.image.get_width()/2
        self.halfy = self.image.get_height()/2
        self.bombcount = 0
        self.ang = -np.rad2deg(np.arctan(self.vy/self.vx))/2
        self.curr_image = pg.transform.rotate(self.image,self.ang)
        self.score = score
        self.pos = self.image.get_rect().move(self.yspeed, height)
    def drop(self):
        self.bombcount += 1
        weapons = ['AGM','Bomb'][np.random.randint(0,2)]
        if self.bombcount > self.timeout:
            exec('%s((self.pos.left+self.pos.right)/2,(self.pos.bottom+self.pos.top)/2,self.vx)' % weapons)
            self.bombcount = 0
    def move(self):
        ''' Assign images and sounds per threat state accorind to the following:
        state = 2: planehit
        state = 3: tankhit
        state = 4: crash''' 
        self.xlast = self.pos.centerx
        self.ylast = self.pos.centery
        if self.state:
            if self.state == 1:                
                self.vy += env.Gspec*Env().tstep/3
                self.ang = -np.rad2deg(np.arctan(self.vy/self.vx))
                self.curr_image = pg.transform.rotate(self.image,self.ang)
                self.pos = self.pos.move(self.vx,self.vy)
                if self.pos.left > env.screen_width:
                    self.pos.left = -self.image.get_width()
                elif self.pos.left < -self.image.get_width():
                    self.pos.left = env.screen_width
                if self.pos.bottom > env.ground*env.screen_height:
                    if tank_collide(self.pos.centerx,t1):
                        self.state = 3
                    else: self.state = 4 
                    MiniNuke(self.xlast,self.ylast)
            if self.state == 2:                
                self.curr_image = explode
                AirExplosion(self.xlast,self.ylast)   
        else:
            self.drop()
            self.pos = self.pos.move(self.vx,self.vy)
            if self.pos.left > env.screen_width:           
                self.pos.left = -self.image.get_width()
                self.cyclecount += 1
                if self.cyclecount > self.cyclemax:
                    play_sound('flyby')
                    self.cyclecount = 0 
                    self.cyclemax = np.random.randint(2,5) + 1
                    self.vy = self.yspeed = -self.yspeed
                    self.vx = np.random.randint(4,6)
                    self.ang = -self.ang    
                    self.curr_image = pg.transform.rotate(self.image,self.ang)
                    self.pos = self.pos.move(self.vx,self.vy)
                self.cyclecount += 1
            elif self.pos.right < 0:
                self.pos.left = env.screen_width
                self.cyclecount += 1
                if self.cyclecount > self.cyclemax:
                    play_sound('flyby')
                    self.cyclecount = 0 
                    self.cyclemax = np.random.randint(2,5) + 1
                    self.vy = self.yspeed = -self.yspeed
                    self.vx = -np.random.randint(4,6)
                    self.ang = -self.ang    
                    self.curr_image = pg.transform.rotate(self.image,self.ang)
                    self.pos = self.pos.move(self.vx,self.vy)
                self.cyclecount += 1
            if self.pos.bottom > (1-self.service_floor)*env.screen_height:
                self.pos.bottom = (1-self.service_floor)*env.screen_height
                self.vy = 0
                self.curr_image = pg.transform.rotate(self.image,0)           
            if self.pos.top < (1-self.service_ceil)*env.screen_height:
                self.pos.top = (1-self.service_ceil)*env.screen_height
                self.vy = 0
                self.curr_image = pg.transform.rotate(self.image,0)
                         
class Button():
    def __init__(self, txt, location, action, bg=WHITE, fg=BLACK, size=(120, 30), font_name="Comic Sans", font_size=14):
        self.color = bg  # the static (normal) color
        self.bg = bg  # actual background color, can change on mouseover
        self.fg = fg  # text color
        self.size = size
        self.font = pg.font.SysFont(font_name, font_size)
        self.txt = txt
        self.txt_surf1 = self.font.render(self.txt, 1, BLUE)
        self.txt_surf2 = self.font.render(self.txt, 1, self.fg)
        self.txt_rect1 = self.txt_surf1.get_rect(center=[s//2 for s in self.size])
        self.txt_rect2 = self.txt_surf2.get_rect(center=[s//2 - 1 for s in self.size])
        self.surface = pg.surface.Surface(size)
        self.rect = self.surface.get_rect(center=location)
        self.call_back_ = action
    def draw(self):
        self.mouseover()
        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf1, self.txt_rect1)
        self.surface.blit(self.txt_surf2, self.txt_rect2)
        screen.blit(self.surface, self.rect)
    def mouseover(self):
        self.bg = self.color
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = GREY  # mouseover color
    def call_back(self):
        self.call_back_()

class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """
    def __init__(self, file_name,w,h):
        """ Constructor. Pass in the file name of the sprite sheet. """
        self.sprite_sheet = pg.image.load(file_name).convert()
        self.imgAttr(w,h)
    def imgAttr(self,w,h):
        xdim = self.sprite_sheet.get_width()
        ydim = self.sprite_sheet.get_height()
        xdenom = 2; ydenom = 1
        while xdim/xdenom >= w:
            xdenom += 1
            if ydim / ydenom >= h:
                ydenom += 1
        self.numel = xdenom*ydenom
        self.rows = ydenom + 1
        self.columns = xdenom
        #print('rows = %f columns = %f' % (self.rows,self.columns))
        self.frame_width = xdim//xdenom
        self.frame_height = ydim//ydenom
    def get_image(self, x, y, width, height, alpha_val = 255, colorkey = BLACK):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """
        image = pg.Surface([width, height]).convert()
        image.set_alpha(alpha_val)
        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0,0), (x, y, width, height))
        image.set_colorkey(colorkey)
        return image

class AirExplosion(pg.sprite.Sprite):
    ''' Explosion animation to occur upon aerial impacts '''
    def __init__(self,xpos,ypos,imgseed = "airexp.png", transp_color = BLACK, w=65, h=65):
        super().__init__()
        self.explode = []
        self.level = None
        sprite_sheet = SpriteSheet(imgseed,w,h)
        width = sprite_sheet.frame_width
        height = sprite_sheet.frame_height
        alpha= 255
        count = 0
        for row in range(sprite_sheet.rows):
            for col in range(sprite_sheet.columns):
                image = sprite_sheet.get_image(
                    row*width+1, col*height+1, width, height, alpha_val = alpha, colorkey = transp_color)    
                self.explode.append(image)
                alpha -= alpha // sprite_sheet.numel
                count += 1
        self.xpos = xpos
        self.ypos = ypos
        self.halfx = width//2
        self.halfy = height//2
        self.image = self.explode[0]
        self.frame = 0
        self.rect = self.image.get_rect()
        env.airexplosions.append(self)
    def update(self,index):   
        if self.frame < len(self.explode):
            self.image = self.explode[self.frame]
            screen.blit(self.image,(
            self.xpos - self.halfx, self.ypos - 2*self.halfy)) 
        else:
            self.kill_instance(index)
        self.frame += 1
    def kill_instance(self,index):
        del env.airexplosions[index]

class MiniNuke(pg.sprite.Sprite):
    """Explosion animation to occur upon ground impacts"""
    def __init__(self,xpos,ypos,imgseed = 'groundExp2.bmp', transp_color = BLACK, w=125, h=91):
        super().__init__()
        self.explode = []
        self.level = None
        sprite_sheet = SpriteSheet(imgseed,w,h)
        width = 124
        height = 90
        alpha= 255
        count = 0
        for row in range(5):
            for col in range(5):
                image = sprite_sheet.get_image(
                    row*width+1, col*height+1, width, height, alpha_val = alpha, colorkey = transp_color)    
                self.explode.append(image)
                #alpha -= alpha // sprite_sheet.numel
                count += 1
        #print('%f images displayed' % count)
        self.xpos = xpos
        self.ypos = ypos
        self.halfx = width//2
        self.halfy = height//2
        self.image = self.explode[0]
        self.frame = 0
        self.rect = self.image.get_rect()
        env.nukes.append(self)
    def update(self,index):   
        if self.frame < len(self.explode):
            self.image = self.explode[self.frame]
            screen.blit(self.image,(
                self.xpos - self.halfx, self.ypos - 2*self.halfy)) 
        else:
            self.kill_instance(index)
        self.frame += 1
    def kill_instance(self,index):
        del env.nukes[index]

class GroundExplosion(pg.sprite.Sprite):
    """Explosion animation to occur upon ground impacts"""
    def __init__(self,xpos,ypos,imgseed = 'groundExp.bmp', transp_color = BLACK, w=151, h=176):
        super().__init__()
        self.explode = []
        self.level = None
        sprite_sheet = SpriteSheet(imgseed,w,h)
        width = sprite_sheet.frame_width
        height = sprite_sheet.frame_height
        alpha= 255
        count = 0
        for row in range(sprite_sheet.rows):
            for col in range(sprite_sheet.columns):
                image = sprite_sheet.get_image(
                    row*width+1, col*height+1, width, height, alpha_val = alpha, colorkey = transp_color)    
                self.explode.append(image)
                #alpha -= alpha // sprite_sheet.numel
                count += 1
        print('%f images displayed' % count)
        self.xpos = xpos
        self.ypos = ypos
        self.halfx = width//2
        self.halfy = height//2
        self.image = self.explode[0]
        self.frame = 0
        self.rect = self.image.get_rect()
        env.groundexplosions.append(self)
    def update(self,index):   
        if self.frame < len(self.explode):
            self.image = self.explode[self.frame]
            screen.blit(self.image,(
                self.xpos - self.halfx, self.ypos - 2*self.halfy)) 
        else:
            self.kill_instance(index)
        self.frame += 1
    def kill_instance(self,index):
        del env.groundexplosions[index]

# env = Env()
# env.screen_width = int(bgraw.get_width())
# env.screen_height = int(bgraw.get_height())
# #rho_data = np.array(pd.read_excel(r'C:\Users\dougi\Downloads\cannons\Python\air_density_table.xlsx','Reduced',2))

def backtoMenu():
    env.gamestate = 'MainMenu'
    env.Gspec = env.Gshift[0]
    env.delete_all()
    t1.reset()
    MainMenu(screen,IMAGES,env,t1)
    
def quit_press():
    print('Quitting to main menu')
    env.delete_all()
    backtoMenu()
    
def exit_press():
    print('Thanks for playing.')
    pg.quit()
    sys.exit()
    
def controls_page():
    env.controls = True

def new_game():
    env.gamestate = 'NewGame'
    env.delete_all()
    t1.score = 0    
    GameLoop(screen,IMAGES,env,t1)
    print('Starting New Game...')
    
def resume_menu():
    env.gamestate = 'MainMenu'
    env.controls = env.pause = False

def mousebuttondown(buttons):
    pos = pg.mouse.get_pos()
    try:
        for button in buttons:
            if button.rect.collidepoint(pos):
                button.call_back()
    except:
        if buttons.rect.collidepoint(pos):
            buttons.call_back()
    
def play_sound(switch, duration = 1500, vol = 1.0):
    mixer.music.pause()
    turret.set_volume(0.20)
    exec('%s.set_volume(%s)' % (switch,vol))
    exec('%s.play(loops=0, maxtime = %s )' % (switch,duration))
    mixer.music.unpause()

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def message_display(text, loc = [env.screen_width/2,env.screen_height/2],size=14,color=BLACK):
    largeText = pg.font.Font('freesansbold.ttf',size)
    TextSurf, TextRect = text_objects(text, largeText, color)
    TextRect.center = ((loc[0]),(loc[1]))
    screen.blit(TextSurf, TextRect)

def tank_collide(point, target_obj):
    if ((target_obj.xlast - (env.hitrad+2)*target_obj.half) < point < (target_obj.xlast + (env.hitrad-2)*(target_obj.half))):
        target_obj.state = 2
        return True
    return False

def collision_detect(xpoint,ypoint,target_obj):
    for k in target_obj:
        if ((k.xlast - (env.hitrad-1)*k.half) < xpoint < (k.xlast + (env.hitrad-1)*(k.half))):
            if ((k.ylast - (env.hitrad-1)*k.halfy) < ypoint < (k.ylast + (env.hitrad-1)*(k.halfy))):     
                k.state += 1
                k.image = k.explode
                AirExplosion(k.xlast,k.ylast)
                play_sound('explosion')
                return True
    return False

# def rho_interp(Qy):
#     norm = (1-Qy/env.screen_height)*100000
#     if norm>=0:
#         ind=rho_data[rho_data[:,0] < norm]
#         ind= np.size(ind,0)
#         f=(norm-rho_data[ind-1,0])
#         if ind >= len(rho_data):
#             ind = len(rho_data)-1
#         return rho_data[ind-1,1]+ f*(rho_data[ind,1]-rho_data[ind-1,1])/(rho_data[ind,0]-rho_data[ind-1,0])
#     else:
#         return rho_data[1,0]

def update_sprites():
    for i,exp in enumerate(env.groundexplosions):
        exp.update(i)
    for i,exp in enumerate(env.airexplosions):
        exp.update(i)
    for i,nuke in enumerate(env.nukes):
        nuke.update(i)
    for i,cloud in enumerate(env.cloud_list):
        cloud.update()

def Pause():
    env.gamestate = 1
    
def UnPause():
    env.gamestate = 0

def normalize(val,valmax,standard):
    return val/valmax * standard

def resize(screen,event,env,t1):
    old_surface = screen
    xscale = event.w/env.screen_width
    yscale = event.h/env.screen_height
    env.screen_width = event.w
    env.screen_height = event.h
    i = 1
    while i < len(IMAGES):
        pg.transform.smoothscale(IMAGES[i],(int(IMAGES[i].get_width()*xscale), int(IMAGES[i].get_height()*yscale)))
        i +=1
    bg = pg.transform.smoothscale(bgraw,(env.screen_width,env.screen_height))
    screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
    screen.blit(old_surface, (0,0))
    del old_surface
    t1.gunlen = 50*(xscale**2+yscale**2)**0.5 / 2
    [twidth,theight] = Ltank.get_rect()[2:]
    a = theight//2; b = twidth//2
    env.screen_width = int(screen.get_width())
    env.screen_height = int(screen.get_height())
    return a,b,env,bg,screen,t1

def GameLoop(screen,IMAGES,env,t1):
    mixer.music.stop()
    button_01 = Button("Quit to Main Menu", (80, 30), quit_press)
    button_02 = Button('Pause', (80, 70),Pause, bg=(50, 200, 20))
    button_03 = Button("Return to Game", (env.screen_width//2, 11*env.screen_height//16), UnPause, bg = ORANGE,size=(env.screen_width//4,env.screen_height//6.5), font_size = 15)
    buttons = [button_01, button_02]
    bg = IMAGES[0]
    env.gamestate = 0
    env.buildthreats()
    env.screen_width = int(bg.get_width())
    env.screen_height = int(bg.get_height())
    #seed clouds
    for k in range(2):
        Cloud()
    [twidth,theight] = Ltank.get_rect()[2:]
    a = theight//2
    b = twidth//2
    rat = 0.820
    count = env.fire_spacing
    gameloop = True
    #pg.init()
    scorespec =False
    effects=0
    vel_adj = t1.V_muzz//50
    DMG_CL = [GREEN, BLUE, ORANGE, RED]
    RLD_CL = 255/env.fire_spacing
    temp = 255
    msg = ['Begin level %d'  % env.gamediff,'3','2','1','GO!']
    for m in msg:
        play_sound('clocktick')
        while effects < env.text_effects:
            clock.tick(1/env.tstep)
            screen.blit(bg, (0, 0)) 
            keys = pg.key.get_pressed()
            if keys[pg.K_ESCAPE] or keys[ord('q')]:
                pg.quit() 
                env.delete_all()
                gameloop = False
                sys.exit()
            message_display(m, [env.screen_width//2, env.screen_height//2], int(3*effects)+12, BLACK) 
            message_display(m, [env.screen_width//2, env.screen_height//2], int(3*effects)+10, COLORS[effects % len(COLORS)])  
            effects += 1
            pg.display.flip()
        effects = 0
    
    while gameloop == True:
        msg = '+%d'
        clock.tick(1/env.tstep)
        screen.blit(bg, (0, 0)) 
        keys = pg.key.get_pressed()    
        if keys[pg.K_SPACE]:          
            if count == env.fire_spacing: #can_pos:
                t1.shoot()
                count = 0
                temp = count * RLD_CL
        if count < env.fire_spacing:
            count += 1
            temp = count * RLD_CL
        if keys[pg.K_ESCAPE] or keys[ord('q')]:
            pg.quit() 
            env.delete_all()
            gameloop = False
            sys.exit()
    ##--CANNON MOVEMENT ADJUST--##       
        if keys[pg.K_LEFT]:
            play_sound('tanksnip')
            t1.xpos -= t1.xspeed #can_pos
            if t1.xpos < 0: #can_pos
                t1.xpos = env.screen_width + twidth
        if keys[pg.K_RIGHT]:
            play_sound('tanksnip') 
            t1.xpos += t1.xspeed
            if t1.xpos > env.screen_width+twidth:
                t1.xpos = 0 #-twidth
    ##--MUZZLE VELOCITY ADJUST--##
        if keys[pg.K_UP] or keys[ord('w')]:
            t1.V_muzz += vel_adj #m/s
            if t1.V_muzz > t1.Vorig:
                t1.V_muzz = t1.Vorig
        elif keys[pg.K_DOWN] or keys[ord('s')]:
            t1.V_muzz -= vel_adj #m/s
            if t1.V_muzz < 0:
                t1.V_muzz = 0
    ##--GRAVITY MULTIPLE ADJUST--##        
        if keys[pg.K_0] or keys[ord('0')]:
            env.Gspec = env.Gshift[0] #scalar multiple
        elif keys[pg.K_1] or keys[ord('1')]:
            env.Gspec = env.Gshift[1] #scalar multiple
        elif keys[pg.K_2] or keys[ord('2')]:
            env.Gspec = env.Gshift[2] #scalar multiple
        elif keys[pg.K_3] or keys[ord('3')]:
            env.Gspec = env.Gshift[3] #scalar multiple
        elif keys[pg.K_4] or keys[ord('4')]:
            env.Gspec = env.Gshift[4] #scalar multiple
        elif keys[pg.K_5] or keys[ord('5')]:
            env.Gspec = env.Gshift[5] #scalar multiple
        elif keys[ord('a')]:
            t1.can_ang += env.ang_step
            play_sound('turret')
        if keys[ord('d')]:
            t1.can_ang -= env.ang_step
            play_sound('turret')
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); gameloop = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position
                #print('button was pressed at {0}'.format(mouse_pos))
                mousebuttondown(buttons)
            if event.type == pg.VIDEORESIZE:            
                [a,b,env,bg,screen,t1] = resize(screen,event,env,t1)
                
        # DAMAGE TRACKING BAR  
        # CHECKS FOR GAME COMPLETION (DAMAGE > DAMAGE LIMIT)
        if env.gamestate:
            buttons = [button_03]
            while env.gamestate:    
                for button in buttons:
                    button.draw()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit(); gameloop = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        #print('button was pressed at {0}'.format(mouse_pos))
                        mousebuttondown(buttons)
                    if event.type == pg.VIDEORESIZE:            
                        [a,b,env,bg,screen,t1] = resize(screen,event,env,t1)
                pg.display.flip()
            buttons = [button_01, button_02]
                
            
        for i,thr in enumerate(env.threat_list):
            thr.move()
            if thr.state:
                screen.blit(thr.curr_image,(thr.pos.centerx,thr.pos.centery))
                play_sound('planedown')               
                if thr.state == 2:
                    play_sound('planehit')
                    screen.blit(thr.curr_image,(thr.pos.left,thr.pos.bottom))
                    del env.threat_list[i]
                    screen.blit(thr.curr_image,(thr.pos.left,thr.pos.centery))
                    t1.score += 2*thr.score
                    scorespec = 2*thr.score
                    effects=0    
                elif thr.state == 3:
                    play_sound('tankhit')
                    del env.threat_list[i]
                    t1.damage += env.hit_damage
                    t1.score += thr.score
                    scorespec=thr.score
                    effects=0
                elif thr.state == 4:
                    play_sound('crash')
                    del env.threat_list[i]
                    t1.score += thr.score
                    scorespec=thr.score
                    effects=0
                if ((not env.bomb_list) and (not env.threat_list)):
                    scorespec = t1.score
                    if env.gamediff < 10:
                        msg = 'Level %d Complete! Score: %d'  % (env.gamediff,scorespec)
                        env.gamediff +=1
                    else:
                        msg = 'You Win!  Final Score %d'  % (scorespec)
                        with open('hiscore.dat','r+') as f:
                            hs = f.readlines()
                        if int(hs[0]) < t1.score:
                            msg = 'You Win! %d is a New High Score!'  % (scorespec)
                            with open('hiscore.dat','w+') as f:
                                f.write(str(t1.score))
                    effects=0
                    gameloop = False
                    while effects < env.text_effects:
                        screen.blit(bg,(0,0))    
                        for i,bull in enumerate(env.bullet_list):
                            bull.update(env)
                            screen.blit(bull.curr_image,(int(bull.xpos),int(bull.ypos)))
                            if bull.state:
                                del env.bullet_list[i]
                        update_sprites()
                        message_display(msg, [env.screen_width//2+1, env.screen_height//2+1], int(effects)+25, BLACK)
                        message_display(msg, [env.screen_width//2, env.screen_height//2], int(effects)+25, GUN)
                        t1.draw(rat,env)   
                        pg.display.flip()
                        effects += 0.5
                    GameLoop(screen,IMAGES,env,t1)
            else:
                screen.blit(thr.curr_image, thr.pos)      
                
        for i,bom in enumerate(env.bomb_list):
            bom.update(env)
            screen.blit(bom.curr_image,(int(bom.xpos),int(bom.ypos)))
            if bom.state:
                if bom.state == 3:
                    t1.damage += env.hit_damage
                    play_sound('tankhit')
                del env.bomb_list[i]
                if ((not env.bomb_list) and (not env.threat_list)):
                    scorespec = t1.score
                    if env.gamediff < 10:
                        msg = 'Level %d Complete! Score: %d'  % (env.gamediff,scorespec)
                        env.gamediff +=1
                    else:
                        msg = 'You Win!  Final Score %d'  % (scorespec)
                        with open('hiscore.dat','r+') as f:
                            hs = f.readlines()
                        if int(hs[0]) < t1.score:
                            msg = 'You Win! %d is a New High Score!'  % (scorespec)
                            with open('hiscore.dat','w+') as f:
                                f.write(str(t1.score))
                    effects=0
                    gameloop = False
                    while effects < env.text_effects:
                        screen.blit(bg,(0,0))    
                        for i,bull in enumerate(env.bullet_list):
                            bull.update(env)
                            screen.blit(bull.curr_image,(int(bull.xpos),int(bull.ypos)))
                            if bull.state:
                                del env.bullet_list[i]
                        update_sprites()
                        message_display(msg, [env.screen_width//2+1, env.screen_height//2+1], int(effects)+25, BLACK)
                        message_display(msg, [env.screen_width//2, env.screen_height//2], int(effects)+25, GUN)
                        t1.draw(rat,env)   
                        pg.display.flip()
                        effects += 0.5
                    GameLoop(screen,IMAGES,env,t1)
        
        for i,HF in enumerate(env.agm_list): #blit hellfire missiles
            HF.update(env)
            screen.blit(HF.curr_image,(int(HF.xpos),int(HF.ypos)))
            if HF.state:
                #GroundExplosion(HF.xpos,HF.ypos)
                #screen.blit(HF.curr_image,(int(HF.xpos),int(HF.ypos)))
                if HF.state == 3:
                    t1.damage += env.hit_damage
                    play_sound('tankhit')
                    screen.blit(HF.curr_image,(int(HF.xpos),int(HF.ypos)))
                elif HF.state == 1:
                    play_sound('crash')
                    screen.blit(HF.curr_image,(HF.pos.left,HF.pos.centery))
                    t1.score += HF.score
                    AirExplosion(HF.xpos,HF.ypos)
                    scorespec= HF.score
                    effects=0
                del env.agm_list[i]
                if ((not env.agm_list) and (not env.threat_list)):
                    scorespec = t1.score
                    if env.gamediff < 10:
                        msg = 'Level %d Complete! Score: %d'  % (env.gamediff,scorespec)
                        env.gamediff +=1
                    else:
                        msg = 'You Win!  Final Score %d'  % (scorespec)
                        with open('hiscore.dat','r+') as f:
                            hs = f.readlines()
                        if int(hs[0]) < t1.score:
                            msg = 'You Win! %d is a New High Score!'  % (scorespec)
                            with open('hiscore.dat','w+') as f:
                                f.write(str(t1.score))
                    effects=0
                    gameloop = False
                    while effects < env.text_effects:
                        screen.blit(bg,(0,0))    
                        for i,bull in enumerate(env.bullet_list):
                            bull.update(env)
                            screen.blit(bull.curr_image,(int(bull.xpos),int(bull.ypos)))
                            if bull.state:
                                del env.bullet_list[i]                  
                        update_sprites()
                        message_display(msg, [env.screen_width//2+1, env.screen_height//2+1], int(effects)+25, BLACK)
                        message_display(msg, [env.screen_width//2, env.screen_height//2], int(effects)+25, GUN)
                        t1.draw(rat,env)   
                        pg.display.flip()
                        effects += 0.5
                    GameLoop(screen,IMAGES,env,t1)
                    #backtoMenu()

        for i,bull in enumerate(env.bullet_list):
            bull.update(env)
            screen.blit(bull.curr_image,(int(bull.xpos),int(bull.ypos)))
            if bull.state:
                if bull.state == 3:
                    t1.damage += env.hit_damage//3
                    play_sound('tankhit')
                elif bull.state == 4:
                    t1.score += 5000
                    scorespec=5000
                    effects=0
                screen.blit(bull.curr_image,(int(bull.xpos),int(bull.ypos)))
                del env.bullet_list[i]      
        
        update_sprites()
        
        
        try:
            dmg = normalize(t1.damage,env.dmg_limit,env.screen_width//2)
            pg.draw.rect(screen, BLACK, [env.screen_width//4, 0.075*env.screen_height-1, env.screen_width//2+2, 20], 0)
            pg.draw.rect(screen, DMG_CL[t1.damage//120], [env.screen_width//4 + 2, 0.075*env.screen_height + 2.5, dmg, 15], 0)
            message_display('DAMAGE: %d / %d' % (t1.damage, env.dmg_limit), [env.screen_width//2, 0.075 * env.screen_height-8], 14, RED)
        except IndexError:
            t1.image = explode
            msg = 'You Lose!  Final Score %d'
            with open('hiscore.dat','r+') as f:
                hs = f.readlines()
            if int(hs[0]) < t1.score:
                msg = '%d is a New High Score!'
                with open('hiscore.dat','w+') as f:
                    f.write(str(t1.score))
            scorespec = t1.score
            effects=0
            gameLoop = False
            while effects < env.text_effects:
                screen.blit(bg,(0,0))
                for thr in env.threat_list:
                    thr.move()
                    screen.blit(thr.curr_image, thr.pos) 
                for i,bom in enumerate(env.bomb_list):
                    bom.update(env)
                    screen.blit(bom.curr_image,(int(bom.xpos),int(bom.ypos)))
                    if bom.state:
                        #screen.blit(bom.curr_image,(int(bom.xpos),int(bom.ypos)))
                        if bom.state == 3:
                            t1.damage += env.hit_damage
                            play_sound('tankhit')
                            #screen.blit(bom.curr_image,(int(bom.xpos),int(bom.ypos)))
                        del env.bomb_list[i]
                for i,bull in enumerate(env.bullet_list):
                     bull.update(env)
                     screen.blit(bull.curr_image,(int(bull.xpos),int(bull.ypos)))
                     if bull.state:
                         del env.bullet_list[i]
                message_display(msg % (scorespec), [env.screen_width//2, env.screen_height//2], int(effects)+24, BLACK)
                message_display(msg % (scorespec), [env.screen_width//2, env.screen_height//2], int(effects)+25, RED)                     
                t1.draw(rat,env)    
                pg.display.flip()
                effects += 0.5
            backtoMenu()
            
        
        # MUZZLE POWER TRACKER
        power = normalize(t1.Vadj*t1.V_muzz, t1.Vadj*t1.Vorig, env.screen_height//2)
        pg.draw.rect(screen, BLACK, [0.925*env.screen_width, env.screen_height//4-1, 20, env.screen_height//2+2], 0)   #t1.Vadj*Vorig], 0)
        pg.draw.rect(screen, ORANGE, [0.925*env.screen_width + 2, env.screen_height//4 + env.screen_height//2-power, 15, power], 0)
        message_display('GUN POWER: %d / %d' % (t1.Vadj*t1.V_muzz, t1.Vadj*t1.Vorig), [0.925*env.screen_width, env.screen_height//4-20], 14)
        
        # RELOAD TRACKER
        reload = normalize(count,env.fire_spacing,env.screen_height//2)
        
        pg.draw.rect(screen, BLACK, [0.075*env.screen_width, env.screen_height//4-1, 20, env.screen_height//2+2], 0)   #t1.Vadj*Vorig], 0)
        pg.draw.rect(screen, (255-temp, temp, 0), [0.075*env.screen_width + 2, env.screen_height//4 + env.screen_height//2-reload, 15, reload], 0)
        message_display('RELOAD', [0.075*env.screen_width+9, env.screen_height//4-20], 14)  
        # OUTPUT SCORE
        if scorespec and effects<env.text_effects:
            message_display(msg % (scorespec), [env.screen_width//2, env.screen_height//2], 3*effects+25, GUN)
            effects +=1
        message_display('Gravity: %d' % (env.Gspec), [env.screen_width//2 -11, 0.025*env.screen_height+1], 24,BLACK)
        message_display('Gravity: %d' % (env.Gspec), [env.screen_width//2 -10, 0.025*env.screen_height], 24, RED)
        message_display('SCORE: %d' % (t1.score), [0.925*env.screen_width - 1, 0.025 * env.screen_height+1], 20, BLACK)
        message_display('SCORE: %d' % (t1.score), [0.925*env.screen_width, 0.025 * env.screen_height], 20, BLUE)   
        
        for button in buttons:
            button.draw()   
        # MOVE IMAGES

            
        t1.draw(rat,env)
        pg.display.flip()
        pg.event.pump()
    #GameLoop(screen,IMAGES,env,t1)
    MainMenu(screen,IMAGES,env)

def MainMenu(screen,IMAGES,env,t1):
    mixer.music.play(loops=-1)
    mixer.music.set_volume(0.25)
    scr_left = (0.180*env.screen_width, 0.6*env.screen_height)
    scr_mid = (0.49*env.screen_width, 0.6*env.screen_height)
    scr_right = (0.8*env.screen_width, 0.6*env.screen_height)
    topsize = (env.screen_width//4,env.screen_height//6.5)
    button_NG = Button("New Game", scr_left, new_game, bg = GUN, size=topsize, font_size = 90)
    button_Quit = Button('Quit Game', scr_right, exit_press, bg=(50, 200, 20), size=topsize, font_size = 90)
    button_KEYS = Button("Keypad Controls", scr_mid, controls_page, bg = ORANGE, size=topsize, font_size = 60)
    button_return = Button("Return to Menu", (scr_right[0], 11*env.screen_height//16), resume_menu, bg = ORANGE, size=topsize, font_size = 60)
    main_button = [button_NG,button_Quit,button_KEYS]
    current_button = main_button
    bg = IMAGES[0]
    with open('hiscore.dat','r') as f:
        hs = f.readlines()
        msg = 'HI SCORE: %d' % int(hs[0]) 
    env.screen_width = int(bg.get_width())
    env.screen_height = int(bg.get_height())
    menuloop = True
    pg.init()
    count = 1
    loc = env.screen_width
    thr1 = Threat(F16a, 380, 6, env.screen_height*.9, timeout=0)
    thr2 = Threat(B2, 380, 3, env.screen_height*.98, timeout=0)
    env.controls = False #Already set to false, just in case
    while menuloop == True:
        clock.tick(1/env.tstep)
        screen.blit(bg, (0, 0))
        screen.blit(CANNONS, ((env.screen_width-CANNONS.get_width())//2,env.screen_height*0.15))
        keys = pg.key.get_pressed()    
        if keys[pg.K_SPACE]:          
            count += 1; count %= env.fire_spacing+1
        if keys[pg.K_ESCAPE] or keys[ord('q')]:
            pg.quit(); sys.exit()
            menuloop = False
    ##--CANNON MOVEMENT ADJUST--##       
        if keys[pg.K_LEFT]:
            t1.xpos -= t1.xspeed #can_pos
            if t1.xpos < 0: #can_pos
                t1.xpos = env.screen_width + twidth
        if keys[pg.K_RIGHT]: 
            t1.xpos += t1.xspeed
            if t1.xpos > env.screen_width+twidth:
                t1.xpos = 0 #-twidth
    ##--MUZZLE VELOCITY ADJUST--##
        if keys[pg.K_UP] or keys[ord('w')]:
            t1.V_muzz += t1.Vadj #m/s
            if t1.V_muzz > t1.Vorig:
                t1.V_muzz = t1.Vorig
        elif keys[pg.K_DOWN] or keys[ord('s')]:
            t1.V_muzz -= t1.Vadj #m/s
            if t1.V_muzz < 0:
                t1.V_muzz = 0        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); menuloop = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position
                #print('button was pressed at {0}'.format(mouse_pos))
                mousebuttondown(current_button)
            if event.type == pg.VIDEORESIZE:            
                [a,b,env,bg,screen,t1] = resize(screen,event,env,t1)   
                scr_left = (0.180*env.screen_width, 0.6*env.screen_height)
                scr_mid = (0.49*env.screen_width, 0.6*env.screen_height)
                scr_right = (0.8*env.screen_width, 0.6*env.screen_height)
                topsize = (env.screen_width//4,env.screen_height//6.5)
                button_NG = Button("New Game", scr_left, new_game, bg = GUN, size=topsize, font_size = 90)
                button_Quit = Button('Quit Game', scr_right, exit_press, bg=(50, 200, 20), size=topsize, font_size = 90)
                button_KEYS = Button("Keypad Controls", scr_mid, controls_page, bg = ORANGE, size=topsize, font_size = 60)
                button_return = Button("Return to Menu", (scr_right[0], 11*env.screen_height//16), resume_menu, bg = ORANGE, size=topsize, font_size = 60)
                main_button = [button_NG,button_Quit,button_KEYS]
        loc -= 2
        if loc == -menutank.get_width():#-menutank.get_width():
            loc = env.screen_width
        screen.blit(menutank,(loc, env.screen_height*env.ground-menutank.get_height()))
        for button in main_button:
            pg.draw.rect(screen,BLACK,(button.rect[0]-10,button.rect[1]-10,button.rect[2]+20,button.rect[3]+20))
            button.draw()
            current_button = main_button 
        thr1.move();screen.blit(thr1.curr_image, thr1.pos)
        thr2.move();screen.blit(thr2.curr_image, thr2.pos)
        if env.controls:
            screen.blit(controls,(0,0))
            current_button = button_return
            pg.draw.rect(screen,BLACK,(current_button.rect[0]-10,current_button.rect[1]-10,current_button.rect[2]+20,current_button.rect[3]+20))
            current_button.draw()
        message_display(msg, [env.screen_width//2+2, 4*env.screen_height//5+2], 35, BLACK)
        message_display(msg, [env.screen_width//2, 4*env.screen_height//5], 35, BLUE)
        pg.display.flip()
        pg.event.pump()

# MUSIC
mixer.init()
soundtrack = mixer.music.load('6128F_-_01_-_N000.mp3')


tanksnip = mixer.Sound('tanksnip.wav')
gun = mixer.Sound('Cannon.wav')
explosion = mixer.Sound('c4sound.wav')
flyby = mixer.Sound('flyby.wav')
f16fly = mixer.Sound('f-16.wav')
planedown = mixer.Sound('FireballDeath.wav')
planehit = mixer.Sound('Bomb1.wav')
clocktick = mixer.Sound('clocktick.wav')
bulletbomb = mixer.Sound('Bomb2.wav')
tankhit = mixer.Sound('Bomb3.wav')
bulletmiss = mixer.Sound('grenade.wav')
turret = mixer.Sound('turret.wav')
bombdrop = mixer.Sound('bombdrop.wav')
crash = mixer.Sound('breakdown.wav')
missile = mixer.Sound('missile3.wav')
bababouey = mixer.Sound('bababouey.wav')

tanksnip.set_volume(0.20)
tanksnip.set_volume(0.5)
gun.set_volume(1.0)
turret.set_volume(0.12)
flyby.set_volume(0.15)
SOUNDS = [soundtrack,tanksnip,gun,explosion,flyby,bombdrop,planedown,planehit,bulletmiss,tankhit]
IMAGES = [bgraw,F16a,Ltank,B2]
clock = pg.time.Clock()
t1 = Tank(env.screen_width/2,env.screen_height/2)
screen=pg.display.set_mode([env.screen_width,env.screen_height],pg.RESIZABLE)
pg.display.set_caption("Cannons")
screen.fill(TEAL)
timer = 0
env.gamediff = 1
MainMenu(screen,IMAGES,env,t1)