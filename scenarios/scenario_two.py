#!/usr/bin/env python
"""

"""

from scenario import AsymmetricVariableFlowsManhattan

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ScenarioTwo(AsymmetricVariableFlowsManhattan):
    def __init__(self,sg_mh,prob=1500.0/3600,begin=0,end=7200):
        super(ScenarioTwo,self).__init__(sg_mh,1,begin,end,prob)