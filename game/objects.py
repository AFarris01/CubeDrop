#!/usr/bin/python
#
############################### File Descriptor ################################
#  This file is part of the 'game' module for the program 'CubeDrop'           #
#  objects.py  -  By: Andrew Farris                                            #
#                                                                              #
#  CubeDrop is designed to be a good-ole-fasioned Tetris(TM) clone to use      #
#  as practice for using pygame, and a few other python libraries I haven't    #
#  made frequent use of. In addition, it is intended to expand on the initial  #
#  game idea by adding some features I found in another tetris clone I used to #
#  have on Gameboy(TM), and other stuff I thought was cool.                    #
#                                                                              #
#  This file contains object definitions for the CubeDrop game.                #
#                                                                              #
#################################### Legal #####################################
#                                                                              #
#  (C)opyright 2011 Andrew Farris                                              #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation, either version 3 of the License, or           #
#  (at your option) any later version.                                         #
#                                                                              #
#  This program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                              #
################################################################################
#TODO: Remove the 'self.image' attribute from the Floor object
#TODO: don't create a surface when making a SpawnBox
#TODO: Don't create a surface when making a Wall
#TODO: Check the input arguments for Wall
#TODO: Cube object absolutely should NOT load the cube graphic from disk every 
#      time a cube is created

try:
    import logging
    import pygame.rect
    from math import floor
    import pygame.font
    from pygame import sprite
    from pygame import Surface
    from pygame import SRCALPHA
    from pygame import transform
    from pygame import PixelArray
except ImportError, err:
    raise SystemExit, "ERROR in %s: Couldn't load a required module: %s" % (__name__,err)

logger = logging.getLogger( __name__ )

class Floor( object ):
    """
    Sprite used to represent the absolute 'floor' of the board.
    Basically used for collision detection only.
    """
    def __init__(self, boardrect):
        """
        INPUTS:
            boardrect = a pygame.rect.Rect describing the gameboard geometry
        RETURNS:
            a new Floor object
        ERRORS:
            None
        """
        self.rect = pygame.rect.Rect( 0,0,boardrect.width,1 )
        self.rect.bottom = boardrect.bottom
        

class SpawnBox( object ):
    """
    Box where pieces are designated to spawn. Pieces spawn in the center of the
    spawnbox
    """
    def __init__( self, boardrect, width, height, cubelen ):
        """
        INPUTS:
            boardrect = rect describing total board geometry
            width     = width of spawn box, as a multiple of cubelen
            height    = height of spawn box, as a multiple of cubelen
            cubelen   = the side-length of the cubes
        RETURNS:
            a new SpawnBox
        ERRORS:
            None
        """
        logger.debug( 'Creating a SpawnBox!' )
        halfbrd = floor(boardrect.width/(2*cubelen))
        logger.debug('Half-board is %r units across.' % halfbrd)
        halfme = floor(width/2.0)
        logger.debug('Half of me is %r units across.' % halfme)
        self.rect = pygame.Rect( (halfbrd-halfme)*cubelen, 0, width*cubelen, height*cubelen )
        logger.debug('My Rect: %r' % self.rect)
        self._spawnpoint = (halfbrd-1)*cubelen
        logger.debug( 'My spawnpoint: %r' % self._spawnpoint )
        logger.debug( 'Done creating a SpawnBox' )
    
    def spawnpoint(self):
        return self._spawnpoint


class Wall( object ):
    """
    Sprite used to represent the absolute 'wall' of the board.
    Basically used for collision detection only.
    """
    def __init__(self, boardrect, side):
        """
        INPUTS:
            boardrect = A pygame.Rect object for the gameboard
            side      = A string representing which side to attach this 'wall'
                        to. Valid values: 'left', and 'right'
        RETURNS:
            a 'Wall' object
        ERRORS:
            TypeError on unrecognized argument for 'side'
        """
        self.rect = pygame.rect.Rect(0,0,1,boardrect.height)
        
        if side == 'left':
            self.rect.left = 0
        elif side == 'right':
            self.rect.right = boardrect.width
        else:
            raise TypeError, "Unrecognized argument %s for side." % side


class Cube( sprite.DirtySprite ):
    """
    Basic sprite class, containing a little cube
    """
    CubeLen = None
    def __init__(self, graphic, sig = '', pos=[], color=None, cubelen=None):
        """
        INPUTS:
            graphic = image graphic of form (image,rect)
            sig     = A string signature denoting the shape of which this cube
                      is a member
            pos     = a list containing the top-left coordinates
                      of this cube in the given shape signature
            color   = the color to make the Cube (None means whatever the image
                      already is)
            cubelen = cube side length.
        RETURNS:
            a valid Cube object
        ERRORS:
            ValueError if both self.CubeLen and cubelen arg are undefined
        """
        if self.__class__.CubeLen==None and cubelen==None:
            raise ValueError, "Need to specify cube size: set either self.CubeLen or the cubelen keyword arg"
        elif self.__class__.CubeLen==None and cubelen!=None:
            self.__class__.CubeLen = cubelen
            
        sprite.DirtySprite.__init__(self) #call Sprite initializer
        self.image, self.rect = graphic
        self.ShapeSig = sig
        self.ShapePos = pos
        
        cc = self.__class__.CubeLen
        if (self.rect[:2] != [cc, cc]):
            self.image = transform.smoothscale( self.image, (cc,cc) )
            self.rect = self.image.get_rect()
            
        #TODO: This needs to be improved upon
        if color != None:
            basecol = transform.average_color( self.image )
            trans = PixelArray( self.image )
            trans.replace( basecol, color, distance = 0.08 )
            self.image = trans.make_surface()
        
    def update( self ):
        """
        Not Implimented
        """
        pass

    def stepup( self ):
        """
        Step the cube by one 'height' up
        """
        self.rect.bottom -= self.rect.height
        
    def stepleft( self ):
        """
        Step the cube by one 'width' to the left
        """
        self.rect.left -= self.rect.width
        
    def stepright( self ):
        """
        Step the cube by one 'width' to the left
        """
        self.rect.left += self.rect.width
        
    def stepdown( self ):
        """
        Step the cube down by one 'height'
        """
        self.rect.bottom += self.rect.height
        

class FallerGroup( sprite.RenderUpdates ):
    def stepleft( self ):
        for each in self:
            each.stepleft()
            
    def stepright( self ):
        for each in self:
            each.stepright()
            
    def stepup( self ):
        for each in self:
            each.stepup()
            
    def stepdown( self ):
        for each in self:
            each.stepdown()


#TODO: Make this load a backdrop from an external source
class Backdrop( sprite.DirtySprite ):
    """
    basic sprite to hold the static backdrop
    """
    def __init__(self, boardrect):
        """
        INPUTS:
            boardrect = a pygame.rect.Rect object that describes the game board
                        geometry
        RETURNS:
            None
        ERRORS:
            None
        """
        sprite.DirtySprite.__init__(self) #call Sprite initializer
        background = Surface( (boardrect.width, boardrect.height) )
        background = background.convert()
        background.fill((250, 250, 250))
        
        if pygame.font:
            font = pygame.font.Font(None, 36)
            text = pygame.font.render("Test of CubeDrop!", 1, (10, 10, 10))
            textpos = text.get_rect(centerx=background.get_width()/2)
            background.blit(text, textpos)
        
        self.image = background
        self.rect = background.get_rect()


class ScoreKeeper( object ):
    """
    Score Keeping object for the game
    """
    def __init__( self ):
        """
        INPUTS:
            None
        RETURNS:
            A ScoreKeeper object
        ERRORS:
            None
        """
        self.SCORES = { 'removed':10, 'stepdown':1, 'drop':2 }
        self._score = 0
        
    def reset( self ):
        self._score = 0
        
    def mark( self, number, state='removed' ):
        """
        Update the internal score count
        
        INPUTS:
            number = the number of events to count for scoring
            state  = a string representing the type of event to be scored.
                     If an invalid state is given, 
                     Valid values are: 'removed', 'stepdown', 'drop'
        RETURNS:
            None
        ERRORS:
            None
        """
        self._score += number * self.SCORES.get( state, 0 )
        
    def renderscore( self, infont ):
        """
        Render the current score as an image
        
        INPUTS:
            infont = a pygame.Font object
        RETURNS:
            pygame.Surface, pygame.rect.Rect
        ERRORS:
            None
        """
        counter_img = infont.render( "%i" % self._score, True, (255,255,255) )
        return counter_img, counter_img.get_rect()
        
    def get_score( self ):
        return self._score
