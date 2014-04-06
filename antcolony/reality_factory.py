from environment import EnvironmentParameters
from world_generator_factory import ChessboardWorldGeneratorFactory, CrossedChessboardWorldGeneratorFactory, HexagonWorldGeneratorFactory, SimpleWorldGeneratorFactory, SlightlyRandomizedWorldGeneratorFactory, UpperLeftCornerDistanceCrossedChessboardWorldGeneratorFactory, UpperLeftCornerDistanceHexagonWorldGeneratorFactory
from reality import Reality
from world import World

class JsonRealityDeserializer(object):
    @classmethod
    def from_json_world(cls, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, json_world):
        world = World.from_json(json_world)
        environment_parameters = EnvironmentParameters.from_world(world, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant)
        return Reality(world, environment_parameters)

class AbstractRealityFactory(object):
    @classmethod
    def create_reality(cls, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, number_of_dimensions, *args, **kwargs):
        generator = cls.get_generator(number_of_dimensions, *args, **kwargs)
        world = generator.generate()
        environment_parameters = EnvironmentParameters.from_world(world, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant)
        return Reality(world, environment_parameters)

class SimpleRealityFactory(AbstractRealityFactory):
    @classmethod
    def get_generator(cls, number_of_dimensions, number_of_points):
        return SimpleWorldGeneratorFactory.create_world_generator(number_of_dimensions, number_of_points)

class SlightlyRandomizedRealityFactory(AbstractRealityFactory):
    @classmethod
    def get_generator(cls, number_of_dimensions, number_of_points):
        return SlightlyRandomizedWorldGeneratorFactory.create_world_generator(number_of_dimensions, number_of_points)

class ChessboardRealityFactory(AbstractRealityFactory):
    @classmethod
    def get_generator(cls, number_of_dimensions, width):
        return ChessboardWorldGeneratorFactory.create_world_generator(number_of_dimensions, width)

class CrossedChessboardRealityFactory(AbstractRealityFactory):
    @classmethod
    def get_generator(cls, number_of_dimensions, width):
        return CrossedChessboardWorldGeneratorFactory.create_world_generator(number_of_dimensions, width)

class HexagonRealityFactory(AbstractRealityFactory):
    @classmethod
    def get_generator(cls, number_of_dimensions, width):
        return HexagonWorldGeneratorFactory.create_world_generator(number_of_dimensions, width)

class UpperLeftCornerDistanceCrossedChessboardRealityFactory(AbstractRealityFactory):
    @classmethod
    def get_generator(cls, number_of_dimensions, width):
        return UpperLeftCornerDistanceCrossedChessboardWorldGeneratorFactory.create_world_generator(number_of_dimensions, width)

class UpperLeftCornerDistanceHexagonRealityFactory(AbstractRealityFactory):
    @classmethod
    def get_generator(cls, number_of_dimensions, width):
        return UpperLeftCornerDistanceHexagonWorldGeneratorFactory.create_world_generator(number_of_dimensions, width)



if __name__=='__main__':
    from pprint import pprint
    #reality = SlightlyRandomizedRealityFactory.create_reality(0, 1, 2, 20)
    reality = ChessboardRealityFactory.create_reality(0, 1, 2, 10)
    pprint(reality)
    print len(reality.world.points), len(reality.world.edges)

