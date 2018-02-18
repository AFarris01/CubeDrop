#!/usr/bin/python
#
############################### File Descriptor ################################
#  This file is the main file for the 'CubeDrop' Program                       #
#  cubedrop.py  -  By: Andrew Farris                                           #
#                                                                              #
#  This program is designed to be a good-ole-fasioned Tetris(TM) clone to use  #
#  as practice for using pygame, and a few other python libraries I haven't    #
#  made frequent use of.                                                       #
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
#TODO: All program resources (images and sound) should be loaded from a single 
#      source, then just repeatedly read/copied from there, instead of 
#      repeatedly loading from the hard-disk


#------------------------------------------------------------------------------#
#                    Library Setup and Global Data                             #
#------------------------------------------------------------------------------#

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
#h = logging.StreamHandler()
#f = logging.Formatter("%(asctime)s [%(levelname)s] %(funcName)s %(lineno)d  %(message)s")
#h.setFormatter(f)
#logger.addHandler( h )

DEBUG       = True
VERSION     = "0.8.0"
COPYRIGHT   = "Copyright \xc2\xa9 2011 Andrew Farris -- GNU GPL v3"
WEBSITE     = "N/A"
PROGNAME    = "CubeDrop"

#CUBELEN = 30
CUBELEN = 50
#CUBELEN = 15
BOARDWIDTH = 14
#BOARDWIDTH = 60
BOARDHEIGHT = 20
#BOARDHEIGHT = 40
MAXFPS = 60

# record the current execution path as the central resource path
PATH = os.path.dirname(os.path.realpath(__file__))
print PATH
IMAGEDIR = 'data'
SOUNDDIR = 'data'
FONTDIR  = 'data'


AUTHORS = []
try:
    with open( os.path.join( PATH, 'AUTHORS' ) ) as authfile:
        for line in authfile: 
            AUTHORS.append( line.strip() )
except IOError:
    logger.exception("DERP! No AUTHORS File found in execution directory!")
    AUTHORS.append("")
	
	
#------------------------------------------------------------------------------#
#                         Global Utility Functions                             #
#------------------------------------------------------------------------------#


def Debugging( option, opt, value, parser ):
    """
        Callback for enabling/disabling debugging via the command line. 
        This function shouldnt need to be called by itself
        
        INPUTS:
            option = optionparser 'option' object
            opt    = the actual option found in the call
            value  = any 'value' data collected with 'opt'
            parser = a reference to the actual optionparser object
        RETURNS:
            None
    """
    global DEBUG
    
    if str(option) == '-d/--debug':
        DEBUG = True
    elif str(option) == '--no-debug':
        DEBUG = False
        
        
def ReportOnModule( mdname, isinit ):
    if isinit:
        logger.info( "%s Module Initialized Successfully!" % mdname )
    else:
        logger.warning( "%s Module failed to initialize..." % mdname )
        
        
def PrintProgramData():
    print "%s -- v%s " % ( PROGNAME, VERSION )
    print COPYRIGHT
    ######### Display Program Authors #########
    print "\n%s:\n\t" % ( "Authors" if len(AUTHORS)>1 else "Author" ) + "\t".join( AUTHORS )
        
    ######### Display platform data #########
    logger.info( "Platform:\n\t%s" % platform.platform() )
    
    ######### Display Python, Pygame, and any other relevant Versions #########
    logger.info( "Software Versions:\n\t"+"\n\t".join((
                                               platform.python_implementation()+
                                               ' '+platform.python_version(),
                                               'Pygame ' + pygame.ver,
                                               'SDL '+ ".".join( `n` for n in pygame.get_sdl_version() )
                                             )) )
    
    ######### Display presence checks for required pygame modules #########
    logger.info( "Essential Subsystems:" )
    logger.info( '\t%s' % ( "Sound SubSystem is Available." if pygame.mixer else "Sound SubSystem Unavailable." ) )
    logger.info( '\t%s' % ( "Font SubSystem is Available." if pygame.font else "Font SubSystem Unavailable." ) )
    logger.info( '\t%s' % ( "Music SubSystem is Available." if pygame.mixer_music else "Music SubSystem Unavailable." ) )

def FireUpPygame():
    logger.info( "Starting PyGame Modules:" )
    logger.info( "Display subsystem is starting..." )
    pygame.display.init()
    ReportOnModule( 'Display', pygame.display.get_init() )
    logger.info( "Font subsystem is starting..." )
    pygame.font.init()
    ReportOnModule( 'Font', pygame.font.get_init() )
    logger.info( "Sound subsystem is starting..." )
    pygame.mixer.pre_init(44100, -16, 2)
    pygame.mixer.init()
    ReportOnModule( 'Sound', pygame.mixer.get_init() )
    atexit.register(pygame.quit)
    
def MakeBorders( resources, background, *args ):
    bordermaker = gui.Border( resources.get('image','Borders') )
    bgrect=background.get_rect()
    retsurf=pygame.Surface( (bgrect.width, bgrect.height), SRCALPHA )
    for each in args:
        itemborder = bordermaker.makeborder( each, background )
        retsurf.blit( itemborder[0], itemborder[1] )
    
    return retsurf
    
#------------------------------------------------------------------------------#
#                        Class Definitions                                     #
#------------------------------------------------------------------------------#


class CMDLineParser( optparse.OptionParser ):
    """
        Command-line Option Parser custom class, that pre-sets up the parser
        with the needed options, and some custom data
    """
    
    descript = "This program is designed to be a good-ole-fasioned Tetris(TM) clone."
    
    # Use a variable substitution and inline conditional to create an author list
#    descript += "\n%s:\n\t" % ( "Authors" if len(AUTHORS)>1 else "Author" ) + "\t".join( AUTHORS )
    
    def __init__( self ):
        """
            Create an instance of this custom option-parser.
        """
        optparse.OptionParser.__init__( self, version = VERSION, 
                                        description = self.descript 
                                      )
        self.add_option( '-d', '--debug', action = 'callback', 
                         callback = Debugging, 
                         help="Enable Debugging %s"%('[default]' if DEBUG else '')
                       )
        self.add_option( '--no-debug', action = 'callback', 
                         callback = Debugging, 
                         help="Disable Debugging %s" % ('[default]' if not DEBUG else '')
                       )


#------------------------------------------------------------------------------#
#                         Main Program Execution                               #
#------------------------------------------------------------------------------#


if __name__ == '__main__':
    ######### Parse Command-Line Options #########
    parser = CMDLineParser(  )
    (options, args) = parser.parse_args()
    
    # do stuff based on any options left
    parser.destroy()
    
    logging.basicConfig(level=logging.DEBUG)
    
    ######### Display Startup Message w/ Program Name and Version #########
    PrintProgramData()
    
    #########?? Show Splash Screen while loading external resources ??#########
    FireUpPygame()

    ######### Create required game objects (display, menus, etc.) #########
    width = (BOARDWIDTH+4)*CUBELEN
    height = (BOARDHEIGHT)*CUBELEN + 10
    screen = pygame.display.set_mode( (width, height), RESIZABLE )
    background = pygame.Surface( (width, height) ).convert()
    background.fill((255,255,255))
    pygame.key.set_repeat(300,50)
    pygame.display.set_caption('CubeDrop')
    gameclock = pygame.time.Clock()
    screen.blit(pygame.font.SysFont('Arial', CUBELEN*2,).render("Loading...",True,(255,255,255),(0,0,0)),(CUBELEN,CUBELEN))
    pygame.display.flip()
    
    resources = game.ResourceManager( PATH, IMAGEDIR, SOUNDDIR, FONTDIR )
    resources.LoadImage( 'boxxen.png', 'Cube' )
    resources.LoadImage( 'borders.png', 'Borders' )
    resources.LoadImage( 'backdrop.png', 'Backdrop' )
    resources.LoadFont( 'Biolinum_Re-0.4.1RO.ttf', 'sysfont', CUBELEN )
    resources.LoadSound( 'rotate.ogg', 'rotate' )
    resources.LoadSound( 'remove.ogg', 'remove' )
    resources.LoadSound( 'bump.ogg', 'bump' )
    resources.LoadSound( 'drop.ogg', 'drop' )
    resources.LoadSound( 'end.ogg', 'end' )
    
    background.blit( pygame.transform.smoothscale(resources.get('image', 'Backdrop')[0], (width, height)), (0,0) )
    
    isgame = game.GameBoard(resources, BOARDWIDTH, BOARDHEIGHT, CUBELEN, level=1, leveling=True, sets=['base'])
    isgame.rect.topleft=(5,5)

    previewrect = pygame.Rect(width-3*CUBELEN-5,5, 3*CUBELEN, 9*CUBELEN )
    preview = game.Previewer( previewrect, isgame )
    scorerect = pygame.Rect(width-3*CUBELEN-5,10*CUBELEN, 3*CUBELEN, 2*CUBELEN )    
    levelrect = pygame.Rect(width-3*CUBELEN-5,13*CUBELEN, 3*CUBELEN, 2*CUBELEN )
    linesrect = pygame.Rect(width-3*CUBELEN-5,16*CUBELEN, 3*CUBELEN, 2*CUBELEN )
    
    borders = MakeBorders( resources, background, isgame.rect, previewrect, scorerect, levelrect, linesrect )
    pygame.mixer.music.load( os.path.join(PATH,SOUNDDIR,'bgm.ogg') )
    
    #########?? Kill the Splash Screen ??#########
    
    ######### Show the display #########    
    screen.blit(background, (0,0))
    pygame.display.flip()
    
    buttons = ['New Game','High Scores','Options','Exit']
    colors = [(115,251,251),(182,115,250),(182,250,115),(250,115,115)]
    callbacks = [None,None,None,sys.exit]
        
    menus = gui.Menu( screen.get_rect(), zip(buttons,colors,callbacks), resources.get('font','sysfont') )
    options = gui.OptionsMenu( screen.get_rect() )

    def OpenOptions(event):
        pygame.mixer.music.stop()
        pygame.mouse.set_visible(1)
        options.MenuActivate()
        menus.MenuDeactivate()
        isgame.Deactivate()
        print "Opening Options!"
        
    def OpenMain(event):
        pygame.mixer.music.stop()
        pygame.mouse.set_visible(1)
        menus.MenuActivate()
        options.MenuDeactivate()
        isgame.Deactivate()
        
    def OpenGame(event):
        defs = {'base':options.base.state,
                'extended':options.extended.state,
                'hard':options.hard.state,
                'troll':options.troll.state,
                'custom':options.custom.state
                }
        enabled = []
        for each in defs:
            if defs[each]:
                enabled.append(each)
        isgame.activesets(enabled)
        isgame.SetStart(options.start.value)
        logging.debug( "Enabled Pieces: %r" % isgame.pieces.pieces)
        isgame.reset()
        options.MenuDeactivate()
        pygame.mouse.set_visible(0)
        menus.MenuDeactivate()
        pygame.mixer.music.play(-1)
        print "Starting Game!"
        isgame.Activate()

    options.back.on_mouse_click = OpenMain
    menus.fetchwidget('Options').on_mouse_click = OpenOptions
    menus.fetchwidget('New Game').on_mouse_click = OpenGame
    
    manager = gui.Manager( menus, options, isgame )

    ######### Begin Pygame Main Loop #########
    cont = True
    while cont:
        try:
            gameclock.tick(MAXFPS)
            for event in pygame.event.get():
                if menus:
                    menus.EventCatch( event )
                elif options:
                    options.EventCatch( event )
                elif isgame:
                    isgame.EventCatch( event )
                
                if event.type == QUIT:
                    logger.debug("Caught Quit signal. Stopping.")
                    cont = False
                    
            dirtyspots=[]
            
            if manager.statechanged():
                screen.blit(background,(0,0))
                pygame.display.flip()
            
            if options:
                options.clear( screen, background )
                options.update()
                dirtyspots += options.draw( screen )
            elif isgame:
                screen.blit( borders, (0,0) )
                isgame.clear( screen, background )
                isgame.update()
                dirtyspots += isgame.draw( screen )
                fon = resources.get('font','sysfont')
                
#                l = resources.get('font','sysfont').render( "Score:", True, (255,255,255) )
                s = isgame.scoreboard.renderscore( fon )
#                s[1].top = l.get_rect().bottom
#                screen.blit(l,scorerect,area=l.get_rect())
                screen.blit(s[0],scorerect,area=s[1])
                dirtyspots += [scorerect]
                
                lin = fon.render( "L:%i" % isgame.scoreboard.get_lines(), True, (255,255,255))
                screen.blit(lin,linesrect,area=lin.get_rect())
                dirtyspots += [scorerect]
                
                s = fon.render( "Lvl: %i" % isgame.Level, True, (255,255,255) )
                screen.blit(s,levelrect,area=s.get_rect())
                dirtyspots += [levelrect]

                if preview.NeedPreview():
                    pygame.display.flip()
                    preview.clear( screen, background )
                    preview.update()
                    dirtyspots += preview.draw( screen )
                    
            else:
                OpenMain(None)
                menus.clear( screen, background )
                menus.update()
                dirtyspots += menus.draw( screen )
            
            pygame.display.update( dirtyspots )
            
        except KeyboardInterrupt:
            logger.info('Caught a keyboard interrupt, stopping!')
            cont = False
