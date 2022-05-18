#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 12:31:55 2020

@author: antonio
"""
import os
import traci
import traceback
import torch
import math
import random
import threading

import numpy as np
import traci.constants as tc

from functools import partial
from collections import defaultdict, namedtuple
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import concurrent.futures

from TD3PER.td3_agent import Agent


class IntersectionManager:
    """Intersection Manager for each intersection that regulates
    the vehicles in each intersection.
    """

    def __init__(self, inter_id, inductionloops, seed, train=False):
        self._id = inter_id
        self._traci = traci

        self._num_queues = 4

        self._in_lanes = set(['Ai0', 'Ai1', 'Ai2', 'Ai3', 'Ai4', 'Ai5', 'Ai6', 'Ai7'])
        self._out_lanes = set(['Ao0', 'Ao1', 'Ao2', 'Ao3', 'Ao4', 'Ao5', 'Ao6', 'Ao7'])

        # self._id_veh_inter = set() # The params of vehicles inside the intersection

        self._max_dist_detect = 50
        self._queue_width = 12
        self._scaler = 1
        self._input_variables = 16 # speed, acceleration, etc
        self.max_vehicles = 32

        self.state = defaultdict(partial(np.ndarray, 0))
        self.new_state = defaultdict(partial(np.ndarray, 0))

        self.raw_data = defaultdict(list)
        self.new_raw_data = defaultdict(list)

        self.actions = defaultdict(list)
        self.rewards = defaultdict(list)
        self.reward = -999
        self.score = 0
        self.vehicles_removed = set()
        self.vehicles_first_time_outside = set()

        self._activeRequest = False
        self._greenTimeSoFar = 0
        self._greenTimer = 60
        self._tlspeds = False
        self._WALKINGAREAS = [':A0_w0', ':A0_w1', ':A0_w2', ':A0_w3'] # N, E, S, W
        self._CROSSINGS = [':A0_c0', ':A0_c1', ':A0_c2', ':A0_c3'] # N, E, S, W
            # check both sides of the crossing

        # PPO variables
        self._SEED = seed
        self._GAMMA = 0.9
        self._LOG_EACH = 1

        self._TrainingRecord = namedtuple('TrainingRecord', ['ep', 'reward'])
        self._Transition = namedtuple('Transition', ['s', 'a', 'a_log_p', 'r', 's_'])
        self._training_records = []
        self._running_reward = -1000

        torch.manual_seed(self._SEED)
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # PPO Agent
        # self.agent = Agent(self._device)
        # Define and build DDPG agent
        hidden_size = tuple([2048, 256, 256, 128])

        gamma = 0.9
        tau = 0.01
        self.extra_variables = 6 # Timer (1), quarter (4), and priority signal (1)
        self.observation_space = self._input_variables * self.max_vehicles + self.extra_variables
        action_space = 1
        checkpoint_dir = 'ckpt/'
        self.batch_size = 128

        self.test = train
        self.workers = os.cpu_count() - 1
        self.rw_data = defaultdict(list)
        self.already_update = False
        self.cycle = 60

# =============================================================================
#         # DDPG
# =============================================================================
        # self.agent = DDPG(gamma,
        #               tau,
        #               hidden_size,
        #               observation_space,
        #               action_space,
        #               checkpoint_dir=checkpoint_dir
        #               )

        # # Initialize replay memory
        # replay_size = 4096*16
        # self.memory_crash = ReplayMemory(int(replay_size))
        # self.memory_normal = ReplayMemory(int(replay_size))
        # self.action_noise = 0.5
        # Initialize OU-Noise
        # nb_actions = 1
        # noise_stddev = 5
        # self.ou_noise = OrnsteinUhlenbeckActionNoise(mu=np.zeros(nb_actions),
        #                                         sigma=float(noise_stddev) * np.ones(nb_actions))

# =============================================================================
#         # TD3
# =============================================================================
        # state_dim = observation_space
        # action_dim = action_space
        # max_action = 1
        # min_action = -1
        # discount = 0.99
        # tau = 0.005

        # self.agent = TD3.TD3(state_dim, action_dim, max_action, min_action)
        # self.replay_buffer = utils_TD3.ReplayBuffer(state_dim, action_dim)

        # self._exit = False

# =============================================================================
#         # TD3-PER
# =============================================================================
        state_size = self.observation_space
        action_size = action_space
        self.agent = Agent(state_size, action_size)
        self.LEARN_EVERY = 60
        self.epoch = 0

        # self._score = 0

    def reset_values(self):
        self.rewards = defaultdict(list)
        self.vehicles_removed = set()
        self.actions = defaultdict(list)
        self.vehicles_first_time_outside = set()
        self._exit = False
        self.already_update = False

    def first_state(self):
        # self.state = self.new_state.copy()
        # self.raw_data = self.new_raw_data
        self.raw_data = self.obtain_state()
        self.state = self._update_state(self.raw_data)
        return self.raw_data

    def update_state(self):
        self.new_raw_data = self.obtain_state()
        self.new_state = self._update_state(self.new_raw_data)
        return self.new_raw_data

    def swap_states(self):
        if self.new_raw_data:
            self.raw_data = self.new_raw_data.copy()
            self.state = self.new_state.copy()
        else:
            self.raw_data = defaultdict(list)
            self.state = defaultdict(partial(np.ndarray, 0))

    def _update_state_mp(self, data):
        state = defaultdict(partial(np.ndarray, 0))
        # print('Data: ', data)
        veh, val = data
        # print(f'veh: {veh}; \n val: {val}')
        try:
            state = self.set_vehicle_highlight(state, veh, val)
            state = self.set_other_vehicles(state, self.new_raw_data, veh)
            state = self.zero_padding(state, veh)
        except Exception as e:
            print(f"_update_state_mp throws {e}")
            print(traceback.format_exc())
        return state

    def _update_state(self, rw_data):
        if rw_data and not rw_data == [-1]:
            # print('There are something')
            # These might be a defaultdict
            state = defaultdict(partial(np.ndarray, 0))
            # with ThreadPoolExecutor(max_workers=self.workers) as executor:
            #     results = executor.map(self._update_state_mp, rw_data.items())
            #     for k in results:
            #         key = list(k.keys())[0]
            #         state[key] = k[key]

            for k, v in rw_data.items():
                # Highlight the vehicle selected
                state = self.set_vehicle_highlight(state, k, v)
                state = self.set_other_vehicles(state, rw_data, k)
                state = self.zero_padding(state, k)

            return state
        else:
            state = defaultdict(partial(np.ndarray, 0))

    def set_vehicle_highlight(self, state, k, v):
        # state[k] = list(np.array(v[:2])/100) + [queue/3] + list(np.array(v[2:6])/np.array([13.89, 3, 2, 1])) + list(np.array(v[9:])/np.array([5, 5, 360]))
        # queue = self.transform_queue(queue)
        # state[k] = list(np.array(v[:2])) + queue + list(np.array(v[2:]))
        ctime = self._traci.simulation.getTime()
        timer = ctime - (ctime // self.cycle) * self.cycle
        state[k] = [timer/(self.cycle-1)]
        state[k] += self._get_quarter(timer)
        state[k] += [self._get_priority(v, timer)]
        state[k] += v[:]

        # state[k] += [self.is_inside(k, self._id)]
        return state

    def _get_quarter(self, timer):
        quarter = self.cycle//4

        if timer < quarter:
            return [1.0, 0.0, 0.0, 0.0]
        elif quarter <= timer < quarter*2:
            return [0.0, 1.0, 0.0, 0.0]
        elif quarter*2 <= timer < quarter*3:
            return [0.0, 0.0, 1.0, 0.0]
        elif quarter*3 <= timer < quarter*4:
            return [0.0, 0.0, 0.0, 1.0]
        else:
            return [0.0, 0.0, 0.0, 0.0]

    def _get_priority(self, v, timer):
        """
        Return -1 or +1 depends on the queue and the timer
        The first quarter is for N queue
        the second quarter is for S queue
        third quarter is for E queue
        fourth quarter is for W queue

        Parameters
        ----------
        v : custom variable
            the important is the [-5:-1] digits that includes the queue
            [N, S, E, W]

        timer : int
            counter that goes from 0 to _cycle_var.

        Returns
        -------
        veh : int
            +1 if the vehicle has priority.
            -1 if the vehicle hasn't priority
        """
        queue = np.where(np.array(v[-5:-1]) == 1.0)[0][0]

        quarter = self.cycle//4

        if queue == 0: # N queue
            if timer < quarter:
                return 1.0
        elif queue == 1: # S queue
            if quarter <= timer < quarter*2:
                return 1.0
        elif queue == 2: # E queue
            if quarter*2 <= timer < quarter*3:
                return 1.0
        elif queue == 3: # W queue
            if quarter*3 <= timer < quarter*4:
                return 1.0
        else:
            return -1.0
        return -1.0

    def set_other_vehicles(self, state, rw_data, k):
        i = self._input_variables + self.extra_variables

        for k2, v2 in rw_data.items():
            if not k == k2:
                (x,y) = v2[:2]
                # rel_x = np.floor(x*self._scaler)
                # rel_y = np.floor(y*self._scaler)
                # queue = self.obtain_queue(x, y)
                # queue = self.transform_queue(queue)

                # state[k] += list(np.array(v2[:2])) + queue + list(np.array(v2[2:]))
                state[k] += v2[:-1]

                state[k] += [self.dist_to_veh(k, x, y, rw_data)]
                i += self._input_variables

                if i >= self.observation_space - 1:
                    break
        return state

    def zero_padding(self, state, k):
        l = len(state[k])
        pad = self.observation_space - l
        # print(f'Padding with: {pad/self._input_variables}')
        state[k] += list(np.zeros(pad))
        return state

    def is_inside(self, veh, int_id):
        r = self._traci.vehicle.getRoadID(veh)
        if r[:1+len(int_id)] == f':{int_id}': # Dentro de la interseccion, para penalizar más que estén dentro
            return 1.0
        else:
            return 0.0

    def dist_to_veh(self, veh, x2, y2, rw_data):
        [x1, y1] = rw_data[veh][:2]
        dist = math.hypot((x2 - x1), (y2 - y1))/(2*self._max_dist_detect)
        dist = self.transform_dist(dist)
        return dist
        # return dist/(2*self._max_dist_detect)*2-1

    def transform_actions(self, actions):
        actions = (actions + 1) / 2 # [0,1]
        actions = actions*13 # [0,13]
        actions = actions + 0.5 # [0.5, 13.5]
        return actions

    def select_actions_mp(self, veh):
        # print(f'Executing {veh} Task on thread: {threading.current_thread().name}')
        s = torch.Tensor(self.state[veh]).to(self._device)

        try:
            # action = self.agent.calc_action(state=s, action_noise=self.ou_noise) #calc_action(s)
            if self.agent.memory.is_full() or self.test:
                action = self.agent.select_action(state=s) #calc_action(s)
            # Filling the replay buffer with random actions
            else:
                print(f'Len buff: {len(self.agent.memory)}')
                action = torch.Tensor([[np.random.uniform(-1, 1)]])
                # action = self.agent.select_action(state=s) #calc_action(s)
        except Exception as e:
            print("Error on select action: " + str(e))
            print(traceback.format_exc())
            print('Selecting 0.0 action')
            action = 0
        self.actions[veh] = action#.cpu()

    def select_actions(self):
        if self.raw_data and not self.raw_data == [-1]:
            # print('There are something')
            # with ThreadPoolExecutor(max_workers=3) as executor:
                # future = executor.map(self.select_actions_mp, self.raw_data)
                # print(results.result())
            # keys = self.raw_data.keys()
            # with ThreadPoolExecutor(max_workers=self.workers) as executor:
                # results = executor.map(self.select_actions_mp, keys)

            for k, v in self.raw_data.items():
                s = torch.Tensor(self.state[k]).to(self._device)
                try:
                    # action = self.agent.calc_action(state=s, action_noise=self.ou_noise) #calc_action(s)
                    if self.agent.memory.is_full() or self.test:
                        action = self.agent.select_action(state=s) #calc_action(s)


                    # Filling the replay buffer with random actions
                    else:
                        # print(f'Len buff: {len(self.agent.memory)}')
                        # action = torch.Tensor([[np.random.uniform(-1, 1)]])
                        action = self.agent.select_action(state=s) #calc_action(s)

                    # action = traci.vehicle.getSpeedWithoutTraCI(k)
                    # action = self.transform_actions(action)
                    # action = torch.Tensor([(action/13.89-0.5)*2])
                except Exception as e:
                    print("Error on select action: " + str(e))
                    print(traceback.format_exc())
                    print('Selecting 0.0 action')
                    action = 0
                # I delete the actions_dict before next+1 perform_action() to avoid perform actions twice
                self.actions[k] = action#.cpu()
        return self.actions

    def perform_actions(self):
        if self.actions:
            for k, v in self.actions.items():
                try:
                    # traci.vehicle.setSpeedMode(k, 31)
                    v = (v + 1)/2*13.39 + 0.5
                    traci.vehicle.slowDown(k, v, traci.simulation.getDeltaT())
                except Exception as e:
                    print(f"Error while perform action")
                    print(e)
                # print(f'Vehicle: {k}; Action: {v[0]}')


    def obtain_exit(self):
        return self._exit

    def obtain_collisions(self):
        # Obtain the number of vehicles involved in collision:
        collision_veh = set(traci.simulation.getCollidingVehiclesIDList())
        if collision_veh:
            print('WARNING!!!! --- collided vehicles on the road')
            print(collision_veh)
            self._exit = True

            for veh in collision_veh:
                self.rewards[veh] += -10
                # traci.vehicle.setSpeed(veh, 0.01) # Le pongo una velocidad baja para que suba el tiempo medio de espera y joda al sistema
                # self.new_state[veh][-1] = 1
                try:
                    self.new_state[veh][-1] = 1
                    self._exit = True

                except Exception as e:
                    print(f"Error while obtain collisions")
                    print(traceback.format_exc())
                    self._exit = True


                self.vehicles_removed.add(veh)
            return len(collision_veh)
        else:
            return 0

    def obtain_reward(self):
        if self.raw_data and not self.raw_data == [-1]:
            # Obtain reward:
            # rel_speed = []
            w1 = -0.05
            w2 = -0.075
            w3 = -0.075
			
            stepLength = traci.simulation.getDeltaT()
            for k, v in self.actions.items():
                try:
                    # speed = traci.vehicle.getSpeed(k)
                    # max_speed = traci.vehicle.getAllowedSpeed(k)
                    # rel_speed.append(speed/max_speed)
                    # self.rewards[k] = speed/max_speed # ratio between current speed and max_speed
                    # low_speed = 1 + np.abs(max_speed - speed) # Penalizamos las velocidades bajas
                    # speed_dev = 1 #+ np.abs(speed - self.actions[k][0]) # Penalizo las acciones cuando intenta ir rápido, pero va lento por congestión

                    # r = traci.vehicle.getRoadID(k)
                    # if r[-2:] == self._id: #  Aproximandose a la interseccion:
                        # factor = 1
                    # elif r[:1+len(self._id)] == f':{self._id}': # Dentro de la interseccion, para penalizar más que estén dentro
                        # factor = 2
                    # else:
                        # factor = 1

                    # speed_notraci = traci.vehicle.getSpeedWithoutTraCI(k)
                    # v = (v + 1)/2*13.39 + 0.5
                    # rew = stepLength + np.abs(speed_notraci - v)

                    speed = traci.vehicle.getSpeed(k)
                    max_speed = traci.vehicle.getAllowedSpeed(k)
                    delay = 1 - speed/max_speed
                    wt = self._traci.vehicle.getWaitingTime(k)
                    acc_wt = self._traci.vehicle.getAccumulatedWaitingTime(k)

                    rew = w1*delay + w2*wt + w3*acc_wt
                    if k in self.rewards:
                        self.rewards[k] += rew #-stepLength #-(rew * low_speed * speed_dev * factor) #-stepLength * low_speed * speed_dev * factor #-stepLength self.rewards[k]*1
                    else:
                        self.rewards[k] = rew #-stepLength #-(rew * low_speed * speed_dev * factor)#-stepLength * low_speed * speed_dev * factor #-stepLength

                    # print(f'{k}; A: {v[0][0]:.2f}; S:{speed:.2f}; Max_s: {max_speed:.2f}; S notraci: {speed_notraci:.2f}; Reward: {self.rewards[k]}')
                    # if self.rewards[k]>0:
                        # print('STOP')
                except Exception as e:
                    print(f"Error while obtain reward, the vehicle doesn't exist111")
                    print(e)
                    print(traceback.format_exc())


            # Obtain the state, action, reward, and new_state for each vehicle
            self.already_update = False
            for k in self.raw_data.items():
                try:
# =============================================================================
#                     s = torch.Tensor([self.state[k[0]]]).to(self._device)
#                     r = torch.Tensor([self.rewards[k[0]]]).to(self._device)
#                     a = torch.Tensor([self.actions[k[0]]]).view((1, -1)).to(self._device)
#                     # done = True if r.cpu()[0] > 0 else False
#                     done = k[0] in self.vehicles_first_time_outside
#
#                     mask = torch.Tensor([done]).to(self._device)
#
#                     new_s = torch.Tensor([self.new_state[k[0]]]).to(self._device)
# =============================================================================
                    s = self.state[k[0]]
                    r = self.rewards[k[0]]
                    a = self.actions[k[0]]
                    done = k[0] in self.vehicles_first_time_outside

                    new_s = self.new_state[k[0]]
                    # desire_shape = self.observation_space

                    # TD3
# =============================================================================
#                     # if (len(s) == desire_shape) and (len(new_s) == desire_shape):
#                         # self.replay_buffer.add(s, a, new_s, r, done)
#
#                     # if len(self.replay_buffer) > self.batch_size:
#                         # self.agent.train(self.replay_buffer, self.batch_size)
# =============================================================================

                    if (len(s) == self.observation_space) and (len(new_s) == self.observation_space):
                        self.agent.step(s, a, r, new_s, done)
                        self.score += r

                        # The replay buffer is full
                        if self.agent.memory.is_full():
                            if self.epoch % self.LEARN_EVERY == 0 and self.already_update == False:
                                print(f'Updating agent bcs: {self.epoch}')
                                self.agent.learn()
                                self.already_update = True

                        # self.epoch += 1

                except Exception as e:
                    # print(f"Error while obtain reward, the vehicle doesn't exist22222")
                    # print(e)
                    # print(traceback.format_exc())
                    print('')
                # else:
                    # print('Look at me!')
                # try:
                # epoch_value_loss = 0
                # epoch_policy_loss = 0
            self.epoch += 1

        self.actions.clear()
        # if self._exit:
            # self._traci.close()

        return self.score


    def get_score(self):
        return self.score

    def control_tls(self):
        # self._greenTimer = self._greenTimer - self._traci.simulation.getDeltaT()
        self._traci.trafficlight.setRedYellowGreenState(
                 self._id, 'rrGGGGGGrrGGGGGGrrGGGGGGrrGGGGGGrrrrGG')

    def step(self):
        self.control_tls() # Control the tls associated in the intersection


    def obtain_position(self, queue, x, y):
        d = self._max_dist_detect #* self._scaler

        if queue == 0:  # N queue
            return [int(d - y), int(np.abs(x))]

        elif queue == 1:  # S queue
            return [int(d + y), int(x)]

        elif queue == 2:  # E queue
            return [int(d - x), int(y)]

        elif queue == 3:  # W queue
            return [int(d + x), int(np.abs(y))]

        else:
            return 0

    def obtain_queue(self, x, y):
        if x >= 0 and y >= 0:  # E wueue
            return 2

        elif x < 0 and y >= 0:  # N queue
            return 0

        elif x >= 0 and y < 0:  # S queue
            return 1

        elif x < 0 and y < 0:  # W queue
            return 3

        else:
            return 4

    def obtain_state(self):

        vehicles = self._obtain_vehicles_in_intersection()
        if not vehicles == -1 and not vehicles == set():
            data = self._obtain_vehicles_params(vehicles)
            return data
        else:
            return defaultdict(list)

    def _obtain_vehicles_in_intersection(self):
        try:
            # https://sumo.dlr.de/pydoc/traci.constants.html
            self._traci.junction.subscribeContext(self._id,
                                                  tc.CMD_GET_VEHICLE_VARIABLE,
                                                  self._max_dist_detect,
                                                  [tc.VAR_ROAD_ID])

            vehicles = traci.junction.getContextSubscriptionResults(self._id)

            if vehicles:
                # print(f'\n Found {len(vehicles)} vehicles before filtering')
                # print(f'\t Keys: {vehicles.keys()}')
                return self._remove_moving_away(self._id, vehicles) # If vehicles are approaching the intersection

            else:
                # print('No vehicles found')
                return -1

        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())
            return 0

    def _remove_moving_away(self, j, v):
        """ Obtain the vehicles that are aproaching the intersection or are inside. """
        # stepLength = traci.simulation.getDeltaT()
        for key, val in v.items():
            if not key in self.vehicles_removed:
                if not (val[tc.VAR_ROAD_ID][-2:] == j) and not (val[tc.VAR_ROAD_ID][:1+len(j)] == f':{j}'):
                    # speed = traci.vehicle.getSpeed(key)
                    # neg_speed = 1 + np.abs(speed - self.actions[key])
                    # traci.vehicle.setSpeedMode(key, 31)
                    self.rewards[key] += 10 #-stepLength
                    self.vehicles_removed.add(key)
            else:
                if not (val[tc.VAR_ROAD_ID][-2:] == j) and not (val[tc.VAR_ROAD_ID][:1+len(j)] == f':{j}'):
                    # speed = traci.vehicle.getSpeed(key)
                    # neg_speed = 1 + np.abs(speed - self.actions[key])
                    self.rewards[key] += 10 #-stepLength

        vehicles = set()
        for veh, val in v.items():
            if (val[tc.VAR_ROAD_ID][-2:] == j): # If vehicles are approaching the intersection
                vehicles.add(veh)
            elif (val[tc.VAR_ROAD_ID][:1+len(j)] == f':{j}'): # If vehicles are inside the intersection
                vehicles.add(veh)
            elif not veh in self.vehicles_first_time_outside: # If vehicles is just leaving the intersection
                vehicles.add(veh)
                self.vehicles_first_time_outside.add(veh)

        return vehicles

    def _obtain_vehicles_params(self, vehicles):
        """
        Parameters
        ----------
        vehicles : TYPE
            DESCRIPTION.

        Returns
        -------
        updated data.

        """
        data = defaultdict(list)

        for veh in vehicles:
            new_params = self._obtain_veh_params(veh)
            data[veh] = new_params

        return data


    def _obtain_veh_params(self, veh):
        """
        Parameters
        ----------
        vehicle : str
            the identifier of the vehicle to obtain it's params.

        Returns
        -------
        params : list(params)
            multiple params.

        """
        self._position = self._traci.junction.getPosition(self._id)

        (x, y) = self._traci.vehicle.getPosition(veh)
        center_x = self._position[0]  # - self._max_dist_detect
        center_y = self._position[1]  # + self._max_dist_detect
        rel_x = (x - center_x)/self._max_dist_detect
        rel_y = (y - center_y)/self._max_dist_detect  #center_y - y

        rel_x = self.transform_position(rel_x)
        rel_y = self.transform_position(rel_y)

        dist = math.hypot((center_x - x), (center_y - y)) / self._max_dist_detect # Return the Euclidean norm
        dist = self.transform_dist(dist)

        speed = self._traci.vehicle.getSpeed(veh)/15
        # acc = self._traci.vehicle.getAcceleration(veh)
        inlane = self._traci.vehicle.getLaneIndex(veh)
        if inlane == 1:
            inlane = [0.0, 0.0, 1.0]
        elif inlane == 2:
            inlane = [0.0, 1.0, 0.0]
        elif inlane == 3:
            inlane = [1.0, 0.0, 0.0]
        else:
            inlane = [0.0, 0.0, 0.0]
        way = self._get_way(veh) # Way that the vehicle follows (right:+2; straigh:+1; left:0)/2
        queue = self.obtain_queue(rel_x, rel_y)
        queue = self.transform_queue(queue)

        # wt = self._traci.vehicle.getWaitingTime(veh)
        # acc_wt = self._traci.vehicle.getAccumulatedWaitingTime(veh)
        # vtype = self._traci.vehicle.getTypeID(veh)
        # width = self._traci.vehicle.getWidth(veh)
        # length = self._traci.vehicle.getLength(veh)
        angle = self._traci.vehicle.getAngle(veh)/180-1

        # params = [rel_x, rel_y, speed, acc, inlane, way, wt,
                  # acc_wt, vtype, width, length, angle]
        # params = [(rel_x+1)/2, (rel_y+1)/2, dist/self._max_dist_detect, speed] + inlane + way
        params = [rel_x, rel_y, dist, speed*2 - 1, angle] + inlane + way + queue + [self.is_inside(veh, self._id)]

        return params

    def transform_position(self, pos):
        a = 2.025
        b = 5
        return a/(1 + np.exp(-b*pos)) - a/2

    def transform_dist(self, dist):
        a = 2.1
        b = 3
        c = 1.1
        return a * np.exp(-b*dist) - c

    def _get_way(self, veh):

        route = self._traci.vehicle.getRoute(veh)
        route_index = self._traci.vehicle.getRouteIndex(veh)

        try:
            if route_index == len(route) - 1: #It already/is finish
                o = route[route_index - 1].replace(self._id,'')[0]
                d = route[route_index].replace(self._id,'')[0]
            elif not route_index == -1:
                o = route[route_index].replace(self._id,'')[0]
                d = route[route_index + 1].replace(self._id,'')[0]
        except:
            print('An unexpected error has happened, please fix it')
            print(f'route: {route}')
            print(f'route_index: {route_index}')
            o = 'l'
            d = 'r'
        od = o+d
        # l:left, r:right, t:top, b:bottom
        forward_way = set(['lr', 'rl', 'bt', 'tb'])
        turn_right = set(['lb', 'rt', 'br', 'tl'])
        turn_left = set(['lt', 'rb', 'bl', 'tr'])

        if od in forward_way:  # Forward path
            return [0.0, 1.0, 0.0]

        elif od in turn_left:  # This is the left-turn path
            return [1.0, 0.0, 0.0]

        elif od in turn_right:  # This is the right-turn path
            return [0.0, 0.0, 1.0]

        else:
            print('There is an error with get_way')
            print(f'route: {route}')
            print(f'route_index: {route_index}')
            print(f'od: {od}')
            return [0,0,0]

    def transform_queue(self, queue):
        if queue == 0:
            queue = [0.0, 0.0, 0.0, 1.0]
        elif queue == 1:
            queue = [0.0, 0.0, 1.0, 0.0]
        elif queue == 2:
            queue = [0.0, 1.0, 0.0, 0.0]
        elif queue == 3:
            queue = [1.0, 0.0, 0.0, 0.0]
        else:
            queue = [0.0, 0.0, 0.0, 0.0]
        return queue