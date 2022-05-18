#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 18:45:14 2020

@author: antonio
"""


    """check whether a person has requested to cross the street"""

activeRequest = False
greenTimeSoFar = 0

WALKINGAREAS = [':A0_w0', ':A0_w1', ':A0_w2', ':A0_w3'] # N, E, S, W
CROSSINGS = [':A0_c0', ':A0_c1', ':A0_c2', ':A0_c3'] # N, E, S, W
    # check both sides of the crossing

TLSID = self._traci.trafficlight.getIDList()[0]
MIN_GREEN_TIME = 10
if not activeRequest:
    activeRequest = checkWaitingPersons(WALKINGAREAS)

greenTimeSoFar = greenTimeSoFar + traci.simulation.simualtionstep()

if greenTimeSoFar > MIN_GREEN_TIME and activeRequest:
    # check whether someone has pushed the button
    # switch to the next phase
    traci.trafficlight.setRedYellowGreenState(
        TLSID, 'GGrrrrrrGGrrrrrrGGrrrrrrGGrrrrrrGGGGrr')
    # reset state
    activeRequest = False
    greenTimeSoFar = 0

else:
    traci.trafficlight.setRedYellowGreenState(
        TLSID, 'rrGGGGGGrrGGGGGGrrGGGGGGrrGGGGGGrrrrGG')

def checkWaitingPersons(WALKINGAREAS):
    for edge in WALKINGAREAS:
        peds = traci.edge.getLastStepPersonIDs(edge)
        print(peds)
        # check who is waiting at the crossing
        # we assume that pedestrians push the button upon
        # standing still for 1s
        for ped in peds:
            if (traci.person.getWaitingTime(ped) >= 1 and
                    traci.person.getNextEdge(ped) in CROSSINGS):
                numWaiting = traci.trafficlight.getServedPersonCount(TLSID, 2)
                print("%s: pedestrian %s pushes the button (waiting: %s)" %
                      (traci.simulation.getTime(), ped, numWaiting))
                return True
    return False
