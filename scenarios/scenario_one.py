#!/usr/bin/env python
"""

"""

from scenario import AsymmetricVariableFlowsManhattan

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ScenarioOne(AsymmetricVariableFlowsManhattan):
    def __init__(self,sg_mh,prob=500.0,begin=0,end=3600*5):
        super(ScenarioOne,self).__init__(sg_mh,1,begin,end,prob)
        self.begin = begin