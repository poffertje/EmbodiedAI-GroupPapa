import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import pygame
import scipy
import random
import os
from scipy.interpolate import make_interp_spline, BSpline

from typing import Union, Tuple

from experiments.aggregation.aggregation import Aggregations
from experiments.covid.population import Population
from experiments.flocking.flock import Flock


def _plot_covid(data) -> None:
    """
    Plot the data related to the covid experiment. The plot is based on the number of Susceptible,
    Infected and Recovered agents

    Args:
    ----
        data:

    """
    output_name = "experiments/covid/plots/Covid-19-SIR%s.png" % time.strftime(
        "-%m.%d.%y-%H:%M", time.localtime()
    )
    fig = plt.figure()
    plt.plot(data["S"], label="Susceptible", color=(1, 0.5, 0))  # Orange
    plt.plot(data["I"], label="Infected", color=(1, 0, 0))  # Red
    plt.plot(data["R"], label="Recovered", color=(0, 1, 0))  # Green
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
    x1= range(t)
    x_new = np.linspace(0, t, 100)
    y1 = data1
    y2 = data2
    y3 = data3 #wandering agents
    a_BSpline = scipy.interpolate.make_interp_spline(x1, y1)
    b_BSpline = scipy.interpolate.make_interp_spline(x1, y2)
    c_BSpline = scipy.interpolate.make_interp_spline(x1, y3)
    y1_new = a_BSpline(x_new)
    y2_new = b_BSpline(x_new)
    y3_new = c_BSpline(x_new)
    plt.title('Rate of Aggregation')
    plt.plot(x_new, y1_new, label = "Site 1", color = 'red')
    plt.plot(x_new, y2_new, label = "Site 2", color = 'blue')
    plt.plot(x_new, y3_new, label = "Wandering", color = 'black', linestyle='--')
    plt.legend()
    plt.xlabel('Number of Frames'), plt.ylabel('Number of Cockroaches')
    plt.show()
    # print("site1")
    # print(data1)
    # print("site2")
    # print(data2)
    print("Site 1 last reading: %d " % data1[-1])
    print("Site 2 last reading: %d " % data2[-1])
    print("Wandering last reading: %d" %data3[-1])



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

    def plot_simulation(self,data1=None,data2=None, data3=None) -> None:
        """Depending on the type of experiment, plots the final data accordingly"""
        if self.swarm_type == "covid":
            _plot_covid(self.swarm.points_to_plot)

        elif self.swarm_type == "flock":
            _plot_flock()

        elif self.swarm_type == "aggregation":
            _plot_aggregation(data1,data2, data3)

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
        obstacle_scale = [100,100]
        obstacle_loc = [500,500]
        obstacle_filename = "experiments/covid/images/lockdown-border.png"

        if self.iter == float("inf"):
            while self.running:
                init = time.time()
                # if len(self.swarm.objects.obstacles) < 4:
                #     self.swarm.objects.add_object(
                #         file=obstacle_filename, pos=[random.randint(100,900),random.randint(100,900)],
                #         scale=[random.randint(50,200),random.randint(50,200)], obj_type="obstacle"
                #     )
                self.simulate()
            self.plot_simulation()
        else:
            for i in range(self.iter):
                self.simulate()

    def make_screenshot(self, index):
        # Get the path to the current folder
        folder, _ = os.path.split(os.path.dirname(__file__))
        # Find a path to the screenshot folder
        folder = os.path.join(folder, 'experiments/%s/screenshots' %self.swarm_type)
        # If the path does not exist yet, then create one
        if not os.path.exists(folder):
            os.makedirs(folder)
        # Save the screenshot as a png with the index corresponding to the frame index
        pygame.image.save(self.screen, os.path.join(folder, f'screenshot_30radius_100population{index:03d}.png'))
