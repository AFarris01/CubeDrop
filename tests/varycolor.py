import math
from pygame import Color

def varycolor(NumberOfColors):
    # VARYCOLOR Produces colors with maximum variation 
    # Created for MatLab by Daniel Helmick 8/12/2008
    # converted for use with python/pygame by Andrew Farris 7/18/2011
    
    ColorSet=[]

    #Take care of the anomolies (Remember: [R, G, B])
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
        EachSec = math.floor(NumberOfColors/6)
        print "EachSec: ", EachSec
        
        #how many extra colors are there? 
        ExtraPlots = (NumberOfColors % 6)
        print "ExtraPlots: ", ExtraPlots
        
        #initialize our vector
        ColorSet=[0 for c in range(NumberOfColors)]
        
        #This is to deal with the extra colors that don't fit nicely into the
        #segments
        Adjust=[0 for c in range(6)]
        for m in range(ExtraPlots):
            Adjust[m]=1
        print "Adjust: ", Adjust
        
        SecOne   = EachSec+Adjust[0]
        SecTwo   = EachSec+Adjust[1]
        SecThree = EachSec+Adjust[2]
        SecFour  = EachSec+Adjust[3]
        SecFive  = EachSec+Adjust[4]
        SecSix   = EachSec+Adjust[5]
        
        print "Secs-- 1:%i, 2:%i, 3:%i, 4:%i, 5:%i, 6:%i" % (SecOne, SecTwo, SecThree, SecFour, SecFive, SecSix)
        
        for m in range(1,int(SecOne)+1):
            print "SecOne Colors: ", 255.0*((m-1.0)/(SecOne-1.0))
            ColorSet[int(m)-1]=Color( 0, 255, int(round(255.0*((m-1)/(SecOne-1)))) )

        for m in range(1,int(SecTwo)+1):
            print "SecTwo Colors: ", 255.0*((SecTwo-m)/(SecTwo))
            ColorSet[int(m+SecOne)-1]=Color( 0, int(round(255.0*((SecTwo-m)/(SecTwo)))), 255 )
        
        for m in range(1,int(SecThree)+1):
            print "SecThree Colors: ", 255.0*((m)/(SecThree))
            ColorSet[int(m+SecOne+SecTwo)-1]=Color( int(round(255.0*((m)/(SecThree)))), 0, 255 )
        
        for m in range(1,int(SecFour)+1):
            print "SecFour Colors: ", 255.0*((SecFour-m)/(SecFour))
            ColorSet[int(m+SecOne+SecTwo+SecThree)-1]=Color( 255, 0, int(round(255.0*((SecFour-m)/(SecFour)))) )

        for m in range(1,int(SecFive)+1):
            print "SecFive Colors: ", 255.0*((m)/(SecFive))
            ColorSet[int(m+SecOne+SecTwo+SecThree+SecFour)-1]=Color( 255, int(round(255.0*((m)/(SecFive)))), 0 )
            
        for m in range(1,int(SecSix)+1):
            print "SecSix Colors: ", 255.0*((SecSix-m)/(SecSix))
            ColorSet[int(m+SecOne+SecTwo+SecThree+SecFour+SecFive)-1]=Color( int(round(255.0*((SecSix-m)/(SecSix)))), 255, 0 )
        
    return ColorSet
