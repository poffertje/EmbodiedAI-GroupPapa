from experiments.aggregation.cockroach import Cockroach
from experiments.aggregation.config import config
from experiments.aggregation.scenarios import experiment0
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

        aggregation_loc, aggregation_scale, _ = experiment0(self.screen)
        aggregation_filename = "experiments/aggregation/images/greyc1.png"

        "Add aggregation site"
        self.objects.add_object(
            file=aggregation_filename, pos=aggregation_loc, scale=aggregation_scale, obj_type="site"
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

            self.add_agent(Cockroach(pos=np.array(coordinates), v=None, flock=self, state="wandering", index=index))