import random
from point import Point, FoodPoint, AnthillPoint

class AbstractPointGenerator(object):
    def __init__(self, number_of_dimensions):
        self.number_of_dimensions = number_of_dimensions
    def generate_all(self, number_of_points):
        """ generator """
        assert number_of_points >= 2, 'number_of_points needs to be at least 2 to allow for anthill and food'
        yield AnthillPoint(self.generate_coordinates())
        yield FoodPoint(self.generate_coordinates(), 15)
        result_coordinates = {}
        while len(result_coordinates) < number_of_points-2:
            coordinates = self.generate_coordinates()
            if coordinates not in result_coordinates:
                point = Point(coordinates)
                result_coordinates[coordinates] = point
                yield point
    def generate_coordinates(self):
        raise NotImplementedError()

class SimplePointGenerator(AbstractPointGenerator):
    def __init__(self, number_of_dimensions, min_boundary, max_boundary):
        super(SimplePointGenerator, self).__init__(number_of_dimensions)
        self.min_boundary = min_boundary
        self.max_boundary = max_boundary
    def generate_coordinates(self):
        return tuple(
            [
                random.randint(self.min_boundary, self.max_boundary)
                for i in xrange(self.number_of_dimensions)
            ]
        )

