#!/usr/bin/python

import logging
import textwidget
from pygame import rect, sprite, font, Surface, gfxdraw
from pygame.locals import SRCALPHA, BLEND_RGBA_SUB

logger=logging.getLogger(__name__)


class SpriteTextWidget( textwidget.TextWidget, sprite.Sprite ):
    def __init__(self, text="", colour=(0,0,0), size=32
                , highlight_increase = 20, font_filename=None
                , show_highlight_cursor = True):
        sprite.Sprite.__init__(self)
        textwidget.TextWidget.__init__(self, text, colour, size,
                                       highlight_increase, font_filename, 
                                       show_highlight_cursor)


class RadioButton( sprite.DirtySprite ):
    def __init__(self, size=20, state=False):
        sprite.DirtySprite.__init__(self)
        self.image = Surface( (size,size), SRCALPHA )
        self.rect = self.image.get_rect()
        self.checkpat = [(0.0,  0.6), (0.15, 0.55), (0.25, 0.75), (0.5, 0.4), 
                         (0.95, 0.05), (0.95, 0.10), (0.6, 0.5), (0.25, 0.95)]
        self._empty = Surface( (size,size), SRCALPHA )
        self._truesurf = Surface( (size,size), SRCALPHA )
        self._state_ = state
        self._gen_patterns()
        
    @property
    def state(self):
        """I'm the 'state' property."""
        return self._state_

    @state.setter
    def state(self, value):
        try:
            self._state_ = bool(value)
        except:
            self._state_ = False

    def _gen_patterns(self):
        tw = -int(0.2*self.rect.width)
        th = -int(0.2*self.rect.height)
        target = self.rect.inflate( tw, th )
        gfxdraw.filled_trigon(self._empty, 0,0, self.rect.width,0, 0,self.rect.height, (90,90,90) )
        gfxdraw.filled_trigon(self._empty, self.rect.width,0, 0,self.rect.height, self.rect.width, self.rect.height, (180,180,180) )
        self._empty.fill((255,255,255), rect=target)
        
        pat = self.checkpat[:]
        for point in pat:
            x,y = point
            x = int(self.rect.width*x)
            y = int(self.rect.height*y)
            pat[pat.index(point)] = (x,y)
        gfxdraw.filled_polygon(self._truesurf, pat, (0,182,12))
        
    def update(self):
        self.image.blit( self._empty, (0,0) )
        if self.state:
            self.image.blit( self._truesurf, (0,0) )
            
    def on_mouse_click( self, event ):
        self.on_mouse_button_up( event )
        
    def on_mouse_button_down( self, event ):
        pass
        
    def on_mouse_button_up( self, event ):
        if self.rect.collidepoint(event.pos):
            if self.state:
                self.state = False
            else:
                self.state = True
                
                
class SpinButton( sprite.DirtySprite ):
    def __init__(self, mmax=100, mmin=1, step=1, default=1, size=20):
        sprite.DirtySprite.__init__(self)
        
        self._minval_ = 0
        self._maxval_ = 0
        self._value_  = 0
        
        self.maxval = mmax
        self.minval = mmin
        self.value  = default
        self.step = step  #FIXME: step needs error-checking
        
        # check for font module
        if not font.get_init():
            font.init()
            
        self._font = font.SysFont('sans', size)
        w1, h1 = self._font.size(str(self.maxval)+'+')
        w2, h2 = self._font.size(str(self.minval)+'-')
        wmax = max(int(1.1*w1),int(1.1*w2))
        hmax = max(int(1.1*h1),int(1.1*h2))
        
        self._border = int((wmax*0.08 + hmax*0.08)/2.0)
        navwid = max(self._font.size('+')[0],self._font.size('-')[0])
        navheight = int(hmax//2)
        
        self.image = Surface( (wmax,hmax), SRCALPHA ).convert()
        self.rect = self.image.get_rect()
        self._empty = Surface( (wmax,hmax), SRCALPHA ).convert()
        self._full = Surface( (wmax,hmax), SRCALPHA ).convert()
        
        self._uprect = rect.Rect( self.rect.width - navwid, 0, navwid, navheight )
        self._downrect = rect.Rect( self.rect.width - navwid, navheight, navwid, navheight )
        
        self._make_bg()
        self._make_nav()
        
    @property
    def minval(self):
        return self._minval_
        
    @minval.setter
    def minval(self, value):
        if value > self._maxval_:
            logger.warning('minval cannot exceed maxval!')
            self._minval_ = self._maxval_
        else:
            self._minval_ = value
                    
    @property
    def maxval(self):
        return self._maxval_

    @maxval.setter
    def maxval(self, value):
        if value < self._minval_:
            logger.warning('maxval cannot be lower than minval!')
            self._maxval_ = self._minval_
        else:
            self._maxval_ = value
            
    @property
    def value(self):
        return self._value_

    @value.setter
    def value(self, value):
        if value < self._minval_:
            logger.warning('cannot set current value lower than minval!')
            self._value_ = self._minval_
        elif value > self._maxval_:
            logger.warning('cannot set current value higher than maxval!')
            self._value_ = self._maxval_
        else:
            self._value_ = value
        
    def _make_bg( self ):
        light = (180,180,180)
        shade = (90,90,90)
        top = (255,255,255)
        target = self.rect.inflate( -self._border, -self._border )
        gfxdraw.filled_trigon(self._empty, 0,0, self.rect.width,0, 0,self.rect.height, light )
        gfxdraw.filled_trigon(self._empty, self.rect.width,0, 0,self.rect.height, self.rect.width, self.rect.height, shade )
        self._empty.fill(top, rect=target)
        
        gfxdraw.vline(self._empty, self._uprect.left,   self._uprect.top, self._downrect.bottom, shade )
        gfxdraw.vline(self._empty, self._uprect.left+1, self._uprect.top, self._downrect.bottom, light )

        gfxdraw.hline(self._empty, self._uprect.left,   self._uprect.right, self._uprect.bottom, shade )
        gfxdraw.hline(self._empty, self._downrect.left, self._downrect.right, self._downrect.top, light )
        
        
    def _make_nav( self ):
        arrow = [(0.15, 0.5), (0.45, 0.2), (0.5,  0.2), (0.8,  0.5), 
                 (0.75, 0.55), (0.5,  0.35), (0.45, 0.35), (0.2, 0.55)]
        up=[]
        down=[]
        for x,y in arrow:
            ux = int(self._uprect.width*x)
            uy = int(self._uprect.height*y)
            dx = int(self._downrect.width*(1-x))
            dy = int(self._downrect.height*(1-y))
            up.append( (ux,uy) )
            down.append( (dx,dy) )
            
        gfxdraw.filled_polygon(self._empty.subsurface(self._uprect), up, (90,90,90))
        gfxdraw.filled_polygon(self._empty.subsurface(self._downrect), down, (90,90,90))
        
    def update(self):
        self.image.blit( self._empty, (0,0) )
        valsurf = self._font.render(str(self.value), True, (0,0,0))
        mid=int((self.rect.width - self._uprect.width)/2.0)
        valrect = valsurf.get_rect()
        valrect.centerx=mid
        self.image.blit( valsurf, valrect )
            
    def on_mouse_click( self, event ):
        self.on_mouse_button_up( event )
        
    def on_mouse_button_down( self, event ):
        pass
        
    def on_mouse_button_up( self, event ):
        xpos,ypos=event.pos
        selfx,selfy=self.rect.topleft
        tx,ty = xpos-selfx, ypos-selfy
        if self.rect.collidepoint(event.pos):
            if event.button == 4: # mosuewheel up
                self.value += self.step
            elif event.button == 5: # mousewheel down
                self.value -= self.step
            elif self._uprect.collidepoint((tx,ty)):
                self.value += self.step
            elif self._downrect.collidepoint((tx,ty)):
                self.value -= self.step
