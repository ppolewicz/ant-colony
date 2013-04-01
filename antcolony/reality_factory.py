from environment import EnvironmentParameters
from world_generator_factory import SlightlyRandomizedWorldGeneratorFactory
from reality import Reality

class RealityFactory(object):
    @classmethod
    def create_reality(cls, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, number_of_points, number_of_dimensions):
        #generator = SimpleWorldGeneratorFactory.create_world_generator(number_of_points, number_of_dimensions)
        generator = SlightlyRandomizedWorldGeneratorFactory.create_world_generator(number_of_points, number_of_dimensions)
        world = generator.generate()
        anthill = world.get_anthill()
        environment_parameters = EnvironmentParameters(min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, anthill)
        return Reality(world, environment_parameters)


if __name__=='__main__':
    from pprint import pprint
    reality = RealityFactory.create_reality(0, 1, 20, 2)
    pprint(reality)


