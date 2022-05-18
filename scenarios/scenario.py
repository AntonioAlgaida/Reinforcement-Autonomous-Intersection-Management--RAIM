#!/usr/bin/env python
"""

"""

from api_sumo import SumoScenario,Flow,Route,CarType,VehDist
from manhattan_utils import get_edges

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class AsymmetricVariableFlowsManhattan(SumoScenario):
    def __init__(self,sg_mh,groupspertime,*args):
        super(AsymmetricVariableFlowsManhattan,self).__init__()
        if groupspertime not in [1,2,4,20]:
            raise AtributeError('Groups_per_time must be 1, 2, 4 or 20')
        self.gpt = groupspertime
        self.sg = sg_mh
        self.args = args
        self._create_flows()

    def _get_intervals(self):
        for i in range(0,len(self.args),self.gpt*3):
            group = self.args[i:i+self.gpt*3]
            probNS = probSN = probWE = probEW = 0
            beginNS = beginSN = beginWE = beginEW = 0
            endNS = endSN = endWE = endEW = 0

            #La variable grupos por tiempo, es el numero de fujos diferentes que hay en un intervalo
            if self.gpt == 1: #siendo posibles uno, todos los sentidos con el mismo flujo
#                beginNS = beginSN = beginWE = beginEW = group[0]
#                endNS = endSN = endWE = endEW = group[1]
#                probNS = probSN = probWE = probEW = group[2]
                beginNS = beginSN = beginWE = beginEW = \
                beginNW = beginSE = beginWS = beginEN = group[0]

                beginNS_ped = beginSN_ped = beginWE_ped = beginEW_ped = \
                beginSE_ped = beginWS_ped = beginEN_ped = beginNW_ped = \
                beginNE_ped = beginES_ped = beginSW_ped = beginWN_ped = group[0]

                endNS = endSN = endWE = endEW = endNW = \
                endSE = endWS = endEN = group[1]

                endNS_ped = endSN_ped = endWE_ped = endEW_ped = \
                endNW_ped = endSE_ped = endWS_ped = endEN_ped = \
                endNE_ped = endES_ped = endSW_ped = endWN_ped = group[1]

                probNS = probSN = probWE = probEW = \
                probNW = probSE = probWS = probEN = group[2]

                probNS_ped = probSN_ped = probWE_ped = probEW_ped = \
                probNW_ped = probSE_ped = probWS_ped = probEN_ped = \
                probNE_ped = probES_ped = probSW_ped = probWN_ped = 0.0001
            elif self.gpt == 2: #dos, la direccion NS-SN con un flujo y WE-EW con otro
#                beginNS = beginSN = group[0]; beginWE = beginEW = group[3]
#                endNS = endSN = group[1]; endWE = endEW = group[4]
#                probNS = probSN = group[2]; probWE = probEW = group[5]
                beginNS = beginSN = beginNS_ped = beginSN_ped = beginNW = \
                beginSE = beginNW_ped = beginSE_ped = beginNE_ped = beginES_ped = group[0]
                endNS = endSN = endNS_ped = endSN_ped = endNW = endSE = \
                endNW_ped = endSE_ped = endNE_ped = endES_ped = group[1]
                probNS = probSN = probNW = probSE = group[2]
                probNS_ped = probSN_ped = probNW_ped = \
                probSE_ped = probNE_ped = probES_ped = 0.0001

                beginWE = beginEW = beginWE_ped = beginEW_ped = beginWS = \
                beginEN = beginWS_ped = beginEN_ped = beginSW_ped = beginWN_ped = group[3]
                endWE = endEW =  endWE_ped = endEW_ped = endWS = endEN = \
                endWS_ped = endEN_ped = endSW_ped = endWN_ped = group[4]
                probWE = probEW = probWS = probEN = group[5]
                probWE_ped = probEW_ped = probWS_ped = \
                probEN_ped = probSW_ped = probWN_ped = 0.0001

            elif self.gpt == 4: # cuatro, NS,SN,WE,EW cada uno con un flujo diferente
                beginNS = beginNS_ped = beginNW = beginNW_ped = beginNE_ped = group[0]
                beginSN = beginSN_ped = beginSE = beginSE_ped = beginES_ped = group[3]
                beginWE = beginWE_ped = beginWS = beginWS_ped = beginSW_ped = group[6]
                beginEW = beginEW_ped = beginEN = beginEN_ped = beginWN_ped = group[9]
                endNS = endNS_ped = endNW = endNW_ped = endNE_ped = group[1]
                endSN = endSN_ped = endSE = endSE_ped = endES_ped = group[4]
                endWE = endWE_ped = endWS = endWS_ped = endSW_ped = group[7]
                endEW = endEW_ped = endEN = endEN_ped = endWN_ped = group[10]
                probNS = probNS_ped = probNW = probNW_ped = probNE_ped = group[2]
                probSN = probSN_ped = probSE = probSE_ped = probES_ped = group[5]
                probWE = probWE_ped = probWS = probWS_ped = probSW_ped = group[8]
                probEW = probEW_ped = probEN = probEN_ped = probWN_ped = group[11]

            else: # 20, uno para cada flujo, incluido los peatones
                beginNS = group[0]; endNS = group[1]; probNS = group[2];
                beginNS_ped = group[3]; endNS_ped = group[4]; probNS_ped = group[5];
                beginSN = group[6]; endSN = group[7]; probSN = group[8];
                beginSN_ped = group[9]; endSN_ped = group[10]; probSN_ped = group[11];
                beginWE = group[12]; endWE = group[13]; probWE = group[14];
                beginWE_ped = group[15]; endWE_ped = group[16]; probWE_ped = group[17];
                beginEW = group[18]; endEW = group[19]; probEW = group[20];
                beginEW_ped = group[21]; endEW_ped = group[22]; probEW_ped = group[23];
                beginNW = group[24]; endNW = group[25]; probNW = group[26];
                beginNW_ped = group[27]; endNW_ped = group[28]; probNW_ped = group[29];
                beginSE = group[30]; endSE = group[31]; probSE = group[32];
                beginSE_ped = group[33]; endSE_ped = group[34]; probSE_ped = group[35];
                beginWS = group[36]; endWS = group[37]; probWS = group[38];
                beginWS_ped = group[39]; endWS_ped = group[40]; probWS_ped = group[41];
                beginEN = group[42]; endEN = group[43]; probEN = group[44];
                beginEN_ped = group[45]; endEN_ped = group[46]; probEN_ped = group[47];
                beginNE_ped = group[48]; endNE_ped = group[49]; probNE_ped = group[50];
                beginES_ped = group[51]; endES_ped = group[52]; probES_ped = group[53];
                beginSW_ped = group[54]; endSW_ped = group[55]; probSW_ped = group[56];
                beginWN_ped = group[57]; endWN_ped = group[58]; probWN_ped = group[59];

#                beginNE_ped = beginES_ped = beginSW_ped = beginWN_ped =
#                endNE_ped = endES_ped = endSW_ped = endWN_ped =
#                probNE_ped = probES_ped = probSW_ped = probWN_ped =

            yield beginNS, endNS, probNS,\
            beginNS_ped, endNS_ped, probNS_ped,\
            beginSN, endSN, probSN,\
            beginSN_ped, endSN_ped, probSN_ped,\
            beginWE, endWE, probWE,\
            beginWE_ped, endWE_ped, probWE_ped,\
            beginEW, endEW, probEW,\
            beginEW_ped, endEW_ped, probEW_ped,\
            beginNW, endNW, probNW,\
            beginNW_ped, endNW_ped, probNW_ped,\
            beginSE, endSE, probSE,\
            beginSE_ped, endSE_ped, probSE_ped,\
            beginWS, endWS, probWS,\
            beginWS_ped, endWS_ped, probWS_ped,\
            beginEN, endEN, probEN,\
            beginEN_ped, endEN_ped, probEN_ped,\
            beginNE_ped, beginES_ped, beginSW_ped,\
            beginWN_ped, endNE_ped, endES_ped, endSW_ped,\
            endWN_ped, probNE_ped, probES_ped, probSW_ped, probWN_ped

    def _create_flows(self):
        flows = 'flow{}_{}_{}'.format
        routs = 'rout{}_{}'.format
        for i in range(1,self.sg.cols-1):
            routeid = routs('NS',i)
            self.add_route(Route(routeid,get_edges(0,i,self.sg.rows-1,
                                                   i,self.sg.rows,
                                                   self.sg.cols,
                                                   straight=True,
                                                   pedestrians=False)))
                # Pedestrians
            routeid = routs('NS_ped',i)
            self.add_route(Route(routeid,get_edges(0,i,self.sg.rows-1,
                                                   i,self.sg.rows,
                                                   self.sg.cols,
                                                   straight=True,
                                                   pedestrians=True)))

            routeid = routs('SN',i)
            self.add_route(Route(routeid,get_edges(self.sg.rows-1,i,0,
                                                   i,self.sg.rows,
                                                   self.sg.cols,
                                                   straight=True,
                                                   pedestrians=False)))

                # Pedestrians
            routeid = routs('SN_ped',i)
            self.add_route(Route(routeid,get_edges(self.sg.rows-1,i,0,
                                                   i,self.sg.rows,
                                                   self.sg.cols,
                                                   straight=True,
                                                   pedestrians=True)))

        for i in range(1,self.sg.rows-1):
            routeid = routs('WE',i)
            self.add_route(Route(routeid,get_edges(i,0,
                                                   i,self.sg.cols-1,
                                                   self.sg.rows,self.sg.cols,
                                                   straight=True,
                                                   pedestrians=False)))
            routeid = routs('WE_ped',i)
            self.add_route(Route(routeid,get_edges(i,0,
                                                   i,self.sg.cols-1,
                                                   self.sg.rows,self.sg.cols,
                                                   straight=True,
                                                   pedestrians=True)))

            routeid = routs('EW',i)
            self.add_route(Route(routeid,get_edges(i,self.sg.cols-1,
                                                   i,0,
                                                   self.sg.rows,self.sg.cols,
                                                   straight=True,
                                                   pedestrians=False)))
            routeid = routs('EW_ped',i)
            self.add_route(Route(routeid,get_edges(i,self.sg.cols-1,
                                                   i,0,
                                                   self.sg.rows,self.sg.cols,
                                                   straight=True,
                                                   pedestrians=True)))
            # Rutas girando a la derecha
        # Rutas NW y SE
        k=0
        for i in range(1,self.sg.cols-1):
            for j in range(1,self.sg.rows-1):
                routeid = routs('NW',k)
                self.add_route(Route(routeid,get_edges(0,i,
                                                       j,0,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=False)))

                # Pedestrians
                routeid = routs('NW_ped',k)
                self.add_route(Route(routeid,get_edges(0,i,
                                                       j,0,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))


                routeid = routs('SE',k)
                self.add_route(Route(routeid,get_edges(self.sg.rows-1,i,
                                                       j,self.sg.cols-1,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=False)))

                # Pedestrians
                routeid = routs('SE_ped',k)
                self.add_route(Route(routeid,get_edges(self.sg.rows-1,i,
                                                       j,self.sg.cols-1,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))
                k+=1
        # Rutas WS y EN
        k=0
        for i in range(1,self.sg.rows-1):
            for j in range(1,self.sg.cols-1):
                routeid = routs('WS',k)
                self.add_route(Route(routeid,get_edges(i,0,
                                                       self.sg.rows-1,j,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=False)))

                routeid = routs('EN',k)
                self.add_route(Route(routeid,get_edges(i,self.sg.cols-1,
                                                       0,j,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=False)))

                routeid = routs('WS_ped',k)
                self.add_route(Route(routeid,get_edges(i,0,
                                                       self.sg.rows-1,j,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))

                routeid = routs('EN_ped',k)
                self.add_route(Route(routeid,get_edges(i,self.sg.cols-1,
                                                       0,j,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))
                k+=1

        # Rutas NE_ped, ES_ped, SW_ped y WN_ped
        k=0
        for i in range(1,self.sg.rows-1):
            for j in range(1,self.sg.cols-1):
                routeid = routs('NE_ped',k)
                self.add_route(Route(routeid,get_edges(0,j,
                                                       i,self.sg.cols-1,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))

                routeid = routs('ES_ped',k)
                self.add_route(Route(routeid,get_edges(i,self.sg.cols-1,
                                                       self.sg.rows-1,j,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))

                routeid = routs('SW_ped',k)
                self.add_route(Route(routeid,get_edges(self.sg.rows-1,j,
                                                       i,0,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))

                routeid = routs('WN_ped',k)
                self.add_route(Route(routeid,get_edges(i,0,
                                                       0,j,
                                                       self.sg.rows,self.sg.cols,
                                                       straight=False,
                                                       pedestrians=True)))
                k+=1

        self.add_car_type(CarType(_id='car_gasoline',
                                  vClass="passenger",
                                  carFollowModel="Krauss",
                                  minGap=0.5,
                                  length=3,
                                  maxSpeed='31.0',
                                  probability=0.30,
                                  emissionClass='HBEFA3/PC_G_EU5'))

        self.add_car_type(CarType(_id='car_diesel',
                                  vClass="passenger",
                                  carFollowModel="Krauss",
                                  minGap=0.5,
                                  length=3,
                                  maxSpeed='31.0',
                                  probability=0.40,
                                  emissionClass='HBEFA3/PC_D_EU5'))

        self.add_car_type(CarType(_id='pedestrian',
                                  vClass="pedestrian",
                                  probability=0.40,
                                  carFollowModel="Krauss"))

        self.add_car_type(CarType(_id='motorcycle',
                                  vClass="motorcycle",
                                  carFollowModel="Krauss",
                                  minGap=0.5,
                                  length=1,
                                  probability=0.05,
                                  emissionClass='HBEFA3/LDV_G_EU5'))

        self.add_car_type(CarType(_id='moped',
                                  vClass="moped",
                                  carFollowModel="Krauss",
                                  minGap=0.5,
                                  length=1,
                                  probability=0.05,
                                  emissionClass='HBEFA3/LDV_G_EU4'))

        self.add_car_type(CarType(_id='delivery',
                                  vClass="delivery",
                                  carFollowModel="Krauss",
                                  minGap=0.5,
                                  probability=0.10,
                                  emissionClass='HBEFA3/HDV_D_EU5'))

        self.add_car_type(CarType(_id='bus',
                                  vClass="bus",
                                  carFollowModel="Krauss",
                                  minGap=0.5,
                                  probability=0.10,
                                  emissionClass='HBEFA3/Bus'))

        self.add_car_type(VehDist(_id='typedist1',
                                  vTypes='car_gasoline car_diesel motorcycle moped delivery bus'))

        # debería ser maxSpeed = 14
        j = 0


#        for probNS,probSN,probWE,probEW,beginNS,beginSN,\
#        beginWE,beginEW,endNS,endSN,endWE,endEW in self._get_intervals():

        for beginNS, endNS, probNS, beginNS_ped, endNS_ped, probNS_ped,\
            beginSN, endSN, probSN, beginSN_ped, endSN_ped, probSN_ped, beginWE,\
            endWE, probWE, beginWE_ped, endWE_ped, probWE_ped, beginEW, endEW,\
            probEW, beginEW_ped, endEW_ped, probEW_ped, beginNW, endNW, probNW,\
            beginNW_ped, endNW_ped, probNW_ped, beginSE, endSE, probSE,\
            beginSE_ped, endSE_ped, probSE_ped, beginWS, endWS, probWS,\
            beginWS_ped, endWS_ped, probWS_ped, beginEN, endEN, probEN,\
            beginEN_ped, endEN_ped, probEN_ped, beginNE_ped, beginES_ped,\
            beginSW_ped, beginWN_ped, endNE_ped, endES_ped, endSW_ped,\
            endWN_ped, probNE_ped, probES_ped, probSW_ped, probWN_ped in self._get_intervals():
                j+=1
                for i in range(1,self.sg.cols-1):
                    routeid = routs('NS',i)
                    self.add_flow(Flow(flows('NS',i,j),beginNS,endNS,vehsPerHour=probNS,route=routeid,departSpeed='max',
                                       tpe='typedist1'))

                    routeid = routs('NS_ped',i)
                    self.add_flow(Flow(flows('NS_ped_',i,j),beginNS_ped,endNS_ped,vehsPerHour=probNS_ped,route=routeid,tpe='pedestrian'))

                    routeid = routs('SN',i)
                    self.add_flow(Flow(flows('SN',i,j),beginSN,endSN,vehsPerHour=probSN,route=routeid,departSpeed='max',tpe='typedist1'))

                    routeid = routs('SN_ped',i)
                    self.add_flow(Flow(flows('SN_ped_',i,j),beginSN_ped,endSN_ped,vehsPerHour=probSN_ped,route=routeid,tpe='pedestrian'))

                for i in range(1,self.sg.rows-1):
                    routeid = routs('WE',i)
                    self.add_flow(Flow(flows('WE',i,j),beginWE,endWE,vehsPerHour=probWE,route=routeid,departSpeed='max',tpe='typedist1'))

                    routeid = routs('EW',i)
                    self.add_flow(Flow(flows('EW',i,j),beginEW,endEW,vehsPerHour=probEW,route=routeid,departSpeed='max',tpe='typedist1'))


                # Rutas NW y SE
                k=0
                for i in range(1,self.sg.cols-1):
                    for m in range(1,self.sg.rows-1):
                        routeid = routs('NW',k) # Hay que reducir la probabilidad de que los coches giren
                        # O incluso, ser un parámetro de diseño.
                        self.add_flow(Flow(flows('NW_'+str(i),m,j),
                                           beginNW,endNW,
                                           vehsPerHour=probNW/((self.sg.cols-2)*(self.sg.rows-2)),
                                           route=routeid,departSpeed='max',
                                           tpe='typedist1'))
                        routeid = routs('SE',k) # Hay que reducir la probabilidad de que los coches giren
                        # O incluso, ser un parámetro de diseño.
                        self.add_flow(Flow(flows('SE_'+str(i),m,j),
                                           beginSE,endSE,
                                           vehsPerHour=probSE/((self.sg.cols-2)*(self.sg.rows-2)),
                                           route=routeid,departSpeed='max',
                                           tpe='typedist1'))
                        k+=1
                # Rutas WS y EN
                k=0
                for i in range(1,self.sg.cols-1):
                    for m in range(1,self.sg.rows-1):
                        routeid = routs('WS',k) # Hay que reducir la probabilidad de que los coches giren
                        # O incluso, ser un parámetro de diseño.
                        self.add_flow(Flow(flows('WS_'+str(i),m,j),
                                           beginWS,endWS,
                                           vehsPerHour=probWS/((self.sg.rows-2)*(self.sg.cols-2)),
                                           route=routeid,departSpeed='max',
                                           tpe='typedist1'))

                        routeid = routs('EN',k) # Hay que reducir la probabilidad de que los coches giren
                        # O incluso, ser un parámetro de diseño.
                        self.add_flow(Flow(flows('EN_'+str(i),m,j),
                                           beginEN,endEN,
                                           vehsPerHour=probEN/((self.sg.rows-2)*(self.sg.cols-2)),
                                           route=routeid,departSpeed='max',
                                           tpe='typedist1'))
                        k+=1


