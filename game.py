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


def LoadImage( name, colorkey = None ):
    """
        Load an image file, given a filename. Also allows setting a special 
        transparency 'colorkey' for the given image file. If the loaded image
        format supports transparency without using a colorkey (i.e. .png, .gif),
        any supplied colorkey is ignored.
        
        INPUTS:
            name     = short filename of object (not including path)
            colorkey = RGB 3-tuple representing the color of transparency
                     = None: [default] Dont set colorkey data
                     = -1: Read the colorkey of the top-left corner and use that
        RETURNS:
            (image object, image.rect)
    """
    fullname = os.path.join( PATH, RESOURCEDIR, name)
    
    try:
        image = pygame.image.load( fullname )
    except pygame.error, message:
        print "OOPS: Failed to load image data from %s. Cannot continue." % (fullpath)
        raise SystemExit, message
    else:
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    
        if ( colorkey is not None ) and ( image.get_alpha() is None ):
            if colorkey is -1:
                colorkey = image.get_at( (0,0) )
            image.set_colorkey( colorkey, RLEACCEL )
            
        return image, image.get_rect()


def hitfloor( fallersprite, fallensprite ):
    """
        simple falling Collision-detector
    """
#    fallerbottom = fallersprite.rect[1] + fallersprite.rect[3] + 1
#    absbottom = pygame.display.get_surface().get_rect()[3]
    screenrect = pygame.display.get_surface().get_rect()
    conds = [
                (fallersprite.rect.bottom ) == fallensprite.rect.top,
                fallersprite.rect.left == fallensprite.rect.left
            ]
    
    if all( conds ) or ( fallersprite.rect.bottom >= screenrect.bottom ):
        return True
    else:
        return False


class Floor( pygame.sprite.DirtySprite ):
    """
        Sprite used to represent the absolute 'floor' of the board.
        Basically used for collision detection only.
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        s = pygame.display.get_surface().get_rect() #get board size
        self.image = pygame.Surface( (s.width,1) ).convert()
        self.image.set_alpha( 0 ) # Make the 'floor' completely transparent
        self.rect = self.image.get_rect()
        self.rect.bottom = s.bottom
        

class SpawnBox( object ):
    def __init__( self ):
        s = pygame.display.get_surface().get_rect()
        self.rect = pygame.Rect( 0, 0, s.width, CUBELEN*2 )

        
class CollDetector( object ):
    """
        Sprite used to detect collisions for determining if a row can be eliminated or not.
    """
    def __init__( self ):
        s = pygame.display.get_surface().get_rect() #get board size
        self.rect = pygame.Rect(0,0,s.width,1)
        self.reset()
        
    def stepup( self ):
        self.rect.bottom = self.rect.bottom - CUBELEN
        
    def reset( self ):
        s = pygame.display.get_surface().get_rect() #get board size
        self.rect.bottom = math.floor(s.height - 0.5*CUBELEN)
        
        
class Wall( pygame.sprite.DirtySprite ):
    """
        Sprite used to represent the absolute 'wall' of the board.
        Basically used for collision detection only.
    """
    def __init__(self, side):
        """
            INPUTS:
                side = A string representing which side to attach this 'wall'
                       to. Valid values: 'left', and 'right'
            RETURNS:
                a valid 'Wall' object
        """
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        s = pygame.display.get_surface().get_rect() #get board size
        self.image = pygame.Surface( (1,s.height) ).convert()
        self.image.set_alpha( 0 ) # Make the 'wall' completely transparent
        self.rect = self.image.get_rect()
        
        if side == 'left':
            self.rect.left = 0
        elif side == 'right':
            self.rect.right = s.width
        else:
            raise TypeError, "Unrecognized argument %s given." % side


class Cube( pygame.sprite.DirtySprite ):
    """
        Basic sprite class, containing a little cube
    """
    def __init__(self, sig = '', pos=[], color=None):
        """
            INPUTS:
                sig = A string signature denoting the shape of which this cube
                      is a member
                pos = a list containing the top-left coordinates
                      of this cube in the given shape signature
            RETURNS:
                a valid Cube object
        """
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = LoadImage( 'boxxen.png' )
        self.ShapeSig = sig
        self.ShapePos = pos
        
        if (self.rect[:2] != [CUBELEN, CUBELEN]):
            self.image = pygame.transform.smoothscale( self.image, (CUBELEN,CUBELEN) )
            self.rect = self.image.get_rect()
            
        if color != None:
            basecol = pygame.transform.average_color( self.image )
            trans = pygame.PixelArray( self.image )
            trans.replace( basecol, color, distance = 0.08 )
            self.image = trans.make_surface()
        
    def update( self ):
        """
            move based on the mouse position
        """
        pass

    def stepup( self ):
        """
            Step the cube by one 'height' up
        """
        self.rect.bottom -= self.image.get_height()
        
    def stepleft( self ):#, terrain ):
        """
            Step the cube by one 'width' to the left
        """
        prestep = self.rect.copy()
        self.rect.left -= self.image.get_width()
        conds = [
                    self.rect.left >= 0#,
#                    not pygame.sprite.spritecollideany( self, terrain )
                ]
                
        if not all( conds ):
            self.rect = prestep.copy()
        
    def stepright( self ):#, terrain ):
        """
            Step the cube by one 'width' to the left
        """
        prestep = self.rect.copy()
        maxsize = pygame.display.get_surface().get_rect()
        width = self.image.get_width()
        self.rect.left += width
        conds = [
                    ( self.rect.left ) <= ( maxsize[2] - width )#,
#                    not pygame.sprite.spritecollideany( self, terrain )
                ]
        
        if not all( conds ):
            self.rect = prestep.copy()
        
    def stepdown( self ):#, terrain ):
        """
            Step the cube down by one 'height'
        """
        prestep = self.rect.copy()
        maxsize = pygame.display.get_surface().get_rect()
        self.rect.bottom += (GRAVITY * self.image.get_height())
        conds = [
                    self.rect.bottom <= maxsize[3]
                ]
                
        if not all( conds ):
            self.rect = prestep.copy()
        
        
class Backdrop( pygame.sprite.DirtySprite ):
    """
        basic sprite to hold the static backdrop
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        background = pygame.Surface( (WIDTH, HEIGHT) )
        background = background.convert()
        background.fill((250, 250, 250))
        
        if pygame.font:
            font = pygame.font.Font(None, 36)
            text = font.render("Test of CubeDrop!", 1, (10, 10, 10))
            textpos = text.get_rect(centerx=background.get_width()/2)
            background.blit(text, textpos)
        
        self.image = background
        self.rect = background.get_size()


class FPSMon( pygame.sprite.DirtySprite ):
    def __init__( self ):
        pygame.sprite.Sprite.__init__( self ) #call Sprite initializer
        self.font = pygame.font.Font(None, 25)
        self.image, self.rect = pygame.Surface((0,0)), pygame.Rect(0,0,0,0)
        
    def update( self, inclock ):
        screenright = pygame.display.get_surface().get_rect()[3]
        counter_img = self.font.render( "%5.0f FPS" % inclock.get_fps(), True, (0,0,0), (255,255,255) )
        counter_img = counter_img.convert()
        self.image = counter_img
        self.rect = self.image.get_rect()
        self.rect.right = screenright - self.image.get_width()*0.6
        
        
class ScoreKeeper( pygame.sprite.DirtySprite ):
    def __init__( self ):
        pygame.sprite.Sprite.__init__( self ) #call Sprite initializer
        self.font = pygame.font.Font(None, 25)
        msg = "Score:"
        w,h = self.font.size( msg )
        self.image = pygame.Surface((1.5*w,2*h)).convert()
        self.image.fill( (255,255,255) )
        fs = self.font.render( "Score:", True, (0,0,0), (255,255,255) )
        self.image.blit(fs,(0,0))
        
        self.rect = self.image.get_rect()
        self.SCORES= { 'removed':10, 'stepdown':1, 'drop':2 }
        self._score = 0
        
    def update( self, inclock ):
        self.image.fill( (255,255,255) )
        fs = self.font.render( "Score:", True, (0,0,0), (255,255,255) )
        self.image.blit(fs,(0,0))
        counter_img = self.font.render( "%i" % self._score, True, (0,0,0), (255,255,255) )
        counter_img = counter_img.convert()
        self.image.blit( counter_img, (0,self.rect.height/2) )
        self.rect = self.image.get_rect()
        
    def countscore( self, number, state='removed' ):
        self._score += number * self.SCORES.get( state, 0 )
        
    def renderscore( self, infont ):
        counter_img = infont.render( "%i" % self._score, True, (0,0,0) )
        return counter_img
        

def GenerateShape(shapedef, xoffset=0, yoffset=0, spritelist=None, mcolor=None):
    """
        Generate a list of cubes, positioned appropriately, based on a provided
        shape definition.

        INPUTS:
            shapedef = a string, designating the shape layout. Rules are:
                       0 is empty space, 1 is a cube, i.e.: "111", "1011"
                       for 2D shapes, seperate rows with a comma, i.e. "111,001"
            xoffset  = distance from the left side of the destination surface 
                       that the left edge of the shape should appear.
            yoffset  = distance from the top side of the destination surface 
                       that the left edge of the shape should appear.
            spritelist = list of sprites to be manipulated. If this is None, 
                         then new 'Cube' objects are created instead.
        RETURNS:
            an array of 'Cube' objects fitting the shape definition, with 
            appropriately positioned Rects
    """
    #TODO: If we get a spritelist, do the operation in-place
    numcubes = shapedef.count( '1' )
    shapearray = shapedef.split(',')
    if spritelist is None:
        shape = [ Cube(color=mcolor) for x in range(numcubes) ]
    else:
        shape = spritelist
    
    nummoved = 0
    for eachrow in range(len(shapearray)):
        for eachchar in range(len(shapearray[eachrow])):
            if shapearray[eachrow][eachchar] == '1':
                newx = xoffset + ( eachchar * shape[ nummoved ].rect.width )
                newy = yoffset + ( eachrow * shape[ nummoved ].rect.height )
#                print "Found a One! Offsets: (%i, %i)" % (newx, newy) #DEBUG
                shape[ nummoved ].rect.left = newx
                shape[ nummoved ].rect.top = newy
                shape[ nummoved ].ShapeSig = shapedef
                shape[ nummoved ].ShapePos = [newx,newy]
                nummoved += 1
#            elif eachchar == '0': #DEBUG
#                print "Found a zero!"
#            else:
#                pass
    
    #DEBUG: 
    print "Made a shape! Rects:"
    for each in shape:
        print each.rect
    return shape


def blankArray( rows, cols ):
    """
        Generate a blank signature array, of dimension [rows][cols]
        
        INPUTS:
            rows = # of rows to create in the array
            cols = # of cols to create in the array
        RETURNS:
            An array, filled with '0', of the given dimensions
    """
    return [['0' for y in range(rows)] for x in range(cols)]


def CW( strinput ):
    """
        Rotate the given input string signature CW by 90 degrees
        
        INPUTS:
            strinput = the string signature to rotate (i.e. '110,011')
        RETURNS:
            string signature that has been properly rotated.
    """
    #TODO: This function is really messy, and has too many loops... need to find a better way to do this
    print "Rotating Clockwise!"
    
    # Generate a 2D array from the input string
    origarray = [list(a) for a in strinput.split(',')]
#    print origarray
    
    #Resize the signature so each row has the same number of cols (if they dont already)
    maxcolsize = max(len(col) for col in origarray)
    for row in origarray:
        row.extend(['0' for x in range(maxcolsize-len(row))])
    
    # Prepare the return array
    rowsize = len(origarray)
    retarray = blankArray( rowsize, maxcolsize )
    for i in range( rowsize ):
#        print "\tNow on Row %i from source" % i
        for j in range( maxcolsize ):
#            print "\t\tNow on Column %i from source" % j
#            print "\t\t\tMoving point from (%i,%i) in source to (%i,%i) in dest." % ( i,j,j,maxcolsize - 1 - i )
            retarray[j][rowsize - 1 - i] = origarray[i][j]
            
#    print retarray
    # Re-build a format string from the return array
    retstr = ','.join(''.join(entry) for entry in retarray)
    
    return retstr


def Rotate( spritelist, direction=None ):
    """
        Take a list of sprites, and rotate them all, provided all the shape 
        signatures match. If they do not match, then don't do anything.
        
        INPUTS:
            spritelist = a list of sprites that are to be rotated. Note, they
                         must have a 'ShapeSig' attribute.
            direction  = The direction they must turn, as a pygame keycode.
                         K_LEFT == CCW rotation, K_RIGHT == CW rotation
        RETURNS:
            None. Rotation operation is in-place
    """
    #TODO: This function needs to do some bounds checking, or possibly provide a
    #      utility to rotate CCW, for when external bounds-checking fails.
    absbottom = min([x.rect.bottom for x in spritelist])
    absleft = min( [x.rect.left for x in spritelist] )

#    print "xoffset, yoffset = (%i,%i)" % ( absleft, absbottom )
    
    signatures = [each.ShapeSig for each in spritelist]
    
    if all( x == signatures[0] for x in signatures ):
        print "Shape signatures OK. Rotating..."
        newsig = CW(signatures[0])
        return GenerateShape( newsig, xoffset=absleft, yoffset=absbottom-CUBELEN, spritelist=spritelist )
    else:
        print "Shape Signatures don't match, not gonna rotate..."
        return spritelist
    
    
def FallCatcher( linesite, board ):
    """
        Return an object with a rect encompassing the area on the gameboard 
        above where the given line was deleted.
    """
    brdrect = board.get_rect()
    print "Creating a fallcatcher with rect: %r" % brdrect
    class catcher( object ):
        def __init__( self ):
            self.rect = pygame.Rect(0,0,brdrect.width,linesite)
            
    return catcher()
    
    
def TickDrop( thefaller, thefallen, thefloor ):
    # If there's any collisions between the falling group, and the fallen, 
    # then consider the fallers to have fallen
    conds = [
            pygame.sprite.spritecollide( thefloor, thefaller, False ),
            pygame.sprite.groupcollide( thefaller, thefallen, False, False, collided = hitfloor )
            ]
    if any( conds ):
        if pygame.sprite.spritecollide( thefloor, thefaller, False ): 
            print "A Sprite Touched Down!"
        if pygame.sprite.groupcollide( thefaller, thefallen, False, False, collided = hitfloor ):
            print "A sprite Hit other touchdowns!"
        touchdowns = thefaller.sprites()
        thefaller.empty()
        thefallen.add( touchdowns )
    else:
        for each in thefaller.sprites():
            each.stepdown()


SHAPES = [ '1111', '011,110', '110,011','100,111','001,111', '11,11', '010,111' ]
EXTENDEDSHAPES = [ '1', '1,1', '101,111', '01,11' ] # '111,101,111'
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
