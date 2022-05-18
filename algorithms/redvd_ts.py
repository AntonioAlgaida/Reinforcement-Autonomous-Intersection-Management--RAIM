#!/usr/bin/env python
"""

"""

from random import uniform

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class REDVDAlgorithm2(ManhattanAlgorithm):
    def __init__(self,minth,maxth,delta,min_green_time,min_red_time,maxp,avgmode,\
                 mincycle,maxcycle,deltacycle,liminc,limdec,wq=0.5,lanes=1):
        super(REDVDAlgorithm2,self).__init__(wq,lanes)
        self.min_green_time = min_green_time
        self.min_red_time = min_red_time
        self.minth = minth
        self.maxth = maxth
        self.mincycle = mincycle
        self.maxcycle = maxcycle
        self.delta = delta
        self.deltacycle = deltacycle
        self.maxp = maxp
        self.liminc = liminc
        self.limdec = limdec
        self.avgmode = avgmode

#    def setFile(self,file):
#        self.file = file

    def reset_algorithm(self,sm):
        super(REDVDAlgorithm2,self).reset_algorithm(sm)
        for i in range(len(self.ids)):
            self.cycles[i] = self.mincycle
            self.ocurs[i] = 0
            for j in range(2):
                self.count[i][j] = 0
                self.lastgreentime[i][j] = (self.mincycle-10)//2

    def prepare_algorithm(self,sm):
        super(REDVDAlgorithm2,self).prepare_algorithm(sm)
        self.count = [[-1]*2 for _ in range(len(self.ids))]
        self.cycles = [self.mincycle for _ in range(len(self.ids))]
        self.lastgreentime = [[(self.mincycle-10)//2]*2 for _ in range(len(self.ids))]
        self.ocurs = [0 for _ in range(len(self.ids))]
        for i in range(len(self.ids)):
            self.changestate[i] = i*14

    def _when_green(self,index,num):
        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
                            self.queues[index][1 if num == 0 else 3]))
        if avg < self.minth:
            self.count[index][num] = -1
            self.ocurs[index] = -1 if self.ocurs[index] > 0 else self.ocurs[index]-1
            pa = 0
        elif avg > self.maxth:
            self.count[index][num] = 0
            self.ocurs[index] = 1 if self.ocurs[index] < 0 else self.ocurs[index]+1
            pa = 1
        else:
            self.count[index][num] += 1
            pb = self.maxp*(avg-self.minth)/(self.maxth-self.minth) + 1e-12
            pa = pb / (1-self.count[index][num]*pb)
            pa = 1 if pa > 1 else pa
            self.ocurs[index] = 0

        if self.ocurs[index] == self.liminc:
            self.cycles[index] += self.deltacycle
        elif self.ocurs[index] == -self.limdec:
            self.cycles[index] -= self.deltacycle

        gt = self.lastgreentime[index][num]
        if uniform(0,1) < pa:
            gt += self.delta

        if gt > self.cycles[index] - self.min_red_time - 10:
            gt = self.cycles[index] - self.min_red_time - 10
        elif gt < self.min_green_time:
            gt = self.min_green_time

        if self.cycles[index] > self.maxcycle:
            self.cycles[index] = self.maxcycle
        elif self.cycles[index] < self.mincycle:
            self.cycles[index] = self.mincycle

        #self.lastgreentime[index][num] = gt
        self.lastgreentime[index][1-num] = self.cycles[index] - 10 - gt
        self.changestate[index]   = self.sm.time + gt

#        self.file.write(('{}'+',{}'*4+'\n').format(self.sm.time,self.ids[index],self.cycles[index],self.changestate[index],num))

    def _when_NS(self,index):
        self._when_green(index,0)

    def _when_WE(self,index):
        self._when_green(index,1)