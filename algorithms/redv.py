#!/usr/bin/env python
"""

"""

from random import uniform

from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class REDVAlgorithm(ManhattanAlgorithm):
    def __init__(self,cycle,min_green_time,min_red_time,minth,maxth,delta,\
                maxp,avgmode,wq=0.5,lanes=1, greentime_pre=15):
        super(REDVAlgorithm,self).__init__(wq,lanes)
        self.cycle = cycle
        self.min_green_time = min_green_time
        self.min_red_time = min_red_time
        self.minth = minth
        self.maxth = maxth
        self.delta = delta
        self.maxp = maxp
        self.avgmode = avgmode
        self.limitup = cycle - min_red_time - 10
        self.greentime_pre =greentime_pre

    def prepare_algorithm(self,sm):
        super(REDVAlgorithm,self).prepare_algorithm(sm)
        self.count = [[-1]*2 for _ in range(len(self.ids))]
        self.lastgreentime = [[(self.cycle-10)//2]*2 for _ in range(len(self.ids))]

    def reset_algorithm(self,sm):
        super(REDVAlgorithm,self).reset_algorithm(sm)
        for i in range(len(self.ids)):
            for j in range(2):
                self.count[i][j] = -1
                self.lastgreentime[i][j] = (self.cycle-10)//2

    def _when_green(self,index,num):
        avg = self.avgmode((self.queues[index][0 if num == 0 else 2],\
                            self.queues[index][1 if num == 0 else 3]))
        print("Average queue is: ", avg)
#        print("Queue 0/2: ", self.queues[index][0 if num == 0 else 2])
#        print("Queue 1/3:", self.queues[index][1 if num == 0 else 3])
#        gt = self.lastgreentime[index][num]
#        if avg < self.minth:
#            # Disminuimos el ciclo
#            gt -= self.delta
#        elif avg > self.maxth:
#             #Aumentamos el ciclo
#             gt += self.delta
#        # Entre medias, nada.
#
#        if gt > self.limitup:
#            gt = self.limitup
#        elif gt < self.min_green_time:
#            gt = self.min_green_time
#
#        self.lastgreentime[index][1-num] = self.cycle - 20 - gt
#        self.changestate[index]   = self.sm.time + gt

        #Comprobamos que estamos en los límites de max y min cicle, si no estamos,
        # Si es porque hemos quitado, se lo volvemos a añadir,
        # Si es porque hemos añadido, se lo quitamos a la otra rama





        if avg < self.minth:
            print('avg: {} < minth: {}'.format(avg,self.minth))
            self.count[index][num] = -1
            pa = 0
        elif avg > self.maxth:
            print('avg: {} > maxth: {}'.format(avg,self.maxth))
            self.count[index][num] = 0
            pa = 1
        else:
            print('minth: {} < avg: {} < maxth: {}'.format(self.minth,avg,self.maxth))
            self.count[index][num] += 1
            print('count[{}][{}]: {}'.format(index,num,self.count[index][num]))
            pb = self.maxp*(avg-self.minth)/(self.maxth-self.minth) + 1e-12
            print('pb: {}'.format(pb))

            pa = pb / (1-self.count[index][num]*pb)
            print('pa before correction: {}'.format(pa))
            pa = 1 if pa > 1 else pa
            print('pa after correction: {}'.format(pa))

        gt = self.lastgreentime[index][num]

        print('Green time before decision: {}'.format(gt))
        dec=uniform(0,1)

        print('Checking if dec:{} < pa:{}'.format(dec,pa))
        if dec < pa:
            gt += self.delta
            self.count[index][num] = 0 # Esta línea no estaba incluida en el algoritmo original
        print('Green time after decision: {}'.format(gt))

        if gt > self.limitup:
            gt = self.limitup
        elif gt < self.min_green_time:
            gt = self.min_green_time
        # -20 ya que es tiempo de amarillo+clear
        # Cálculo del tiempo en verde de la rama complementaria
        #self.lastgreentime[index][num] = gt
        self.lastgreentime[index][1-num] = self.cycle - 20 - gt
        self.changestate[index]   = self.sm.time + gt


    def _when_NS_pre(self,index):
        self.changestate[index] += self.greentime_pre

    def _when_NS(self,index):
        self._when_green(index,0)

    def _when_WE_pre(self,index):
        self.changestate[index] += self.greentime_pre

    def _when_WE(self,index):
        self._when_green(index,1)