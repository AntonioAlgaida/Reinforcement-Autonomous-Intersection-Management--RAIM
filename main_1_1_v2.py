# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 16:49:54 2020

@author: anton
"""

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import time
import torch
import random
import platform
import traceback
import subprocess

import numpy as np

from torch.utils.tensorboard import SummaryWriter
from collections import defaultdict

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.path.append("/usr/share/sumo/bin") # Para linux
    sys.path.append("/usr/share/sumo/tools") # Para linux
    #sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

# sys.path.append("/usr/share/sumo/bin") # Para linux
# sys.path.append("/usr/share/sumo/tools") # Para linux

#%
pltf = platform.system()
if pltf == "Windows":
    print("Your system is Windows")
    netgenBinary = checkBinary('netgenerate.exe')
    sumoBinary = checkBinary('sumo-gui.exe')

else:
    print("Your system is Linux")
    netgenBinary = checkBinary('netgenerate')
    sumoBinary = checkBinary('sumo-gui')
#%
if pltf == "Windows":
    root = 'E:/api-sumo_v3/1x1/VAST4'
else:
    root = '/root/RAIM'

os.chdir(root)

sys.path.append(f"{root}/algorithms")
sys.path.append(f"{root}/api_sumo")
sys.path.append(f"{root}/api_sumo/sumo_elems")
sys.path.append(f"{root}/graphs")
sys.path.append(f"{root}/scenarios")

from algorithms import *  # noqa
from api_sumo import *  # noqa
from graphs import *  # noqa
from scenarios import *  # noqa

# %
SEED = 42

torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)

# Writer will output to ./runs/ directory by default
writer = SummaryWriter()
#%%
# Params
nrows = 1
# Number of columns:
ncols = 1
# Number of lanes:
nlanes = 2
# Lenght (m):
length = 200

# Estas líneas son *heredadas* y van a estar deprecated en la versión v3
red_manhattan = ManhattanGraph(3, 3, 300)
escenario = ScenarioThree(red_manhattan, 250, 500, 800, 900)

# Crea la simulación
nlanes = 2
simulacion = SumoSimulation(red_manhattan, gui=False, lanes=nlanes,
                            nrows=nrows, ncols=ncols, leng=length,
                            seed=SEED, flow=25)

# Algoritmo para controlar los semáforos. Deprecated in v3
Fixed = FixedAlgorithm(greentime=(120-10)//2, lanes=nlanes)

#%
# simulacion.im.agent.load_param()
# simulacion.im.agent.load_checkpoint(checkpoint_path='ckpt/ep_collisions_70.pth.tar')
# simulacion.im.agent.load_checkpoint(step=15)
# simulacion.im.agent.load_imitationLearning(path='ckpt/m_4096_2048_1024_0.0209.pkl')
# simulacion.im.agent.load('ckpt/TD3/150')
# simulacion.im.agent.load('ckpt/TD3/300_best')


#%
time_now = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
start_time = time.time()
epochs = 1000000
rewards = []
training_records = []
training_tripinfo = []
aux = []
collisions = []
# simulacion.create_route_files_v2()

flow = 50
i = 0
change_seed_every = 5
best_timeloss = 9999
best_collisions = 9999

try:
    for epoch in np.arange(epochs):
        simulacion.i_ep = epoch
        simulacion.seed = int(epoch/change_seed_every)
        simulacion.change_algorithm(Fixed)
        simulacion.change_scenario(escenario)
        # simulacion.flow = flow
        if simulacion.im.agent.memory.is_full():
            elapsed_time = time.time() - start_time
            print(time.strftime("Elapsed time: %H:%M:%S", time.gmtime(elapsed_time)))
            simulacion.simulation_duration = 5*60
            simulacion.flow = flow
        else:
            elapsed_time = time.time() - start_time
            print(time.strftime("Elapsed time: %H:%M:%S", time.gmtime(elapsed_time)))
            simulacion.simulation_duration = 5*60
            simulacion.flow = np.random.randint(25, 600)

        [r,t,s,a,c] = simulacion.run_simulation()
        rewards.append(r)
        training_records.append(t)
        ti = simulacion.getTripinfo()
        collisions.append(np.sum(c))

        if ti[0] > 0: # No ha habido error en tripInfo por el # de veh
            try:
                training_tripinfo.append(ti)
                aux.append(ti)
                a = np.reshape(training_tripinfo, (-1, 9))

                b = np.reshape(aux, (-1, 9))

                writer.add_scalar('Global/Density', flow, i)
                writer.add_scalar('Global/# of Vehicles', ti[0], i)
                writer.add_scalar('Global/# Collisions', np.sum(c), i)
                writer.add_scalar('Global/Reward', t[1], i)

                writer.add_scalar('Timeloss/Total', ti[1], i)
                writer.add_scalar('Duration/Total', ti[2], i)
                writer.add_scalar('wTime/Total', ti[3], i)
                writer.add_scalar('Timeloss/Relative', ti[4], i)
                writer.add_scalar('Duration/Average', ti[5], i)
                writer.add_scalar('wTime/Average', ti[6], i)
                writer.add_scalar('Timeloss/Average', ti[7], i)
                writer.add_scalar('Timeloss/Max', ti[8], i)
                i += 1
                # flow += 50
                if len(a) > 250:
                    # if np.mean(a[:,7][-1000:]) < 0.5:
                    if np.var(a[:,7][-250:]) < 0.005*flow or len(a) > 1000:
                        flow += 25
                        simulacion.flow = flow
                        print(f'Increasing flow to: {flow} due to, the var is: {np.var(a[:,7][-100:])}')
                        training_tripinfo = []
                        best_timeloss = 9999
                        best_collisions = 9999

                # Guardamos el mejor
                if best_collisions >= np.sum(c) and best_timeloss >= ti[7]:
                    best_timeloss = ti[7]
                    best_collisions = np.sum(c)
                    # simulacion.im.agent.save_checkpoint(str(flow) + '_best')
                    simulacion.im.agent.save('ckpt/TD3/' + str(flow) + '_best')

                print(f'Simulation: {epoch}; Mean duration: {ti[5]:.2f}, Mean wtime: {ti[6]:.2f}, Mean timeloss: {ti[7]:.2f}, flow: {simulacion.flow}, reward: {t[1]}\n')
                # print(f'Training records: {t}')
            except Exception as e:
                print("type error: " + str(e))
except Exception as e:
    print("type error: " + str(e))
    print(traceback.format_exc())
    simulacion.close_simulation()

elapsed_time = time.time() - start_time
print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

simulacion.im.agent.save_weights()