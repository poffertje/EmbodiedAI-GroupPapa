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
        self.min_bound = int(area(500,110)[0])
        self.max_bound = int(area(500,110)[1])

    def change_state(self,new_state):
        self.state = new_state

    def site_behavior(self):
        if self.state == "wandering":
            nr_neighbours = len(self.flock.find_neighbors(self, config["cockroach"]["radius_view"]))
            probability = float(0 if nr_neighbours == 0 else 1 - (1/nr_neighbours))
            if np.random.choice([True, False], p=[probability, 1 - probability]):
                self.join()
        elif self.state == "joining":
            if time.time() - self.time > 0.50:
                self.still()
            else:
                pass
        elif self.state == "still":
            self.counter += 1
            if self.counter % 100 == 0:
                nr_neighbours = len(self.flock.find_neighbors(self, config["cockroach"]["radius_view"]))
                probability = (config["base"]["n_agents"]-nr_neighbours)/config["base"]["n_agents"]
                if np.random.choice([True, False], p=[probability, 1 - probability]):
                    self.leave()
        elif self.state == "leaving":
            if time.time()-self.time > 5.0:
                self.state = 'wandering'

    def update_actions(self):
        # avoid any obstacles in the environment
        for obstacle in self.flock.objects.obstacles:
            collide = pygame.sprite.collide_mask(self, obstacle)
            if bool(collide):
                self.avoid_obstacle()

        # if the cockroach is inside an aggregation site, the site_behaviour function should determine what should be
        # done
        if self.pos[0] > self.min_bound and self.pos[0] < self.max_bound and self.pos[1] > self.min_bound and self.pos[1] < self.max_bound:
            self.site_behavior()

        # if the cockroach is outside the aggregation site, it should just wander (and if for some reason, the cockroach
        # is outside the site but in a different state, make sure to have it wander)
        else:
            if self.state != "wandering":
                self.change_state("wandering")
            else:
                pass

    def join(self):
        self.change_state("joining")
        self.time = time.time()

    def still(self):
        self.change_state("still")
        self.v = [0,0]

    def ___(self):
        self.change_state("wandering")
        self.set_velocity()

    def leave(self):
        self.change_state("leaving")
        self.time = time.time()
        self.v = self.set_velocity()