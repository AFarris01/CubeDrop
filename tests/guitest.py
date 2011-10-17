#!/usr/bin/python

try:
    import os
    import sys
    import math
    import atexit
    import random
    import pygame
    import logging
    import optparse #TODO: This needs to be changed to argparse for future versions of python
    import platform
    from pygame.locals import *
    
    import gui
    import game
except ImportError, err:
    raise SystemExit, "ERROR in %s: Couldn't load a required module: %s" % (__name__,err)

logger = logging.getLogger( __name__ )
atexit.register( logging.shutdown )


CUBELEN = 30
BOARDWIDTH = 14
BOARDHEIGHT = 20
MAXFPS = 60

# record the current execution path as the central resource path
PATH = os.path.realpath( '.' )  
IMAGEDIR = 'data'
SOUNDDIR = 'data'
FONTDIR  = 'data'

logging.basicConfig(level=logging.DEBUG)
logger.info( "Starting PyGame Modules:" )
logger.info( "Display subsystem is starting..." )
pygame.display.init()
logger.info( "Font subsystem is starting..." )
pygame.font.init()

atexit.register(pygame.quit)

width = (BOARDWIDTH+4)*CUBELEN
height = (BOARDHEIGHT)*CUBELEN + 10
screen = pygame.display.set_mode( (width, height), RESIZABLE )

resources = game.ResourceManager( PATH, IMAGEDIR, SOUNDDIR, FONTDIR )
resources.LoadImage( 'boxxen.png', 'Cube' )
resources.LoadImage( 'borders.png', 'Borders' )
resources.LoadImage( 'backdrop.png', 'Backdrop' )
resources.LoadFont( 'Biolinum_Re-0.4.1RO.ttf', 'sysfont', CUBELEN )

######### Create required game objects (display, menus, etc.) #########
background = pygame.Surface( (width, height) ).convert()
background.fill((255,255,255))
pygame.key.set_repeat(300,50)
pygame.display.set_caption('CubeDrop')
pygame.mouse.set_visible(1)
gameclock = pygame.time.Clock()

background.blit( pygame.transform.smoothscale(resources.get('image', 'Backdrop')[0], (width, height)), (0,0) )

screen.blit(background, (0,0))
pygame.display.flip()

buttons = ['New Game','High Scores','Options','Exit']
colors = [(115,251,251),(182,115,250),(182,250,115),(250,115,115)]
callbacks = [None,None,None,sys.exit]
    
menus = gui.Menu( screen.get_rect(), zip(buttons,colors,callbacks), resources.get('font','sysfont') )
options = gui.OptionsMenu( screen.get_rect() )

def OpenOptions(event):
    options.MenuActivate()
    menus.MenuDeactivate()
    print "Opening Options!"
    
def OpenMain(event):
    menus.MenuActivate()
    options.MenuDeactivate()
    print "Opening Main!"

options.back.on_mouse_click = OpenMain
menus.fetchwidget('Options').on_mouse_click = OpenOptions

######### Begin Pygame Main Loop #########
cont = True
prevstate=(bool(menus),bool(options))
while cont:
    gameclock.tick(MAXFPS)
    for event in pygame.event.get():
        if menus:
            menus.EventCatch( event )
        elif options:
            options.EventCatch( event )
        
        if event.type == QUIT:
            logger.debug("Caught Quit signal. Stopping.")
            cont = False
            
    dirtyspots=[]
    
    if not ((bool(menus),bool(options)) == prevstate):
        prevstate = (bool(menus),bool(options))
        screen.blit(background,(0,0))
        pygame.display.flip()
    
    if menus:
        menus.clear( screen, background )
        menus.update()
        dirtyspots = menus.draw( screen )
    elif options:
        options.clear( screen, background )
        options.update()
        dirtyspots = options.draw( screen )
    
    pygame.display.update( dirtyspots )
