#!/usr/bin/env python
"""

"""

from scenario import AsymmetricVariableFlowsManhattan

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ScenarioThree(AsymmetricVariableFlowsManhattan):
    def __init__(self,sg_mh,lowDens=100.0,medDens=500.0,highDens=1000.0,duration=3600):
        super(ScenarioThree,self).__init__(sg_mh,2,\
            duration*0,duration*1,lowDens,duration*0,duration*1,lowDens,
            duration*1,duration*2,medDens,duration*1,duration*2,medDens,
            duration*2,duration*3,highDens,duration*2,duration*3,highDens,
            duration*3,duration*4,medDens,duration*3,duration*4,highDens,
            duration*4,duration*5,lowDens,duration*4,duration*5,highDens,
            duration*5,duration*6,lowDens,duration*5,duration*6,medDens,
            duration*6,duration*7,lowDens,duration*6,duration*7,lowDens)