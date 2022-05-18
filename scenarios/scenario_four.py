#!/usr/bin/env python
"""

"""

from scenario import AsymmetricVariableFlowsManhattan

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ScenarioFour(AsymmetricVariableFlowsManhattan):
    def __init__(self,sg_mh,lowDens=250.0,medDens=500.0,highDens=775.0,duration=1800):
        super(ScenarioFour,self).__init__(sg_mh,2,\
            duration*0,duration*1,lowDens,duration*0,duration*1,lowDens,
            duration*1,duration*2,medDens,duration*1,duration*2,medDens,
            duration*2,duration*3,highDens,duration*2,duration*3,highDens,
            duration*3,duration*4,highDens,duration*3,duration*4,highDens,
            duration*4,duration*5,highDens,duration*4,duration*5,highDens,
            duration*5,duration*6,highDens,duration*5,duration*6,highDens,
            duration*6,duration*7,medDens,duration*6,duration*7,medDens,
            duration*7,duration*8,lowDens,duration*7,duration*8,lowDens,
            duration*8,duration*9,lowDens,duration*8,duration*9,lowDens,
            duration*9,duration*10,medDens,duration*9,duration*10,lowDens,
            duration*10,duration*11,medDens,duration*10,duration*11,lowDens,
            duration*11,duration*12,medDens,duration*11,duration*12,lowDens,
            duration*12,duration*13,highDens,duration*12,duration*13,lowDens,
            duration*13,duration*14,highDens,duration*13,duration*14,medDens,
            duration*14,duration*15,highDens,duration*14,duration*15,highDens,
            duration*15,duration*16,highDens,duration*15,duration*16,highDens,
            duration*16,duration*17,medDens,duration*16,duration*17,highDens,
            duration*17,duration*18,lowDens,duration*17,duration*18,highDens,
            duration*18,duration*19,lowDens,duration*18,duration*19,medDens,
            duration*19,duration*20,lowDens,duration*19,duration*20,lowDens,
            duration*20,duration*21,highDens,duration*20,duration*21,lowDens,
            duration*21,duration*22,lowDens,duration*21,duration*22,highDens,
            duration*22,duration*23,highDens,duration*22,duration*23,lowDens,
            duration*23,duration*24,lowDens,duration*23,duration*24,highDens,
            duration*24,duration*25,highDens,duration*24,duration*25,lowDens,
            duration*25,duration*26,lowDens,duration*25,duration*26,highDens,
            duration*26,duration*27,highDens,duration*26,duration*27,highDens,
            duration*27,duration*28,highDens,duration*27,duration*28,highDens,
            duration*28,duration*29,highDens,duration*28,duration*29,highDens,
            duration*29,duration*30,highDens,duration*29,duration*30,highDens,
            duration*30,duration*31,lowDens,duration*30,duration*31,lowDens,
            duration*31,duration*32,lowDens,duration*31,duration*32,lowDens,
            duration*32,duration*33,lowDens,duration*32,duration*33,lowDens,
            duration*33,duration*34,lowDens,duration*33,duration*34,lowDens,
            duration*34,duration*35,highDens,duration*34,duration*35,highDens,
            duration*35,duration*36,lowDens,duration*35,duration*36,lowDens,
            duration*36,duration*37,highDens,duration*36,duration*37,highDens,
            duration*37,duration*38,lowDens,duration*37,duration*38,lowDens,
            duration*38,duration*39,highDens,duration*38,duration*39,highDens,
            duration*39,duration*40,lowDens,duration*39,duration*40,lowDens,
            duration*40,duration*41,highDens,duration*40,duration*41,highDens,
            duration*41,duration*42,lowDens,duration*41,duration*42,lowDens)