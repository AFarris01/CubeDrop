#!/usr/bin/python


from math import ceil
from pygame import Surface
from pygame.locals import SRCALPHA


class Border( object ):
    def __init__( self, borderobj ):
        bimg, brect = borderobj
        if brect.width != brect.height != 15:
            raise ValueError, "Border Object Dimensions are Incorrect! Need Aspect 1:1, and w=15. Provided: %r" % brect
        self.topleft      = bimg.subsurface(0,0,5,5)
        self.topborder    = bimg.subsurface(5,0,5,5)
        self.topright     = bimg.subsurface(10,0,5,5)
        self.leftborder   = bimg.subsurface(0,5,5,5)
        self.rightborder  = bimg.subsurface(10,5,5,5)
        self.bottomleft   = bimg.subsurface(0,10,5,5)
        self.bottomborder = bimg.subsurface(5,10,5,5)
        self.bottomright  = bimg.subsurface(10,10,5,5)
        
    def makeborder( self, recttoborder, background ):
        bordrect = recttoborder.copy()
        bordrect.inflate_ip( 10,10 )
        retsurf = Surface( (bordrect.width, bordrect.height), SRCALPHA ).convert()
        retsurf.blit( background, (0,0), area=bordrect )
        cwidth, cheight = 0,0

        #Make Top & Bottom Border
        while cwidth < recttoborder.width:
            retsurf.blit( self.topborder, (cwidth+5,0) )
            retsurf.blit( self.bottomborder, (cwidth+5,bordrect.height-5) )
            cwidth += 5
            
        #Make Left & Right Border
        while cheight < recttoborder.height:
            retsurf.blit( self.leftborder, (0,cheight+5) )
            retsurf.blit( self.rightborder, (bordrect.width-5,cheight+5) )
            cheight += 5
        
        #Install Corners
        retsurf.blit( self.topleft, (0,0) )
        retsurf.blit( self.topright, (bordrect.width-5,0) )
        retsurf.blit( self.bottomleft, (0,bordrect.height-5) )
        retsurf.blit( self.bottomright, (bordrect.width-5,bordrect.height-5) )
        
        #Return surface, [rect]
        return retsurf, bordrect
