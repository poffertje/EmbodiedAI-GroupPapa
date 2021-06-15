import numpy as np
import pygame
import time

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *

class Person(Agent):
    """ """
    def __init__(
            self, pos, v, flock, state, index: int, color, timer, age, resistance
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
        self.index = index
        self.state = state
        self.flock = flock
        self.timer = timer
        self.stop_timer = 0
        self.avoided_obstacles: bool = False
        self.prev_pos = None
        self.prev_v = None
        self.age = age
        self.counter = 1
        self.resistance = resistance

    def update_actions(self):
        # Obtain statistics of the current population
        self.evaluate()

        # Avoid obstacles
        self.check_for_obstacles()

        # Random stopping of agents to have more natural behaviour
        if self.stop_timer == 0 and self.counter % 100 == 0:
            if np.random.choice([True, False], p=[0.05, 0.95]):
                self.stop()

        # Continue walking after an agent has stopped
        if time.time() - self.stop_timer >= 2 and self.stop_timer != 0:
            self.continue_walk()

        # Check if agent can be recovered after certain amount of time has passed
        self.check_recover()

        # if self.age <= 25:
        #     if self.state == "I":
        #         self.check

        # Check if agent will be infected and whether the agent will keep distance
        self.infect_distancing()

        # Used for the continue_walk function
        self.counter += 1


    def evaluate(self):
        if self.index == 0:
            for agent in self.flock.agents:
                self.flock.datapoints.append(agent.state)

    def check_recover(self):
        if self.timer != None:
            if np.random.choice([True, False], p=[self.resistance, 1-self.resistance]):
                if time.time() - self.timer >= 10 and self.state == "I":
                    Agent.set_color(self, [0, 255, 0])
                    self.state = "R"

    def infect_distancing(self):
        neighbours = self.flock.find_neighbors(self, config["person"]["radius_view"])

        for neighbour in neighbours:

            # social distancing
            if dist(self.pos, neighbour.pos) <= config["person"]["radius_view"]:
                self.v = [self.v[1]*-1, self.v[0]*-1]

            # probability of getting infected
            if neighbour.state == "I" and self.state == "S":
                if np.random.choice([True, False], p=[self.resistance,1-self.resistance]):
                    Agent.set_color(self,[255,69,0])
                    self.timer = time.time()
                    self.state = "I"

    def stop(self):
        self.v = [0,0]
        self.stop_timer = time.time()

    def continue_walk(self):
        self.v = self.set_velocity()
        self.stop_timer = 0

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