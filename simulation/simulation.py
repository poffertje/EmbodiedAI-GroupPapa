import random

import matplotlib.pyplot as plt
from matplotlib import gridspec
import os
import pygame
import numpy as np

from sys import exit
from time import strftime
from simulation.utils import randrange
from scipy.interpolate import make_interp_spline

from typing import Union, Tuple
from experiments.covid.scenarios import scenario8 as scenarios

from experiments.aggregation.aggregation import Aggregations
from experiments.covid.population import Population
from experiments.flocking.flock import Flock
from experiments.covid.config import config
from experiments.covid.person import Person


def _plot_covid(data) -> None:
    """
    Plot the data related to the covid experiment. The plot is based on the number of Susceptible,
    Infected and Recovered agents

    Args:
    ----
        data:

    """
    folder, _ = os.path.split(os.path.dirname(__file__))

    folder = os.path.join(folder, 'experiments/covid/plots')

    if not os.path.exists(folder):
        os.makedirs(folder)

    output_name = folder + "/Covid-19-SIR-%s-%s.png" % (scenarios()[2], strftime("%H-%M-%S"))

    fig = plt.figure(figsize=(20,7))
    plt.subplot(1, 2, 1,)
    plt.title("Covid-19 Simulation S-E-I-R")
    plt.plot(data["S"], label="Susceptible", color=(1, 0.5, 0))  # Orange
    plt.plot(data["I"], label="Infected", color=(1, 0, 0))  # Red
    plt.plot(data["E"], label="Exposed", color="pink")  # Pink
    plt.plot(data["R"], label="Recovered", color=(0, 1, 0))  # Green
    if scenarios()[6] == "Janssen":
        plt.plot(data["V"], label="Vaccinated", color="blue", linestyle='dotted')  # Blue
    elif scenarios()[6] == "Pfizer" or scenarios()[6] == "Sinovac":
        plt.plot(data["V1"], label="1st vaccination", color="blue", linestyle='dotted')  # Blue
        plt.plot(data["V2"], label="2nd vaccination", color="magenta", linestyle='dotted')  # Magenta
    plt.xlabel("Time")
    plt.ylabel("Population")
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.title("Covid-19 Simulation: Dead, Hospitalised, Severe")
    plt.plot(data["D"], label="Dead", color=(0, 0, 0), linestyle='dotted')  # Blue
    plt.plot(data["H"], label="Hospitalized", color='blue')  # Grey
    plt.plot(data["C"], label="Severe", color="maroon")  # Maroon
    plt.plot(data["SID"], label = "Severe Death", color ="crimson",linestyle='dotted' )
    plt.plot(data["UI"], label = "Infected (UC)", color ="red")

    #plt.tick_params(axis='x', labelsize=8)
    #plt.xticks(np.arange(0, len(data['UI'])+1, 250))

    plt.xlabel("Time")
    plt.ylabel("Population")
    plt.legend()
    fig.savefig(output_name)
    print("No. of Susceptible: ", data["S"][-1])
    print("No. of Death: ", data["D"][-1])
    print("No. of Most Infected", max(data["I"]))
    print("No. of Most Severely Infected", max(data["C"]))
    print("No of Severe Deaths", data["SID"][-1])
    plt.show()


def _plot_flock() -> None:
    """Plot the data related to the flocking experiment. TODO"""
    pass


def _plot_aggregation(data1, data2, data3) -> None:
    """Plot the data related to the aggregation experiment. TODO"""
    t = len(data1)
    x1 = range(t)
    x_new = np.linspace(0, t, 100)
    y1 = data1
    y2 = data2
    y3 = data3  # wandering agents
    a_BSpline = make_interp_spline(x1, y1)
    b_BSpline = make_interp_spline(x1, y2)
    c_BSpline = make_interp_spline(x1, y3)
    y1_new = a_BSpline(x_new)
    y2_new = b_BSpline(x_new)
    y3_new = c_BSpline(x_new)
    plt.title('Rate of Aggregation')
    plt.plot(x_new, y1_new, label="Site 1", color='red')
    plt.plot(x_new, y2_new, label="Site 2", color='blue')
    plt.plot(x_new, y3_new, label="Wandering", color='black', linestyle='--')
    plt.legend()
    plt.xlabel('Number of Frames'), plt.ylabel('Number of Cockroaches')
    plt.show()


"""
General simulation pipeline, suitable for all experiments 
"""


class Simulation:
    """
    This class represents the simulation of agents in a virtual space.
    """

    def __init__(
            self,
            num_agents: int,
            screen_size: Union[Tuple[int, int], int],
            swarm_type: str,
            iterations: int):
        """
        Args:
        ----
            num_agents (int):
            screen_size (Union[Tuple[int, int], int]):
            swarm_type (str):
            iterations (int):
        """
        # general settings
        self.screensize = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        self.sim_background = pygame.Color("gray21")
        self.iter = iterations
        self.swarm_type = swarm_type
        self.site_infection = [0, 0, 0, 0]
        self.closure_index = 0
        self.airport_open = False
        self.hospital_open = False
        self.released = 0


        # swarm settings
        self.num_agents = num_agents
        if self.swarm_type == "flock":
            self.swarm = Flock(screen_size)

        elif self.swarm_type == "aggregation":
            self.swarm = Aggregations(screen_size)

        elif self.swarm_type == "covid":
            self.swarm = Population(screen_size)

        else:
            print("None of the possible swarms selected")
            exit()

        # update
        self.to_update = pygame.sprite.Group()
        self.to_display = pygame.sprite.Group()
        self.running = True

    def plot_simulation(self, data1=None, data2=None, data3=None) -> None:
        """Depending on the type of experiment, plots the final data accordingly"""

        if self.swarm_type == "covid":
            _plot_covid(self.swarm.points_to_plot)

        elif self.swarm_type == "flock":
            _plot_flock()

        elif self.swarm_type == "aggregation":
            _plot_aggregation(data1, data2, data3)

    def initialize(self) -> None:
        """Initialize the swarm, specifying the number of agents to be generated"""

        # initialize a swarm type specific environment
        self.swarm.initialize(self.num_agents)

    def simulate(self) -> None:
        """Here each frame is computed and displayed"""

        self.screen.fill(self.sim_background)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.swarm.update()
        self.swarm.display(self.screen)

        pygame.display.flip()

    def run(self) -> None:
        """
        Main cycle where the initialization and the frame-by-frame computation is performed.
        The iteration con be infinite if the parameter iter was set to -1, or with a finite number of frames
        (according to iter)
        When the GUI is closed, the resulting data is plotted according to the type of the experiment.
        """

        # initialize the environment and agent/obstacle positions
        self.initialize()
        print("Executing", scenarios()[2])

        # Set the scenario
        lockdown = scenarios()[0]
        airport = scenarios()[4]
        hospital_policy = scenarios()[9]

        if self.iter == float("inf"):
            while self.running:
                if lockdown:
                    self.check_closure()
                self.simulate()
            self.plot_simulation()

        else:
            for i in range(self.iter):
                severe = []
                infected_underlying = []
                combined = []
                self.released = 0

                for agent in self.swarm.agents:
                    if hospital_policy:
                        if not agent.hospitalized:
                            if agent.state == "C":
                                severe.append(agent)
                            elif agent.underlying_conditions and agent.state == "I":
                                infected_underlying.append(agent)
                    elif not hospital_policy:
                        if not agent.hospitalized:
                            if agent.state == "C" or agent.state == "I":
                                combined.append(agent)


                if any(self.swarm.vacant_beds.values()):
                    if hospital_policy:

                        if len(severe) != 0:
                            considered_patient = random.choice(severe)
                            considered_patient.hospital_check()

                        elif len(infected_underlying) != 0:
                            considered_patient = random.choice(infected_underlying)
                            considered_patient.hospital_check()

                    elif not hospital_policy:
                        if len(combined) != 0:
                            considered_patient = random.choice(combined)
                            considered_patient.hospital_check()

                for agent in self.swarm.agents:
                    if agent.state == "R":
                        if 685 <= agent.pos[0] <= 895 and 105 <= agent.pos[1] <= 315 and agent.hospitalized:
                            self.released += 1
                        elif not (685 <= agent.pos[0] <= 895 and 105 <= agent.pos[1] <= 320) and agent.hospitalized:
                            agent.hospitalized = False
                            x = randrange(-1, 1)
                            y = randrange(0, 1)
                            agent.v = [x, y]
                            self.swarm.vacant_beds[agent.bed_nr] = True
                            self.swarm.hospitalization -= 1

                self.check_hospital_occupation()

                if lockdown:
                    self.check_closure()

                if i >= self.iter / 4 and airport:
                    if i == self.iter / 4:
                        self.spawn_tourists()
                    elif i == self.iter / 4 + scenarios()[6]:
                        self.remove_closure(0)
                        self.swarm.objects.add_object(file="experiments/covid/images/BordersAirportOpen.png",
                                                      pos=[500, 500],
                                                      scale=[1000, 1000], obj_type="obstacle", index=0)
                        self.airport_open = True
                        for agent in self.swarm.agents:
                            agent.airport_open = True
                            if agent.index >= config["base"]["n_agents"]:
                                agent.v = [0.0, 1.0]
                    elif i >= self.iter / 4 + scenarios()[6]:
                        if self.airport_open:
                            self.check_airport_occupation()

                self.simulate()

            self.plot_simulation()

    def check_airport_occupation(self):
        airport_citizens = 0
        for agent in self.swarm.agents:
            if agent.index >= config["base"]["n_agents"]:
                if 120 <= agent.pos[0] <= 295 and 120 <= agent.pos[1] <= 315:
                    airport_citizens += 1
        if airport_citizens == 0:
            self.remove_closure(0)
            self.swarm.objects.add_object(file="experiments/covid/images/BordersAirport.png",
                                          pos=[500, 500],
                                          scale=[1000, 1000], obj_type="obstacle", index=0)
            for agent in self.swarm.agents:
                agent.airport_open = False
            self.airport_open = False

    def check_hospital_occupation(self):
        if self.released > 0:
            self.remove_closure(-14)
            self.add_closure("experiments/covid/images/HospitalOpen.png", -14)
            self.hospital_open = True
            for agent in self.swarm.agents:
                agent.hospital_open = True
        elif self.released == 0:
            self.remove_closure(-14)
            self.add_closure("experiments/covid/images/HospitalClosed.png", -14)
            self.hospital_open = False
            for agent in self.swarm.agents:
                agent.hospital_open = False

    def make_screenshot(self, index):
        # Get the path to the current folder
        folder, _ = os.path.split(os.path.dirname(__file__))
        # Find a path to the screenshot folder
        folder = os.path.join(folder, 'experiments/%s/screenshots' % self.swarm_type)
        # If the path does not exist yet, then create one
        if not os.path.exists(folder):
            os.makedirs(folder)
        # Save the screenshot as a png with the index corresponding to the frame index
        pygame.image.save(self.screen, os.path.join(folder, f'screenshot_30radius_100population{index:03d}.png'))

    def check_closure(self):
        self.site_infection = [0, 0, 0, 0]
        lockdown_threshold = scenarios()[4]

        for agent in self.swarm.agents:
            if agent.state == "I" and agent.pos[0] < 500 and agent.pos[1] < 500:
                self.site_infection[0] += 1
            elif agent.state == "I" and agent.pos[0] > 500 and agent.pos[1] < 500:
                self.site_infection[1] += 1
            elif agent.state == "I" and agent.pos[0] < 500 and agent.pos[1] > 500:
                self.site_infection[2] += 1
            elif agent.state == "I" and agent.pos[0] > 500 and agent.pos[1] > 500:
                self.site_infection[3] += 1

        if len(self.swarm.objects.obstacles) < 6:
            if self.site_infection[0] >= config["base"]["n_agents"] * lockdown_threshold:
                border_file = "experiments/covid/images/Borders1.png"
                self.closure_index = 1
                self.add_closure(border_file, self.closure_index)
            if self.site_infection[1] >= config["base"]["n_agents"] * lockdown_threshold:
                border_file = "experiments/covid/images/Borders2.png"
                self.closure_index = 2
                self.add_closure(border_file, self.closure_index)
            if self.site_infection[2] >= config["base"]["n_agents"] * lockdown_threshold:
                border_file = "experiments/covid/images/Borders3.png"
                self.closure_index = 3
                self.add_closure(border_file, self.closure_index)
            if self.site_infection[3] >= config["base"]["n_agents"] * lockdown_threshold:
                border_file = "experiments/covid/images/Borders4.png"
                self.closure_index = 4
                self.add_closure(border_file, self.closure_index)

        if self.site_infection[0] == 0 and len(self.swarm.objects.obstacles) > 1:
            self.remove_closure(1)
        if self.site_infection[1] == 0 and len(self.swarm.objects.obstacles) > 1:
            self.remove_closure(2)
        if self.site_infection[2] == 0 and len(self.swarm.objects.obstacles) > 1:
            self.remove_closure(3)
        if self.site_infection[3] == 0 and len(self.swarm.objects.obstacles) > 1:
            self.remove_closure(4)

    def add_closure(self, file, index):
        object_present = False
        for object in self.swarm.objects.obstacles:
            if object.index == index:
                object_present = True

        if not object_present:
            self.swarm.objects.add_object(file=file, pos=[500, 500],
                                          scale=[1000, 1000], obj_type="obstacle", index=index)

    def remove_closure(self, index):
        for obstacle in self.swarm.objects.obstacles:
            if obstacle.index == index:
                self.swarm.objects.obstacles.remove(obstacle)
            else:
                pass

    def spawn_tourists(self):
        number_infected = 0
        for i in range(10):
            coordinates_x = randrange(125, 295)
            coordinates_y = randrange(125, 295)
            coordinates = [coordinates_x, coordinates_y]
            age = np.random.choice(
                [np.random.randint(1, 25), np.random.randint(26, 64), np.random.randint(65, 90)]
                , p=[0.28, 0.52, 0.20])
            if number_infected < 2:
                number_infected += 1
                state = "I"
                color = [255, 69, 0]
                timer = 1
                recovery_timer = np.random.randint(1000, 1400)
                vaccination_timer = None
            else:
                state = "S"
                color = [255, 165, 0]
                timer = None
                recovery_timer = None

            self.swarm.add_agent(
                Person(pos=np.array(coordinates), v=np.array([0.0, 0.0]), flock=self.swarm, state=state,
                       index=config["base"]["n_agents"] + i,
                       color=color, timer=timer,
                       age=age,
                       recovery_time=recovery_timer,
                       mask_on=True, infection_probability=0.0, underlying_conditions=False, vaccination_timer=None,
                       severe_case=None, vaccinated=False))
