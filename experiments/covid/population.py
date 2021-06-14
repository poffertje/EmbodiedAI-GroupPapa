import time
import random
import pygame

from experiments.covid.config import config
from experiments.covid.person import Person
from simulation.swarm import Swarm
from simulation.utils import *


class Population(Swarm):
    """Class that represents the Population for the Covid experiment. TODO"""

    def __init__(self, screen_size) -> None:
        super(Population, self).__init__(screen_size)
        # To do

    def initialize(self, num_agents: int) -> None:
        """
        Args:
            num_agents (int):

        """
        # To Do
        # code snipet (not complete) to avoid initializing agents on obstacles
        # given some coordinates and obstacles in the environment, this repositions the agent

        for index, agent in enumerate(range(num_agents)):
            coordinates = generate_coordinates(self.screen)

            if config["population"]["obstacles"]:  # you need to define this variable
                for obj in self.objects.obstacles:
                    rel_coordinate = relative(
                        coordinates, (obj.rect[0], obj.rect[1])
                    )
                    try:
                        while obj.mask.get_at(rel_coordinate):
                            coordinates = generate_coordinates(self.screen)
                            rel_coordinate = relative(
                                coordinates, (obj.rect[0], obj.rect[1])
                            )
                    except IndexError:
                        pass

            if index % 5 == 0:
                resistance = 0.65
                resistance = resistance * 0.75
                self.add_agent(Person(pos=np.array(coordinates), v=None, flock=self, state="I", index=index,
                                      color=[255,69,0],timer=time.time(),
                                      age=np.random.choice([random.randint(5,35), random.randint(36,75)], p=[0.7, 0.3]),
                                      resistance=resistance))
            else:
                resistance = 0.65
                self.add_agent(Person(pos=np.array(coordinates), v=None, flock=self, state="S", index=index,
                                      color=[255,165,0],timer=None,
                                      age=np.random.choice([random.randint(5,35), random.randint(36,75)], p=[0.7, 0.3]),
                                      resistance=resistance))
