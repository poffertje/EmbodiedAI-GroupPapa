import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import pygame
import scipy
import random
import os
from simulation.utils import *
from scipy.interpolate import make_interp_spline, BSpline

from typing import Union, Tuple
from experiments.covid.scenarios import scenario2 as scenarios

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

    output_name = folder + "/Covid-19-SIR-%s-%s.png" % (scenarios()[3], time.strftime("%H-%M-%S"))

    fig = plt.figure()
    plt.plot(data["S"], label="Susceptible", color=(1, 0.5, 0))  # Orange
    plt.plot(data["I"], label="Infected", color=(1, 0, 0))  # Red
    plt.plot(data["R"], label="Recovered", color=(0, 1, 0))  # Green
    plt.plot(data["D"], label="Dead", color=(0, 0, 0), linestyle='--')  # Blue
    plt.title("Covid-19 Simulation S-I-R")
    plt.xlabel("Time")
    plt.ylabel("Population")
    plt.legend()
    fig.savefig(output_name)
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
    a_BSpline = scipy.interpolate.make_interp_spline(x1, y1)
    b_BSpline = scipy.interpolate.make_interp_spline(x1, y2)
    c_BSpline = scipy.interpolate.make_interp_spline(x1, y3)
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
            sys.exit()

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

        # Set the scenario
        lockdown = scenarios()[0]
        airport = scenarios()[5]

        if self.iter == float("inf"):
            while self.running:

                if lockdown:
                    self.check_closure()
                self.simulate()

            self.plot_simulation()

        else:
            for i in range(self.iter):

                if lockdown:
                    self.check_closure()
                if i >= self.iter/2 and airport:
                    if i == self.iter/2:
                        self.spawn_tourists()
                    elif i == scenarios()[6]:
                        self.remove_closure(0)
                        self.swarm.objects.add_object(file="experiments/covid/images/BordersAirportOpen.png", pos=[500, 500],
                                                      scale=[1000, 1000], obj_type="obstacle", index=0)

                        for agent in self.swarm.agents:
                            if agent.index > config["base"]["n_agents"]:
                                agent.v = [0.0,1.0]

                self.simulate()

            self.plot_simulation()

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
        for i in range(10):
            coordinates_x = randrange(125, 295)
            coordinates_y = randrange(125, 295)
            coordinates = [coordinates_x, coordinates_y]
            state = np.random.choice(["S", "I"], p=[0.8, 0.2])
            if state == "S":
                color = [255, 165, 0]
            elif state == "I":
                color = [255, 69, 0]
            self.swarm.add_agent(Person(pos=np.array(coordinates), v=None, flock=self.swarm, state=state,
                                        index=config["base"]["n_agents"] + i,
                                        color=color, timer=None,
                                        age=np.random.choice(
                                            [random.randint(1, 25), random.randint(26, 64), random.randint(65, 90)]
                                            , p=[0.28, 0.52, 0.20]),
                                        recovery_time=None,
                                        social_distancing=np.random.choice([True, False],
                                                                           p=[scenarios()[1], 1 - scenarios()[1]]),
                                        mask_on=True))
