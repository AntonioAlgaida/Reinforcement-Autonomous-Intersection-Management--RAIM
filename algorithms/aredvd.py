#!/usr/bin/env python
"""

"""
import pandas as pd
import numpy as np
from random import uniform

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class AREDVDAlgorithm(ManhattanAlgorithm):
    def __init__(self,minth,maxth,delta1,delta2,min_green_time,min_red_time,maxp,avgmode,\
                 mincycle,maxcycle,deltacycle,liminc,limdec,greentime_pre=15,
                 wq=0.5, lanes=1, alpha=0.1, beta=0.9,target_min=0.4,target_max=0.6):
        super(AREDVDAlgorithm,self).__init__(wq,lanes)
        self.greentime_pre = greentime_pre
        self.min_green_time = min_green_time
        self.min_red_time = min_red_time
        self.minth = minth
        self.maxth = maxth
        self.mincycle = mincycle
        self.maxcycle = maxcycle
        self.delta1 = delta1
        self.delta2 = delta2
        self.deltacycle = deltacycle
        self.maxp = maxp
        self.maxp_ns = maxp
        self.maxp_we = maxp
        self.maxp_pre_ns = maxp
        self.maxp_pre_we = maxp
        self.liminc = liminc
        self.limdec = limdec
        self.avgmode = avgmode
        self.alpha = alpha
        self.beta = beta
        self.target_min = minth+target_min*(maxth-minth)
        self.target_max = minth+target_max*(maxth-minth)
        columns = ['greentime_pre','min_green_time','min_red_time','minth','maxth',
       'mincycle','maxcycle','delta1','delta2','deltacycle','index','num',
       'maxp','maxp_ns','maxp_we','liminc','time',
       'limdec','alpha','beta','target_min','target_max','count','ocurs','cycles',
       'avg', 'pa','pb','greentime']
#        self.history = pd.DataFrame(columns=columns)
        self.history = np.matrix(columns)
    def reset_algorithm(self,sm):
        super(AREDVDAlgorithm,self).reset_algorithm(sm)
        for i in range(len(self.ids)):
            self.cycles[i] = self.mincycle
            self.ocurs[i] = 0
            for j in range(2):
                self.count[i][j] = 0
                self.lastgreentime[i][j] = (self.mincycle-10)//2

    def prepare_algorithm(self,sm):
        super(AREDVDAlgorithm,self).prepare_algorithm(sm)
        self.count = [[-1]*2 for _ in range(len(self.ids))]
        self.cycles = [self.mincycle for _ in range(len(self.ids))]
        self.lastgreentime = [[(self.mincycle-10)//2]*2 for _ in range(len(self.ids))]
        self.ocurs = [0 for _ in range(len(self.ids))]


    def _when_green(self,index,num):
#        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
#                            self.queues[index][1 if num == 0 else 3]))

        index1 = 0 if num == 0 else 2
        index2 = 1 if num == 0 else 3
        avg = self.avgmode((
                (self.queues[index][index1] + 1.8*self.queues_ped[index][index1]),\
                (self.queues[index][index2] + 1.8*self.queues_ped[index][index2])))

        self.maxp = self.maxp_ns if num == 0 else self.maxp_we
        pb = 0
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
            pa = 0.99999 if pa >= 1 else pa
            self.ocurs[index] = 0

        if avg > self.target_max and self.maxp <=0.5:
            self.maxp = self.maxp+self.alpha
        elif avg < self.target_min and self.maxp >=0.01:
            self.maxp = self.maxp*self.beta

        gt = self.lastgreentime[index][num]
        if self.ocurs[index] == self.liminc:
            self.cycles[index] += self.deltacycle
#            gt += self.deltacycle

        elif self.ocurs[index] == -self.limdec:
            self.cycles[index] -= self.deltacycle
#            gt -= self.deltacycle

        if num == 0:
            self.maxp_ns = self.maxp
        else:
            self.maxp_we = self.maxp

        if pa == 0:
            gt -= self.delta1
        elif pa == 1:
            gt += self.delta1
        elif uniform(0,1) < pa:
            gt += self.delta2

#        # Si este tiempo en verde es mayor que el ciclo que tenemos
            # No lo entiendo
#        if gt > self.cycles[index] - self.min_red_time - 20:
#            gt = self.cycles[index] - self.min_red_time - 20

        if gt < self.min_green_time:
            gt = self.min_green_time

        if self.cycles[index] > self.maxcycle:
            self.cycles[index] = self.maxcycle
        elif self.cycles[index] < self.mincycle:
            self.cycles[index] = self.mincycle

        self.lastgreentime[index][num] = gt
        # Si el tiempo en verde para esta rama + la otra + los tiempos en rojo
        # es mayor que el tiempo máximo de ciclo actual, podemos, o aumentar el ciclo,
        # o en el caso de que si al aumentar se supere el maxcycle, se disminuye la rama contraria
#        if gt + self.lastgreentime[index][1-num] + 20 > self.maxcycle:
        if gt + self.lastgreentime[index][1-num] + 20 > self.cycles[index]:
#            self.cycles[index] += self.deltacycle
#            if self.cycles[index] > self.maxcycle:
#                self.cycles[index] = self.maxcycle
#                self.lastgreentime[index][1-num] = self.cycles[index] - 20 - gt
            self.lastgreentime[index][1-num] = self.cycles[index] - 20 - gt
            if self.lastgreentime[index][1-num] < self.min_green_time:
                self.lastgreentime[index][1-num] = self.min_green_time
                gt = self.cycles[index] - self.lastgreentime[index][1-num] - 20

        self.changestate[index] = self.sm.time + gt

        a = [self.greentime_pre,self.min_green_time,self.min_red_time,self.minth,self.maxth,
             self.mincycle,self.maxcycle,self.delta1,self.delta2,self.deltacycle,index,num,
             self.maxp,self.maxp_ns,self.maxp_we,self.liminc,self.sm.time,
             self.limdec,self.alpha,self.beta,self.target_min,self.target_max,
             self.count[index][num],self.ocurs[index],self.cycles[index],avg,
             pa,pb,gt]
        self.history = np.vstack((self.history,a))

    def _when_pre_green(self,index,num):
        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
                            self.queues[index][1 if num == 0 else 3]))
#        index1 = 0 if num == 0 else 2
#        index2 = 1 if num == 0 else 3
#        avg = self.avgmode((
#                (self.queues[index][index1] + 1.8*self.queues_ped[index][index1]),\
#                (self.queues[index][index2] + 1.8*self.queues_ped[index][index2])))
        self.maxp_pre = self.maxp_pre_ns if num == 0 else self.maxp_pre_we
        pb = 0
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
            pb = self.maxp_pre*(avg-self.minth)/(self.maxth-self.minth) + 1e-12
            pa = pb / (1-self.count[index][num]*pb)
            pa = 0.99999 if pa >= 1 else pa
            self.ocurs[index] = 0

        if avg > self.target_max and self.maxp_pre <=0.5:
            self.maxp_pre += self.alpha
        elif avg < self.target_min and self.maxp_pre >=0.01:
            self.maxp_pre *= self.beta

        gt = self.lastgreentime[index][num]
        if self.ocurs[index] == self.liminc:
            self.cycles[index] += self.deltacycle
#            gt += self.deltacycle

        elif self.ocurs[index] == -self.limdec:
            self.cycles[index] -= self.deltacycle
#            gt -= self.deltacycle

        if num == 0:
            self.maxp_pre_ns = self.maxp_pre
        else:
            self.maxp_pre_we = self.maxp_pre

        if pa == 0:
            gt -= self.delta1
        elif pa == 1:
            gt += self.delta1
        elif uniform(0,1) < pa:
            gt += self.delta2

#        # Si este tiempo en verde es mayor que el ciclo que tenemos
            # No lo entiendo
#        if gt > self.cycles[index] - self.min_red_time - 20:
#            gt = self.cycles[index] - self.min_red_time - 20

        if gt < self.min_green_time:
            gt = self.min_green_time

        if self.cycles[index] > self.maxcycle:
            self.cycles[index] = self.maxcycle
        elif self.cycles[index] < self.mincycle:
            self.cycles[index] = self.mincycle

        self.lastgreentime[index][num] = gt
        # Si el tiempo en verde para esta rama + la otra + los tiempos en rojo
        # es mayor que el tiempo máximo de ciclo actual, podemos, o aumentar el ciclo,
        # o en el caso de que si al aumentar se supere el maxcycle, se disminuye la rama contraria
#        if gt + self.lastgreentime[index][1-num] + 20 > self.maxcycle:
        if gt + self.lastgreentime[index][1-num] + 20 > self.cycles[index]:
#            self.cycles[index] += self.deltacycle
#            if self.cycles[index] > self.maxcycle:
#                self.cycles[index] = self.maxcycle
#                self.lastgreentime[index][1-num] = self.cycles[index] - 20 - gt
            self.lastgreentime[index][1-num] = self.cycles[index] - 20 - gt
            if self.lastgreentime[index][1-num] < self.min_green_time:
                self.lastgreentime[index][1-num] = self.min_green_time
                gt = self.cycles[index] - self.lastgreentime[index][1-num] - 20

        self.changestate[index] = self.sm.time + gt

#        a = [self.greentime_pre,self.min_green_time,self.min_red_time,self.minth,self.maxth,
#             self.mincycle,self.maxcycle,self.delta1,self.delta2,self.deltacycle,index,num,
#             self.maxp,self.maxp_ns,self.maxp_we,self.liminc,self.sm.time,
#             self.limdec,self.alpha,self.beta,self.target_min,self.target_max,
#             self.count[index][num],self.ocurs[index],self.cycles[index],avg,
#             pa,pb,gt]
#        self.history = np.vstack((self.history,a))

    def _when_NS_pre(self,index):
        self._when_pre_green(index,0)
#        self.changestate[index] += self.greentime_pre

    def _when_NS(self,index):
        self._when_green(index,0)

    def _when_WE_pre(self,index):
        self._when_pre_green(index,1)
#        self.changestate[index] += self.greentime_pre

    def _when_WE(self,index):
        self._when_green(index,1)