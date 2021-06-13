import numpy as np
import pygame
import time

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *

class Person(Agent):
    """ """
    def __init__(
            self, pos, v, flock, state, index: int, color, timer
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
        self.timer = timer

    def update_actions(self):
        if np.random.choice([True, False], p=[0.1, 0.9]):
            self.v = self.wander(30, randrange(0, 10), randrange(0, 180))
        if self.timer != None:
            if time.time() - self.timer >= 10 and self.state == "I":
                Agent.set_color(self, [0, 255, 0])
                self.state == "R"
        neighbours = self.flock.find_neighbors(self, config["person"]["radius_view"])
        for neighbour in neighbours:
            if neighbour.state == "I" and self.state == "S":
                Agent.set_color(self,[255,69,0])
                self.timer = time.time()
                self.state = "I"
        self.evaluate()

    def evaluate(self):
        if self.index == 0:
            for agent in self.flock.agents:
                self.flock.datapoints.append(agent.state)
