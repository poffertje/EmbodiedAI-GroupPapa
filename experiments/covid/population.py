from experiments.covid.config import config
from experiments.covid.person import Person
from experiments.covid.scenarios import scenario6 as scenario
from simulation.swarm import Swarm
from simulation.utils import generate_coordinates
from pygame.sprite import collide_mask
import numpy as np
PR_SEVERE = config["base"]["percentage_underlying"]


class Population(Swarm):
    """Class that represents the Population for the Covid experiment. TODO"""

    def __init__(self, screen_size) -> None:
        super(Population, self).__init__(screen_size)
        self.lockdown = scenario()[0]
        self.airport = scenario()[5]
        self.borders = scenario()[8]
        self.hospital = scenario()[9]

    def initialize(self, num_agents: int) -> None:
        """
        Args:
            num_agents (int):

        """
        # To Do
        # code snippet (not complete) to avoid initializing agents on obstacles
        # given some coordinates and obstacles in the environment, this repositions the agent
        if self.lockdown:
            self.add_lockdown()

        if self.airport:
            self.add_airport()

        if self.hospital:
            self.add_hospital()

        if self.borders:
            self.add_outer_border()

        masked_agents = 0
        underlying_conditions = 0
        infection_probability = 0.1
        underlying_conditions_proportion = round(config["base"]["percentage_underlying"] * config["base"]["n_agents"])
        severe_agents = 0
        for index, agent in enumerate(range(num_agents)):
            coordinates = generate_coordinates(self.screen)
            infected_color = [255, 69, 0]
            state = "I"

            if masked_agents < config["base"]["n_agents"] * scenario()[2]:
                masked = True
                masked_agents += 1
            else:
                masked = False

            if underlying_conditions < underlying_conditions_proportion:
                conditions = True
                severe = np.random.choice([True, False], p=[PR_SEVERE, 1 - PR_SEVERE])
                if severe_agents <= 30:
                    severe = True
                    infected_color = [128, 0, 0]
                    infection_probability = np.random.uniform(0.5, 0.6)
                    state = "C"
                    severe_agents += 1
                underlying_conditions += 1
            else:
                conditions = False

            age = np.random.choice([np.random.randint(1, 25), np.random.randint(26, 64),
                                                              np.random.randint(65, 90)]
                                                             , p=[0.28, 0.52, 0.20])
            if index % 5 == 0:
                current_person = Person(pos=np.array(coordinates), v=None, flock=self, state=state, index=index,
                                        color=infected_color, timer=1,
                                        age=age,
                                        recovery_time=np.random.randint(1000, 1400),
                                        social_distancing=np.random.choice([True, False],
                                                                           p=[scenario()[1], 1 - scenario()[1]]),
                                        mask_on=masked, infection_probability=infection_probability, underlying_conditions=conditions,
                                        severe_case=severe,vaccinated=False,vaccination_timer=None)
            else:
                if conditions:
                    vaccination_timer = 50
                elif 70 <= age <= 90:
                    vaccination_timer = 300
                elif 50 <= age <= 69:
                    vaccination_timer = 600
                elif 40 <= age <= 49:
                    vaccination_timer = 900
                else:
                    vaccination_timer = 1200
                current_person = Person(pos=np.array(coordinates), v=None, flock=self, state="S", index=index,
                                        color=[255, 165, 0], timer=None,
                                        age=age,
                                        recovery_time=None,
                                        social_distancing=np.random.choice([True, False],
                                                                           p=[scenario()[1], 1 - scenario()[1]]),
                                        mask_on=masked, infection_probability=infection_probability, underlying_conditions=conditions,
                                        severe_case=False, vaccinated=False, vaccination_timer=vaccination_timer)
            self.check_border_collision(current_person)
            self.add_agent(current_person)

    def add_outer_border(self):
        obstacle_filename = "experiments/covid/images/Borders.png"
        obstacle_loc = [500, 500]
        obstacle_scale = [1000, 1000]
        self.objects.add_object(
            file=obstacle_filename, pos=obstacle_loc,
            scale=obstacle_scale, obj_type="obstacle", index=0
        )

    def add_hospital(self):
        logo_filename = "experiments/covid/images/Pharmacy.png"

        bed_filename = "experiments/covid/images/Bed.png"
        hospital_filename = "experiments/covid/images/HospitalClosed.png"
        hospital_loc = [500, 500]
        hospital_scale = [1000, 1000]

        self.objects.add_object(
            file=hospital_filename, pos=hospital_loc,
            scale=hospital_scale, obj_type="obstacle", index=-14
        )

        self.objects.add_object(
            file=logo_filename, pos=[790, 105],
            scale=[40, 40], obj_type="site", index=-15)

        addition = 0

        for i in range(12):
            if i < 4:
                self.objects.add_object(
                    file=bed_filename, pos=[730 + addition, 155],
                    scale=[25, 25], obj_type="site", index=-i - 2
                )
                addition += 40
            if i >= 4 and i < 8:
                if i == 4:
                    addition = 0
                self.objects.add_object(
                    file=bed_filename, pos=[730 + addition, 210],
                    scale=[25, 25], obj_type="site", index=-i - 2
                )
                addition += 40
            if i >= 8 and i < 12:
                if i == 8:
                    addition = 0
                self.objects.add_object(
                    file=bed_filename, pos=[730 + addition, 265],
                    scale=[25, 25], obj_type="site", index=-i - 2
                )
                addition += 40

    def add_airport(self):
        obstacle_filename = "experiments/covid/images/BordersAirport.png"
        obstacle_loc = [500, 500]
        obstacle_scale = [1000, 1000]
        self.objects.add_object(
            file=obstacle_filename, pos=obstacle_loc,
            scale=obstacle_scale, obj_type="obstacle", index=0
        )
        self.objects.add_object(file="experiments/covid/images/airport.png", pos=[210, 210],
                                scale=[150, 150], obj_type="site", index=-1)

    def check_border_collision(self, person):
        for obj in self.objects.obstacles:
            while True:
                if self.airport:
                    while 120 <= person.pos[0] <= 330 and 120 <= person.pos[1] <= 330:
                        person.pos = np.array(generate_coordinates(self.screen))

                if self.hospital:
                    while 685 <= person.pos[0] <= 895 and 105 <= person.pos[1] <= 315:
                        person.pos = np.array(generate_coordinates(self.screen))

                collide = collide_mask(person, obj)
                if collide is not None:
                    person.pos = np.array(generate_coordinates(self.screen))
                else:
                    break
