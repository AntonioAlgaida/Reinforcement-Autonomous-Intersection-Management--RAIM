#!/usr/bin/env python
"""

"""

from random import uniform
import numpy as np

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class REDVDAlgorithm(ManhattanAlgorithm):
    def __init__(self,minth,maxth,delta,min_green_time,maxp,avgmode,\
                 maxcycle,deltacycle,liminc,limdec,inc_mid=-1,inc_maxth=1,inc_minth=-1,
                 wq=0.5,lanes=1):
        super(REDVDAlgorithm,self).__init__(wq,lanes)
        self.min_green_time = min_green_time
        self.min_red_time = min_green_time
        self.minth = minth
        self.maxth = maxth
        self.inc_mid = inc_mid
        self.inc_maxth = inc_maxth
        self.inc_minth = inc_minth
        if maxcycle < 2*min_green_time + 10:
            maxcycle = 2*min_green_time + 10
            print('WARNING: The maxcycle was less than 4*min_green_time + clear_time')
            print('The new maxcycle is: {}'.format(maxcycle))

        self.mincycle = 2*min_green_time + 10
        self.maxcycle = maxcycle
        self.delta = delta
        self.deltacycle = deltacycle
        self.maxp = maxp
        self.liminc = liminc
        self.limdec = limdec
        self.avgmode = avgmode
        columns = ['index','num','time','count','ocurs','cycle','avg',
                   'pa','greentime','greentime_compl']
        self.history = np.matrix(columns)
    def reset_algorithm(self,sm):
        super(REDVDAlgorithm,self).reset_algorithm(sm)
        for i in range(len(self.ids)):
            self.cycles[i] = self.mincycle
            self.ocurs[i] = 0
            for j in range(2):
                self.count[i][j] = 0
                self.lastgreentime[i][j] = (self.mincycle-5)//2
                self.ocurs[i][j] = 0

    def prepare_algorithm(self,sm):
        super(REDVDAlgorithm,self).prepare_algorithm(sm)
        self.count = [[-1]*2 for _ in range(len(self.ids))]
        self.cycles = [self.mincycle for _ in range(len(self.ids))]
        self.lastgreentime = [[(self.mincycle-5)//2]*2 for _ in range(len(self.ids))]
        self.ocurs = [[0]*2 for _ in range(len(self.ids))]


    def _when_green(self,index,num):
        #print('\n\nEntrando en _when_PRE_green {} {}'.format(index,num))
        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],
                            self.queues[index][1 if num == 0 else 3]))
        #print('AVG para coches: {}'.format(avg))
        if avg < self.minth:
            #print('avg < minth({})'.format(self.minth))
            self.count[index][num] = -1
            self.ocurs[index][num] = -1 if self.ocurs[index][num] > 0 else self.ocurs[index][num]+self.inc_minth
            pa = 0
        elif avg > self.maxth:
            #print('avg > maxth({})'.format(self.maxth))
            self.count[index][num] = 0
            self.ocurs[index][num] = 1 if self.ocurs[index][num] < 0 else self.ocurs[index][num]+self.inc_maxth
            pa = 1
        else:
            self.count[index][num] += 1
            pb = self.maxp*(avg-self.minth)/(self.maxth-self.minth) + 1e-12
            pa = pb / (1-self.count[index][num]*pb)
            pa = 1 if pa > 1 else pa
            #print('In between, pa: {}'.format(pa))
#            self.ocurs[index][num] = 0
            self.ocurs[index][num] = -1 if self.ocurs[index][num] > 0 else self.ocurs[index][num]+self.inc_mid

        if self.ocurs[index][num] >= self.liminc:
            #print('ocurs({}) >= liminc({})'.format(self.ocurs[index][num],self.liminc))
            self.cycles[index] += self.deltacycle
            #print('Cycle has been increased in {}. New cycle: {}'.format(self.deltacycle,self.cycles[index]))
        elif self.ocurs[index][num] <= -self.limdec:
            #print('ocurs({}) <= limdec({})'.format(self.ocurs[index][num],self.limdec))
            self.cycles[index] -= self.deltacycle
            #print('Cycle has been decreased in {}. New cycle: {}'.format(self.deltacycle,self.cycles[index]))

        if self.cycles[index] > self.maxcycle:
            #print('cycle {} > maxcycle{}'.format(self.cycles[index],self.maxcycle))
            self.cycles[index] = self.maxcycle
        elif self.cycles[index] < self.mincycle:
            #print('cycle {} < mincycle{}'.format(self.cycles[index],self.mincycle))
            self.cycles[index] = self.mincycle

        gt = self.lastgreentime[index][num]
        #print('Current greentime: {}'.format(gt))
        if uniform(0,1) < pa:
            gt += self.delta
            #print('Increasing green time: {} cos uniform<pa({})'.format(gt,pa))

        if gt > self.cycles[index] - self.min_red_time - 10:
            #print('gt {}> cycle {} - min_red_time {} - 10'.format(gt,self.cycles[index],self.min_red_time))
            gt = self.cycles[index] - self.min_red_time - 10
            #print('Before reducing, greentime: {}'.format(gt))

        if gt < self.min_green_time:
            #print('gt {} < min_green_time {}'.format(gt,self.min_green_time))
            gt = self.min_green_time

        #self.lastgreentime[index][num] = gt
        #print('Updating complementary arm form {}s'.format(self.lastgreentime[index][1-num]))
        self.lastgreentime[index][1-num] = self.cycles[index] - 10 - gt
        #print('To {}s'.format(self.lastgreentime[index][1-num]))
        #print('Finally, greentime is: {}, cycle: {}, gt comp: {}'.format(gt,self.cycles[index],self.lastgreentime[index][1-num]))
        self.changestate[index] = self.sm.time + gt

        b = self.sm.time
        c = self.cycles[index]
        d = gt
        f = self.lastgreentime[index][1-num]
        e = self.ocurs[index][num]
        m = pa
        n = avg
        o = index
        p = num
        q = self.count[index][num]
        a = [o,p,b,q,e,c,n,m,d,f]
        self.history = np.vstack((self.history,a))

    def _when_NS(self,index):
        self._when_green(index,0)

    def _when_WE(self,index):
        self._when_green(index,1)