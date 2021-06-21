import numpy as np
import pygame
import time

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *

PR_SEVERE = config["base"]["percentage_underlying"]

class Person(Agent):
    """ """

    def __init__(
            self, pos, v, flock, state, index: int, color, timer, age, recovery_time, social_distancing, mask_on,
            infection_probability, underlying_conditions, severe_case
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
        self.infection_probability = infection_probability  # changed
        self.avoided_obstacles: bool = False
        self.prev_pos = None
        self.prev_v = None
        self.mask_on = mask_on
        self.social_distancing = social_distancing
        self.previous_nr_of_agents = config["base"]["n_agents"]
        self.population_size = config["base"]["n_agents"]
        self.airport_open = False
        self.hospital_open = False
        self.hospitalized = False
        self.bed_nr = None
        self.underlying_conditions = underlying_conditions
        self.severe_case = severe_case

    def update_actions(self):
        # Obtain statistics of the current population
        self.evaluate()

        # Avoid obstacles
        self.check_for_obstacles()

        # Make sure that hospitalized agents remain in their bed
        if self.hospitalized and self.state == "I":
            self.v = [0.0,0.0]

        # Random stopping of agents to have more natural behaviour
        if self.stop_timer == 0 and self.counter % 100 == 0 and self.v[0] != 0.0 and self.v[1] != 0.0  and not self.hospitalized:
            if np.random.choice([True, False], p=[0.05, 0.95]):
                self.stop()

        # Continue walking after an agent has stopped
        if time.time() - self.stop_timer >= 2 and self.stop_timer != 0 and not self.hospitalized:
            self.continue_walk()

        # Check if agent will die
        if self.timer is not None:
            if ((self.counter + 1) - self.timer) % 500 == 0:
                self.check_death()
            elif (self.counter - self.timer) == self.recovery_time:
                self.recover()

        if self.index >= config["base"]["n_agents"]:
            if 120 <= self.pos[0] <= 330 and 120 <= self.pos[1] <= 330:
                inside = True
            else:
                inside = False

            if self.infection_probability != 0.01 and not inside:
                self.infection_probability = 0.01
                self.v = self.set_velocity()

        # Check if agent will be infected and whether the agent will keep distance
        self.infect_distancing()

        # Prevent agents from entering the hospital by having a non-physical border
        if self.hospital_open:
            self.hospital_control()

        # Prevent agents from entering the airport by having a non-physical border
        if self.airport_open:
            self.airport_control()

        if self.mask_on and self.counter == 1:
            self.wear_mask()

        # Used for the continue_walk function
        self.counter += 1

    def airport_control(self):
        if 110 <= self.pos[0] <= 330 and 315 <= self.pos[1] <= 340:
            if self.v[1] < 0.0:
                y_v = randrange(0, 1)
                self.v[1] = y_v

    def hospital_control(self):
        if 675 <= self.pos[0] <= 905 and 315 <= self.pos[1] <= 340:
            if self.v[1] < 0.0:
                y_v = randrange(0, 1)
                self.v[1] = y_v

    def evaluate(self):
        if self.index == 0:
            for agent in self.flock.agents:
                self.flock.datapoints.append(agent.state)

            current_nr_of_agents = len(self.flock.agents)
            if self.previous_nr_of_agents < current_nr_of_agents:
                self.population_size += 10

            self.previous_nr_of_agents = current_nr_of_agents

            for i in range(0, self.population_size - current_nr_of_agents):
                self.flock.datapoints.append("D")

    def wear_mask(self):
        self.mask_on = True
        Agent.set_color(self, [255, 255, 255], (0, 4, 8, 4))
        if self.infection_probability != 0.0:
            self.infection_probability = 0.01

    def take_mask_of(self):
        self.mask_on = False
        infected_color = [256, 69, 0]
        if self.severe_case:
            infected_color = [128, 0, 0]
        Agent.set_color(self, infected_color)

    def hospital_check(self):
        if any(self.flock.vacant_beds.values()):
            vacant_beds = [k for k, v in self.flock.vacant_beds.items() if v == True]
            i = random.choice(vacant_beds)
            if i == 1 or i == 5 or i == 9:
                if i == 1:
                    self.pos = np.array([730.0, 155.0])
                elif i == 5:
                    self.pos = np.array([730.0, 210.0])
                elif i == 9:
                    self.pos = np.array([730.0, 265.0])
            elif i == 2 or i == 6 or i == 10:
                addition = 40
                if i == 2:
                    self.pos = np.array([730.0 + addition, 155.0])
                elif i == 6:
                    self.pos = np.array([730.0 + addition, 210.0])
                elif i == 10:
                    self.pos = np.array([730.0 + addition, 265.0])

            elif i == 3 or i == 7 or i == 11:
                addition = 80
                if i == 3:
                    self.pos = np.array([730.0 + addition, 155.0])
                elif i == 7:
                    self.pos = np.array([730.0 + addition, 210.0])
                elif i == 11:
                    self.pos = np.array([730.0 + addition, 265.0])

            elif i == 4 or i == 8 or i == 12:
                addition = 120
                if i == 4:
                    self.pos = np.array([730.0 + addition, 155.0])
                elif i == 8:
                    self.pos = np.array([730.0 + addition, 210.0])
                elif i == 12:
                    self.pos = np.array([730.0 + addition, 265.0])
            self.v = [0.,0.]
            self.bed_nr = i
            self.flock.hospitalization += 1
            self.hospitalized = True
            self.take_mask_of()
            self.flock.vacant_beds[i] = False

    def check_death(self):
        a, h, k = 1.1, 11.4, 8.7
        probability = ((a ** (self.age - h)) + k) / 10000
        if np.random.choice([True, False], p=[probability, 1 - probability]):
            if self.hospitalized:
                self.flock.hospitalization -= 1
                self.flock.vacant_beds[self.bed_nr] = True
            self.die()
        else:
            pass

    def recover(self):
        Agent.set_color(self, [0, 255, 0])
        self.state = "R"
        self.timer = None
        if self.mask_on:
            self.mask_on = False
        if self.hospitalized:
            self.v = [0.0, 1.0]

    def infect_distancing(self):
        neighbours = self.flock.find_neighbors(self, self.radius_view)

        for neighbour in neighbours:

            # social distancing
            if self.social_distancing:
                if dist(self.pos, neighbour.pos) <= self.radius_view:
                    self.v = [neighbour.v[1], neighbour.v[0]]

            # probability of getting infected
            if neighbour.state == "I" and self.state == "S":
                infected_color = [255, 69, 0]
                if self.underlying_conditions:
                    self.severe_case = np.random.choice([True, False], p=[PR_SEVERE, 1 - PR_SEVERE])
                    if self.severe_case:
                        infected_color = [128, 0, 0]



                probability = (self.infection_probability + neighbour.infection_probability) / 2
                if np.random.choice([True, False], p=[probability, 1 - probability]):
                    if self.mask_on:
                        Agent.set_color(self, infected_color, (0, 0, 8, 4))
                    else:
                        Agent.set_color(self, infected_color)
                    self.timer = self.counter
                    self.state = "I"
                    self.recovery_time = np.random.randint(1000, 1400)

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
