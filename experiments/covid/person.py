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
        self.avoided_obstacles: bool = False
        self.prev_pos = None
        self.prev_v = None
        self.in_lockdown = False

    def update_actions(self):
        self.evaluate()
        # Avoid obstacles
        self.check_for_obstacles()

        for object in self.flock.objects.obstacles:
            if self.pos[0] and self.pos[1] in range(int(area(object.pos[0],object.scale[0])[0]),int(area(object.pos[1],object.scale[1])[1])):
                self.in_lockdown = True
            else:
                self.in_lockdown = False

        if self.timer != None:
            if time.time() - self.timer >= 10 and self.state == "I":
                Agent.set_color(self, [0, 255, 0])
                self.state = "R"

        neighbours = self.flock.find_neighbors(self, config["person"]["radius_view"])

        for neighbour in neighbours:
            if neighbour.state == "I" and self.state == "S" and self.in_lockdown == neighbour.in_lockdown:
                if np.random.choice([True, False], p=[0.1, 0.9]):
                    Agent.set_color(self,[255,69,0])
                    self.timer = time.time()
                    self.state = "I"

    def evaluate(self):
        if self.index == 0:
            for agent in self.flock.agents:
                self.flock.datapoints.append(agent.state)

    def check_for_obstacles(self):
        # Avoid any obstacles in the environment
        for obstacle in self.flock.objects.obstacles:
            collide = pygame.sprite.collide_mask(self, obstacle)
            if bool(collide):
                # If a roach gets stuck because when avoiding the obstacle ended up inside of the object,
                # reset the position to the previous one and do a 180 degree turn
                if not self.avoided_obstacles:
                    self.prev_pos = self.pos.copy()
                    self.prev_v = self.v.copy()

                else:
                    self.pos = self.prev_pos.copy()
                    self.v = self.prev_v.copy()

                self.avoided_obstacles = True
                self.avoid_obstacle()
                return

        self.prev_v = None
        self.prev_pos = None
        self.avoided_obstacles = False