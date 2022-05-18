#!/usr/bin/env python
"""

"""

from elem import Elem

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class Edge(Elem):
    def __init__(self,_id,frm,to):
        # Set the basic attributes of an edge
        attr         = dict()
        attr['from'] = frm.id
        attr['to']   = to.id
#        attr['sidewalkWidth'] = 6
        super(Edge,self).__init__('edge',_id,attr)
        # Adds 'to' as neighbor from 'frm'
        frm.connections[to.id] = frm.get_weight(to)