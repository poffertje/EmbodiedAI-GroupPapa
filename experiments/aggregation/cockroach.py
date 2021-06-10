import numpy as np
import time
from experiments.aggregation.config import config
from simulation.agent import Agent
from simulation.utils import *
import matplotlib.pyplot as plt


class Cockroach(Agent):
    """ """

    def __init__(
            self, pos, v, flock, state, index: int, leader, image, color, loc1,
            loc2,scale1,scale2
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
            index=index,
            color=color,
        )
        self.avoided_obstacles: bool = False
        self.prev_pos = None
        self.prev_v = None
        self.state = state
        self.flock = flock
        self.time = 0
        self.counter = 0
        self.site_name = ""
        self.loc1 = loc1
        self.scale1 = scale1
        self.min_bound1 = int(area(loc1[0], scale1[0])[0]) + 5
        self.max_bound1 = int(area(loc1[0], scale1[0])[1]) - 5
        self.radius1 = (self.max_bound1 - self.min_bound1)/2
        self.loc2 = loc2
        self.scale2 = scale2
        self.min_bound2 = int(area(loc2[0], scale2[0])[0]) + 5
        self.max_bound2 = int(area(loc2[0], scale2[0])[1]) - 5
        self.radius2 = (self.max_bound2 - self.min_bound2)/2

        self.leader = leader
        self.timer = time.time()
        self.largest_site_pos = [0, 0]
        self.largest_site_size = 0
        self.largest_radius = 0

    def change_state(self, new_state):
        self.state = new_state

    def site_behavior(self, site_name, leader):
        if leader:
            # Wandering state
            if self.state == "wandering":
                self.join()

            # Joining state
            elif self.state == "joining":
                # Update the attribute to evaluate the number of agents
                self.site_name = site_name
                if self.site_name == "site1":
                    Agent.set_color(self,(255,0,0))
                current_site_pos, current_site_size, radius = site_info(site_name)
                if current_site_size > self.largest_site_size:
                    self.largest_site_size = current_site_size
                    self.largest_site_pos = current_site_pos
                    self.largest_radius = radius

                elif time.time() - self.time > 0.25:
                    self.still()
                else:
                    pass

            # Still state
            elif self.state == "still":
                self.leave()

            # Leaving state
            elif self.state == "leaving":
                if time.time() - self.time > 5.0:
                    self.state = 'wandering'

        elif not(leader):
            # Wandering state
            if self.state == "wandering":
                # Get number of still neighbours
                nr_neighbours = self.count_still_neighbours()
                if nr_neighbours >= 0 and nr_neighbours <= 5:
                    probability = 0.05
                elif nr_neighbours > 5 and nr_neighbours <= 10:
                    probability = 0.10
                else:
                    probability = 0.50
                # print("Joining probability: %f" % probability)
                if np.random.choice([True, False], p=[probability, 1 - probability]):
                    self.join()

            # Joining state
            elif self.state == "joining":
                # Update the attribute to evaluate the number of agents
                self.site_name = site_name
                if time.time() - self.time > np.random.normal(0.25, 0.1, 1):
                    self.still()
                else:
                    pass

            # Still state
            elif self.state == "still":
                self.counter += 1
                # Every 200 iterations consider leaving
                if self.counter % 200 == 0:
                    nr_neighbours = self.count_still_neighbours()
                    # probability = 1/np.exp(np.log(nr_neighbours+1)/np.log(10))
                    a, h, k = 3.2, 1.5, 0.6
                    probability = (a * np.exp((-k) * (nr_neighbours) + h)) + 0.02
                    if probability > 1:
                        probability = 1
                    # print("Leaving probability: %f" % probability)
                    if np.random.choice([True, False], p=[probability, 1 - probability]):
                        self.leave()

            # Leaving state
            elif self.state == "leaving":
                if time.time() - self.time > 5.0:
                    self.state = 'wandering'

    # Update the state of the roach
    def update_actions(self):
        # Call to evaluate the agents on site
        self.evaluate()
        # Avoid obstacles
        self.check_for_obstacles()

        # If a cockroach is inside an aggregation site, the site_behaviour function should determine
        # what the next action is going to be
        if (time.time() - self.timer < config["cockroach"]["explore_timer"] and self.leader) or not(self.leader):
            if isInside(self.loc1[0], self.loc1[1], self.radius1, self.pos[0],
                        self.pos[1]):
                self.site_behavior("site1", self.leader)

            elif isInside(self.loc2[0], self.loc2[1], self.radius2,self.pos[0],
                          self.pos[1]):
                self.site_behavior("site2", self.leader)
            else:
                # If the cockroach is outside the aggregation site, it should just wander (and if for some reason, the cockroach
                # is outside the site but in a different state, make sure to have it wander)
                if np.random.choice([True, False], p=[0.1, 0.9]):
                    # Wiggle motion
                    if (self.leader and time.time() - self.timer < config["cockroach"]["explore_timer"]) or not (
                    self.leader):
                        self.v = self.wander(randrange(0,30),randrange(-10,10),randrange(0,180))
                if self.state != "wandering":
                    self.change_state("wandering")
                else:
                    pass

        elif time.time() - self.timer >= config["cockroach"]["explore_timer"] and self.leader and self.state != "still":
            self.counter += 1
            if self.counter == 1:
                self.state = "wandering"
                if self.largest_site_size != 0:
                    self.v = [self.largest_site_pos[0] - self.pos[0], self.largest_site_pos[1] - self.pos[1]]
            elif self.largest_site_pos != [0, 0]:
                if isInside(self.largest_site_pos[0], self.largest_site_pos[1], self.largest_radius, self.pos[0],
                            self.pos[1]):
                    if self.state != "joining":
                        self.join()
                    elif self.state == "joining":
                        if time.time() - self.time > randrange(1, 3):
                            self.still()

    def join(self):
        self.change_state("joining")
        self.time = time.time()

    def still(self):
        self.change_state("still")
        self.v = [0, 0]

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
        count_wandering_agents = 0

        # Access the list of all agents and add one to the counter for each instance of cockroach with state "still"
        for agent in self.flock.agents:
            # Check whether agent is in "still" state
            if agent.state == "still":
                if agent.site_name == "site1":
                    count_on_site_agents_1 += 1
                elif agent.site_name == "site2":
                    count_on_site_agents_2 += 1
            else:
                count_wandering_agents += 1

        # Comment/uncomment as needed
        # print("Number of roaches on site 1: %s" % count_on_site_agents_1)
        # print("Number of roaches on site 2: %d" % count_on_site_agents_2)

        return count_on_site_agents_1, count_on_site_agents_2, count_wandering_agents

    def count_still_neighbours(self):
        # Find all current neighbours
        neighbours = self.flock.find_neighbors(self, config["cockroach"]["radius_view"])

        still_neighbours = []
        # For each neighbour in the list check which ones are still
        for neighbour in neighbours:
            if neighbour.state == "still" or neighbour.state == "joining":
                still_neighbours.append(neighbour)

        nr_neighbours = len(still_neighbours)

        return nr_neighbours

    def check_for_obstacles(self):
        # Avoid any obstacles in the environment
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
