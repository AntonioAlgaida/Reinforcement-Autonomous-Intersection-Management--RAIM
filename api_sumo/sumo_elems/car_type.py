#!/usr/bin/env python
"""

"""

from elem import Elem

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class CarType(Elem):
    def __init__(self,_id,\
                    accel=None,\
                    decel=None,\
                    sigma=None,\
                    tau=None,\
                    length=None,\
                    minGap=None,\
                    maxSpeed=None,\
                    speedFactor=None,\
                    speedDev=None,\
                    color=None,\
                    vClass=None,\
                    emissionClass=None,\
                    guiShape=None,\
                    width=None,\
                    imgFile=None,\
                    impatience=None,\
                    laneChangeModel=None,\
                    carFollowModel=None,\
                    personCapacity=None,\
                    containerCapacity=None,\
                    boardingDuration=None,\
                    loadingDuration=None,\
                    latAlignment=None,\
                    minGapLat=None,\
                    maxSpeedLat=None,\
                    probability=None):
        # Set the basic attributes of a car type
        attr= dict()
        attr['accel']=accel
        attr['decel']=decel
        attr['sigma']=sigma
        attr['tau']=tau
        attr['length']=length
        attr['minGap']=minGap
        attr['maxSpeed']=maxSpeed
        attr['speedFactor']=speedFactor
        attr['speedDev']=speedDev
        attr['color']=color
        attr['vClass']=vClass
        attr['emissionClass']=emissionClass
        attr['guiShape']=guiShape
        attr['width']=width
        attr['imgFile']=imgFile
        attr['impatience']=impatience
        attr['laneChangeModel']=laneChangeModel
        attr['carFollowModel']=carFollowModel
        attr['personCapacity']=personCapacity
        attr['containerCapacity']=containerCapacity
        attr['boardingDuration']=boardingDuration
        attr['loadingDuration']=loadingDuration
        attr['latAlignment']=latAlignment
        attr['minGapLat']=minGapLat
        attr['maxSpeedLat']=maxSpeedLat
        attr['probability']=probability
        super(CarType,self).__init__('vType',_id,attr)