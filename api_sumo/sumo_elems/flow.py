#!/usr/bin/env python
"""

"""

from elem import Elem

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class Flow(Elem):
    def __init__(self,_id,\
                begin,\
                end,\
                vehsPerHour=None,\
                period=None,\
                probability=None,\
                number=None,\
                tpe=None,\
                route=None,\
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
                arrivalPosLat=None,\
                fromJunction=None,\
                toJunction=None):
        if vehsPerHour==None and period==None and\
            probability==None and number==None:
                raise ValueError('vehsPerHour,period,probability or number must be defined')
        # Set the basic attributes of a flow
        attr= dict()
        attr['begin']=begin
        attr['end']=end
        attr['vehsPerHour']=vehsPerHour
        attr['period']=period
        attr['probability']=probability
        attr['number']=number
        attr['type']=tpe
        attr['route']=route
        attr['color']=color
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
        attr['fromJunction']=fromJunction
        attr['toJunction']=toJunction
        super(Flow,self).__init__('flow',_id,attr)