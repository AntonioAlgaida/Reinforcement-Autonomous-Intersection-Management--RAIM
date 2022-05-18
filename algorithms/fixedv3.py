#!/usr/bin/env python
"""

"""

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class FixedAlgorithmv3(ManhattanAlgorithm):
    def __init__(self,greentime=1,greentime_ped=20,wq=0.5,lanes=1):
        super(FixedAlgorithmv3,self).__init__(wq,lanes)
        self.greentime = greentime
        self.greentime_ped = greentime_ped
    def _when_NS_pre(self,index):
        self.changestate[index] += self.greentime

    def _when_NS(self,index):
        self.changestate[index] += self.greentime_ped

    def _when_WE_pre(self,index):
        self.changestate[index] += self.greentime

    def _when_WE(self,index):
        self.changestate[index] += self.greentime_ped