import random
from math import sqrt
from point import Point, FoodPoint, AnthillPoint

class PointGeneratorException(Exception):
    pass

class CannotSetPointException(PointGeneratorException):
    pass

class CoordinatesExhaustedException(PointGeneratorException):
    pass

class AbstractPointGenerator(object):
    FOOD_AMOUNT = 1500
    def __init__(self, number_of_dimensions):
        self.number_of_dimensions = number_of_dimensions
    def _reliably_set_point(self, point_index, point_factory, coordinate_generator):
        """ creates an unique point and updates the index, or loops endlessly if creating a point is not possible """
        while 1:
            point = self._try_to_set_point(point_index, point_factory, coordinate_generator(), False)
            if point is not None:
                return point
    def _try_to_set_point(self, point_index, point_factory, coordinates, crash_on_error=False):
        if coordinates not in point_index:
            point = point_factory(coordinates)
            point_index[coordinates] = point
            return point
        elif crash_on_error:
            raise CannotSetPointException()
        return None
    def get_food_amount(self):
        return self.FOOD_AMOUNT
    def generate_all(self, number_of_points):
        """ generator! """
        assert number_of_points >= 2, 'number_of_points needs to be at least 2 to allow for anthill and food'
        point_index = {}
        yield self._generate_anthill(point_index)
        yield self._generate_foodpoint(point_index)
        while len(point_index) < number_of_points:
            yield self._reliably_set_point(point_index, Point, self._generate_coordinates)
    def _generate_anthill(self, point_index):
        return self._reliably_set_point(point_index, AnthillPoint, self._generate_coordinates)
    def _generate_foodpoint(self, point_index):
        return self._reliably_set_point(point_index, lambda coords: FoodPoint(coords, self.get_food_amount()), self._generate_coordinates)
    def _generate_symmetrical_coordinates(self, value):
        return tuple(
            [
                value
                for i in xrange(self.number_of_dimensions)
            ]
        )
    def _generate_coordinates(self):
        raise NotImplementedError()

class SimplePointGenerator(AbstractPointGenerator):
    def __init__(self, number_of_dimensions, min_boundary, max_boundary):
        super(SimplePointGenerator, self).__init__(number_of_dimensions)
        assert min_boundary <= max_boundary
        self.min_boundary = min_boundary
        self.max_boundary = max_boundary
    def _get_width(self):
        return self.max_boundary - self.min_boundary +1
    def _generate_coordinates(self):
        return tuple(
            [
                random.randint(self.min_boundary, self.max_boundary-1)
                for i in xrange(self.number_of_dimensions)
            ]
        )

class AbstractLimitedNumberPointGenerator(SimplePointGenerator):
    def __init__(self, number_of_dimensions, min_boundary, max_boundary, *args, **kwargs):
        super(AbstractLimitedNumberPointGenerator, self).__init__(number_of_dimensions, min_boundary, max_boundary, *args, **kwargs)
        self.points_returned = 0
        self.max_points = None # child class needs to set this
    def _try_to_set_point(self, point_index, point_factory, coords, crash_on_error=False):
        #if self.points_returned > 9:
        #    print self.points_returned
        #    raw_input()
        if self.max_points - self.points_returned <= 0:
            raise CoordinatesExhaustedException()
        point = super(AbstractLimitedNumberPointGenerator, self)._try_to_set_point(point_index, point_factory, coords, crash_on_error)
        if point is not None: # anthill or foodpoint could have already been placed
            self.points_returned += 1
        return point

class ChessboardPointGenerator(AbstractLimitedNumberPointGenerator):
    ANTHILL_DISTANCE_FROM_CHESSBOARD_CORNER = 0.2
    FOODPOINT_DISTANCE_FROM_CHESSBOARD_CORNER = 0.7
    def __init__(self, number_of_dimensions, min_boundary, max_boundary, *args, **kwargs):
        super(ChessboardPointGenerator, self).__init__(number_of_dimensions, min_boundary, max_boundary, *args, **kwargs)
        self.max_points = (max_boundary - min_boundary)**number_of_dimensions
        self.counter = 0
    def _generate_point_on_diagonal(self, point_index, point_factory, distance_from_corner):
        width = self._get_width()-1
        coords = self._generate_symmetrical_coordinates(self.min_boundary + round(width * distance_from_corner))
        point = self._try_to_set_point(point_index, point_factory, coords, True)
        return point
    def _generate_anthill(self, point_index):
        return self._generate_point_on_diagonal(point_index, AnthillPoint, self.ANTHILL_DISTANCE_FROM_CHESSBOARD_CORNER)
    def _generate_foodpoint(self, point_index):
        return self._generate_point_on_diagonal(point_index, lambda coords: FoodPoint(coords, self.get_food_amount()), self.FOODPOINT_DISTANCE_FROM_CHESSBOARD_CORNER)
    def _generate_coordinates(self):
        max_value = self._get_width() -1
        result = []
        for dimension_number in reversed(xrange(self.number_of_dimensions)):
            value = self.min_boundary + (self.counter / (max_value**dimension_number) % max_value )
            result.append(value)
        # uncomment those for testing
        #print self.points_returned, result, width
        #self.points_returned += 1
        self.counter += 1
        return tuple(result)

class HexagonPointGenerator(AbstractLimitedNumberPointGenerator):
    def __init__(self, number_of_dimensions, min_boundary, max_boundary, *args, **kwargs):
        super(HexagonPointGenerator, self).__init__(number_of_dimensions, min_boundary, max_boundary, *args, **kwargs)
        assert number_of_dimensions == 2
        self.max_points = 2+6+1
        self.counter = 0
    def generate_all(self, number_of_points):
        """ generator! """
        assert number_of_points >= 2, 'number_of_points needs to be at least 2 to allow for anthill and food'
        #assert number_of_points == self.max_points, '%s can only generate %d-point worlds' % (self.__class__.__name__, self.max_points)

        L = self._get_width() / 2.0 -2
        result = []
        result.append( (L, 0) )
        result.append( (L / 2.0, L * sqrt(3) / 2.0) )
        result.append( (-L / 2.0, L * sqrt(3) / 2.0) )
        result.append( (-L, 0) )
        result.append( (-L / 2.0, -L * sqrt(3) / 2.0) )
        result.append( (L / 2.0, -L * sqrt(3) / 2.0) )

        result.append( (0, 0) )

        yield AnthillPoint(
            #(0, 0)
            (-2.5, 2.5)
        )
        yield FoodPoint(
            #(self.max_boundary, self.max_boundary),
            (self.max_boundary+2.5, self.max_boundary-2.5),
            self.get_food_amount()
        )

        i = 0
        while i < len(result):
            x, y = result[i]
            result[i] = (x+L+1, y+L+1)
            yield Point(result[i])
            i += 1
        # uncomment those for testing
        #print self.points_returned, result, width
        #self.points_returned += 1
        #self.counter += 1
        #return tuple(result)


if __name__=='__main__':
    from pprint import pprint
    pprint(list(HexagonPointGenerator(2, 0, 10).generate_all(9)))
    #generator_2d = ChessboardPointGenerator(number_of_dimensions=2, min_boundary=0, max_boundary=1)
    #assert generator_2d._generate_coordinates() == (0, 0)
    #assert generator_2d._generate_coordinates() == (0, 1)
    #assert generator_2d._generate_coordinates() == (1, 0)
    #assert generator_2d._generate_coordinates() == (1, 1)

    #generator_3d = ChessboardPointGenerator(number_of_dimensions=3, min_boundary=0, max_boundary=1)
    #assert generator_3d._generate_coordinates() == (0, 0, 0)
    #assert generator_3d._generate_coordinates() == (0, 0, 1)
    #assert generator_3d._generate_coordinates() == (0, 1, 0)
    #assert generator_3d._generate_coordinates() == (0, 1, 1)
    #assert generator_3d._generate_coordinates() == (1, 0, 0)
    #assert generator_3d._generate_coordinates() == (1, 0, 1)
    #assert generator_3d._generate_coordinates() == (1, 1, 0)
    #assert generator_3d._generate_coordinates() == (1, 1, 1)

