import numpy as np
import time
from experiments.aggregation.config import config
from simulation.agent import Agent
from simulation.utils import *
import matplotlib.pyplot as plt

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
        self.avoided_obstacles: bool = False
        self.prev_pos = None
        self.prev_v = None
        self.state = state
        self.flock = flock
        self.time = 0
        self.counter = 0
        self.site_name = ""
        # self.min_bound = int(area(config["base"]["object_location"][0],110)[0])+5
        # self.max_bound = int(area(config["base"]["object_location"][1],110)[1])-5
        self.min_bound1 = int(area(config["base"]["site1_location"][0],90)[0])+5
        self.max_bound1 = int(area(config["base"]["site1_location"][0],90)[1])-5
        self.min_bound2 = int(area(config["base"]["site2_location"][0],90)[0])+5
        self.max_bound2 = int(area(config["base"]["site2_location"][0],90)[1])-5
        self.T0 = 1
        self.t = self.T0
        self.C = 0.1
        self.T = self.T0

    def change_state(self, new_state):
        self.state = new_state

    def site_behavior(self,site_name):
        if self.state == "wandering":
            neighbours = self.flock.find_neighbors(self, config["cockroach"]["radius_view"])
            still_neighbours = []
            for neighbour in neighbours:
                if neighbour.state == "still" or neighbour.state == "joining":
                    still_neighbours.append(neighbour)
            if len(still_neighbours) > 5:
                nr_neighbours = len(still_neighbours)
            else:
                nr_neighbours = len(neighbours)
            probability = float(0 if nr_neighbours == 0 else 1 - (1/nr_neighbours))
            if np.random.choice([True, False], p=[probability, 1 - probability]):
                self.join()
        elif self.state == "joining":
            self.site_name = site_name
            if time.time() - self.time > 0.25:
                self.still()
            else:
                pass
        elif self.state == "still":
            self.counter += 1
            if self.counter % 200 == 0:
                nr_neighbours = len(self.flock.find_neighbors(self, config["cockroach"]["radius_view"]))
                #if nr_neighbours > 6:
                probability = (1/nr_neighbours)**(1/self.T)
                # print(probability)
                    #probability = 1/(nr_neighbours*2)
                if np.random.choice([True, False], p=[probability, 1-probability]):
                    self.leave()
        elif self.state == "leaving":
            if time.time()-self.time > 5.0:
                self.state = 'wandering'
    #update action
    def update_actions(self):
        # Call to evaluate the agents on site
        self.evaluate()

        # avoid any obstacles in the environment
        for obstacle in self.flock.objects.obstacles:
            collide = pygame.sprite.collide_mask(self, obstacle)
            if bool(collide):
                # If boid gets stuck because when avoiding the obstacle ended up inside of the object,
                # resets the position to the previous one and do a 180 degree turn back
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

        self.t += 1
        self.T = np.power((self.C * np.log(self.t + self.T0)), -1)
        # if the cockroach is inside an aggregation site, the site_behaviour function should determine what should be
        # done
        # if isInside(config["base"]["object_location"][0],config["base"]["object_location"][1],(self.max_bound-self.min_bound)/2,self.pos[0],self.pos[1]):
        #     self.site_behavior()

        if isInside(config["base"]["site1_location"][0],config["base"]["site1_location"][1],(self.max_bound1-self.min_bound1)/2,self.pos[0],self.pos[1]):
            self.site_behavior("site1")

        elif isInside(config["base"]["site2_location"][0],config["base"]["site2_location"][1],(self.max_bound2-self.min_bound2)/2,self.pos[0],self.pos[1]):
            self.site_behavior("site2")


        # if the cockroach is outside the aggregation site, it should just wander (and if for some reason, the cockroach
        # is outside the site but in a different state, make sure to have it wander)
        else:
            if np.random.choice([True, False], p=[0.1,0.9]):
                self.v += [randrange(-5,5),randrange(-5,5)]
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

    def evaluate(self):
        # This is used to calculate the agents currently on site
        count_on_site_agents_1 = 0
        count_on_site_agents_2 = 0

        # Access the list of all agents and add one to the counter for each instance of cockroach with state "still"
        for agent in self.flock.agents:
            if agent.state == "still":
                if agent.site_name == "site1":
                    count_on_site_agents_1 += 1
                elif agent.site_name == "site2":
                    count_on_site_agents_2 += 1

        # Comment/uncomment as needed
        print("Number of roaches on site 1: %s" % count_on_site_agents_1)
        print("Number of roaches on site 2: %d" % count_on_site_agents_2)
