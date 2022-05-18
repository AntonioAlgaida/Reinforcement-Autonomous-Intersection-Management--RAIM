#!/usr/bin/env python
"""

"""

from random import uniform

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class GreenWaveAlgorithm(ManhattanAlgorithm):
    def __init__(self,greentime,deltatime,nogreenstages=10,wq=0.5,lanes=1):
        super(GreenWaveAlgorithm,self).__init__(wq,lanes)
        self.gt = greentime
        self.dt = deltatime
        self.ul = nogreenstages
    
    def reset_algorithm(self,sm):
        super(GreenWaveAlgorithm,self).reset_algorithm(sm)
        for index in range(len(self.ids)):
            self.changestate[index] = -1
            self.pointers[index] = 6
            i,j = list(map(int,self.ids[index].split('.')))
            if j == 1:
                self.changestate[index]=0
                self.pointers[index]=11
    
    def prepare_algorithm(self,sm):
        super(GreenWaveAlgorithm,self).prepare_algorithm(sm)
        for i in range(len(self.ids)):
            self.changestate[i] = -1
            self.pointers[i] = 6
        self.nexttl = [-1 for i in range(len(self.ids))]
        fn = '{}.{}'.format
        for index in range(len(self.ids)):
            i,j = list(map(int,self.ids[index].split('.')))
            e = fn(i,j+1)
            if e in self.ids:
                self.nexttl[index] = self.ids.index(e)
            if j == 1:
                self.changestate[index] = 0
                self.pointers[index] = 11

    def _when_NS(self,index):
        self.changestate[index] += self.gt
                
    def _when_WE(self,index):
        self.changestate[index] += self.gt
        if self.nexttl[index] > -1:
            self.changestate[self.nexttl[index]] = self.sm.time + self.dt - (self.ul/2)
            