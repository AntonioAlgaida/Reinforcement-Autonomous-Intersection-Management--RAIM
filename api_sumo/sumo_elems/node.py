#!/usr/bin/env python
"""

"""
from math import sqrt
from elem import Elem

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class Node(Elem):
    def __init__(self,_id,x,y,typ=0):
        # Set the basic attributes of a node
        attr         = dict()
        attr['x']    = x
        attr['y']    = y
        attr['type'] = 'traffic_light' if typ else None
        super(Node,self).__init__('node',_id,attr)
        # Set an extra attribute for graphs algorithms
        super(Node,self).__set_attr__('connections',dict())
    
    def get_connections(self):
        '''Returns ids of all neighbors of this node'''
        return self.connections.keys()
        
    def get_weight(self,nbr):
        '''Return the distance between this node and other'''
        if nbr.id not in self.connections:
            return sqrt((self.x-nbr.x)**2 + (self.y-nbr.y)**2)
        return self.connections[nbr.id]