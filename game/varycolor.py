#!/usr/bin/python
#
############################### File Descriptor ################################
#  This file is part of the 'game' module for the program 'CubeDrop'           #
#  varycolor.py  -  By: Andrew Farris                                          #
#                   Based on the script 'varycolor.m' by Daniel Helmick (2008) #
#                                                                              #
#  CubeDrop is designed to be a good-ole-fasioned Tetris(TM) clone to use      #
#  as practice for using pygame, and a few other python libraries I haven't    #
#  made frequent use of. In addition, it is intended to expand on the initial  #
#  game idea by adding some features I found in another tetris clone I used to #
#  have on Gameboy(TM), and other stuff I thought was cool.                    #
#                                                                              #
#  This file contains a general purpose utility for generating a spread of     #
#  RGBA color tuples, suitable for use in pygame.                              #
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
#TODO: Neaten this function up, so it does not require so much copy/pasting
#FIXME: varycolor produces green twice: at the beginning and the end

try:
    import logging
    from pygame import Color
    from math import floor, ceil
except ImportError, err:
    raise SystemExit, "ERROR in %s: Couldn't load a required module: %s" % (__name__,err)

logger = logging.getLogger( __name__ )

def varycolor(NumberOfColors):
    """
    Generate a list of semi-evenly distributed RGBA color tuples
    
    INPUTS:
        NumberOfColors = number of colors required. Can be int or float 
                         (floats are automatically rounded up)
    RETURNS:
        a list of RGBA color tuples
    ERRORS:
        TypeError, if the input is not a number
    """
    logger.debug("Beginning color generation routines...")
    # round up, in case we need extra colors to cover a float #
    NumberOfColors = ceil( NumberOfColors )
    logger.debug("Generating %i colors" % NumberOfColors)
    
    ColorSet=[]

    #Take care of the anomolies [Remember: (R, G, B, A)]
    if NumberOfColors<1:
        pass
    elif NumberOfColors==1:
        ColorSet.append( Color(0, 255, 0) )
    elif NumberOfColors==2:
        ColorSet.append( Color(0, 255, 0) )
        ColorSet.append( Color(0, 255, 255) )
    elif NumberOfColors==3:
        ColorSet.append( Color(0, 255, 0) )
        ColorSet.append( Color(0, 255, 255) )
        ColorSet.append( Color(0, 0, 255) )
    elif NumberOfColors==4:
        ColorSet.append( Color(0, 255, 0) )
        ColorSet.append( Color(0, 255, 255) )
        ColorSet.append( Color(0, 0, 255) )
        ColorSet.append( Color(255, 0, 255) )
    elif NumberOfColors==5:
        ColorSet.append( Color(0, 255, 0) )
        ColorSet.append( Color(0, 255, 255) )
        ColorSet.append( Color(0, 0, 255) )
        ColorSet.append( Color(255, 0, 255) )
        ColorSet.append( Color(255, 0, 0) )
    elif NumberOfColors==6:
        ColorSet.append( Color(0, 255, 0) )
        ColorSet.append( Color(0, 255, 255) )
        ColorSet.append( Color(0, 0, 255) )
        ColorSet.append( Color(255, 0, 255) )
        ColorSet.append( Color(255, 0, 0) )
        ColorSet.append( Color(255, 255, 0) )

    else: # where this function has an actual advantage
        #we have 6 segments to distribute into
        EachSec = floor(NumberOfColors/6)
        logger.debug("EachSec: %r" % EachSec)
        
        #how many extra colors are there? 
        Extras = (NumberOfColors % 6)
        logger.debug("Extras: %r" % Extras)
        
        #initialize our vector
        ColorSet=[0 for c in range(int(NumberOfColors))]
        
        #This is to deal with the extra colors that don't fit nicely into the
        #segments
        Adjust=[0 for c in range(6)]
        for m in range(int(Extras)):
            Adjust[m]=1
        logger.debug("Adjust: %r" % Adjust)
        
        SecOne   = EachSec+Adjust[0]
        SecTwo   = EachSec+Adjust[1]
        SecThree = EachSec+Adjust[2]
        SecFour  = EachSec+Adjust[3]
        SecFive  = EachSec+Adjust[4]
        SecSix   = EachSec+Adjust[5]
        
#        print "Secs-- 1:%i, 2:%i, 3:%i, 4:%i, 5:%i, 6:%i" % (SecOne, SecTwo, SecThree, SecFour, SecFive, SecSix)
        
        for m in range(1,int(SecOne)+1):
#            print "SecOne Colors: ", 255.0*((m-1.0)/(SecOne-1.0))
            ColorSet[int(m)-1]=Color( 0, 255, int(round(255.0*((m-1)/(SecOne-1)))) )

        for m in range(1,int(SecTwo)+1):
#            print "SecTwo Colors: ", 255.0*((SecTwo-m)/(SecTwo))
            ColorSet[int(m+SecOne)-1]=Color( 0, int(round(255.0*((SecTwo-m)/(SecTwo)))), 255 )
        
        for m in range(1,int(SecThree)+1):
#            print "SecThree Colors: ", 255.0*((m)/(SecThree))
            ColorSet[int(m+SecOne+SecTwo)-1]=Color( int(round(255.0*((m)/(SecThree)))), 0, 255 )
        
        for m in range(1,int(SecFour)+1):
#            print "SecFour Colors: ", 255.0*((SecFour-m)/(SecFour))
            ColorSet[int(m+SecOne+SecTwo+SecThree)-1]=Color( 255, 0, int(round(255.0*((SecFour-m)/(SecFour)))) )

        for m in range(1,int(SecFive)+1):
#            print "SecFive Colors: ", 255.0*((m)/(SecFive))
            ColorSet[int(m+SecOne+SecTwo+SecThree+SecFour)-1]=Color( 255, int(round(255.0*((m)/(SecFive)))), 0 )
            
        for m in range(1,int(SecSix)+1):
#            print "SecSix Colors: ", 255.0*((SecSix-m)/(SecSix))
            ColorSet[int(m+SecOne+SecTwo+SecThree+SecFour+SecFive)-1]=Color( int(round(255.0*((SecSix-m)/(SecSix)))), 255, 0 )
        
    logger.debug( 'Finished Generating colors! %i colors generated.' % len(ColorSet) )
    return ColorSet
