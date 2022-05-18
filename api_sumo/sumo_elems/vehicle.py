#!/usr/bin/env python
"""

"""

from elem import Elem

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class Vehicle(Elem):
    def __init__(self,_id,\
                depart,\
                tpe,\
                route,\
                color=None,\
                departLane=None,\
                departPos=None,\
                departSpeed=None,\
                arrivalLane=None,\
                arrivalPos=None,\
                arrivalSpeed=None,\
                line=None,\
                personNumber=None,\
                containerNumber=None,\
                reroute=None,\
                departPosLat=None,\
                arrivalPosLat=None):
        # Set the basic attributes of a vehicle
        attr= dict()
        attr['type']=tpe
        attr['route']=route
        attr['color']=color
        attr['depart']=depart
        attr['departLane']=departLane
        attr['departPos']=departPos
        attr['departSpeed']=departSpeed
        attr['arrivalLane']=arrivalLane
        attr['arrivalPos']=arrivalPos
        attr['arrivalSpeed']=arrivalSpeed
        attr['line']=line
        attr['personNumber']=personNumber
        attr['containerNumber']=containerNumber
        attr['reroute']=reroute
        attr['departPosLat']=departPosLat
        attr['arrivalPosLat']=arrivalPosLat        
        super(Vehicle,self).__init__('vehicle',_id,attr)