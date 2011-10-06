#!/usr/bin/python

import logging

class Manager( object ):
    def __init__( self, *args ):
        self.members = []
        self.add(*args)
        self._prevstate = self._get_state()
            
    def add(self, *args):
        for each in args:
            self.members.append(each)
            
    def _get_state( self ):
        conds=[]
        for each in self.members:
            conds.append( bool(each) )
        return conds
        
    def statechanged( self ):
        currstate = self._get_state()
        if currstate == self._prevstate:
            return False
        else:
            self._prevstate = currstate
            return True
            
    def __nonzero__( self ):
        return statechanged()
            
