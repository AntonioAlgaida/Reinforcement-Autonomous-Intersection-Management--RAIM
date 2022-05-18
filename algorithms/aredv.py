#!/usr/bin/env python
"""

"""

from random import uniform

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class AREDVAlgorithm(ManhattanAlgorithm):
    def __init__(self,cycle,min_green_time,min_red_time,minth,maxth,delta,\
                maxp, avgmode,wq=0.5,lanes=1, greentime_pre=15, alpha = 0.1, beta=0.9):
        super(AREDVAlgorithm,self).__init__(wq,lanes)
        self.cycle = cycle
        self.min_green_time = min_green_time
        self.min_red_time = min_red_time
        self.minth = minth
        self.maxth = maxth
        self.delta = delta
        self.maxp = maxp
        self.maxp_ns = maxp
        self.maxp_we = maxp
        self.maxp_pre_ns = maxp
        self.maxp_pre_we = maxp
        self.avgmode = avgmode
        self.limitup = cycle - min_red_time - 10
        self.greentime_pre = greentime_pre
        self.alpha = alpha
        self.beta = beta
        self.target_min = minth+0.4*(maxth-minth)
        self.target_max = minth+0.6*(maxth-minth)
        self.history = []

    def prepare_algorithm(self,sm):
        super(AREDVAlgorithm,self).prepare_algorithm(sm)
        self.count = [[-1]*2 for _ in range(len(self.ids))]
        self.lastgreentime = [[(self.cycle-10)//2]*2 for _ in range(len(self.ids))]

    def reset_algorithm(self,sm):
        super(AREDVAlgorithm,self).reset_algorithm(sm)
        for i in range(len(self.ids)):
            for j in range(2):
                self.count[i][j] = -1
                self.lastgreentime[i][j] = (self.cycle-10)//2

    def _when_green(self,index,num):
        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
                            self.queues[index][1 if num == 0 else 3]))
#        index1 = 0 if num == 0 else 2
#        index2 = 1 if num == 0 else 3
#        avg = self.avgmode((
#                (self.queues[index][index1] + self.queues_ped[index][index1]),\
#                (self.queues[index][index2] + self.queues_ped[index][index2])))
        self.maxp = self.maxp_ns if num == 0 else self.maxp_we

        if avg < self.minth:
            self.count[index][num] = -1
            pa = 0

        elif avg > self.maxth:
            self.count[index][num] = 0
            pa = 1

        else:
            self.count[index][num] += 1
            pb = self.maxp*(avg-self.minth)/(self.maxth-self.minth) + 1e-12

            pa = pb / (1-self.count[index][num]*pb)
            pa = 1 if pa > 1 else pa

        if avg > self.target_max and self.maxp <=0.5:
            self.maxp = self.maxp+self.alpha
#            self.maxp = self.maxp*self.beta
        elif avg < self.target_min and self.maxp >=0.01:
            self.maxp = self.maxp*self.beta
#            self.maxp = self.maxp+self.alpha

        if num == 0:
            self.maxp_ns = self.maxp
        else:
            self.maxp_we = self.maxp

        gt = self.lastgreentime[index][num]

        dec=uniform(0,1)

        if dec < pa:
            gt += self.delta
            self.count[index][num] = 0 # Esta línea no estaba incluida en el algoritmo original

        if gt > self.limitup:
            gt = self.limitup
        elif gt < self.min_green_time:
            gt = self.min_green_time
        # -20 ya que es tiempo de amarillo+clear
        # Cálculo del tiempo en verde de la rama complementaria
        #self.lastgreentime[index][num] = gt
        self.lastgreentime[index][1-num] = self.cycle - 20 - gt
        self.changestate[index]   = self.sm.time + gt
        self.history.append(self.maxp)

    def _when_pre_green(self,index,num):
#        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
#                            self.queues[index][1 if num == 0 else 3]))
        index1 = 0 if num == 0 else 2
        index2 = 1 if num == 0 else 3
        avg = self.avgmode((
                (self.queues[index][index1] + self.queues_ped[index][index1]),\
                (self.queues[index][index2] + self.queues_ped[index][index2])))
        self.maxp_pre = self.maxp_pre_ns if num == 0 else self.maxp_pre_we

        if avg < self.minth:
            self.count[index][num] = -1
            pa = 0

        elif avg > self.maxth:
            self.count[index][num] = 0
            pa = 1

        else:
            self.count[index][num] += 1
            pb = self.maxp_pre*(avg-self.minth)/(self.maxth-self.minth) + 1e-12

            pa = pb / (1-self.count[index][num]*pb)
            pa = 1 if pa > 1 else pa

        if avg > self.target_max and self.maxp_pre <=0.5:
            self.maxp_pre = self.maxp_pre+self.alpha
#            self.maxp = self.maxp*self.beta
        elif avg < self.target_min and self.maxp_pre >=0.01:
            self.maxp_pre = self.maxp_pre*self.beta
#            self.maxp = self.maxp+self.alpha

        if num == 0:
            self.maxp_pre_ns = self.maxp_pre
        else:
            self.maxp_pre_we = self.maxp_pre

        gt = self.lastgreentime[index][num]

        dec=uniform(0,1)

        if dec < pa:
            gt += self.delta
            self.count[index][num] = 0 # Esta línea no estaba incluida en el algoritmo original

        if gt > self.limitup:
            gt = self.limitup
        elif gt < self.min_green_time:
            gt = self.min_green_time
        # -20 ya que es tiempo de amarillo+clear
        # Cálculo del tiempo en verde de la rama complementaria
        #self.lastgreentime[index][num] = gt
        self.lastgreentime[index][1-num] = self.cycle - 20 - gt
        self.changestate[index]   = self.sm.time + gt
        self.history.append(self.maxp_pre)

    def _when_NS_pre(self,index):
#        self.changestate[index] += self.greentime_pre
        self._when_pre_green(index,0)

    def _when_NS(self,index):
        self._when_green(index,0)

    def _when_WE_pre(self,index):
#        self.changestate[index] += self.greentime_pre
        self._when_pre_green(index,1)

    def _when_WE(self,index):
        self._when_green(index,1)