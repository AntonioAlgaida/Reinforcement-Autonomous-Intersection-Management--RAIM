#!/usr/bin/env python
"""

"""

from collections import defaultdict

from api_sumo import SumoAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ManhattanAlgorithm(SumoAlgorithm):
    def __init__(self,wq,lanes):
        self.lanes = lanes
        n = self.lanes
        NSGREEN = ("G"+"G"*n+"r"+"r"*n)*(2) + 'rrrr'
        NSYELLOW = ("y"+"y"*n+"r"+"r"*n)*(2) + 'ryry'
        WEGREEN = ("r"+"r"*n+"G"+"G"*n)*(2) + 'rrrr'
        WEYELLOW = ("r"+"r"*n+"y"+"y"*n)*(2) + 'yryr'
        CLEAR = ("r"+"r"*n+"r"+"r"*n)*(2) + 'rrrr'

        # Se repiten los estado en yellow tres veces, ya que son el número de
        # segundos que el semáforo está en amarillo

#        Se repiten el estado de clear dos veces ya que se dan dos segundos para
#        que se limpie la intersección

#        program   = [WEGREEN,WEYELLOW, WEYELLOW, WEYELLOW,CLEAR,CLEAR, NSGREEN, NSYELLOW, NSYELLOW, NSYELLOW,CLEAR,CLEAR]
        program = [WEGREEN,
                   WEYELLOW,
                   WEYELLOW,
                   WEYELLOW,
                   CLEAR,
                   CLEAR,
                   NSGREEN,
                   NSYELLOW,
                   NSYELLOW,
                   NSYELLOW,
                   CLEAR,
                   CLEAR,
                   CLEAR]

#        super(ManhattanAlgorithm,self).__init__(program,[0,6])
        super(ManhattanAlgorithm,self).__init__(program,[0,6])

        self.wq = wq

#    def get_statistics(self):
#        return  sum(map(sum,self.waittimes))/(self.sm.num_veh),\
#                sum(map(sum,self.waittimes_ped))/(self.sm.num_ped),\
#                sum(map(sum,self.queues))/(4*len(self.queues))

    def reset_algorithm(self,sm):
        super(ManhattanAlgorithm,self).reset_algorithm(sm)
        for index in range(len(self.ids)):
            for index2 in range(4):
                self.waittimes[index][index2] = 0

                self.queues[index][index2] = 0
                self.lastemptyqueue[index][index2] = 0

    def prepare_algorithm(self,sm):
        super(ManhattanAlgorithm,self).prepare_algorithm(sm)
        self.waittimes = [[0]*4 for i in range(len(self.ids))]
        self.queues = [[0]*4 for i in range(len(self.ids))]
        self.lastemptyqueue = [[0]*4 for i in range(len(self.ids))]

    def _when_NS(self,index):
        raise NotImplementedError('when_NS is not implemented')

    def _when_NS_pre(self,index):
        raise NotImplementedError('when_NS is not implemented')

    def _when_WE(self,index):
        raise NotImplementedError('when_WE is not implemented')

    def _when_WE_pre(self,index):
        raise NotImplementedError('when_WE is not implemented')

    def _when(self,pointer,index):
        i,j = list(map(int,self.ids[index].split('.')))
        fn = '{}.{}/{}.{}'.format
        fp = ':{}.{}_w{}'.format

        n = fn(i-1,j,i,j)
        s = fn(i+1,j,i,j)
        w = fn(i,j-1,i,j)
        e = fn(i,j+1,i,j)

#        ret = []
        if pointer == 0:
            queue1  = self.sm.traci.edge.getLastStepHaltingNumber(w)
            if queue1 == 0:
                self.queues[index][2] *= pow(1-self.wq,self.sm.time-self.lastemptyqueue[index][2])
                self.lastemptyqueue[index][2] = self.sm.time
            else:
                self.queues[index][2]*=1-self.wq
                self.queues[index][2]+=self.wq*queue1

            queue2  = self.sm.traci.edge.getLastStepHaltingNumber(e)

            if queue2 == 0:
                self.queues[index][3] *= pow(1-self.wq,self.sm.time-self.lastemptyqueue[index][3])
                self.lastemptyqueue[index][3] = self.sm.time
            else:
                self.queues[index][3]*=1-self.wq
                self.queues[index][3]+=self.wq*queue2

            self._when_WE(index)

#        if pointer == 1:
#            self._when_WE(index)
#        elif pointer == 0:
#            self._when_WE_pre(index)

        if pointer == 6:
            queue1  = self.sm.traci.edge.getLastStepHaltingNumber(n)

            if queue1 == 0:
                self.queues[index][0] *= pow(1-self.wq,self.sm.time-self.lastemptyqueue[index][0])
                self.lastemptyqueue[index][0] = self.sm.time
            else:
                self.queues[index][0]*=1-self.wq
                self.queues[index][0]+=self.wq*queue1

            queue2  = self.sm.traci.edge.getLastStepHaltingNumber(s)

            if queue2 == 0:
                self.queues[index][1] *= pow(1-self.wq,self.sm.time-self.lastemptyqueue[index][1])
                self.lastemptyqueue[index][1] = self.sm.time
            else:
                self.queues[index][1]*=1-self.wq
                self.queues[index][1]+=self.wq*queue2

            self._when_NS(index)


#        if pointer == 13:
#            self._when_NS(index)
#        elif pointer == 12:
#            self._when_NS_pre(index)

#        return(ret)
#            self._when_NS(index)
