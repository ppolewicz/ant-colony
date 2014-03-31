from point_generator import SimplePointGenerator, ChessboardPointGenerator, HexagonPointGenerator
from edge_generator import ChessboardEdgeGenerator, CrossedChessboardEdgeGenerator, LimitedQuantityEdgeGenerator, LimitedRangeEdgeGenerator
from edge_cost_generator import DistanceEdgeCostGenerator, DistanceFromCornersEdgeCostGenerator, RandomCoefficientEdgeCostGenerator
from util import Corner
from world_generator import SimpleWorldGenerator

class AbstractWorldGeneratorFactory(object):
    """ generates N-dimensional worlds """
    @classmethod
    def create_world_generator(cls, number_of_dimensions, *args, **kwargs):
        raise NotImplementedError()

class DistanceCostWorldGeneratorFactory(AbstractWorldGeneratorFactory):
    """ generates worlds with edge costs equal to distance between the points """
    @classmethod
    def _get_edge_cost_generator(cls):
        return DistanceEdgeCostGenerator()

class CertainPointNumberWorldGeneratorFactory(AbstractWorldGeneratorFactory):
    EDGE_GENERATOR_CLASS = None
    @classmethod
    def create_world_generator(cls, number_of_dimensions, number_of_points):
        point_generator = cls._get_point_generator()
        edge_generator = cls.EDGE_GENERATOR_CLASS()
        edge_cost_generator = cls._get_edge_cost_generator()
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, edge_cost_generator, number_of_points)

class SimpleWorldGeneratorFactory(DistanceCostWorldGeneratorFactory, CertainPointNumberWorldGeneratorFactory):
    EDGE_GENERATOR_CLASS = LimitedQuantityEdgeGenerator
    @classmethod
    def _get_point_generator(cls, number_of_dimensions, number_of_points):
        return SimplePointGenerator(number_of_dimensions, 0, 100)

class SlightlyRandomizedWorldGeneratorFactory(SimpleWorldGeneratorFactory):
    """ generates worlds with edge costs only slightly different than the distance between the points """
    @classmethod
    def _get_edge_cost_generator(cls):
        return RandomCoefficientEdgeCostGenerator(0.8, 1.2)

class AbstractCustomWidthWorldGeneratorFactory(DistanceCostWorldGeneratorFactory):
    EDGE_GENERATOR_CLASS = None
    POINT_GENERATOR_CLASS = None
    @classmethod
    def _get_number_of_points(cls, number_of_dimensions, width):
        return width ** number_of_dimensions
    @classmethod
    def create_world_generator(cls, number_of_dimensions, width):
        point_generator = cls.POINT_GENERATOR_CLASS(number_of_dimensions, 0, width)
        edge_generator = cls.EDGE_GENERATOR_CLASS()
        edge_cost_generator = cls._get_edge_cost_generator()
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, edge_cost_generator, cls._get_number_of_points(number_of_dimensions, width))

class ChessboardWorldGeneratorFactory(AbstractCustomWidthWorldGeneratorFactory):
    """ generates n-dimensional raster-shaped worlds with equal edge costs equal to the distance between the points, like this:
        *----*----*
        |    |    |
        |    |    |
        |    |    |
        |    |    |
        *----*----*
        |    |    |
        |    |    |
        |    |    |
        |    |    |
        *----*----*
        """
    EDGE_GENERATOR_CLASS = ChessboardEdgeGenerator
    POINT_GENERATOR_CLASS = ChessboardPointGenerator

class CrossedChessboardWorldGeneratorFactory(ChessboardWorldGeneratorFactory):
    """ generates 2-dimensional raster-shaped worlds with equal edge costs equal to the distance between the points, like this:
        *----*----*
        |\  /|\  /|
        | \/ | \/ |
        | /\ | /\ |
        |/  \|/  \|
        *----*----*
        |\  /|\  /|
        | \/ | \/ |
        | /\ | /\ |
        |/  \|/  \|
        *----*----*
        """
    EDGE_GENERATOR_CLASS = CrossedChessboardEdgeGenerator

class UpperLeftCornerDistanceCrossedChessboardWorldGeneratorFactory(CrossedChessboardWorldGeneratorFactory):
    @classmethod
    def _get_edge_cost_generator(cls):
        return DistanceFromCornersEdgeCostGenerator([Corner.UPPER_LEFT])

class HexagonWorldGeneratorFactory(AbstractCustomWidthWorldGeneratorFactory):
    EDGE_GENERATOR_CLASS = LimitedRangeEdgeGenerator
    POINT_GENERATOR_CLASS = HexagonPointGenerator
    @classmethod
    def _get_number_of_points(cls, number_of_dimensions, width):
        return 9
    @classmethod
    def _get_edge_cost_generator(cls):
        return RandomCoefficientEdgeCostGenerator(0.5, 2.0)
