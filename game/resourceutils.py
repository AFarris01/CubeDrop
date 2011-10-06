#!/usr/bin/python
#
############################### File Descriptor ################################
#  This file is part of the 'game' module for the program 'CubeDrop'           #
#  resourceutils.py  -  By: Andrew Farris                                      #
#                                                                              #
#  CubeDrop is designed to be a good-ole-fasioned Tetris(TM) clone to use      #
#  as practice for using pygame, and a few other python libraries I haven't    #
#  made frequent use of. In addition, it is intended to expand on the initial  #
#  game idea by adding some features I found in another tetris clone I used to #
#  have on Gameboy(TM), and other stuff I thought was cool.                    #
#                                                                              #
#  This file contains general utilities for loading, caching, and managing     #
#  in-game resources, such as images and sounds.                               #
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
#TODO: flesh out the nullsound class a little more, so more advanced functions
#      can be used, if need be

try:
    import logging
    import os.path
    import pygame.image
    import pygame.mixer
    from pygame.locals import RLEACCEL
    from pygame import error as pygameerror
except ImportError, err:
    raise SystemExit, "ERROR in %s: Couldn't load a required module: %s" % (__name__,err)

logger = logging.getLogger( __name__ )


class NoneSound( object ):
    """ Dummy sound object """
    def play( self ): 
        pass

#FIXME: Make all resources held in a single dictionary!!
class ResourceManager( object ):
    def __init__( self, path, images, sound, fonts ):
        self.PATH = path
        self.IMAGEDIR = images
        self.SOUNDDIR = sound
        self.FONTDIR = fonts
        self._images = {}
        self._sounds = {}
        self._fonts = {}
        
    def get( self, category, alias ):
        if category == 'image':
            return self._images[alias]
        elif category == 'sound':
            return self._sounds[alias]
        elif category == 'font':
            return self._fonts[alias]
        else:
            raise ValueError, "Unknown category %r" % category
        
    def LoadImage( self, name, alias, colorkey=None, path=None, imagedir="" ):
        """
        Load an image file, given a filename. Also allows setting a special 
        transparency 'colorkey' for the given image file. If the loaded image
        format supports transparency without using a colorkey (i.e. .png, .gif),
        any supplied colorkey is ignored.
        
        INPUTS:
            name     = short filename of object (not including path)
            colorkey = RGB 3-tuple representing the color of transparency
                       None: [default] Dont set colorkey data
                       -1: Read the colorkey of the top-left corner and use that
            path     = path to the root resource directory
            imagedir = sub-path under the root resource directory containing image 
                       resources, if applicable (default is empty string: "")
        RETURNS:
            (image object, image.rect)
        ERRORS:
            ValueError exception, if PATH + IMAGEDIR not in global namespace, and 
                                  'path' argument was not defined
            IOError exception, if the image file is not found or fails to load
        """
        fullname = os.path.join( self.PATH, self.IMAGEDIR, name)
        
        try:
            image = pygame.image.load( fullname )
        except pygameerror, message:
            logger.critical("OOPS: Failed to load image data from %s. Cannot continue." % (fullpath))
            raise IOError, message
        else:
            if image.get_alpha() is None:
                image = image.convert()
            else:
                image = image.convert_alpha()
        
            if ( colorkey is not None ) and ( image.get_alpha() is None ):
                if colorkey is -1:
                    colorkey = image.get_at( (0,0) )
                image.set_colorkey( colorkey, RLEACCEL )
                
            self._images[alias] = image, image.get_rect()

    def LoadSound( self, name, alias, path=None, sounddir="" ):
        """
        Load an sound file, given a filename. If the sound subsystem is not 
        loaded, this returns a dummy sound object.
        IMPORTANT -- This function will not produce any error if a sound file does 
                     not exist, when pygame.mixer could not be loaded
        
        INPUTS:
            name     = short filename of object (not including path)
        RETURNS:
            a playable sound object
        ERRORS:
            ValueError exception, if PATH + SOUNDDIR not in global namespace, and 
                                  the 'path' argument was not defined
            IOError exception, when the given file isn't found or can't be loaded
        """
        fullname = os.path.join( self.PATH, self.SOUNDDIR, name)
            
        if not pygame.mixer:
            return NoneSound()
        else:
            fullname = os.path.join( 'data', name )
            
        try:
            sound = pygame.mixer.Sound( fullname )
        except pygameerror, message:
            logger.critical("OOPS: Failed to load sound data from %s. Cannot continue." % (fullpath))
            raise IOError, message
            
        self._sounds[alias] = sound
        
    def LoadFont( self, name, alias, size, path=None, fontdir="" ):
        fullname = os.path.join( self.PATH, self.FONTDIR, name)

        try:
            fonty = pygame.font.Font( fullname, size )
        except pygameerror, message:
            logger.critical("OOPS: Failed to load font data from %s. Cannot continue." % (fullpath))
            raise IOError, message
            
        self._fonts[alias] = fonty
