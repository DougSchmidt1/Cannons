# -*- coding: utf-8 -*-
"""
Created on Tue May  5 12:19:58 2020

@author: dougi
"""


def MainMenuLoop(screen):
    bg = IMAGES[0]
    env.screen_width = int(bg.get_width())
    env.screen_height = int(bg.get_height())
    [twidth,theight] = Ltank.get_rect()[2:]
    a = theight//2
    b = twidth//2
    rat = 0.820
    count = env.fire_spacing
    gameloop = True
    pg.init()
    barreltip_y = env.screen_height - t1.gunlen*np.sin(t1.can_ang)
    barreltip_x = t1.xpos + t1.gunlen*np.cos(t1.can_ang) #can_pos
    scorespec =False
    effects=0
    while gameloop == True:
        clock.tick(1/env.tstep)
        screen.blit(bg, (0, 0)) 
        keys = pg.key.get_pressed()    
        if keys[pg.K_SPACE]:          
            if count == env.fire_spacing: #can_pos:
                #pg.draw.circle(screen,ORANGE,[int(barreltip_x)-b, int(barreltip_y)+1],10)
                img = pg.transform.rotate(gunblast,t1.can_ang)
                screen.blit(img,(int(barreltip_x)-b, int(barreltip_y)-5))
                Bullet(int(barreltip_x)-b, int(barreltip_y)-5,t1.Vadj*t1.V_muzz,t1.can_ang)
                screen.blit(img,(int(barreltip_x)-b, int(barreltip_y)-5))
            count += 1; count %= env.fire_spacing+1
        if keys[pg.K_ESCAPE] or keys[ord('q')]:
            pg.quit(); sys.exit()
            gameloop = False
    ##--CANNON MOVEMENT ADJUST--##       
        if keys[pg.K_LEFT]:
            play_sound('tank')
            t1.xpos -= t1.xspeed #can_pos
            if t1.xpos < 0: #can_pos
                t1.xpos = env.screen_width + twidth
        if keys[pg.K_RIGHT]:
            play_sound('tank') 
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
                # checks if mouse position is over the button
                print('button was pressed at {0}'.format(mouse_pos))
                mousebuttondown()
            if event.type == pg.VIDEORESIZE:
                old_surface = screen
                xscale = event.w/env.screen_width
                yscale = event.h/env.screen_height
                env.screen_width = event.w
                env.screen_height = event.h
                #
                i = 1
                while i < len(IMAGES):
                    #img.get_rect().inflate(xscale,yscale)
                    pg.transform.smoothscale(IMAGES[i],(int(IMAGES[i].get_width()*xscale), int(IMAGES[i].get_height()*yscale)))
                    #img.convert(pg.RESIZABLE)
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

                
        #INSIDE OF THE GAME LOOP  
        t1.update()
        
        barreltip_y = rat*env.screen_height - t1.gunlen*np.sin(t1.can_ang)
        barreltip_x = t1.xpos + t1.gunlen*np.cos(t1.can_ang) #can_pos
        pg.draw.aaline(screen, GUN, [t1.loc-b, (rat*env.screen_height)],[barreltip_x-b, (barreltip_y)], 12)
        #pg.draw.line(screen, GUN, [t1.loc-b, (rat*env.screen_height)+a],[barreltip_x-b, (barreltip_y)+a], 6)
        pg.draw.circle(screen,GUN,[int(barreltip_x)-b, int(barreltip_y)],4)
        
        # DAMAGE TRACKING BAR
        pg.draw.rect(screen, BLACK, [env.screen_width//4, 0.075*env.screen_height, env.screen_width//2, 20], 0)
        pg.draw.rect(screen, RED, [env.screen_width//4 + 2, 0.075*env.screen_height + 2.5, t1.damage, 15], 0)
        message_display('DAMAGE: %d / %d' % (t1.damage, env.screen_width//2), [env.screen_width//2, 0.075 * env.screen_height-8], 14)
        
        # MUZZLE POWER TRACKER
        power = normalize(t1.Vadj*t1.V_muzz, t1.Vadj*t1.Vorig, env.screen_height//2)
        pg.draw.rect(screen, BLACK, [0.925*env.screen_width, env.screen_height//4, 20, env.screen_height//2], 0)   #t1.Vadj*Vorig], 0)
        pg.draw.rect(screen, BLUE, [0.925*env.screen_width + 2, env.screen_height//4 + env.screen_height//2-power, 15, power], 0)
        message_display('GUN POWER: %d / %d' % (t1.Vadj*t1.V_muzz, t1.Vadj*t1.Vorig), [0.925*env.screen_width, env.screen_height//4-20], 14)
        
        # RELOAD TRACKER
        reload = normalize(count,env.fire_spacing,env.screen_height//2)
        pg.draw.rect(screen, BLACK, [0.075*env.screen_width, env.screen_height//4, 20, env.screen_height//2], 0)   #t1.Vadj*Vorig], 0)
        pg.draw.rect(screen, ORANGE, [0.075*env.screen_width + 2, env.screen_height//4 + env.screen_height//2-reload, 15, reload], 0)
        message_display('RELOAD', [0.075*env.screen_width, env.screen_height//4-20], 14)
        
        # OUTPUT SCORE
        if scorespec and effects<100:
            message_display('+%d' % (scorespec), [env.screen_width//2, env.screen_height//2], 2*effects+25, GUN)
            effects +=1

            
        message_display('Gravity: %d' % (env.Gspec), [env.screen_width//2 -10, 0.025*env.screen_height], 16)
        message_display('SCORE %d' % (t1.score), [0.925*env.screen_width, 0.025 * env.screen_height], 16)
        
        for button in buttons:
            button.draw()
        
        # MOVE IMAGES
        for i,thr in enumerate(env.threat_list):
            thr.move()
            if thr.state:
                screen.blit(thr.curr_image,(thr.pos.centerx,thr.pos.centery))
                if thr.state == 1:
                    screen.blit(thr.curr_image,(thr.pos.left,thr.pos.bottom))
                    del env.threat_list[i]
                    screen.blit(thr.curr_image,(thr.pos.left,thr.pos.centery))
                    t1.score += thr.score
                    scorespec=thr.score
                    effects=0
            else:
                screen.blit(thr.curr_image, thr.pos)
                
                
        for i,bom in enumerate(bomb_list):
            bom.update(env)
            screen.blit(bom.curr_image,(int(bom.xpos),int(bom.ypos)))
            if bom.state:
                screen.blit(bom.curr_image,(int(bom.xpos),int(bom.ypos)))
                if bom.state == 2:
                    t1.damage += env.hit_damage
                    screen.blit(bom.curr_image,(int(bom.xpos),int(bom.ypos)))
                del bomb_list[i]
        
        for i,bull in enumerate(bullet_list):
            bull.update(env)
            screen.blit(bull.curr_image,(int(bull.xpos),int(bull.ypos)))
            if bull.state:
                screen.blit(bull.image,(int(bull.xpos),int(bull.ypos)))
                del bullet_list[i]
        
                
        screen.blit(t1.image,(t1.loc - twidth, 0.782*env.screen_height))
        #screen.blit(t1.image, t1.pos)
        pg.display.flip()
        pg.event.pump()

o1 = Threat(B2, 50, 4, 500)
o2 = Threat(F16a, 200, 6, 300, F16abombed)
o3 = Threat(F16a, 320, 6, 300, F16abombed)
o4 = Threat(F16a, 380, 6, 300, F16abombed)
o5 = Threat(B2, 120, 4, 500)
env.threat_list = [o1,o2,o3,o4,o5]
MainLoop(screen,IMAGES,env)