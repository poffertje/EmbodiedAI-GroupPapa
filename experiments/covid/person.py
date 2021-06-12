import numpy as np
import pygame

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *


class Person(Agent):
    """ """
    def __init__(
            self, pos, v, flock, state, index: int, color
    ) -> None:
        super(Person, self).__init__(
            pos,
            v,
            max_speed=config["agent"]["max_speed"],
            min_speed=config["agent"]["min_speed"],
            mass=config["agent"]["mass"],
            width=config["agent"]["width"],
            height=config["agent"]["height"],
            dT=config["agent"]["dt"],
            index=index,
            color=color,
        )
        self.state = state
        self.flock = flock

    def update_actions(self):
        if np.random.choice([True, False], p=[0.1, 0.9]):
            self.v = self.wander(30, randrange(0, 10), randrange(0, 180))