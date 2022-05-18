#!/usr/bin/env python
"""

"""

import subprocess
import sys
import platform
import traceback
import pickle

import pandas as pd
import numpy as np

import traci
import traci.constants as tc

from IntersectionManager import IntersectionManager
from sumolib import checkBinary  # noqa
from collections import defaultdict, namedtuple
from xml.dom import minidom

__author__ = "Bryan Alexis Freire Viteri. Mod by Antonio Guillen Perez"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com antonio.guillen@edu.upct.es"

class SumoSimulation(object):
    def __init__(self,
                 sg=None,
                 ss=None,
                 sa=None,
                 gui=False,
                 sm='sumo',
                 smg='sumo-gui',
                 nc='netconvert',
                 traci_folder='D:\Sumo\tools',
                 lanes=2,
                 ncols=4,
                 nrows=1,
                 leng=300,
                 timer=0,
                 nport=65000,
                 seed=0,
                 i_ep=0,
                 flow=100,
                 simulation_duration=5*60):
        self.sg = sg
        self.ss = ss
        self.sa = sa

        self.sgC = True
        self.ssC = True
        self.saC = True

        self.nc = nc
        plt = platform.system()
        if plt == "Windows":
            print("Your system is Windows")
            self.ng = checkBinary('netgenerate.exe')
            self.smg = checkBinary('sumo-gui.exe')
            self.sm = checkBinary('sumo.exe')

        else:
            print("Your system is Linux")
            self.ng = checkBinary('netgenerate')
            self.smg = checkBinary('sumo-gui')
            self.sm = checkBinary('sumo')

        # sys.path.append(traci_folder)
        import traci

        self._traci = traci
        self.lanes = lanes
        self.ncols = ncols
        self.nrows = nrows
        self.leng = leng
        self.timer = timer

        self.gui = gui
        self.process = None
        self.port = nport
        self.seed = seed
        self.flow = flow

        self.im = IntersectionManager('A0', 'pppqw', seed = self.seed)
        self.running_reward = -1000
        self.rewards = []
        self.training_records = []
        self.i_ep = i_ep

        self.tripinfo_file = 'results/tripinfo_'
        self.simulation_duration = simulation_duration

    @property
    def traci(self):
        return self._traci

    @property
    def time(self):
        return self._time

    def change_graph(self,sg):
        self.sg = sg
        self.sgC = True
        self.saC = True

    def change_scenario(self,ss):
        self.ss = ss
        self.ssC = True
        self.saC = True

    def change_algorithm(self,sa):
        self.sa = sa
        self.saC = True

    def run_simulation(self):
        if not (self.sg and self.ss and self.sa):
            raise ValueError('Graph,Scenario and Algorithm are needed')

        self.init_simulation()
        if self.saC:
            # self.sa.prepare_algorithm(self)
            self.saC = False
        # else:
            # self.sa.reset_algorithm(self)

        TrainingRecord = namedtuple('TrainingRecord', ['ep', 'reward'])

        self.reset_statistics()
        states = []
        actions = []
        self._traci.simulationStep()

        # Obtain state
        states.append(self.im.first_state())
        self.im.control_tls()
        self.im.reset_values()
        self.im.score = 0
        collisions = []

        while self._traci.simulation.getMinExpectedNumber() > 0:
            if self._traci.simulation.getTime() % 25 == 0:
                print(f'Simulation: {self.i_ep}; Time: {self._traci.simulation.getTime()}')

            # Select action based on state
            actions.append(self.im.select_actions())

            # Perform actions based on state
            self.im.perform_actions()
            self._traci.simulationStep()

            states.append(self.im.update_state())
            collisions.append(self.im.obtain_collisions())
            r = self.im.obtain_reward()
            if r:
                self.rewards.append([self._traci.simulation.getTime(), r])
            # states.append(self.im.update_state())
            self.im.swap_states()

#            print(self._time)
            self._time = self._time + traci.simulation.getDeltaT()
            # a.append(self.obtain_loss_time())

            if self._traci.simulation.getTime() > 50000:
                self._traci.simulation.clearPending()

        score = self.im.score
        self.running_reward = self.running_reward * 0.9 + score * 0.1
        self.training_records.append(TrainingRecord(self.i_ep, self.running_reward))

        try:
            if self.i_ep % 20 == 0:
                # self.im.agent.save_checkpoint(str(self.flow))
                self.im.agent.save_weights()

            # with open('log/ppo_training_records.pkl', 'wb') as f:
                    # pickle.dump(self.training_records, f)

        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())

        finally:
            self.close_simulation()
            return [self.rewards, TrainingRecord(self.i_ep, self.running_reward), states, actions, collisions]

    def run_test_simulation(self):
        self.init_simulation()
        self._traci.simulationStep()
        self.im.update_state()
        self.im.control_tls()
        self.im.score = 0

        try:
            self.im.agent.load_param()
            while self._traci.simulation.getMinExpectedNumber() > 0:
                if self._traci.simulation.getTime() % 30 == 0:
                    print(f'Simulation: {self.i_ep}; Time: {self._traci.simulation.getTime()}')
                self.im.select_actions()
                self.im.perform_actions()
                self._traci.simulationStep()
                self.im.update_state()

                if self._traci.simulation.getTime() > 50000:
                    self._traci.simulation.clearPending()

        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())

        finally:
            self.close_simulation()



    def obtain_loss_time(self):
        try:
            junctionID = 'A0'
            dist = 200.0

            # https://sumo.dlr.de/pydoc/traci.constants.html
            traci.junction.subscribeContext(junctionID, tc.CMD_GET_VEHICLE_VARIABLE, dist, [tc.VAR_SPEED, tc.VAR_ALLOWED_SPEED, tc.VAR_ROAD_ID, tc.VAR_DISTANCE])

            # https://sumo.dlr.de/daily/pydoc/traci._vehicle.html
            # traci.vehicle.subscribeContext(str(veh_id), tc.CMD_GET_VEHICLE_VARIABLE, 0.0, [tc.VAR_SPEED])
            # traci.junction.addSubscriptionFilterLanes([-1,0,1], noOpposite=True, downstreamDist=100, upstreamDist=50)

            # traci.vehicle.addSubscriptionFilterDownstreamDistance(50.0)
            # traci.vehicle.addSubscriptionFilterLanes(lanes, noOpposite=True, downstreamDist=100, upstreamDist=50)

            # Eliminar los vehículos que se alejan de la intersección, en función de su ruta?

            stepLength = traci.simulation.getDeltaT()
            scResults = traci.junction.getContextSubscriptionResults(junctionID)
            halting = 0

            a = tc.VAR_SPEED # Current speed
            b = tc.VAR_ALLOWED_SPEED # Maximum speed
            timeLoss = 0
            print(f'\n Found {len(scResults)} vehicles before filtering')
            print(f'\t Keys: {scResults.keys()}')

            scResults = self._remove_moving_away(junctionID, scResults) # If vehicles are approaching the intersection

            if scResults:
                print(f' After filtering {len(scResults)} vehicles')
                print(f'\t Keys: {scResults.keys()}')
                print(f'{scResults}')
                relSpeeds = [d[a] / d[b] for d in scResults.values()]
                # compute values corresponding to summary-output
                running = len(relSpeeds)
                halting = len([1 for d in scResults.values() if d[tc.VAR_SPEED] < 0.1]) # number of vehicles waiting
                meanSpeedRelative = np.mean(relSpeeds)
                # Due to that the vehicles are under the maximum speed,
                # the loss time in the last simulationStep is:
                timeLoss = (1 - meanSpeedRelative) * running * stepLength

            # print(f'Simulation time: {traci.simulation.getTime()}; Timeloss: {timeLoss}; Halting: {halting}')
            return timeLoss
        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())

    def _remove_moving_away(self, j, v):
        return {key:val for key, val in v.items() if (val[tc.VAR_ROAD_ID][-2:] == j) or (val[tc.VAR_ROAD_ID][:1+len(j)] == f':{j}')} # If vehicles are approaching the intersection

#
    def getTripinfo(self):
        total_trips = 0
        total_timeloss = 0
        total_duration = 0
        total_wtime = 0

        average_relative_timeloss = 0
        average_duration = 0
        average_timeloss = 0
        average_wtime = 0
        max_timeloss = 0

        try:
            with open('results/tripinfo_.xml') as f:
                content = f.readlines()
            for line in content:
                if "<tripinfo id=" in line:
                    total_trips += 1
                    xml_string = "<tripinfos>"
                    xml_string = "".join((xml_string, line))
                    xml_string = "/n".join((xml_string, "</tripinfos>"))
                    xml_string = xml_string.replace('>\n', '/>\n')
                    open_data = minidom.parseString(xml_string)
                    intervals_open = open_data.getElementsByTagName('tripinfo')
                    timeloss = float(intervals_open[0].getAttribute('timeLoss'))
                    duration = float(intervals_open[0].getAttribute('duration'))
                    wtime = float(intervals_open[0].getAttribute('waitingTime'))
                    max_timeloss = np.maximum(max_timeloss, timeloss)

                    total_timeloss += timeloss
                    total_duration += duration
                    total_wtime += wtime

                    relative_timeloss = timeloss / duration
                    average_relative_timeloss = ((average_relative_timeloss * (
                            total_trips - 1) + relative_timeloss) / total_trips)

            average_duration = total_duration / total_trips
            average_timeloss = total_timeloss / total_trips
            average_wtime = total_wtime / total_trips

        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())

        finally:
            return [total_trips, total_timeloss, total_duration, total_wtime,
                    average_relative_timeloss, average_duration, average_wtime,
                    average_timeloss, max_timeloss]


        return self.co2em
    def reset_statistics(self):
        self._time = 0
        self.cars = {}
        self.wt = {}
        self.co2em = {}
        for edge in self.sg.iter_edges():
            self.co2em[edge.id] = [0,0,0,0,0,0,0]
        self.num_veh = 0
        self.num_ped = 0
        self.tov = []
        self.df = np.empty([0,6])
        self.y = []
    def _get_statistics(self):



        for edge in self.sg.iter_edges():
#        if edge.id in self.co2em:
            self.co2em[edge.id][0] += self._traci.edge.getCO2Emission(edge.id)
#            self.co2em[edge.id][1] += self._traci.edge.getCOEmission(edge.id)
#            self.co2em[edge.id][2] += self._traci.edge.getHCEmission(edge.id)
#            self.co2em[edge.id][3] += self._traci.edge.getPMxEmission(edge.id)
#            self.co2em[edge.id][4] += self._traci.edge.getNOxEmission(edge.id)
#            self.co2em[edge.id][5] += self._traci.edge.getFuelConsumption(edge.id)
#            self.co2em[edge.id][6] += self._traci.edge.getNoiseEmission(edge.id)

#        else:
#            self.co2em[edge.id] = self._traci.edge.getCO2Emission(edge.id)

#        # Estados de los semáforos en cada instante
#        tlsID = self._traci.trafficlight.getIDList()
#        y_NS = self._traci.trafficlight.getRedYellowGreenState(tlsID[0])
#        if y_NS[1] == 'G':
#            self.y.append(1)
#        else:
#            self.y.append(0)


    def init_simulation(self):

        # *Deprecated* =======================================================
        # self.__create_files()
        # subprocess.call([self.nc,
        #                   '-n=sumodata/nodes_'+str(self.port)+'.xml',
        #                   '-e=sumodata/edges_'+str(self.port)+'.xml',
        #                   '-o=sumodata/net_'+str(self.port)+'.xml',
        #                   '-L='+str(self.lanes),
        #                   '--no-left-connections=True',
        #                   '--no-turnarounds=True',
        #                   '--walkingareas=True',
        #                   '--offset.disable-normalization=True',
        #                   '--no-internal-links=False',
        #                   '--junctions.corner-detail=5',
        #                   '--junctions.limit-turn-speed=5.5',
        #                   '--rectangular-lane-cut=False',
        #                   '--sidewalks.guess=True',
        #                   '--crossings.guess=True',
        #                   '--default.junctions.radius=10',
        #                   '--default.junctions.keep-clear=True',
        #                   '--default.sidewalk-width=6',
        #                   '--default.crossing-width=6'
        #                   ])
        # ====================================================================

        # print('Creating network:')
        command = [self.ng, '-g',
              '--grid.x-number', str(self.ncols),
              '--grid.y-number', str(self.nrows),
              '--grid.length', str(self.leng),
              '--grid.attach-length', str(self.leng),
              '-L', str(self.lanes),
              '--default.sidewalk-width', '3.0',
              '--sidewalks.guess', 'true',
              '--crossings.guess', 'true',
              '--walkingareas', 'true',
              '--bikelanes.guess', 'true',
              '--verbose', 'true',
              '--tls.guess', 'true',
              '--seed', str(self.seed),
              '-o', 'sumodata/net_'+ str(self.nrows)+'_'+str(self.ncols)+'.xml']

        # p = subprocess.run(command, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        # print(p.stdout)
        # print('Done!')
        self.create_route_files_v2()
        # =============================================================================
        #         generate the pedestrians for this simulation

        #         subprocess.call([self.nc,'-n=sumodata/nodes.xml','-e=sumodata/edges.xml','-o=sumodata/net.xml','--no-left-connections=True','--no-turnarounds.except-deadend=True'])
        # =============================================================================
        # -L <int>
        #         The default number of lanes in an edge; default: 1

        # --no-turnarounds.except-deadend <BOOL>
        #       Disables building turnarounds except at dead end junctions; default: false
        #         Hay problemas con los semáforos cuando introducimos este parámetro

        # --no-left-connections <BOOL>
        #       Disables building connections to left; default: false
        #         Hay problemas con los semáforos cuando introducimos este parámetro
        # =============================================================================
        #         import time
        #         time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        if not self.gui:
            self.process = subprocess.Popen([self.sm,
                                             '-n=sumodata/net_'+ str(self.nrows)+'_'+str(self.ncols)+'.xml',
                                              '-r=sumodata/veh_routes_'+str(self.nrows)+'_'+str(self.ncols)+'.xml',
                                              '-X=never',
                                              '--seed=' + str(self.seed),
                                              '--junction-taz',
                                              '--step-length=0.25',
                                              '--remote-port='+str(self.port),
                                              '--tripinfo-output=results/tripinfo_.xml',
                                             '--tripinfo-output.write-unfinished=True',
                                             '--device.emissions.probability=1',
                                             '--waiting-time-memory=1000',
                                             '--collision.check-junctions=true',
                                             '--collision.action=warn'])
#    '--emission-output=results/emission_'+str(self.timer)+'.xml'
        else:
            # ' '.join([self.smg,
            #           '-n=sumodata/net.xml',
            #           '-r=sumodata/routes.xml',
            # '-a=sumodata/peds_cycl_routes_'+str(self.nrows)+'_'+str(self.ncols)+'.xml, sumodata/induction_loops.add.xml',

            #           '--random',
            #           '--remote-port='+str(self.port),
            #           '--tripinfo-output=results/tripinfo.xml'])
            self.process = subprocess.Popen([self.smg,
                                              '-n=sumodata/net_'+ str(self.nrows)+'_'+str(self.ncols)+'.xml',
                                              '-r=sumodata/veh_routes_'+str(self.nrows)+'_'+str(self.ncols)+'.xml',
                                              '-X=never',
                                              '--seed=' + str(self.seed),
                                              '--junction-taz',
                                              '--step-length=0.25',
                                              '--remote-port='+str(self.port),
                                              '--tripinfo-output=results/tripinfo_.xml',
                                             '--tripinfo-output.write-unfinished=True',
                                             '--device.emissions.probability=1',
                                             '--waiting-time-memory=1000',
                                             '--collision.check-junctions=true',
                                             '--collision.action=warn'])

            # self.process = subprocess.Popen([self.smg,
            #                                  '-n=sumodata/net_'+str(self.port)+'.xml',
            #                                   '-r=sumodata/trips.trips.xml',
            #                                   '-a=sumodata/add.xml',
            #                                   '-X=never',
            #                                   '--remote-port='+str(self.port)])

        self._traci.init(self.port)

    def close_simulation(self):
        """Close the simulation."""
        self._traci.close()
        self.process.terminate()
        self.process.kill()

    def create_route_files_v2(self):
        # print('Creating routes')
        self.process = subprocess.Popen([self.sm,
                                 '-n=sumodata/net_'+ str(self.nrows)+'_'+str(self.ncols)+'.xml',
                                 '--remote-port='+str(9999),
                                 ])
        self._traci.init(9999)

        junctions = traci.junction.getIDList()
        borders = []
        for j in junctions:
            if str(j).startswith(('top', 'bottom', 'left', 'right')):
                borders.append(j)

        self.__create_vehicles_route_file(borders)
        # edges = traci.edge.getIDList()
        # borders = []
        # for e in edges:
        #     if not str(e).startswith(':'):
        #         borders.append(e)
        # self.__create_peds_route_file()
        self._traci.close()
        # print('Routes created')

    def __create_vehicles_route_file(self, borders):
        with open('sumodata/veh_routes_' + str(self.nrows) + '_' +\
                  str(self.ncols) + '.xml', 'w') as r:
            r.write('<routes>\n')
            for ct in self.ss.iter_car_types():
                r.write(repr(ct))

            # dic = {'N': 'top',
            #        'S': 'bottom',
            #        'E': 'right',
            #        'W': 'left'}

            # for fl in self.ss.iter_flows():
            #     if fl['type'] == 'typedist1': # Solo vehículos, los peatones van aparte
            #         ide = fl.id
            #         o = dic[ide[4]]
            #         d = dic[ide[5]]
            #         fl['route'] = None
            #         fl['fromJunction'] = o
            #         fl['toJunction'] = d
            #         r.write(repr(fl))

            duration = self.simulation_duration #5*60
            # dens = [200,300,400,500,600,700,800]

            # ================================================================
            # probability:float([0,1]). Probability for emitting a vehicle each
            # second (not together with personsPerHour or period),
            # When this attribute is used, a vehicle will be emitted randomly
            # with the given probability each second. This results in a
            # binomially distributed flow (which approximates a Poisson
            # Distribution for small probabilities).
            # ================================================================
            # Si prob=1 entonces el flujo que se está simulando es 3600veh/h

            dens = self.flow  # veh/h/route

            if dens > 3600:
                print('WARNING: la densidad no puede ser mayor de 3600, set:3600')
                dens = 3600

            prob = dens/3600  # (veh/h)/(veh/h) se queda un ratio adimensional
            for o in borders:
                for d in borders:
                    if not o == d:
                        fid = o+'_'+d
                        r.write('\t<flow id="' + fid +
                                '" begin="' + str(0) +
                                '" end="' + str(duration) +
                                '" probability="' + str(prob) +
                                '" type="car_diesel" departSpeed="max"' +
                                ' fromJunction="' + o +
                                '" toJunction="' + d + '" />\n')
            r.write('</routes>')

    def __create_peds_route_file(self):
        command = ['api_sumo/randomTrips.py',
                   '-n', 'sumodata/net_'+ str(self.nrows)+'_'+str(self.ncols)+'.xml',
                   '-o', 'sumodata/peds_cycl_routes_' + str(self.nrows) +
                         '_' + str(self.ncols) + '.xml',
                   '--persontrips',
                   '--trip-attributes', 'modes="bicycle"',
                   '-e', '1',
                   '--seed', str(self.seed),
                   '--verbose', 'True']

        process = subprocess.run(command, check=True, stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output = process.stdout
        print(output)


