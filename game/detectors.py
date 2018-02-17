#!/usr/bin/python
#
############################### File Descriptor ################################
#  This file is part of the 'game' module for the program 'CubeDrop'           #
#  detectors.py  -  By: Andrew Farris                                          #
#                                                                              #
#  CubeDrop is designed to be a good-ole-fasioned Tetris(TM) clone to use      #
#  as practice for using pygame, and a few other python libraries I haven't    #
#  made frequent use of. In addition, it is intended to expand on the initial  #
#  game idea by adding some features I found in another tetris clone I used to #
#  have on Gameboy(TM), and other stuff I thought was cool.                    #
#                                                                              #
#  This file contains custom-made collision detectors for collision logic.     #
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
#TODO: In CollDetector, require passing in of the board rect, rather than 
#      assuming it's the whole pygame screen
#TODO: explore CollDetector as a throw-away class, rather than a persistant 
#      object (i.e. a new CollDetector is created every time we need to check 
#      for lines removed)

try:
    import logging
    from math import floor
    from pygame.rect import Rect
except ImportError, err:
    raise SystemExit, "ERROR in %s: Couldn't load a required module: %s" % (__name__,err)

logger = logging.getLogger( __name__ )

class FallCatcher( object ):
    """
    Build/return an object with a rect encompassing the area on the  
    game board above where the given line was deleted.
    
    INPUTS:
        linesite  = the y coordinate of where the 'line' was deleted from
        boardrect = a pygame.rect.Rect object that describes the game board 
                    geometry
    RETURNS:
        a 'catcher' object with the appropriate dimensions
    ERRORS:
        None
    """
    def __init__( self, linesite, boardrect ):
        self.rect = Rect(0,0,boardrect.width,linesite)
        logger.debug("Creating a fallcatcher with rect: %r" % self.rect)
    

#FIXME: store default width/height on object creation (if this is persistent)
class CollDetector( object ):
    """
    Imitation Sprite used to detect collisions for determining if a row can
    be eliminated or not.
    """
    def __init__( self, boardrect, cubelen=None ):
        """
        INPUTS:
            boardrect = pygame.rect.Rect object describing the board dimensions
            cubelen   = side length of the game cubes. If this is defined in the 
                        global namespace (CUBELEN) then that value is used, and 
                        cubelen is ignored
        RETURNS:
            a CollDetector object
        ERRORS:
            ValueError exception, if CUBELEN not in global namespace, and 
                                  cubelen was not defined
        """
        if 'CUBELEN' in globals():
            self.CubeLen = CUBELEN
        elif cubelen == None:
            raise ValueError, "CUBELEN not in global namespace, and cubelen was not defined!"
        else:
            self.CubeLen = cubelen
        self.boardbottom = boardrect.height
        self.rect = Rect(0,0,boardrect.width,1)
        self.reset()
        
    def stepup( self ):
        """
        Move self up by one self.CubeLen
        
        INPUTS:
            None
        RETURNS:
            None
        ERRORS:
            None
        """
        self.rect.bottom = self.rect.bottom - self.CubeLen
        
    def reset( self ):
        """
        Reset the CollDetector to default position (bottom of game board)
        
        INPUTS:
            None
        RETURNS:
            None
        ERRORS:
            None
        """
        self.rect.bottom = floor(self.boardbottom - 0.5*self.CubeLen)


#TODO: need a better method to do this
def hitfloor( fallersprite, fallensprite ):
    """
    simple falling Collision-detector
    
    INPUTS:
        fallersprite = The sprite which is 'falling' 
        fallensprite = any immobile sprite (presumably the floor or similar)
    RETURNS:
        Boolean, indicating occurence of collision
    ERRORS:
        None
    """
#    screenrect = pygame.display.get_surface().get_rect()
    conds = [
                (fallersprite.rect.bottom ) == fallensprite.rect.top,
                fallersprite.rect.left == fallensprite.rect.left
            ]
    
    if all( conds ):# or ( fallersprite.rect.bottom >= screenrect.bottom ):
        return True
    else:
        return False
