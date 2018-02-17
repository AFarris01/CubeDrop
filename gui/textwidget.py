#! /usr/bin/env python

# textwidget.py
#
# Copyright 2008 Mark Mruss <selsine@gmail.com>
#
# This file is part of textwidget.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# If you find any bugs or have any suggestions email: selsine@gmail.com
# URL: http://www.learningpython.com
#
# Feel free to use this in whatever manner you want, but if you do end
# up using it, I would appreciate it if you sent me an email and let
# me know.

"""
History:

2008-09-29
- Added the example code
- Changed the way that the font_filename was handled, now the full
path is tested first.
- Added the message types
- Added the ability to turn the messages off
- renamed the .py file to be textwidget.py instead of TextWidget.py
to conform with PEP 8.

0.1.1: 2008/09/24
- Fixed a bug where pygame.local.USEREVENT was not defined for some
versions of pygame. Switched to pygame.USEREVENT. May have to make this
switch based on pygame versions at some point.

0.1: 2008/09/21

- Fixed a bug where the font filename was always being treated as
a full path.
- Fixed a bug where an exception thrown when trying to create the
the PyGame font was not being handled well. Now if the font creation
fails TextWidget will try to use the default font.

Initial release: 2006/12/18
"""

__author__ = "Mark Mruss <selsine@gmail.com>"
__version__ = "0.1.1"
__date__ = "Date: 2008/09/21"
__copyright__ = "Copyright (c) 2008 Mark Mruss"
__license__ = "LGPL"

import os
import pygame

TEXT_WIDGET_CLICK = pygame.USEREVENT + 143

QUIET = False
TEXT_WIDGET_WARNING = 0
TEXT_WIDGET_ERROR = 1
TEXT_WIDGET_NOTICE = 2


class TextWidget(object):
    """This is a helper class for handling text in PyGame.  It performs
    some basic highlighting and tells you when the text has been clicked.
    This is just one of the many ways to handle your text.
    """
    #Hand Cursor
    __hand_cursor_string = (
    "     XX         ",
    "    X..X        ",
    "    X..X        ",
    "    X..X        ",
    "    X..XXXXX    ",
    "    X..X..X.XX  ",
    " XX X..X..X.X.X ",
    "X..XX.........X ",
    "X...X.........X ",
    " X.....X.X.X..X ",
    "  X....X.X.X..X ",
    "  X....X.X.X.X  ",
    "   X...X.X.X.X  ",
    "    X.......X   ",
    "     X....X.X   ",
    "     XXXXX XX   ")
    __hcurs, __hmask = pygame.cursors.compile(__hand_cursor_string
        , ".", "X")
    __hand = ((16, 16), (5, 1), __hcurs, __hmask)

    #Text
    def __get_text(self):
        return self.__m_text
    def __set_text(self, text):
        if (self.__m_text != text):
            self.__m_text = text
            self.update_surface()
    def __del_text(self):
        del self.__m_text
    def __doc_text(self):
        return "The text to be displayed by the text widget"
    text = property(__get_text, __set_text, __del_text, __doc_text)

    #Colour
    def __get_colour(self):
        return self.__m_colour
    def __set_colour(self, colour):
        if (self.__m_colour != colour):
            self.__m_colour = colour
            self.update_surface()
    colour = property(__get_colour, __set_colour)

    #Size
    def __get_size(self):
        return self.__m_size
    def __set_size(self, size):
        if (self.__m_size != size):
            self.__m_size = size
            self.create_font()
    size = property(__get_size, __set_size)

    #Font Filename
    def __get_font_filename(self):
        return self.__m_font_filename
    def __set_font_filename(self, font_filename):
        if (self.__m_font_filename != font_filename):
            self.__m_font_filename = font_filename
            # Try to join with the local path
            full_path = os.path.join(self.__local_path
                    , self.__m_font_filename)
            if (os.access(full_path, os.F_OK)):
                #Full path works so use it
                self.__m_font_filename = full_path
            elif (not os.access(self.__m_font_filename, os.F_OK)):
                #Whoops can't find the fond
                msg = "Font file cannot be found: %s" % \
                    self.__m_font_filename
                self._output_message(msg, TEXT_WIDGET_WARNING)

            self.create_font()
    font_filename = property(__get_font_filename, __set_font_filename)

    #Highlight
    def __get_highlight(self):
        return self.__m_highlight
    def __set_highlight(self, highlight):
        if (not(self.__m_highlight == highlight)):
            #Save the bold_rect
            if (self.__m_highlight):
                self.bold_rect = self.rect
            self.__m_highlight = highlight
            #update the cursor
            self.update_cursor()
            if (highlight):
                self.size += self.highlight_increase
            else:
                self.size -= self.highlight_increase
            if (self.highlight_increase == 0):
                self.create_font()
    highlight = property(__get_highlight, __set_highlight)

    #Show Highlight Cursor
    def __get_highlight_cursor(self):
        return self.__m_highlight_cursor
    def __set_highlight_cursor(self, highlight_cursor):
        if (self.__m_highlight_cursor != highlight_cursor):
            self.__m_highlight_cursor = highlight_cursor
            self.update_cursor()
    highlight_cursor = property(__get_highlight_cursor
        , __set_highlight_cursor)

    def __init__(self, text="", colour=(0,0,0), size=32
                , highlight_increase = 20, font_filename=None
                , show_highlight_cursor = True):
        """Initialize the TextWidget
        @param text = "" - string - The text for the text widget
        @param colour = (0,0,0) - The colour of the text
        @param size = 32 - number - The size of the text
        @param highlight_increase - number - How large do we want the
        text to grow when it is highlighted?
        @param font_filename = None - string the patht to the font file
        to use, None to use the default pygame font.
        @param show_highlight_cursor = True - boolean - Whether or
        not to change the cursor when the text is highlighted.
        The cursor will turn into a hand if this is true.
        """

        #make sure that the pygame font module is initialized
        if (not pygame.font.get_init):
            pygame.font.init()

        #inits
        self.dirty = False
        self.bold_rect = None
        self.highlight_increase = highlight_increase
        self.tracking = False
        self.rect = None

        #Get the local path
        self.__local_path = os.path.realpath(os.path.dirname(__file__))

        #property inits
        self.__m_text = None
        self.__m_colour = None
        self.__m_size = None
        self.__m_font_filename = None
        self.__m_highlight = False
        self.__m_font = None
        self.__m_highlight_cursor = False
        self.__m_rect = None

        self.text = text
        self.colour = colour
        self.size = size
        self.font_filename = font_filename
        self.highlight = False
        self.highlight_cursor = show_highlight_cursor

        self.create_font()

    def __str__(self):
        return "TextWidget: %s at %s" % (self.text, self.rect)

    def update_cursor(self):
        if (self.highlight_cursor):
            if (self.highlight):
                pygame.mouse.set_cursor(*self.__hand)
            else:
                pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def create_font(self):
        """Create the internal font, using the current settings
        """
        if (self.size):
            try:
                self.__m_font = pygame.font.Font(self.font_filename
                    , self.size)
            except Exception, e:
                msg = "Creating font '%s' using file: '%s'" % \
                    (str(e), self.font_filename)
                self._output_message(msg, TEXT_WIDGET_ERROR)
                msg = "Trying with default font: '%s'" % \
                    (pygame.font.get_default_font())
                self._output_message(msg, TEXT_WIDGET_NOTICE)
                self.__m_font_filename = None

                self.__m_font = pygame.font.Font(None, self.size)


            self.update_surface()

    def update_surface(self):
        """Update the current surface, basically render the
        text using the current settings.
        """
        if (self.__m_font):
            self.__m_font.set_bold(self.highlight)
            self.image = self.__m_font.render(self.text
                , True
                , self.colour)
            self.dirty = True
            if (self.rect):
                # Used the current rects center point
                self.rect = self.image.get_rect(center=self.rect.center)
            else:
                self.rect = self.image.get_rect()

    def draw(self, screen):
        """Draw yourself text widget
        @param screen - pygame.Surface - The surface that we will draw
        to
        @returns - pygame.rect - If drawing has occurred this is the
        rect that we drew to.  None if no drawing has occurerd."""

        rect_return = None
        if ((self.image)  and  (self.rect) and (self.dirty)):
            if (self.bold_rect):
                """We may need to overwrite the bold text size
                This gets rid of leftover text when moving from
                bold text to non-bold text.
                """
                rect_return = pygame.Rect(self.bold_rect)
                """Set to None, since we only need to do this
                once."""
                self.bold_rect = None
            else:
                rect_return = self.rect
            #Draw the text
            screen.blit(self.image, self.rect)
            #Dirty no more
            self.dirty = False

            return rect_return

    def on_mouse_button_down(self, event):
        """Called by the main application when the
        MOUSEBUTTONDOWN event fires.
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        #Check for collision
        self.tracking = False
        if (self.rect.collidepoint(event.pos)):
            self.tracking = True

    def on_mouse_button_up(self, event):
        """Called by the main application when the
        MOUSEBUTTONDOWN event fires.
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        #Check for collision
        if ((self.tracking) and (self.rect.collidepoint(event.pos))):
            #Not Tracking anymore
            self.tracking = False
            self.on_mouse_click(event)

    def on_mouse_click(self, event):
        """Called by the main application when the
        MOUSEBUTTONDOWN event fires, and the text widget
        has been clicked on.  You can either let
        this post the event (default) or you can override this
        function call in your app.
        ie. myTextWidget.on_mouse_click = my_click_handler
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        #Create the TEXT_WIDGET_CLICK event
        event_attrib = {}
        event_attrib["button"] = event.button
        event_attrib["pos"] = event.pos
        event_attrib["text_widget"] = self
        e = pygame.event.Event(TEXT_WIDGET_CLICK, event_attrib)
        pygame.event.post(e)


    def _get_msg_type_string(self, msg_type):
        """Overkill much?"""
        type_string = "NOTICE" #default
        if (msg_type == TEXT_WIDGET_WARNING):
            type_string  = "WARNING"
        elif (msg_type == TEXT_WIDGET_ERROR):
            type_string  = "ERROR"
        elif (msg_type == TEXT_WIDGET_NOTICE):
            type_string  = "NOTICE"

        return type_string

    def _output_message(self, message, msg_type):
        """Outputs a warning message if QUIET == False"""
        if (not QUIET):
            full_msg = "TEXT_WIDGET - %s: %s" % \
                (self._get_msg_type_string(msg_type), message)
            print(full_msg)


