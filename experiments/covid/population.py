import time
import random
import pygame

from experiments.covid.config import config
from experiments.covid.person import Person
from simulation.swarm import Swarm
from simulation.utils import *
from experiments.covid.scenarios import scenario3 as scenario


class Population(Swarm):
    """Class that represents the Population for the Covid experiment. TODO"""

    def __init__(self, screen_size) -> None:
        super(Population, self).__init__(screen_size)
        self.lockdown = scenario()[0]

    def initialize(self, num_agents: int) -> None:
        """
        Args:
            num_agents (int):

        """
        # To Do
        # code snipet (not complete) to avoid initializing agents on obstacles
        # given some coordinates and obstacles in the environment, this repositions the agent
        if self.lockdown:
            self.add_lockdown()

        masked_agents = 0

        for index, agent in enumerate(range(num_agents)):
            coordinates = generate_coordinates(self.screen)

            #     if config["population"]["obstacles"]:  # you need to define this variable
            #         for obj in self.objects.obstacles:
            #             rel_coordinate = relative(
            #                 coordinates, (obj.rect[0], obj.rect[1])
            #             )
            #             try:
            #                 while obj.mask.get_at(rel_coordinate):
            #                     coordinates = generate_coordinates(self.screen)
            #                     rel_coordinate = relative(
            #                         coordinates, (obj.rect[0], obj.rect[1])
            #                     )
            #             except IndexError:
            #                 pass

            if masked_agents < config["base"]["n_agents"] * scenario()[2]:
                masked = True
                masked_agents += 1

            else:
                masked = False

            if index % 5 == 0:
                current_person = Person(pos=np.array(coordinates), v=None, flock=self, state="I", index=index,
                                        color=[255, 69, 0], timer=1,
                                        age=np.random.choice([random.randint(1, 25), random.randint(26, 64),
                                                              random.randint(65, 90)]
                                                             , p=[0.28, 0.52, 0.20]),
                                        recovery_time=random.randint(1000, 1400),
                                        social_distancing=np.random.choice([True, False],
                                                                           p=[scenario()[1], 1 - scenario()[1]]),
                                        mask_on=masked)
            else:
                current_person = Person(pos=np.array(coordinates), v=None, flock=self, state="S", index=index,
                                        color=[255, 165, 0], timer=None,
                                        age=np.random.choice(
                                            [random.randint(1, 25), random.randint(26, 64), random.randint(65, 90)]
                                            , p=[0.28, 0.52, 0.20]),
                                        recovery_time=None,
                                        social_distancing=np.random.choice([True, False],
                                                                           p=[scenario()[1], 1 - scenario()[1]]),
                                        mask_on=masked)
            self.check_border_collision(current_person)

            self.add_agent(current_person)

    def add_lockdown(self):
        obstacle_filename = "experiments/covid/images/Borders.png"
        obstacle_loc = [500, 500]
        obstacle_scale = [1000, 1000]
        self.objects.add_object(
            file=obstacle_filename, pos=obstacle_loc,
            scale=obstacle_scale, obj_type="obstacle", index=0
        )

    def check_border_collision(self, person):
        for obj in self.objects.obstacles:
            while True:
                collide = pygame.sprite.collide_mask(person, obj)
                if collide is not None:
                    person.pos = np.array(generate_coordinates(self.screen))
                else:
                    break
