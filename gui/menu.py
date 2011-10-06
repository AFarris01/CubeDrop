#!/usr/bin/python


import logging
import textwidget
from pygame import rect, sprite, font, event
from pygame.locals import *
import widgets


logger = logging.getLogger( __name__ )


class ButtonGroup( sprite.RenderUpdates ):
    def highlight( self, event ):
        for each in self:
            each.highlight = each.rect.collidepoint(event.pos)
            
    def mousedown( self, event ):
        for each in self:
            each.on_mouse_button_down(event)
            
    def mouseup( self, event ):
        for each in self:
            each.on_mouse_button_up(event)
            
    def active( self, event ):
        for each in self:
            each.dirty = True
            
    def setfont( self, fontobj ):
        for each in self:
            each.__m_font = fontobj
            
    def center( self, screct ):
        for each in self:
            each.rect.centerx = screct.centerx
            
    def maxheight( self ):
        try:
            return max([x.rect.bottom for x in self])
        except ValueError:
            return 0
            
    def update( self ):
        for each in self:
            each.update_surface()


class Menu( object ):
    def __init__(self, screenrect, buttons=('Name',(0,0,0),None), fontobj=None):
        self.widgets = ButtonGroup()
        self.buttons = buttons
        self._active = True
        
        if fontobj != None:
            self.font = fontobj
        else:
            self.font = pygame.font.match_font("sans", False, True)

        self.rebuild_menus( screenrect )
        
    def rebuild_menus( self, screenrect ):
        self.widgets.empty()
        shortheight = int(screenrect.height//13)

        for name, color, callback in self.buttons:
            wid = widgets.SpriteTextWidget( name, color )
            wid.size = 2*shortheight
            wid.rect.top = shortheight + self.widgets.maxheight()
            if callback == None:
                wid.on_mouse_click = self.null
            else:
                wid.on_mouse_click = callback
            self.widgets.add( wid )
            
        self.widgets.setfont( self.font )
        self.widgets.center(screenrect)
        self.widgets.update()
        
    def __nonzero__( self ):
        """
        Use this function to determine if the menu is currently running or not
        """
        return self._active
        
    def fetchwidget(self,label):
        mans = self.widgets.sprites()
        for each in mans:
            if each.text == label:
                return each
        
    def draw( self, screen ):
        return self.widgets.draw( screen )
    
    def clear( self, screen, background ):
        return self.widgets.clear( screen, background )
    
    def update( self ):
        pass
        
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
    
    def null( self, event ):
        """Empty button callback"""
        logger.debug('Null event caught! %r' % event)
        
    def MenuActivate( self ):
        self._active = True
        
    def MenuDeactivate( self ):
        self._active = False
