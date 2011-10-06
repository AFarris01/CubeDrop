#!/usr/bin/python
#
############################### File Descriptor ################################
#  This file is part of the 'game' module for the program 'CubeDrop'           #
#  gameutils.py  -  By: Andrew Farris                                          #
#                                                                              #
#  CubeDrop is designed to be a good-ole-fasioned Tetris(TM) clone to use      #
#  as practice for using pygame, and a few other python libraries I haven't    #
#  made frequent use of. In addition, it is intended to expand on the initial  #
#  game idea by adding some features I found in another tetris clone I used to #
#  have on Gameboy(TM), and other stuff I thought was cool.                    #
#                                                                              #
#  This file contains general utilities required by the game to operate.       #
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

try:
    import logging
    from objects import Cube
    from pygame import sprite
    from detectors import hitfloor
    from pygame.locals import K_LEFT, K_RIGHT
except ImportError, err:
    raise SystemExit, "ERROR in %s: Couldn't load a required module: %s" % (__name__,err)

logger = logging.getLogger( __name__ )


def blankArray( rows, cols ):
    """
    Generate a blank signature array, of dimension [rows][cols]
    
    INPUTS:
        rows = # of rows to create in the array
        cols = # of cols to create in the array
    RETURNS:
        An array, filled with '0' strings, of the given dimensions
    ERRORS:
        None
    """
    return [['0' for y in range(rows)] for x in range(cols)]
    

def rectunion( objsequence ):
    """
    Return a rect that bounds a sequence of objects
    """
    sol = None
    for each in objsequence:
        if sol == None:
            sol = each.rect.copy()
        else:
            sol = sol.union( each.rect )
    return sol


def CW( strinput ):
    """
    Rotate the given input string signature CW by 90 degrees
    
    INPUTS:
        strinput = the string signature to rotate (i.e. '110,011')
    RETURNS:
        string signature that has been properly rotated.
    ERRORS:
        None
    """
    #TODO: This function is really messy, and has too many loops... need to find a better way to do this
    logger.debug("Rotating shape %r Clockwise!" % strinput)
    
    # Generate a 2D array from the input string
    origarray = [list(a) for a in strinput.split(',')]
    
    #Resize the signature so each row has the same number of cols (if they dont already)
    maxcolsize = max(len(row) for row in origarray)
    for row in origarray:
        row.extend(['0' for x in range(maxcolsize-len(row))])
    
    # Prepare the return array
    rowsize = len(origarray)
    retarray = blankArray( rowsize, maxcolsize )
    for i in range( rowsize ):
        for j in range( maxcolsize ):
            retarray[j][rowsize - 1 - i] = origarray[i][j]
            
    # Re-build a format string from the return array
    retstr = ','.join(''.join(entry) for entry in retarray)
    logger.debug("Returning shape %r" % retstr)    
    return retstr
    
    
def CCW( strinput ):
    """
    Rotate the given input string signature CCW by 90 degrees
    
    INPUTS:
        strinput = the string signature to rotate (i.e. '110,011')
    RETURNS:
        string signature that has been properly rotated.
    ERRORS:
        None
    """
    #TODO: This function is really messy, and has too many loops... need to find a better way to do this
    logger.debug("Rotating shape %r Counter-Clockwise!" % strinput)
    
    # Generate a 2D array from the input string
    origarray = [list(a) for a in strinput.split(',')]
    
    #Resize the signature so each row has the same number of cols (if they dont already)
    maxcolsize = max(len(row) for row in origarray)
    for row in origarray:
        row.extend(['0' for x in range(maxcolsize-len(row))])
    
    # Prepare the return array
    rowsize = len(origarray)
    retarray = blankArray( rowsize, maxcolsize )
    for i in range( rowsize ):
        for j in range( maxcolsize ):
            retarray[maxcolsize - 1 - j][i] = origarray[i][j]
            
    # Re-build a format string from the return array
    retstr = ','.join(''.join(entry) for entry in retarray)
    logger.debug("Returning shape %r" % retstr)
    return retstr


#TODO: Make this operate in-place if a spritelist is given
def GenerateShape(shapedef, graphic=None, xoffset=0, yoffset=0, spritelist=None, mcolor=None, cubelen=None):
    """
    Generate a list of cubes, positioned appropriately, based on a provided
    shape definition.

    INPUTS:
        shapedef = a string, designating the shape layout. Rules are:
                   0 is empty space, 1 is a cube, i.e.: "111", "1011"
                   for 2D shapes, seperate rows with a comma, i.e. "111,001"
        graphic  = an image resource tuple of (image, rect) form
        xoffset  = distance from the left side of the destination surface 
                   that the left edge of the shape should appear.
        yoffset  = distance from the top side of the destination surface 
                   that the left edge of the shape should appear.
        spritelist = list of sprites to be manipulated. If this is None, 
                     then new 'Cube' objects are created instead.
        mcolor   = RGBA colorkey (as generated by pygame.Color) designating 
                   the color of the cubes to be generated. 
        cubelen  = cube side length
    RETURNS:
        an array of 'Cube' objects fitting the shape definition, with 
        appropriately positioned Rects.
        If 'spritelist' is provided, the operation takes place in-place instead
    ERRORS:
        None
    """
    numcubes = shapedef.count( '1' )
    shapearray = shapedef.split(',')
    if spritelist is None:
        if graphic is None:
            raise ValueError, "GenerateShape requires either 'spritelist' or 'graphic' to be defined."
        shape = [ Cube(graphic, color=mcolor, cubelen=cubelen) for x in range(numcubes) ]
    else:
        shape = spritelist
    
    nummoved = 0
    for eachrow in range(len(shapearray)):
        for eachchar in range(len(shapearray[eachrow])):
            if shapearray[eachrow][eachchar] == '1':
                newx = xoffset + ( eachchar * shape[ nummoved ].rect.width )
                newy = yoffset + ( eachrow * shape[ nummoved ].rect.height )
                shape[ nummoved ].rect.left = newx
                shape[ nummoved ].rect.top = newy
                shape[ nummoved ].ShapeSig = shapedef
                shape[ nummoved ].ShapePos = [newx,newy]
                nummoved += 1
    
    logger.debug("Made a shape! Rects: %r " % ([x.rect for x in shape]))
    if not spritelist:
        return shape

#TODO: Make this function operate in-place
def Rotate( spritelist, direction=K_RIGHT ):
    """
    Take a list of sprites, and rotate them all, provided all the shape 
    signatures match. If they do not match, then don't do anything.
    
    INPUTS:
        spritelist = a list of sprites that are to be rotated. Note, they
                     must have a 'ShapeSig' attribute.
        direction  = The direction they must turn, as a pygame keycode.
                     K_LEFT == CCW rotation, K_RIGHT == CW rotation
                     (NOTE: CURRENTLY NOT IMPLIMENTED)
    RETURNS:
        list of Cube sprites, in the correct orientation
    ERRORS:
        ValueError exception, if the value of direction != pygame.locals.K_LEFT
                              or pygame.locals.K_RIGHT
    """
    absbottom = []
    absleft = []
    signatures = []
    widths = []
    heights = []
    
    for each in spritelist:
        absbottom.append(each.rect.bottom)
        absleft.append(each.rect.left)
        signatures.append(each.ShapeSig)
        widths.append(each.rect.width)
        heights.append(each.rect.height)
    
    absbottom = min(absbottom)
    absleft = min(absleft)
    
    conds = []
    conds.extend(x == signatures[0] for x in signatures)
    conds.extend(y == widths[0] for y in widths)
    conds.extend(z == heights[0] for z in heights)
    
    if all( conds ):
        logger.debug( "Shape signatures OK. Rotating...")
        if direction == K_RIGHT:
            newsig = CW(signatures[0])
        elif direction == K_LEFT:
            newsig = CCW(signatures[0])
        else:
            raise ValueError, "Unexpected value given for 'direction'"
        GenerateShape( newsig, xoffset=absleft, yoffset=absbottom-widths[0], spritelist=spritelist )
    else:
        logger.warning( "Shape Signatures don't match, not gonna rotate...")
    
    
def TickDrop( thefaller, thefallen, thefloor ):
    """
    Use this function to step all 'faller' sprites down, with some collision
    detection. Operation is in-place.
    
    INPUTS:
        thefaller = pygame.sprite.Group containing any falling sprites
        thefallen = pygame.sprite.Group containing any stationary sprites
        thefloor  = object with a *.rect, that represents the floor
    RETURNS:
        True if pieces were emptied, False otherwise
    ERRORS:
        None
    """        
    conds = [
            sprite.spritecollide( thefloor, thefaller, False ),
            sprite.groupcollide( thefaller, thefallen, False, False, collided = hitfloor )
            ]
    if any( conds ):
        if sprite.spritecollide( thefloor, thefaller, False ): 
            logger.debug( "A Sprite Touched Down!")
        if sprite.groupcollide( thefaller, thefallen, False, False, collided = hitfloor ):
            logger.debug("A sprite Hit other touchdowns!")
        touchdowns = thefaller.sprites()
        thefaller.empty()
        thefallen.add( touchdowns )
        return True
    else:
        for each in thefaller.sprites():
            each.stepdown()
        return False
