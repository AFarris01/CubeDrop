#!/usr/bin/python
#
############################### File Descriptor ################################
#  This file is part of the 'game' module for the program 'CubeDrop'           #
#  tetboard.py  -  By: Andrew Farris                                           #
#                                                                              #
#  CubeDrop is designed to be a good-ole-fasioned Tetris(TM) clone to use      #
#  as practice for using pygame, and a few other python libraries I haven't    #
#  made frequent use of. In addition, it is intended to expand on the initial  #
#  game idea by adding some features I found in another tetris clone I used to #
#  have on Gameboy(TM), and other stuff I thought was cool.                    #
#                                                                              #
#  This file contains the core object of CubeDrop - the Tetris game board.     #
#  Defined here are the base behaviors of the board itself, as well as all     #
#  sub-parts of the board, including the cubes etc, with everything wrapped    #
#  up in a sort of pygame widget for simple, straightforward usage.            #
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
    import objects
    import logging
    import detectors
    import gameutils
    import varycolor
    from gui import StaticTextWidget
    from random import uniform
    from pygame import Surface
    from pygame.locals import *
    from pygame import sprite, time, transform, key
    from pygame.mixer import music
except ImportError, err:
    raise SystemExit, "ERROR in %s: Couldn't load a required module: %s" % (__name__,err)

TICKDROP_EVENT = USEREVENT + 1
LINEDROP_EVENT = USEREVENT + 2

logger = logging.getLogger( __name__ )

def wrandom( weightlist ):
    """
    Make a selection, based on a weighted list
    
    INPUTS:
        weightlist = list of 'weights' to pick from, 1 for every item in a 
                     corresponding external list
    RETURNS:
        int, the index of the weightlist entry where the random choice falls
    """
    rnd = uniform(0,1) * sum(weightlist)
    for i, w in enumerate(weightlist):
        rnd -= w
        if rnd < 0:
            return i
            
def printcounts( rlist ):
    """ print out counts for contents of a list (use for judging weighted random) """
    core = set(rlist)
    counts = []
    for each in core:
        counts.append( (rlist.count(each),each) )
    counts = sorted( counts, reverse=True )
    for num,key in counts:
        print "For item %r, count: %r" % ( key,num  )
        

class Boarders( object ):
    """
    Class containing game board edges, for easier access.
    Pun is intended. :)
    """
    def __init__( self, leftside=None, rightside=None, bottom=None ):
        self.left  = leftside
        self.right = rightside
        self.floor = bottom


#TODO: random shape-generation?
class ShapesMgr( object ):
    """
    Container class for game board pieces
    """
    _pieces = {
                'base':['1111', '011,110', '110,011','100,111','001,111', '11,11', '010,111'],
                'extended':['1', '1,1', '101,111', '01,11','1,1,1'],
                'hard':['111,101,111', '101,010', '100,011', '1101','1001','010,101,010','111,000,111'],
                'troll':['1110101011100011000011000100010111,0100111011000100010100100110110110,0100101011100111010011010101010111',
                     '100111010,100101010,110111011'],
                'custom':[]
              }
              
    def __init__( self, extras=None, enabled=['base'], weights={'base':1,'extended':0.6,'hard':0.3,'troll':0.005,'custom':1}, preview=3 ):
        """
        INPUTS:
            extras  = a list of extra shape definition strings
            enabled = a list containing the piece classes that should be
                      enabled for use. Available classes are currently:
                      'base', 'extended', 'hard', 'troll', and 'custom'.
                      NOTE: 'troll' class requires a board width of at least 35
                            cubes to use.
            weights = a dict of weight values of form piece_class:weight_value.
                      weights can be ints or floats. Numbers less than 1 
                      indicate decreasing probability, whereas numbers greater
                      than one indicate increasing probability. Unspeficied
                      weights default to 1.
            preview = length of the piece 'preview' list for the ShapesMgr
        """
        #TODO: Add support for passing an 'extras' dict instead of just a list 
        if extras is not None:
            self.__class__._pieces['custom'] = extras
            
        self.pieces = []
        self._weights = weights
        self.weights = []
        self.preview = preview
                
        self.buildshapes( enabled, weights )
        #FIXME: varycolor produces green twice: at the beginning and the end
        self.colors = varycolor.varycolor( len(self.pieces)+1 )
        
        # Set up piece preview cache
        self._queue=[[None, None] for x in range(preview)]
        self.fillqueue()
            
    def buildshapes( self, enabled, weights=None ):
        self.pieces = []
        self.weights = []
        for index in enabled:
            logger.debug( 'Enabling Shape Set: %r' % index )
            self.pieces.extend( self.__class__._pieces[index] )
            for each in self.__class__._pieces[index]:
                if weights == None:
                    self.weights.append( self._weights.get( index, 1 ) )
                else:
                    self.weights.append( weights.get( index, 1 ) )
        self.colors = varycolor.varycolor( len(self.pieces)+1 )
            
    def _mkpiece( self ):
        index = wrandom( self.weights )
        logger.debug("In _mkpiece: index: %r" % (index))
        logger.debug("In _mkpiece: pieces(%i): %r" % (len(self.pieces),self.pieces))
        logger.debug("In _mkpiece: Weights(%i): %r" % (len(self.weights),self.weights))
        return (self.pieces[index], self.colors[index])
        
    def resetqueue(self):
        self._queue=[[None, None] for x in range(self.preview)]
        logger.debug("In _mkpiece: Queue Reset. %r" % self._queue)
        self.fillqueue()
        
    def fillqueue( self ):
        """
        Fill the piece queue
        """
        #TODO: Make this able to detect/fill empty entries too
        for i in range(self.preview):
            self._queue[i] = self._mkpiece()
        
    def get( self ):
        """
        Return a random piece signature (and a color for it??)
        """
        ret = self._queue.pop(0)
        self._queue.append( self._mkpiece() )
        logging.debug( "Preparing to generate Shape! Stats: (%r,%r)" % ret )
        return ret
        
    def peek( self ):
        """
        Reveal the piece queue (by returning a copy)
        """
        return self._queue[:]


#TODO: Create a keyboard mapping, and an internal function list that the keys are mapped to
class GameBoard( object ):
    """
    Core CubeDrop object. This is the actual gameboard itself. This is meant to
    act like a regular pygame.Sprite, without the actual sprite overhead.
    """
    kMAP = {
            'BUMPLEFT' : K_LEFT,
            'BUMPRIGHT': K_RIGHT,
            'BUMPDOWN' : K_DOWN,
            'DROP'     : K_SPACE,
            'ROTATE'   : K_UP
            }
            
    def __init__( self, resourcemgr, width, height, cubelen, level=1, leveling=False, sets=['base'] ):
        """
            INPUTS:
                resourcemgr = link to an external resource manager
                width   = width of the gameboard (in tiles)
                height  = height of the gameboard (in tiles)
                cubelen = tile side-length (used for making the Cubes etc)
            RETURNS:
            ERRORS:
        """
        # Create the main surface for this object
        self.image = Surface( (width*cubelen, height*cubelen) )
        
        # other important data
        self.rect = self.image.get_rect()
        self.width = width
        self.height = height
        self.cubelen = cubelen
        self.Resources = resourcemgr
        self._previewhook = False
        self._startlevel_ = level
        self.Level = level
        self.Leveling = leveling
        self._active = False
        self._paused = False
        self._gameover = False
        
        # Initialize object groups
        self.wall = sprite.RenderUpdates()
        self.fallen = sprite.RenderUpdates()
        self.faller = objects.FallerGroup()
        
        # a list for sprite groups falling due to line deletion.
        self.fallenfallers = []

        #create important objects
#        background = objects.Backdrop( self.rect )
        l = objects.Wall(self.rect, 'left')
        r = objects.Wall(self.rect, 'right')
        f = objects.Floor(self.rect)
        self.border = Boarders( l,r,f )
        self.scoreboard = objects.ScoreKeeper()
        self.pieces = ShapesMgr(enabled=sets)
        self.spawnbox = objects.SpawnBox( self.rect, 3,2, cubelen )
        
        # Collision Detectors
        self.linefulldetector = detectors.CollDetector(self.rect, cubelen)

        # start a reguler event, used to trigger pieces falling
        self._set_timer( TICKDROP_EVENT )
        
    def activesets( self, shapes ):
        self.pieces.buildshapes( shapes )
        
    def SetStart( self, level ):
        self._startlevel_ = level
        
    def reset( self ):
        self.fallen.empty()
        self.faller.empty()
        self.wall.empty()
        self.fallenfallers=[]
        self.scoreboard.reset()
        self.pieces.resetqueue()
        self.Level = self._startlevel_
        self._set_timer( TICKDROP_EVENT )
        self._gameover = False
        
    def Pause( self ):
        if self._paused:
            self._paused = False
            music.unpause()
            self.wall.empty()
        else:
            self._paused = True
            music.pause()
            s = StaticTextWidget("Paused", (255,255,255), 3*self.cubelen)
            s.rect.center = self.rect.center
            self.wall.add( s )
            
    def GameOver( self ):
        music.stop()
        self.Resources.get('sound','end').play()
        for each in self.fallen:
            each.desaturate()

        self._gameover = True
        s = StaticTextWidget("Game Over!", (255,255,255), 3*self.cubelen)
        t = StaticTextWidget("Score: %s" % self.scoreboard.get_score(), (255,255,255), 2*self.cubelen)
        s.rect.center = self.rect.center
        t.rect.center = self.rect.center
        t.rect.top += s.rect.height
        self.wall.add( s )
        self.wall.add( t )
        
    def _set_timer( self, eventtype ):
        if self.Leveling:
            if (eventtype == TICKDROP_EVENT):
                if 0 < self.Level < 20:
                    t = 2100 - self.Level*100
                    d = 310-(self.Level*10)
                    r = 51-self.Level
                elif 20 <= self.Level < 30:
                    t = 100 - (self.Level % 10)*10
                    d = 310-(self.Level*10)
                    r = 51-self.Level
                elif 30 <= self.Level:
                    t = 10
                    d = 0
                    r = 5
                else:
                    t = 2000
                    d = 300
                    r = 50
                logger.debug("Timer set to %r" % t)
                time.set_timer( TICKDROP_EVENT, t )
                #set_repeat(repeat_delay, repeat_frequency)
                key.set_repeat(d,r)
            elif (eventtype == LINEDROP_EVENT):
                time.set_timer( LINEDROP_EVENT, 100 )
        else:
            if (eventtype == TICKDROP_EVENT):
                time.set_timer( TICKDROP_EVENT, 2000 )
                key.set_repeat(300,500)
            elif (eventtype == LINEDROP_EVENT):
                time.set_timer( LINEDROP_EVENT, 100 )
        
    def maintainfaller( self ):
        """
        check to see if a piece is falling. if not, make one.
        """
        if not self.faller and not self.fallenfallers:
            pcshape, pccolor = self.pieces.get()
            sp = self.spawnbox.spawnpoint()
            graphic = self.Resources.get('image', 'Cube')
            newshape = gameutils.GenerateShape( pcshape, graphic, xoffset=sp, mcolor=pccolor, cubelen=self.cubelen )
            self.faller.add( newshape )
            absbottom = max([x.rect.bottom for x in self.faller])
            if absbottom > self.spawnbox.rect.bottom:
                for sprite in self.faller:
                    sprite.stepup()
                logger.debug('Bumped up shape %r' % pcshape)
            self._previewhook = True
                
    def checkforlines( self ):
        """
        Find/remove any full lines.
        Return the number of thingies to score
        """
        remlines=[]
        while True:
            collisions = sprite.spritecollide( self.linefulldetector, self.fallen, False )
            if len(collisions) >= self.width:
                logger.debug("Detected a full line at %i" % self.linefulldetector.rect.bottom)
                self.fallen.remove( collisions )
                remlines.append( self.linefulldetector.rect.bottom )
                self.Resources.get('sound','remove').play()
            elif len(collisions) > 0:
#                logger.debug("Detected a partially full line at %i" % self.linefulldetector.rect.bottom)
                pass
            else:  
                break
            self.linefulldetector.stepup()
        self.linefulldetector.reset()
        remlines.sort()
        for site in remlines:
            collisions = sprite.spritecollide( detectors.FallCatcher(site,self.rect), self.fallen, True )
            self.fallenfallers.append(sprite.RenderUpdates( collisions ))
            self._set_timer( LINEDROP_EVENT )
        return len(remlines)*self.width*round(0.15*len(remlines)+0.81,1), len(remlines)
    
    def EventCatch( self, event ):
        """Wrapper around _EventCatch to add the ability to pause the game"""
        if event.type == KEYDOWN and self._gameover:
            self.Deactivate()
            print "Game is currently over!"
        elif event.type == KEYDOWN and event.key == K_p:
            self.Pause()
        else:
            if not self._paused:
                self._EventCatch( event )
        
    def _EventCatch( self, event ):
        """
        Use this function to process events, recieved from the main program.
        This is where any actions that need to be performed will take place, i.e. tickdropping, linedrops, key events, etc
        """
        if event.type == TICKDROP_EVENT:
            logger.debug("Drop Tick!")
            gameutils.TickDrop( self.faller, self.fallen, self.border.floor )
                
        elif event.type == LINEDROP_EVENT:
            logger.debug("LineDrop!")
            logger.debug("%i Groups found that need to be dropped" % len(self.fallenfallers))
            for eachgrp in self.fallenfallers:
                logger.debug("TickDropping a group")
                gameutils.TickDrop( eachgrp, self.fallen, self.border.floor )
                if not eachgrp.sprites():
                    logger.debug("Group was emptied, deleting the group.")
                    self.fallenfallers.remove(eachgrp)
            if not self.fallenfallers:
                time.set_timer( LINEDROP_EVENT, 0 )
            
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.Deactivate()
                
            elif event.key == self.__class__.kMAP['BUMPLEFT']:
                logger.debug("bumping a shape left")
                if not sprite.spritecollide( self.border.left, self.faller, False ):
                    logger.debug("No collision between faller and borders")
                    self.faller.stepleft()
                    self.Resources.get('sound','bump').play()
                    if sprite.groupcollide( self.faller, self.fallen, False, False ):
                        # The step resulted in a collision... step back
                        self.faller.stepright()
                else:
                    logger.debug("We're gonna hit the left side!")
                    
            elif event.key == self.__class__.kMAP['BUMPRIGHT']:
                logger.debug("Bumping a shape right")
                if not sprite.spritecollide( self.border.right, self.faller, False ):
                    logger.debug("No collision between faller and borders")
                    self.faller.stepright()
                    self.Resources.get('sound','bump').play()
                    if sprite.groupcollide( self.faller, self.fallen, False, False ):
                        # The step resulted in a collision... step back
                        self.faller.stepleft()
                else:
                    logger.debug("We're gonna hit the right side!")
                    
            elif event.key == self.__class__.kMAP['BUMPDOWN']:
                logger.debug("Bumping a shape down")
                gameutils.TickDrop( self.faller, self.fallen, self.border.floor )
                self.Resources.get('sound','bump').play()
                self.scoreboard.mark( (1,0), 'stepdown' )
                    
            elif event.key == self.__class__.kMAP['DROP']:
                logger.debug("Dropping a shape")
                if self.faller:
                    while True:
                        conds = [
                                sprite.spritecollide( self.border.floor, self.faller, False ),
                                sprite.groupcollide( self.faller, self.fallen, False, False, collided=detectors.hitfloor ),
                                gameutils.rectunion( self.faller ).bottom >= self.rect.height
                                ]
                        if any( conds ):
                            break
                        else:
                            self.faller.stepdown()
                            logger.debug("Bumping a sprite Down.")
                        self.scoreboard.mark( (1,0), 'drop' )
                    self.Resources.get('sound','drop').play()
                else:
                    logger.debug('Tried to drop a shape, but no shape was spawned')
                touchdowns = self.faller.sprites()
                self.faller.empty()
                self.fallen.add( touchdowns )
                
            #FIXME: When rotating near the right side of the board, the piece will be able to clip through
            elif event.key == self.__class__.kMAP['ROTATE']:
                logger.debug("Rotating a shape")
                gameutils.Rotate( self.faller.sprites(), K_RIGHT )
                conds = [
                        sprite.spritecollide( self.border.floor, self.faller, False ),
                        sprite.groupcollide( self.faller, self.fallen, False, False ),
                        gameutils.rectunion( self.faller ).right > self.rect.width
                        ]
                logger.debug('Rotate Conds: %r ' % conds)
                if any(conds):
                    # The rotate resulted in a collision... step back
                    gameutils.Rotate( self.faller.sprites(), K_LEFT )
                    self.Resources.get('sound','rotate').play()
        
    def __nonzero__( self ):
        """
        Use this function to determine if the game is currently running or not
        (i.e. before game should be False, during should be True, when paused etc, false.)
        Have 'KeyEvent' and 'update' modify their behavior depending on this mode
        """
        return self._active

    def Activate( self ):
        self._active = True
        
    def Deactivate( self ):
        self._active = False
        
    def update( self ):
        if not self._paused and not self._gameover:
            self._update()
    
    def _update( self ):
        """
        Used to update the state of the game board 
        """
        if sprite.spritecollideany( self.spawnbox, self.fallen ):
            logger.debug('A sprite is contacting the spawnbox. Game Over!')
            self.GameOver()
        if self.Leveling:
            coef = self.Level - self._startlevel_ + 1
            if (self.scoreboard.get_lines()//(coef*10)) > 0:
                self.Level += 1
                self._set_timer( TICKDROP_EVENT )
        self.maintainfaller()
        self.scoreboard.mark( self.checkforlines() )
        self.faller.update()
        self.fallen.update()
        
    def draw( self, screen ):
        """
        Use this function to do all the actual drawing on the screen, i.e. the faller and fallen etc...
        This will basically contain the regular pygame 'update' calls
        """
        #FIXME -- HACK -- We're basically selectively blitting everything onto 
        #     self.image, then blitting the entire self.image onto the screen. 
        #     This is a horrible hack, and needs to be changed to use
        #     selective blitting as soon as possible.
        dirtyspots = self.fallen.draw( self.image )
        dirtyspots += self.faller.draw( self.image )
        for eachgrp in self.fallenfallers:
            dirtyspots += eachgrp.draw( self.image )
            
        dirtyspots += self.wall.draw( self.image )
#        logger.debug(" ------ PreMove ------ ")
#        logger.debug("Our Rect: %r" % self.rect)
#        logger.debug("Dirtyspots: %r" % dirtyspots)

#        screct = screen.get_rect()
#        for each in dirtyspots:
##            screen.blit( self.image, self.rect.topleft, area=each )
#            each.left += self.rect.left
#            each.top += self.rect.top

#        logger.debug( "------ PostMove ------" )
#        logger.debug("Our Rect: %r" % self.rect)
#        logger.debug("Dirtyspots: %r" % dirtyspots)
        
        screen.blit( self.image, self.rect )
#        return dirtyspots
        return [self.rect]
        
        
    def clear( self, screen, bgimg ):
        """
        Use this function to do all the actual drawing on the screen, i.e. the faller and fallen etc...
        """
        #TODO: Should replace this operation with a dirty layers group, so we 
        #      dont erase/redraw so much every iteration
        #FIXME -- HACK -- We're basically selectively blitting everything onto 
        #     self.image, then blitting the entire self.image onto the screen. 
        #     This is a horrible hack, and needs to be changed to use
        #     selective blitting as soon as possible.
#        for eachgrp in self.fallenfallers:
#            eachgrp.clear( self.image, bgimg )
#            eachgrp.clear( screen, bgimg )
#        self.faller.clear( self.image, bgimg )
#        self.faller.clear( screen, bgimg )
#        self.fallen.clear( self.image, bgimg )
#        self.fallen.clear( screen, bgimg )
        if not self._paused:
            self.image.blit(bgimg, (0,0), area=self.rect)
        
        
#TODO: Use sprite groups to manage the drawings!
class Previewer( sprite.DirtySprite ):
    """
    Use to generate piece previews
    """
    def __init__( self, sizerect, gameboard ):
        """
        gameboard = a GameBoard object
        """
        sprite.DirtySprite.__init__(self) #call Sprite initializer
        self._board = gameboard
        self.rect = Rect(sizerect)
        self.image = Surface( (sizerect.width, sizerect.height), SRCALPHA )
        self.border = int((sizerect.width*0.1 + sizerect.height*0.1)//2)
        
    def _get_shapesurf( self, signature, color ):
        """
        Generate a shape with the given signature, and return a surface 
        containing only that shape on it.
        """
        pic = self._board.Resources.get('image', 'Cube')
        cl = self._board.cubelen
        rpl = sprite.Group(gameutils.GenerateShape(signature, graphic=pic, mcolor=color, cubelen=cl))
        sol = gameutils.rectunion( rpl )
        shapesurf = Surface( (sol.width, sol.height), SRCALPHA )
        rpl.draw(shapesurf)
        return shapesurf

    def _get_shapes( self ):
        """
        Generate a list of shape surfaces from the given board's piece preview
        """
        nextpieces = self._board.pieces.peek()
        logging.debug( "Piece Preview: %r" % nextpieces )
        shapes = []
        for sig,color in nextpieces:
            shapes.append( self._get_shapesurf(sig,color) )
        return shapes
        
    def update( self ):
        surflist = self._get_shapes()
        prev = Rect(0,0,0,0)
        for each in surflist:
            erect = each.get_rect()
#            multiplier = (1.0/(1+surflist.index(each)))**0.5
            multiplier = 1.0/(1+surflist.index(each))
            maxheight = multiplier*(self.rect.height - self.border)
            ourrect = Rect( 0, 0, self.rect.width-self.border, maxheight )
            if not ourrect.contains( erect ):
                erect = erect.fit(ourrect) #fit the rect to the available space
            erect.width = erect.width*multiplier
            erect.height = erect.height*multiplier
            each = transform.smoothscale( each, (erect.width, erect.height) )
            erect.centerx = (self.rect.width-self.border)/2 #center the rect
            erect.top = prev.bottom + self.border
            erect.left += int(self.border//2)
            self.image.blit( each, erect.topleft)#, special_flags=BLEND_RGBA_SUB )
            prev = erect.copy()
            
    def clear( self, screen, background ):
        self.image.blit( background, (0,0), area=self.rect )
        
    def draw( self, screen ):
        screen.blit( self.image, self.rect.topleft )
        return [self.rect.copy()]
        
    def NeedPreview( self ):
        if self._board._previewhook:
            self._board._previewhook = False
            return True
        else:
            return False
            
            
#class PiecePreview( sprite.DirtySprite ):
#    def 
