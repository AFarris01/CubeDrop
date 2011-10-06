#!/usr/bin/python

import os
import sys
import math
import random
import pygame
import varycolor
from pygame.locals import *

PATH = os.path.realpath( '.' )
RESOURCEDIR = 'data'


CUBELEN = 20
BOARDWIDTH = 14
BOARDHEIGHT = 20
GRAVITY = 1
MAXFPS = 60
LINEDROP = USEREVENT+1

#TODO: The game board should be a fixed size of whatever it is, and the size of the cubes should be scaled by the BOARDWIDTH and BOARDHEIGHT
WIDTH = (BOARDWIDTH+4) * CUBELEN
HEIGHT = BOARDHEIGHT * CUBELEN


SHAPES = [ '1111', '011,110', '110,011','100,111','001,111', '11,11', '010,111' ]
EXTENDEDSHAPES = [ '1', '1,1', '101,111', '111,101,111', '01,11' ]
TROLL = ['1110101011100011000011000100010111,0100111011000100010100100110110110,0100101011100111010011010101010111','100111010,100101010,110111011']


if __name__ == '__main__':
    #fire-up pygame
    print "Pygame initialized!\n%i Pygame modules were loaded, and %i failed to load." % pygame.init()

    #Initialize the screen to a particular resolution
    screen = pygame.display.set_mode( (WIDTH, HEIGHT), RESIZABLE )
    
    #set key-repeating to (delay,interval)
    pygame.key.set_repeat(300,50)

    allshapes = SHAPES + EXTENDEDSHAPES
    if BOARDWIDTH >= 35:
        allshapes += TROLL

    allcolors = varycolor.varycolor( len(allshapes)+1 )
    
    #duh
    pygame.display.set_caption('CubeDrop')

    #hide mousey
    pygame.mouse.set_visible(0)

    # Group containing background stuff
    wall = pygame.sprite.RenderUpdates()

    #this group should contain all sprites from pieces that have 'fallen'
    fallen = pygame.sprite.RenderUpdates()

    # a group containing the sprites belonging to the currently falling piece.
    faller = pygame.sprite.RenderUpdates()
    
    # a group containing the sprites falling due to line deletion.
    fallenfallers = []

    #create important objects
    background = Backdrop()
    meter = FPSMon()
    clock = pygame.time.Clock()
    leftwall, rightwall, floor = Wall('left'), Wall('right'), Floor()
    linefulldetector = CollDetector()
    spawnbox = SpawnBox()
    gamemsg = pygame.font.Font( pygame.font.get_default_font(), 40 )
    score = ScoreKeeper()

    # Add needed objects to group
    fallen.add( )
    wall.add( background, meter, score )

    # show the wallpaper while we finish setting things up
    screen.blit( background.image, (0,0) )
    pygame.display.flip()

    # start a reguler event, used to trigger pieces falling
    pygame.time.set_timer( USEREVENT, 2000 )

    # start the game, and allow it to catch keyboard interrupts
    cont = True
    try:
        while cont:
            # Set the game's max FPS
            clock.tick( MAXFPS )
            
            # if the 'faller' group is empty, fill it with a new shape
            if not faller and not fallenfallers:
                randex = random.randrange( len(allshapes) )
                middle = math.floor((BOARDWIDTH/2))*CUBELEN
                faller.add( GenerateShape( allshapes[randex], xoffset=middle, mcolor=allcolors[randex] ) )
                absbottom = max([x.rect.bottom for x in faller])
                if absbottom > spawnbox.rect.bottom:
                    for sprite in faller:
                        sprite.stepup()
                        print '^',
                    print
                
            # process user events
            for event in pygame.event.get():
                if event.type == USEREVENT:
                    print "Drop Tick!"
                    TickDrop( faller, fallen, floor )
                        
                elif event.type == LINEDROP:
                    print "LineDrop!"
                    print "%i Groups found, that need to be dropped" % len(fallenfallers)
                    for eachgrp in fallenfallers:
                        print "TickDropping a group"
                        TickDrop( eachgrp, fallen, floor )
                        if not eachgrp.sprites():
                            print "Group was emptied, deleting the group."
                            fallenfallers.remove(eachgrp)
                        else:
                            print "Group wasn't empty: %r" % eachgrp
                            
                    
                    if not fallenfallers:
                        pygame.time.set_timer( LINEDROP, 0 )
                    
                elif event.type == QUIT:
                    print "Caught Quit signal. Stopping."
                    cont = False
                    break
                    
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    cont = False
                    print "Caught Quit signal. Stopping."
                    break
                    
                elif event.type == KEYDOWN and event.key == K_LEFT:
                    print "Hit LeftArrow, trying to move Left!"
                    if not pygame.sprite.spritecollide( leftwall, faller, False ):
                        print "No collision between faller and borders: "
                        for each in faller.sprites():
                            each.stepleft()
                        if pygame.sprite.groupcollide( faller, fallen, False, False ):
                            # The step resulted in a collision... step back
                            for each in faller.sprites():
                                each.stepright()
                            
                    else:
                        print "We're gonna hit the left side!"
                        print leftwall.rect
                        for each in faller.sprites():
                            print each.rect,
                        print
                        
                elif event.type == KEYDOWN and event.key == K_RIGHT:
                    print "Hit RightArrow, trying to move right!"
                    if not pygame.sprite.spritecollide( rightwall, faller, False ):
                        print "No collision between faller and borders: "
                        for each in faller.sprites():
                            each.stepright()
                        if pygame.sprite.groupcollide( faller, fallen, False, False ):
                            # The step resulted in a collision... step back
                            for each in faller.sprites():
                                each.stepleft()
                    else:
                        print "We're gonna hit the right side!"
                        print rightwall.rect
                        for each in faller.sprites():
                            print each.rect,
                        print
                        
                elif event.type == KEYDOWN and event.key == K_DOWN:
                    print "Hit DownArrow, bumping down by 1!"
#                    if not pygame.sprite.groupcollide( faller, fallen, False, False, collided = hitfloor ):
                    if not pygame.sprite.spritecollide( floor, faller, False ):
                        for each in faller.sprites():
                            each.stepdown()
                        if pygame.sprite.groupcollide( faller, fallen, False, False ):
                            # The step resulted in a collision... step back
                            for each in faller.sprites():
                                each.stepup()
                        else:
                            score.countscore( 1, 'stepdown' )
                    else:
                        touchdowns = faller.sprites()
                        faller.empty()
                        fallen.add( touchdowns )
                        
                        
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    print "Hit Spacebar, Dropping the Shape!"
                    while True:
#                        print "Shape is falling..."
                        conds = [
                                pygame.sprite.spritecollide( floor, faller, False ),
                                pygame.sprite.groupcollide( faller, fallen, False, False, collided = hitfloor )
                                ]
                        if any( conds ):
                            break
                        else:
                            for each in faller.sprites():
                                each.stepdown()
                                print 'v',
                            print
                        score.countscore( 1, 'drop' )
                    touchdowns = faller.sprites()
                    faller.empty()
                    fallen.add( touchdowns )
                    
                elif event.type == KEYDOWN and event.key == K_UP:
                    print "Hit Uparrow... Rotating Shape!"
                    #TODO: need to do collision detection first 
                    sprites = faller.sprites()
                    faller.empty()
                    faller.add( Rotate(sprites) )
                    
            #Detect filled lines
            remlines=[]
            while True:
                collisions = pygame.sprite.spritecollide( linefulldetector, fallen, False )
                width = screen.get_rect().width
                if len(collisions) >= math.floor( width/CUBELEN ):
                    print "Detected a full line at %i" % linefulldetector.rect.bottom
                    fallen.remove( collisions )
                    score.countscore( len(collisions) )
                    remlines.append( linefulldetector.rect.bottom )
                elif len(collisions) > 0:
#                    print "Detected a partially full line at %i" % linefulldetector.rect.bottom
                    pass
                else: 
                    break
                linefulldetector.stepup()
            linefulldetector.reset()
            
            remlines.sort()
            for site in remlines:
                collisions = pygame.sprite.spritecollide( FallCatcher(site,screen), fallen, True )
                fallenfallers.append(pygame.sprite.RenderUpdates( collisions ))
                pygame.time.set_timer( LINEDROP, 100 )
#            print "FallenFallers: %r" % fallenfallers
#            print "Fallen: %r" % fallen

            # clear everything, preparing for redraw...
            #TODO: Should replace this operation with a dirty layers group, so we 
            #      dont erase/redraw so much every iteration
            for eachgrp in fallenfallers:
                eachgrp.clear( screen, background.image )
            wall.clear( screen, background.image )
            faller.clear( screen, background.image )
            fallen.clear( screen, background.image )
            
            # Update all the groups
            faller.update()
            fallen.update()
            wall.update( clock )
            
            # redraw everything in it's new positions, and update the display
            dirtyspots = wall.draw( screen )
            dirtyspots += fallen.draw( screen )
            dirtyspots += faller.draw( screen )
            for eachgrp in fallenfallers:
                dirtyspots += eachgrp.draw( screen )
                
            # Detect End-of-Game scenerio
            if pygame.sprite.spritecollideany( spawnbox, fallen ):
                cont = False
                msg = "GAME OVER!"
                w,h = gamemsg.size(msg)
                scoresurf = score.renderscore( gamemsg )
                msgsurf = gamemsg.render( msg, True, (0,0,0) )
                screct = screen.get_rect()
                xpos = (screct.width - w)/2
                ypos = (screct.height - h)/2
                scorexpos = (screct.width - scoresurf.get_width())/2
                screen.blit( msgsurf, (xpos, ypos) )
                screen.blit( scoresurf, (scorexpos, ypos+h) )
                dirtyspots += [pygame.Rect( xpos, ypos, w, h ), pygame.Rect(scorexpos, ypos+h, scoresurf.get_width(), scoresurf.get_height())]
                
            pygame.display.update( dirtyspots )
            
            key=0
            if not cont:
                while key == 0:
                    clock.tick( MAXFPS )
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            key = event.key
            
    except KeyboardInterrupt:
        print "Caught Quit signal. Stopping."
