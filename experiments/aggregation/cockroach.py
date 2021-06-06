import numpy as np
import time
from experiments.aggregation.config import config
from simulation.agent import Agent
from simulation.utils import *


class Cockroach(Agent):
    """ """
    def __init__(
            self, pos, v, flock, state, index: int, image: str = "experiments/aggregation/images/ant.png"
    ) -> None:
        super(Cockroach, self).__init__(
            pos,
            v,
            image,
            max_speed=config["agent"]["max_speed"],
            min_speed=config["agent"]["min_speed"],
            mass=config["agent"]["mass"],
            width=config["agent"]["width"],
            height=config["agent"]["height"],
            dT=config["agent"]["dt"],
            index=index
        )
        self.state = state
        self.flock = flock
        self.time = 0
        self.counter = 0

    def change_state(self,new_state):
        self.state = new_state

    def site_behavior(self):
        min_bound = int(area(500,200)[0])
        max_bound = int(area(500,200)[1])
        if self.pos[0] and self.pos[1] in range(min_bound,max_bound):
            if self.state == "wandering":
                nr_neighbours = len(self.flock.find_neighbors(self, config["cockroach"]["radius_view"]))
                probability = nr_neighbours/config["base"]["n_agents"]
                print(probability)
                if np.random.choice([True,False],p=[probability,1-probability]):
                    self.change_state("joining")
                    self.time = time.time()
            elif self.state == "joining":
                if time.time()-self.time == 2.00:
                    self.change_state("still")
            elif self.state == "still":
                self.counter+=1
                if self.counter % 5 == 0:
                    nr_neighbours = len(self.flock.find_neighbors(self, config["cockroach"]["radius_view"]))
                    probability =  (config["base"]["n_agents"]-nr_neighbours)/config["base"]["n_agents"]
                    if np.random.choice([True, False], p=[probability, 1 - probability]):
                        self.change_state("leaving")
                        self.time = time.time()
        elif not(self.pos[0] and self.pos[1] in range(min_bound,max_bound)):
            if self.state == "leaving":
                if time.time()-self.time == 6.00:
                    self.change_state("wandering")

    def update_actions(self):
        # avoid any obstacles in the environment
        for obstacle in self.flock.objects.obstacles:
            collide = pygame.sprite.collide_mask(self, obstacle)
            if bool(collide):
                self.avoid_obstacle()

        self.site_behavior()