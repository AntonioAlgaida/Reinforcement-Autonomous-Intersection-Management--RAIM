#!/usr/bin/env python
"""

"""

from elem import Elem

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class VehDist(Elem):
    def __init__(self,_id,\
                    vTypes=None):
        # Set the basic attributes of a car type
        attr= dict()
        attr['vTypes']=vTypes
        super(VehDist,self).__init__('vTypeDistribution',_id,attr)