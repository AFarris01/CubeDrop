#!/usr/bin/python

import logging
import widgets
import textwidget
from pygame import rect, sprite, font, event
from pygame.locals import *
from menu import ButtonGroup

logger = logging.getLogger( __name__ )


class StaticTextWidget(widgets.SpriteTextWidget):
    def __init__( self, text, color, size ):
        widgets.SpriteTextWidget.__init__(self, text, color, size, 
                                          highlight_increase=0, 
                                          show_highlight_cursor=False)
    def __get_highlight(self):
        return False
    def __set_highlight(self,value):
        pass

    highlight = property(__get_highlight, __set_highlight)

class OptionsMenu( object ):
    def __init__( self, screenrect, color=(255,255,255) ):
        self.widgets = ButtonGroup()
        shortheight = int(screenrect.height//27)
        sz = shortheight*2
        left = int(screenrect.width//20)
        indent = int(screenrect.width//10)
        self._active = False
        
        optionslabel = StaticTextWidget('Options--', color, 3*shortheight)
        optionslabel.rect.topleft = (left, self.widgets.maxheight()+shortheight)
        self.widgets.add(optionslabel)
        
        startlabel = StaticTextWidget('Starting Level:  ', color, 2*shortheight)
        startlabel.rect.topleft = (left+indent, self.widgets.maxheight()+shortheight)
        self.start = widgets.SpinButton(size=int(1.5*shortheight))
        self.start.rect.bottomleft = (startlabel.rect.right, startlabel.rect.bottom)
        self.widgets.add( startlabel, self.start )
        
        pieceslabel = StaticTextWidget('Available Pieces-', color, 2*shortheight)
        pieceslabel.rect.topleft = (left, self.widgets.maxheight()+2*shortheight)
        self.widgets.add( pieceslabel )
        
        baselabel = StaticTextWidget('Base:  ', color, 2*shortheight)
        baselabel.rect.topleft = (left+indent, self.widgets.maxheight()+shortheight)
        self.base = widgets.RadioButton(sz, True)
        self.base.rect.bottomleft = (baselabel.rect.right, baselabel.rect.bottom)
        self.widgets.add( baselabel, self.base )
        
        extendedlabel = StaticTextWidget('Extended:  ', color, 2*shortheight)
        extendedlabel.rect.topleft = (left+indent, self.widgets.maxheight()+shortheight)
        self.extended = widgets.RadioButton(sz, False)
        self.extended.rect.bottomleft = (extendedlabel.rect.right, extendedlabel.rect.bottom)
        self.widgets.add( extendedlabel, self.extended )
        
        hardlabel = StaticTextWidget('Hard:  ', color, 2*shortheight)
        hardlabel.rect.topleft = (left+indent, self.widgets.maxheight()+shortheight)
        self.hard = widgets.RadioButton(sz, False)
        self.hard.rect.bottomleft = (hardlabel.rect.right, hardlabel.rect.bottom)
        self.widgets.add( hardlabel, self.hard )
        
        trolllabel = StaticTextWidget('Troll:  ', color, 2*shortheight)
        trolllabel.rect.topleft = (left+indent, self.widgets.maxheight()+shortheight)
        self.troll = widgets.RadioButton(sz, False)
        self.troll.rect.bottomleft = (trolllabel.rect.right, trolllabel.rect.bottom)
        self.widgets.add( trolllabel, self.troll )
        
        customlabel = StaticTextWidget('Custom:  ', color, 2*shortheight)
        customlabel.rect.topleft = (left+indent, self.widgets.maxheight()+shortheight)
        self.custom = widgets.RadioButton(sz, False)
        self.custom.rect.bottomleft = (customlabel.rect.right, customlabel.rect.bottom)
        self.widgets.add( customlabel, self.custom )
        
        self.back = widgets.SpriteTextWidget( "<- Back", color, 2*shortheight, highlight_increase=5)
        self.back.rect.bottomleft = (left, self.widgets.maxheight()+3*shortheight)
        self.widgets.add( self.back )
        
    def __nonzero__( self ):
        """
        Use this function to determine if the menu is currently running or not
        """
        return self._active
        
    def MenuActivate( self ):
        self._active = True
        
    def MenuDeactivate( self ):
        self._active = False
        
    def EventCatch( self, event ):
        if (event.type == ACTIVEEVENT):
            self.widgets.active(event)
        elif (event.type == MOUSEMOTION):
            self.widgets.highlight(event)
        elif (event.type == MOUSEBUTTONDOWN):
            self.widgets.mousedown(event)
        elif (event.type == MOUSEBUTTONUP):
            self.widgets.mouseup(event)
        elif (event.type == textwidget.TEXT_WIDGET_CLICK):
            logger.debug( "Widget was Clicked! %r" % event.text_widget)
        
    def draw( self, screen ):
        return self.widgets.draw( screen )
    
    def clear( self, screen, background ):
        return self.widgets.clear( screen, background )
        
    def update( self ):
        for each in self.widgets:
            each.update()
