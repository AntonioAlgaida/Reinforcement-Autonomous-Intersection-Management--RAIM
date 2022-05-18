# Reinforcement-Autonomous-Intersection-Management--RAIM
This is the repository of the code used for **RAIM** project

Paper: "_RAIM: Reinforced Autonomous Intersection Management - AIM based on MADRL_"

Conference: Real-World RL Workshop. 34th NeurIPS 2020 Conf

[Link to paper](https://www.researchgate.net/publication/357957238_RAIM_Reinforced_Autonomous_Intersection_Management_-_AIM_based_on_MADRL)

[Virtual Presentation](https://www.youtube.com/watch?v=hvf3lwQG8lI)

## Installation
Take a look to requeriments.txt

To install a requeriments.txt file:
create a new virtual environment

```bash
conda create -n RAIM python=3.8 anaconda
```

```bash
conda activate RAIM
conda install --file requirements.tx
```

## How to run
Just run the _main_1_1_v2.py_ file

## How it works
In this repository there is the code to run the paper "_RAIM: Reinforced Autonomous Intersection Management - AIM based on MADRL_"

In this paper, I make use of Deep Reinforcement Learning to train a new Autonomous Intersection Management system.

### What is an Autonomous Intersection Management (AIM) systems
AIM is a decentralyzed system located virtually in the mobile communication system that control connected autonomous vehicles at urban intersections.

### What is Reinforced AIM
Reinforced AIM, or RAIM, is an advanced technique that makes use Deep Reinforcement Learning to determine for each vehicle within an intersection or in the approaches, the speed at which it must travel during the next time interval in order to avoid collisions and minimize travel time. 

RAIM makes use of Twin Delayed Deep Deterministic Policy Gradients (TD3), PER (Prioritized Experience Replay), and Curriculum-based learning through Self-Play.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
