import numpy as np
import pygame
import time

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *
from experiments.covid.scenarios import scenario9 as scenarios

PR_SEVERE = config["base"]["percentage_underlying"]
# assuming 50 frames = 1 day
# -----------------------------
vaccine_type = scenarios()[6]
PINK = (255, 128, 209)
BLUE = (100, 149, 237)
MAGENTA = (153, 50, 204)
RED = (255, 69, 0)
GREEN = (0, 255, 0)
MAROON = (128, 0, 0)
AIRPORT = scenarios()[4]
if vaccine_type == 'Pfizer':
    FIRST_IMMUNITY_TIME = 350
    SECOND_IMMUNITY_TIME = 700
    SECOND_SHOT_TIME = 1400  # 28 days
    FIRST_IMMUNITY_PROB = (1 - 0.685)
    SECOND_IMMUNITY_PROB = (1 - 0.95)
    FIRST_SEVERE_PROB = 0.57
    SECOND_SEVERE_PROB = 0.047
elif vaccine_type == 'Sinovac':
    FIRST_IMMUNITY_TIME = 350
    SECOND_IMMUNITY_TIME = 700
    SECOND_SHOT_TIME = 800  # about 2 weeks
    FIRST_IMMUNITY_PROB = (1 - 0.16)
    FIRST_SEVERE_PROB = 0  # need to find
    SECOND_IMMUNITY_PROB = (1 - 0.67)
    SECOND_SEVERE_PROB = 0
else:
    JANSSEN_IMMUNITY_TIME = 500
    JANSSEN_SEVERE_PROB = 0.2
    JANSSEN_IMMUNITY_PROB = 0.34


class Person(Agent):
    """ """

    def __init__(
            self, pos, v, flock, state, index: int, color, timer, age, recovery_time, mask_on, infection_probability,
            underlying_conditions, severe_case, vaccinated, vaccination_timer
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
        self.previous_nr_of_agents = config["base"]["n_agents"]
        self.population_size = config["base"]["n_agents"]
        self.airport_open = False
        self.hospital_open = False
        self.hospitalized = False
        self.bed_nr = None
        self.underlying_conditions = underlying_conditions
        self.severe_case = severe_case
        self.vaccination_timer = vaccination_timer
        self.vaccinated = vaccinated
        self.p_severe = PR_SEVERE
        self.second_dose_timer = None
        self.incubation_period = 0
        self.second_severe_attack = 250
        self.second_severe_timer = None

    def update_actions(self):
        # Obtain statistics of the current population
        self.evaluate()

        # Check for vaccination
        if vaccine_type is not None:
            if self.state == "S" or self.state == "E" or (self.vaccinated == "V1" and self.state != "I") or \
                    (self.vaccinated == "V1" and self.state != "C"):
                self.vaccination_check()

        # After incubation period has passed, make agent infected.
        if self.counter == self.incubation_period:
            self.incubation_check()

        # Avoid obstacles
        self.check_for_obstacles()

        # Make sure that hospitalized agents remain in their bed
        if self.hospitalized and (self.state == "I" or self.state == "C"):
            self.v = [0.0, 0.0]

        # Random stopping of agents to have more natural behaviour
        if self.stop_timer == 0 and self.counter % 100 == 0 and self.v[0] != 0.0 and self.v[
            1] != 0.0 and not self.hospitalized:
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
            elif self.state == "I" and self.underlying_conditions and self.timer == self.second_severe_timer:
                self.severe_case = np.random.choice([True, False], p=[self.p_severe, 1 - self.p_severe])
                if self.severe_case:
                    infected_color = MAROON
                    self.state = "C"
                    Agent.set_color(self, infected_color)

        if AIRPORT:
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

    def incubation_check(self):
        infected_color = RED
        self.state = "I"
        if self.underlying_conditions:
            self.second_severe_timer = self.counter + self.second_severe_attack
            self.severe_case = np.random.choice([True, False], p=[self.p_severe, 1 - self.p_severe])
            if self.severe_case:
                infected_color = MAROON
                self.state = "C"
        if self.mask_on:
            Agent.set_color(self, infected_color, (0, 0, 8, 4))
            Agent.set_color(self, (255, 255, 255), (0, 4, 8, 4))
        else:
            Agent.set_color(self, infected_color)
        self.timer = self.counter
        self.recovery_time = np.random.randint(500, 700)

    def vaccination_check(self):
        if vaccine_type == "Janssen":
            if self.counter == self.vaccination_timer and self.vaccination_timer is not None:
                if self.state == "S" or self.state == "E":
                    if self.underlying_conditions:
                        self.p_severe = self.p_severe * JANSSEN_SEVERE_PROB
                    self.vaccinated = "V"
                    self.vaccination_timer += JANSSEN_IMMUNITY_TIME
                    Agent.set_color(self, BLUE)
                    if self.mask_on:
                        Agent.set_color(self, (255, 255, 255), (0, 4, 8, 4))
        elif vaccine_type == "Pfizer" or vaccine_type == "Sinovac":
            if self.counter == self.vaccination_timer and self.vaccination_timer is not None and self.vaccinated != "V1":
                if self.state == "S" or self.state == "E":  # FIRST SHOT
                    self.vaccinated = "V1"
                    Agent.set_color(self, BLUE)
                    self.second_dose_timer = self.vaccination_timer + SECOND_SHOT_TIME
                    self.vaccination_timer += FIRST_IMMUNITY_TIME  # new timer for when the first dose's immunity
                    # should kick in
                    if self.mask_on:
                        Agent.set_color(self, (255, 255, 255), (0, 4, 8, 4))
            elif self.vaccinated == "V1" and self.state != "I" and self.state != "C":  # SECOND SHOT
                if self.counter == self.second_dose_timer:
                    Agent.set_color(self, MAGENTA)
                    self.vaccination_timer += SECOND_IMMUNITY_TIME  # new timer for when the second dose's immunity
                    # should kick in
                    if self.underlying_conditions:
                        self.p_severe = self.p_severe * SECOND_SEVERE_PROB
                    if self.mask_on:
                        Agent.set_color(self, (255, 255, 255), (0, 4, 8, 4))
                    self.vaccinated = "V2"

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
                if agent.hospitalized:
                    self.flock.datapoints.append("H")
                if agent.vaccinated is not None:
                    self.flock.datapoints.append(agent.vaccinated)

            current_nr_of_agents = len(self.flock.agents)

            if self.previous_nr_of_agents < current_nr_of_agents:
                self.population_size += 10

            self.previous_nr_of_agents = current_nr_of_agents

            for i in range(0, self.population_size - current_nr_of_agents):
                self.flock.datapoints.append("D")

    def wear_mask(self):
        Agent.set_color(self, (255, 255, 255), (0, 4, 8, 4))
        if self.infection_probability != 0.0:
            self.infection_probability = 0.01

    def take_mask_of(self):
        self.mask_on = False
        color = (255, 69, 0)
        if self.state == "C":
            color = MAROON
        if self.state == "I":
            color = RED
        self.infection_probability = 0.1
        Agent.set_color(self, color)

    def hospital_check(self):
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
        self.v = [0., 0.]
        self.bed_nr = i
        self.flock.hospitalization += 1
        self.hospitalized = True
        self.take_mask_of()
        self.flock.vacant_beds[i] = False

    def check_death(self):
        if self.severe_case and not self.hospitalized:
            probability = np.random.uniform(0.5, 0.6)
        elif self.severe_case and self.hospitalized:
            probability = 0.21
        else:
            a, h, k = 1.1, 11.4, 8.7
            probability = ((a ** (self.age - h)) + k) / 10000
        if np.random.choice([True, False], p=[probability, 1 - probability]):
            if self.index != 0:
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
            # probability of getting infected
            if (neighbour.state == "I" or neighbour.state == "C") and (self.state == "S" or self.state == "E"):
                exposed_color = PINK
                probability = (self.infection_probability + neighbour.infection_probability) / 2
                if self.vaccinated == "V1":  # Pfizer or Sinovac
                    if self.counter > self.vaccination_timer:
                        probability = probability * FIRST_IMMUNITY_PROB
                elif self.vaccinated == "V":  # Janssen
                    if self.counter >= self.vaccination_timer:
                        probability = probability * JANSSEN_IMMUNITY_PROB
                elif self.vaccinated == "V2":  # Pfizer or Sinovac
                    if self.counter >= self.vaccination_timer:
                        probability = probability * SECOND_IMMUNITY_PROB
                if self.state != "E":
                    if np.random.choice([True, False], p=[probability, 1 - probability]):
                        self.state = "E"
                        self.incubation_period = np.random.randint(100, 700) + self.counter
                        Agent.set_color(self, exposed_color)
                        if self.mask_on:
                            Agent.set_color(self, (255, 255, 255), (0, 4, 8, 4))

    def stop(self):
        self.v = [0, 0]
        self.stop_timer = time.time()

    def continue_walk(self):
        self.v = self.set_velocity()
        self.stop_timer = 0

    def die(self):
        self.flock.agents.remove(self)

    def check_for_obstacles(self):
        # avoid any obstacles in the environment
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
