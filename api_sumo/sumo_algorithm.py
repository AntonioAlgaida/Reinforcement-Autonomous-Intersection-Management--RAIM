#!/usr/bin/env python
"""

"""
import numpy as np
__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class SumoAlgorithm(object):
    def __init__(self,program,keypoints):
        self.pgm = program
        self.kps = keypoints

    def get_statistics(self):
        raise NotImplementedError('get_statistics is not implemented')

    def prepare_algorithm(self,sm):
        self.sm = sm
        self.traci = sm.traci
        self.ids = self.traci.trafficlights.getIDList()
        self.pointers = [0 for i in range(len(self.ids))]
        self.changestate = [0 for i in range(len(self.ids))]

    def reset_algorithm(self,sm):
        self.sm = sm
        self.traci = sm.traci
        self.ids = self.traci.trafficlights.getIDList()
        for index in range(len(self.ids)):
            self.pointers[index] = 0
            self.changestate[index] = 0

    def step(self):
        for index,id in enumerate(self.ids):
            if self.sm.time == self.changestate[index]:
                self.pointers[index] += 1
                self.pointers[index] %= len(self.pgm)
                self.traci.trafficlights.setRedYellowGreenState(id,\
                    self.pgm[self.pointers[index]])
                if self.pointers[index] in self.kps:
                    self._when(self.pointers[index],index)
                else:
                    self.changestate[index] += 1
    def _when(self,pointer,index):
        raise NotImplementedError('_when is not implemented')