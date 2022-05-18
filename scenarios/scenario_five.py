#!/usr/bin/env python
"""

"""

from scenario import AsymmetricVariableFlowsManhattan

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ScenarioFive(AsymmetricVariableFlowsManhattan):
    def __init__(self,sg_mh):
        super(ScenarioFive,self).__init__(sg_mh,4,\
            0,7200,500.0/3600,0,7200,250.0/3600,\
            0,7200,500.0/3600,0,7200,250.0/3600)