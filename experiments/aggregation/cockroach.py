import numpy as np
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

    def change_state(self,new_state):
        self.state = new_state

    def site_behavior(self):
        if self.pos == #check if cockroach is in the site which is round
            if self.state == "wandering":
                nr_neighbours = len(self.flock.find_neighbors(self, config["cockroach"]["radius_view"]))
                probability = config["base"]["n_agents"]/nr_neighbours
                if np.random.choice([True,False],p=[probability,1-probability]):
                    self.change_state("joining")

    def update_actions(self):