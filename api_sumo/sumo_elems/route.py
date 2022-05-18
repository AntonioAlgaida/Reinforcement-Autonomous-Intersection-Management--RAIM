#!/usr/bin/env python
"""

"""

from elem import Elem

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class Route(Elem):
    def __init__(self,_id,edges,color=None):
        # Set the basic attributes of a route
        attr         = dict()
        attr['edges'] = edges
        attr['color']   = color
        super(Route,self).__init__('route',_id,attr)