from experiments.aggregation.cockroach import Cockroach
from experiments.aggregation.config import config
from experiments.aggregation.scenarios import experiment0, experiment1, experiment2
from simulation.utils import *
from simulation.swarm import Swarm


class Aggregations(Swarm):
    """ """
    def __init__(self, screen_size) -> None:
        super(Aggregations, self).__init__(screen_size)

    def initialize(self, num_agents: int) -> None:

        obstacle_loc = config["base"]["object_location"]
        obstacle_scale = [700, 700]
        obstacle_filename = "experiments/flocking/images/redd.png"

        "Add containing object (outer circle)"
        self.objects.add_object(
            file=obstacle_filename, pos=obstacle_loc, scale=obstacle_scale, obj_type="obstacle"
        )

        if config["base"]["experiment"] == 'experiment 1':
            aggregation_loc1, aggregation_loc2, aggregation_scale1, aggregation_scale2, big = experiment1(self.screen)
        else:
            aggregation_loc1, aggregation_loc2, aggregation_scale1, aggregation_scale2, big = experiment2(self.screen)
        aggregation_filename = "experiments/aggregation/images/greyc1.png"


        self.objects.add_object(
            file=aggregation_filename if not(big) else "experiments/aggregation/images/greyc2.png", pos=aggregation_loc1, scale=aggregation_scale1, obj_type="site"
        )

        self.objects.add_object(
            file=aggregation_filename, pos=aggregation_loc2, scale=aggregation_scale2, obj_type="site"
        )

        min_x, max_x = area(obstacle_loc[0], obstacle_scale[0])
        min_y, max_y = area(obstacle_loc[1], obstacle_scale[1])

        # add agents to the environment
        for index, agent in enumerate(range(num_agents)):
            coordinates = generate_coordinates(self.screen)

            while (
                    coordinates[0] >= max_x
                    or coordinates[0] <= min_x
                    or coordinates[1] >= max_y
                    or coordinates[1] <= min_y
            ):
                coordinates = generate_coordinates(self.screen)
            # if int(index) % 5 == 0:
            #     self.add_agent(Cockroach(pos=np.array(coordinates), v=None, flock=self, state="wandering", index=index,
            #                              leader=True, image=None, color=(0, 0, 255)))
            # else:
            self.add_agent(Cockroach(pos=np.array(coordinates), v=None, flock=self, state="wandering", index=index,
                                    leader=False, image="experiments/aggregation/images/ant.png", color=None,
                                    loc1=aggregation_loc1,loc2 = aggregation_loc2, scale1= aggregation_scale1,
                                    scale2 = aggregation_scale2))