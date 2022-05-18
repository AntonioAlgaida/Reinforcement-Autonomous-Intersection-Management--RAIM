
from manhattan_algorithm import ManhattanAlgorithm

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class FixedAlgorithm(ManhattanAlgorithm):
    def __init__(self,greentime=20,wq=0.5,lanes=1):
        super(FixedAlgorithm,self).__init__(wq,lanes)
        self.greentime = greentime

    def _when_NS(self,index):
        self.changestate[index] += self.greentime

    def _when_WE(self,index):
        self.changestate[index] += self.greentime