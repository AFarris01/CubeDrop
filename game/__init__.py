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

from tetboard import GameBoard, Previewer
from resourceutils import ResourceManager
