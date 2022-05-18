#!/usr/bin/env python
"""

"""

from random import uniform

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class REDVAlgorithm2(ManhattanAlgorithm):
    def __init__(self,cycle,min_green_time,min_red_time,minth,maxth,delta,\
                maxp,avgmode,wq=0.5,lanes=1, greentime_pre=15, min_green_time_ped=15,
                max_green_time_ped=60):
        super(REDVAlgorithm2,self).__init__(wq,lanes)
        self.cycle = cycle
        self.min_green_time = min_green_time
        self.min_red_time = min_red_time
        self.minth = minth
        self.maxth = maxth
        self.delta = delta
        self.maxp = maxp
        self.avgmode = avgmode
        self.limitup = cycle - min_red_time - 20 - min_green_time_ped*2
        self.greentime_pre = greentime_pre
        self.min_green_time_ped = min_green_time_ped
        self.max_green_time_ped = max_green_time_ped
#        columns = ['index','num','greentime']
#        self.history = np.matrix(columns)
    def prepare_algorithm(self,sm):
        super(REDVAlgorithm2,self).prepare_algorithm(sm)
        self.count = [[-1]*2 for _ in range(len(self.ids))]
        self.lastgreentime = [[(self.cycle-20)//4]*2 for _ in range(len(self.ids))]
        self.lastgreentime_ped = [[(self.cycle-20)//4]*2 for _ in range(len(self.ids))]

    def reset_algorithm(self,sm):
        super(REDVAlgorithm2,self).reset_algorithm(sm)
        for i in range(len(self.ids)):
            for j in range(2):
                self.count[i][j] = -1
                self.lastgreentime[i][j] = (self.cycle-20)//4
                self.lastgreentime_ped[i][j] = (self.cycle-20)//4

    def _when_green(self,index,num):
        print('Entrando en _when_green {} {}'.format(index,num))
        avg = self.avgmode((self.queues_ped[index][0 if num == 0 else 2],\
                            self.queues_ped[index][1 if num == 0 else 3]))
        print('AVG para peatones: {}'.format(avg))

        if avg < self.minth:
            self.count[index][num] = -1
            pa = 0
            print('avg < minth({})'.format(self.minth))
        elif avg > self.maxth:
            self.count[index][num] = 0
            pa = 1
            print('avg > maxth({})'.format(self.maxth))

        else:
            self.count[index][num] += 1
            pb = self.maxp*(avg-self.minth)/(self.maxth-self.minth) + 1e-12
            pa = pb / (1-self.count[index][num]*pb)
            pa = 1 if pa > 1 else pa
            print('In between, pa: {}'.format(pa))

        gt = self.lastgreentime_ped[index][num]
        print('Last greentime_ped: {}'.format(gt))
        dec=uniform(0,1)

        if dec < pa:
            gt += self.delta
            self.count[index][num] = 0 # Esta línea no estaba incluida en el algoritmo original
            print('Increasing gt: {}'.format(gt))

        if gt > self.max_green_time_ped:
            gt = self.max_green_time_ped
            print('WARNING: gt > max green time ped')
        elif gt < self.min_green_time_ped:
            gt = self.min_green_time_ped
            print('WARNING: gt < min green time ped')

        # -20 ya que es tiempo de amarillo+clear
        # Cálculo del tiempo en verde de la rama complementaria
        #self.lastgreentime[index][num] = gt

        self.lastgreentime[index][num] = self.cycle - 20 - gt - self.lastgreentime_ped[index][1-num]\
                                                - self.lastgreentime[index][1-num]
        print('Updating greentime_ped 1- {}'.format(self.lastgreentime_ped[index][1-num]))
        print('cycle: {}, gt: {} lastgeentime: {} lastgreentime 1-:{}'.format(self.cycle, gt, self.lastgreentime[index][num], self.lastgreentime[index][1-num]))
        self.changestate[index] = self.sm.time + gt

    def _when_pre_green(self,index,num):
        print('Entrando en _when_pre_green {} {}'.format(index,num))
        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
                            self.queues[index][1 if num == 0 else 3]))
        print('AVG para coches: {}'.format(avg))
        if avg < self.minth:
            self.count[index][num] = -1
            pa = 0
            print('avg < minth({})'.format(self.minth))
        elif avg > self.maxth:
            self.count[index][num] = 0
            pa = 1
            print('avg > maxth({})'.format(self.maxth))
        else:
            self.count[index][num] += 1
            pb = self.maxp*(avg-self.minth)/(self.maxth-self.minth) + 1e-12
            pa = pb / (1-self.count[index][num]*pb)
            pa = 1 if pa > 1 else pa
            print('In between, pa: {}'.format(pa))

        gt = self.lastgreentime[index][num]
        print('Last greentime: {}'.format(gt))

        dec=uniform(0,1)

        if dec < pa:
            gt += self.delta
            self.count[index][num] = 0 # Esta línea no estaba incluida en el algoritmo original
            print('Increasing gt: {}'.format(gt))

        if gt > self.limitup:
            gt = self.limitup
            print('WARNING: gt > max green time')

        elif gt < self.min_green_time:
            gt = self.min_green_time
            print('WARNING: gt < min green time')

        # -20 ya que es tiempo de amarillo+clear
        # Cálculo del tiempo en verde de la rama complementaria
        #self.lastgreentime[index][num] = gt
        self.lastgreentime_ped[index][num] = self.cycle - 20 - gt - self.lastgreentime_ped[index][1-num]\
                                           - self.lastgreentime[index][1-num]
        print('Updating lastgreentime_ped {}'.format(self.lastgreentime[index][num]))
        print('cycle: {}, gt: {} lastgeentime_ped: {} lastgreentime_ped 1-:{}'.format(self.cycle, gt, self.lastgreentime[index][1-num], self.lastgreentime_ped[index][1-num]))

        if self.lastgreentime_ped[index][num] > self.limitup:
            self.lastgreentime_ped[index][num] = self.limitup
            print('WARNING: self.lastgreentime_ped[index][num] > max green time')

        elif self.lastgreentime_ped[index][num] < self.min_green_time:
            self.lastgreentime_ped[index][num] = self.min_green_time
            print('WARNING: self.lastgreentime_ped[index][num] < min green time')

        self.changestate[index] = self.sm.time + gt

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