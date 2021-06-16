import numpy as np
import pygame
import time

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *


class Person(Agent):
    """ """

    def __init__(
            self, pos, v, flock, state, index: int, color, timer, age, recovery_time, social_distancing, mask_on
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
        self.recovery_time = recovery_time
        self.counter = 1
        self.radius_view = config["person"]["radius_view"]
        self.age = age
        self.infection_probability = 0.1 #changed
        self.avoided_obstacles: bool = False
        self.prev_pos = None
        self.prev_v = None
        self.mask_on = mask_on
        self.social_distancing = social_distancing

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

        # Check if agent will die
        if self.timer is not None:
            if ((self.counter + 1) - self.timer) % 500 == 0:
                self.check_death()
            elif (self.counter - self.timer) == self.recovery_time:
                self.recover()

        # Check if agent will be infected and whether the agent will keep distance
        self.infect_distancing()

        if self.mask_on and self.counter == 1:
            self.wear_mask()

        # Used for the continue_walk function
        self.counter += 1

    def evaluate(self):
        if self.index == 0:
            for agent in self.flock.agents:
                self.flock.datapoints.append(agent.state)
            for i in range(0, config["base"]["n_agents"] - len(self.flock.agents)):
                self.flock.datapoints.append("D")

    def wear_mask(self):
        self.mask_on = True
        Agent.set_color(self, [255, 255, 255], (0, 4, 8, 4))
        self.infection_probability = 0.01

    def take_mask_of(self):
        self.mask_on = False
        # TODO

    def check_death(self):
        a, h, k = 1.1, 11.4, 8.7
        probability = ((a ** (self.age - h)) + k) / 10000
        if np.random.choice([True, False], p=[probability, 1 - probability]):
            self.die()
        else:
            pass

    def recover(self):
        Agent.set_color(self, [0, 255, 0])
        self.state = "R"
        self.timer = None

    def infect_distancing(self):
        neighbours = self.flock.find_neighbors(self, self.radius_view)

        for neighbour in neighbours:

            # social distancing
            if self.social_distancing == True:
                if dist(self.pos, neighbour.pos) <= self.radius_view:
                    self.v = [neighbour.v[1], neighbour.v[0]]

            # probability of getting infected
            if neighbour.state == "I" and self.state == "S":
                probability = (self.infection_probability + neighbour.infection_probability)/2
                if np.random.choice([True, False], p=[probability, 1 - probability]):
                    if self.mask_on:
                        Agent.set_color(self, [255, 69, 0], (0, 0, 8, 4))
                    else:
                        Agent.set_color(self, [255, 69, 0])
                    self.timer = self.counter
                    self.state = "I"
                    self.recovery_time = random.randint(1000, 1400)

    def stop(self):
        self.v = [0, 0]
        self.stop_timer = time.time()

    def continue_walk(self):
        self.v = self.set_velocity()
        self.stop_timer = 0

    def die(self):
        self.flock.agents.remove(self)

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
