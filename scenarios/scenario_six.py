#!/usr/bin/env python
"""

"""
import random

from scenario import AsymmetricVariableFlowsManhattan
__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ScenarioSix(AsymmetricVariableFlowsManhattan):
    def __init__(self,sg_mh,dens,inter,dur):
        flow = ()
        begin = 0
        end = dur
        states = ['lNSWE_lNSWEped',
                  'lNSWE_hNSWEped',
                  'hNSWE_lNSWEped',
                  'hNSWE_hNSWEped',
                  'lNS_lNSped_hWE_hWEped',
                  'lNS_hNSped_hWE_lWEped',
                  'hNS_hNSped_lWE_lWEped',
                  'hNS_lNSped_lWE_hWEped',
                  'random']
        for interval,state in zip(range(inter),states):
            if state == 'lNSWE_lNSWEped':
                for flows in range(20):
                    flow = flow + (begin,end,dens)
                begin = end + 1
                end += dur

            elif state == 'hNSWE_hNSWEped':
                for flows in range(20):
                    flow = flow + (begin,end,dens*2)
                begin = end + 1
                end += dur

            elif state == 'lNSWE_hNSWEped':
                for flows in range(20):
                    if flows < 15:
                        if flows % 2 == 0:
                            flow = flow + (begin,end,dens)
                        else:
                            flow = flow + (begin,end,dens*2)
                    else:
                        flow = flow + (begin,end,dens*2)
                begin = end + 1
                end += dur

            elif state == 'hNSWE_lNSWEped':
                for flows in range(20):
                    if flows < 15:
                        if flows % 2 == 0:
                            flow = flow + (begin,end,dens*2)
                        else:
                            flow = flow + (begin,end,dens)
                    else:
                        flow = flow + (begin,end,dens)
                begin = end + 1
                end += dur

            elif state == 'lNS_lNSped_hWE_hWEped':
                for flows in range(20):
                    #NS
                    if flows in [0,8,2,10]:
                        flow = flow + (begin,end,dens)
                    #NSped
                    elif flows in [1,9,16,3,11,16,18]:
                        flow = flow + (begin,end,dens)
                    #WE
                    elif flows in [4,12,6,14]:
                        flow = flow + (begin,end,dens*2)
                    #WEped
                    elif flows in [5,7,13,15,17,19]:
                        flow = flow + (begin,end,dens*2)
                begin = end + 1
                end += dur

            elif state == 'lNS_hNSped_hWE_lWEped':
                for flows in range(20):
                    #NS
                    if flows in [0,8,2,10]:
                        flow = flow + (begin,end,dens)
                    #NSped
                    elif flows in [1,9,16,3,11,16,18]:
                        flow = flow + (begin,end,dens*2)
                    #WE
                    elif flows in [4,12,6,14]:
                        flow = flow + (begin,end,dens*2)
                    #WEped
                    elif flows in [5,7,13,15,17,19]:
                        flow = flow + (begin,end,dens)
                begin = end + 1
                end += dur

            elif state == 'hNS_hNSped_lWE_lWEped':
                for flows in range(20):
                    #NS
                    if flows in [0,8,2,10]:
                        flow = flow + (begin,end,dens*2)
                    #NSped
                    elif flows in [1,9,16,3,11,16,18]:
                        flow = flow + (begin,end,dens*2)
                    #WE
                    elif flows in [4,12,6,14]:
                        flow = flow + (begin,end,dens)
                    #WEped
                    elif flows in [5,7,13,15,17,19]:
                        flow = flow + (begin,end,dens)
                begin = end + 1
                end += dur

            elif state == 'hNS_lNSped_lWE_hWEped':
                for flows in range(20):
                    #NS
                    if flows in [0,8,2,10]:
                        flow = flow + (begin,end,dens*2)
                    #NSped
                    elif flows in [1,9,16,3,11,16,18]:
                        flow = flow + (begin,end,dens)
                    #WE
                    elif flows in [4,12,6,14]:
                        flow = flow + (begin,end,dens)
                    #WEped
                    elif flows in [5,7,13,15,17,19]:
                        flow = flow + (begin,end,dens*2)
                begin = end + 1
                end += dur

            else:
                for flows in range(20):
                    flow = flow + (begin,end,2*dens*(random.random()+0.1))
                begin = end + 1
                end += dur
        super(ScenarioSix,self).__init__(sg_mh,20,*flow)

#        super(ScenarioSix,self).__init__(sg_mh,16,\
#            0   ,3600, 750.0/3600,
#            0   ,3600, 750.0/3600,
#            0   ,3600, 750.0/3600,
#            0   ,3600, 750.0/3600,
#            0   ,3600, 250.0/3600,
#            0   ,3600, 250.0/3600,
#            0   ,3600, 250.0/3600,
#            0   ,3600, 250.0/3600,
#            0   ,3600, 500.0/3600,
#            0   ,3600, 500.0/3600,
#            0   ,3600, 500.0/3600,
#            0   ,3600, 500.0/3600,
#            0   ,3600, 500.0/3600,
#            0   ,3600, 500.0/3600,
#            0   ,3600, 500.0/3600,
#            0   ,3600, 500.0/3600,
#
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600,
#            3601,7200, 500.0/3600)