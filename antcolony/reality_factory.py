from environment import EnvironmentParameters
from world_generator_factory import SlightlyRandomizedWorldGeneratorFactory
from reality import Reality
from world import World

class RealityFactory(object):
    @classmethod
    def create_reality(cls, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, number_of_points, number_of_dimensions):
        #generator = SimpleWorldGeneratorFactory.create_world_generator(number_of_points, number_of_dimensions)
        generator = SlightlyRandomizedWorldGeneratorFactory.create_world_generator(number_of_points, number_of_dimensions)
        world = generator.generate()
        anthill = world.get_anthill()
        environment_parameters = EnvironmentParameters(min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, anthill)
        return Reality(world, environment_parameters)
    @classmethod
    def from_json_world(cls, json_world, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant):
        w = World.from_json(json_world)
        environment_parameters = EnvironmentParameters.from_world(w, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant)
        return Reality(w, environment_parameters)

if __name__=='__main__':
    from pprint import pprint
    reality = RealityFactory.create_reality(0, 1, 20, 2)
    pprint(reality)

