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

class AREDVDAlgorithm2(ManhattanAlgorithm):
    def __init__(self,minth,maxth,delta1,delta2,delta3,min_green_time,maxcycle,avgmode,\
                 alpha=0.1,beta=0.9,target_min=0.4,target_max=0.6,inc_max=90,\
                 wq=0.5, lanes=1):
        super(AREDVDAlgorithm2,self).__init__(wq,lanes)
        self.minth = minth
        self.maxth = maxth
        self.delta1 = delta1
        self.delta2 = delta2
        self.delta3 = delta3

        self.min_green_time = min_green_time

        if maxcycle < 2*min_green_time + 10:
            maxcycle = 2*min_green_time + 10
            print('WARNING: The maxcycle was less than 4*min_green_time + clear_time')
            print('The new maxcycle is: {}'.format(maxcycle))

        self.maxcycle = maxcycle
#        self.mincycle = mincycle
        self.maxp = 0.5
        self.avgmode = avgmode
        self.alpha = alpha
        self.beta = beta
        self.target_min = minth+target_min*(maxth-minth)
        self.target_max = minth+target_max*(maxth-minth)
        self.inc_max = inc_max

        self.gt = 0

        columns = ['time', 'cycle', 'greentime',
                    'index', 'num', 'maxp_ns', 'maxp_we',
                    'pa', 'avg', 'inc']
        self.history = np.matrix(columns)

    def reset_algorithm(self,sm):
        super(AREDVDAlgorithm2,self).reset_algorithm(sm)
        for i in range(len(self.ids)):
            self.cycles[i] = self.min_green_time*2+10
            self.ocurs[i] = 0
            self.maxp_pre_ns[i] = self.maxp
            self.maxp_pre_we[i] = self.maxp

            for j in range(2):
                self.count[i][j] = 0
                self.lastgreentime[i][j] = self.min_green_time
                self.lastgreentime_ped[i][j] = self.min_green_time


    def prepare_algorithm(self,sm):
        super(AREDVDAlgorithm2,self).prepare_algorithm(sm)
        self.count = [[-1]*2 for _ in range(len(self.ids))]
        self.cycles = [self.min_green_time*2+10 for _ in range(len(self.ids))]
        self.maxp_pre_ns = [self.maxp for _ in range(len(self.ids))]
        self.maxp_pre_we = [self.maxp for _ in range(len(self.ids))]

        self.lastgreentime = [[self.min_green_time]*2 for _ in range(len(self.ids))]

        self.ocurs = [0 for _ in range(len(self.ids))]

    def find_max(self,my_list):
        max_value = max(my_list)
        max_index = my_list.index(max_value)
        return [max_value,max_index]

    def check_boundaries(self, gt, inc, index, num):
        self.gt = gt
        my_list = [self.lastgreentime[index][num],
           self.lastgreentime[index][1-num]]

        if self.gt < self.min_green_time:
#            inc = inc if inc > 0 else -inc
            self.cycles[index] += self.min_green_time - self.gt
            self.gt = self.min_green_time
            print('1 Current gt: {}, current cycle: {}'.format(self.gt,self.cycles[index]))
#            self.check_boundaries(gt, inc, index, num)

        for greentime in my_list:
            if greentime < self.min_green_time:
    #            inc = inc if inc > 0 else -inc
                self.cycles[index] += self.min_green_time - greentime
                greentime = self.min_green_time
                print('2 Current gt: {}, current cycle: {}'.format(greentime,self.cycles[index]))


        if self.cycles[index] > self.maxcycle:
#            times = self.cycles[index] - self.maxcycle
            inc_i = -1
            for time in range(abs(int((self.cycles[index] - self.maxcycle)//inc_i))):
#               print('Cycle({}) > maxcycle({})'.format(self.cycles[index],self.maxcycle))
                self.cycles[index] += inc_i
                [max_value, max_index] = self.find_max(my_list)
                print('Max_value: {}, self.gt: {}, inc: {}, max_index: {}, num: {}'.format(max_value, self.gt, inc, max_index, num))
                if max_value + inc == self.gt - time*inc_i:
                    self.gt += inc_i
                    print('Decreasing self.gt: {}'.format(self.gt))
                elif max_index == 0:
                    self.lastgreentime[index][num] += inc_i
                    print('Decreasing gt[num]: {}'.format(self.lastgreentime[index][num]))
                elif max_index == 1:
                    self.lastgreentime[index][1-num] += inc_i
                    print('Decreasing gt[1-num]: {}'.format(self.lastgreentime[index][1-num]))
            self.check_boundaries(self.gt, inc, index, num)


    def _when_green(self,index,num):
        print('\n\nEntrando en _when_PRE_green {} {}'.format(index,num))

        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
                            self.queues[index][1 if num == 0 else 3]))
        print('AVG para coches: {}'.format(avg))
        self.maxp_pre = self.maxp_pre_ns[index] if num == 0 else self.maxp_pre_we[index]

        if avg > self.target_max and self.maxp_pre <=0.5:
            self.maxp_pre += self.alpha
            print('Increasing maxp_pre: {}'.format(self.maxp_pre))
        elif avg < self.target_min and self.maxp_pre >=0.01:
            self.maxp_pre *= self.beta
            print('Decreasing maxp_pre: {}'.format(self.maxp_pre))

        pb = 0
        if avg <= self.minth:
            self.count[index][num] = -1
            self.ocurs[index] = -1 if self.ocurs[index] > 0 else self.ocurs[index]-1
            pa = 0
            print('avg < minth({})'.format(self.minth))

        elif avg >= self.maxth:
            self.count[index][num] = 0
            self.ocurs[index] = 1 if self.ocurs[index] < 0 else self.ocurs[index]+1
            pa = 1
            print('avg > maxth({})'.format(self.maxth))

        else:
            self.count[index][num] += 1
            pb = self.maxp_pre*(avg-self.minth)/(self.maxth-self.minth) + 1e-12
            pa = pb / (1-self.count[index][num]*pb)
            pa = 0.99999 if pa >= 1 else pa
            self.ocurs[index] = 0
            print('In between, pa: {}'.format(pa))


        self.gt = self.lastgreentime[index][num]

        if num == 0:
            self.maxp_pre_ns[index] = self.maxp_pre
        else:
            self.maxp_pre_we[index] = self.maxp_pre

        inc = 0
#        x = (self.gt-10)/(self.cycles[index]-30-20)*2
#        y = (avg-self.minth)/(self.maxth)*2
#        adapt_delta = y-x
#        ad_delta = int(self.delta1*(adapt_delta))

        if pa == 0:
            if avg <= 0.1:
                avg = 0.1
            inc = -abs(int(self.delta1*self.delta3*self.minth/avg))
            inc = inc if inc > -self.inc_max else -self.inc_max
            self.gt += inc
            self.cycles[index] += inc
            print('Decreasing gt({}) and cycle({}) in {}'.format(self.gt,self.cycles[index],inc))
        elif pa == 1:
            if avg <= 0.1:
                avg = 0.1
            inc = abs(int(self.delta1*self.delta3*self.minth/avg))
            inc = inc if inc < self.inc_max else self.inc_max
            self.gt += inc
            self.cycles[index] += inc
            print('Increasing gt({}) and cycle({}) in {}'.format(self.gt,self.cycles[index],inc))

        elif uniform(0,1) < pa:
            inc = self.delta2
            self.gt += inc
            self.cycles[index] += inc
            print('Increasing gt({}) and cycle({}) in {}'.format(self.gt,self.cycles[index],inc))



        self.check_boundaries(self.gt, inc, index, num)
        self.lastgreentime[index][num] = self.gt

        self.changestate[index] = self.sm.time + self.gt

        b = self.sm.time
        c = self.cycles[index]
        d = self.gt
        h = index
        k = self.maxp_pre_ns[index]
        l = self.maxp_pre_we[index]
        m = pa
        n = avg
        o = index
        p = num
        q = inc
        a = [b,c,d,o,p,k,l,m,n,q]
        self.history = np.vstack((self.history,a))

    def _when_NS(self,index):
        self._when_green(index,0)

    def _when_WE(self,index):
        self._when_green(index,1)