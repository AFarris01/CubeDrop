#!/usr/bin/python

import varycolor
import pygame
from pygame.locals import *
from math import floor

WIDTH = 1024
HEIGHT = 768
NUMCOLORS = 300

SURFWIDTH = int(floor(WIDTH/NUMCOLORS))

pygame.font.init()

class colorBar( pygame.sprite.Sprite ):
    def __init__( self, givencolor, pos ):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface( (SURFWIDTH, HEIGHT) ).convert()
        self.image.fill( givencolor )
        self.rect = self.image.get_rect()
        colname = "%r" % givencolor
        fonty = pygame.font.Font( None, SURFWIDTH )
        rfont = fonty.render( colname, True, (0,0,0), givencolor )
        self.image.blit( pygame.transform.rotate(rfont, 270), (SURFWIDTH/3,0) )
        self.rect.left = pos

if __name__ == '__main__':
    screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
    bg = pygame.Surface( (SURFWIDTH, HEIGHT) ).convert()
    bg.fill( (255,255,255) )
    screen.blit( bg, (0,0) )
    pygame.display.flip()
    
    ColArray  = varycolor.varycolor( NUMCOLORS )
    GradArray = pygame.sprite.Group()
    
    for eachColor in ColArray:
        print "Making Object for ", eachColor
        GradArray.add( colorBar( eachColor, SURFWIDTH*len(GradArray) ) )
        
    print "Drawing..."
    GradArray.draw( screen )
    print "Ready to Display"
    pygame.display.update()
    clock = pygame.time.Clock()
    cont = True
    
    while cont:
        try:
            clock.tick( 30 )
            
            # process user events
            for event in pygame.event.get():
                if event.type == QUIT:
                    print "Caught Quit signal. Stopping."
                    cont = False
                    break
                    
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    cont = False
                    print "Caught Quit signal. Stopping."
                    break
        except KeyboardInterrupt:
            print "Quitting..."
            break
