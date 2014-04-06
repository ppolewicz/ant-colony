from math import hypot
from point import distance_between_points
import random

from util import corner_coordinates, get_average_coordinates

class AbstractEdgeCostGenerator(object):
    def __init__(self, exponent=1):
        self.exponent = exponent
    def register_points(self, points):
        pass
    def get_edge_cost(self, source_point, target_point):
        raise NotImplementedError('%s failed to overload get_edge_cost' % (self.__class__.__name__,))

class DistanceEdgeCostGenerator(AbstractEdgeCostGenerator):
    def get_edge_cost(self, *args, **kwargs):
        return distance_between_points(*args, **kwargs) ** self.exponent

class RandomCoefficientEdgeCostGenerator(DistanceEdgeCostGenerator):
    def __init__(self, min_random_coefficient, max_random_coefficient):
        super(RandomCoefficientEdgeCostGenerator, self).__init__()
        self.min_random_coefficient = min_random_coefficient
        self.max_random_coefficient = max_random_coefficient
    def get_edge_cost(self, source_point, target_point):
        base = super(RandomCoefficientEdgeCostGenerator, self).get_edge_cost(source_point, target_point)
        random_coefficient = random.uniform(self.min_random_coefficient, self.max_random_coefficient)
        result = base * random_coefficient
        assert result >= 0, 'Negative edge cost! base: %s, random_coefficient: %s' % (base, random_coefficient)
        return result

class AbstractDistanceFromPointsEdgeCostGenerator(AbstractEdgeCostGenerator):
    def __init__(self, *args, **kwargs):
        self.reference_points = None
        super(AbstractDistanceFromPointsEdgeCostGenerator, self).__init__(*args, **kwargs)
    def get_edge_cost(self, source_point, target_point):
        t_x, t_y = get_average_coordinates([source_point.coordinates, target_point.coordinates])
        dist = 0
        for reference_point in self.reference_points:  # subclass was supposed to set this in register_points()
            r_x, r_y = reference_point
            dist += hypot(r_x - t_x, r_y - t_y) #** self.exponent
        dist = dist ** self.exponent
        dist += 1
        assert dist >= 0, 'Negative edge cost!'
        return dist

class DistanceFromCornersEdgeCostGenerator(AbstractDistanceFromPointsEdgeCostGenerator):
    def __init__(self, corners, *args, **kwargs):
        self.corners = corners
        super(DistanceFromCornersEdgeCostGenerator, self).__init__(*args, **kwargs)
    def register_points(self, points):
        point_coordinates = [point.coordinates for point in points]
        cc = corner_coordinates(point_coordinates)
        self.reference_points = [cc[id_] for id_ in self.corners]
        #self.reference_points = [cc[id_] for id_ in self.corners] + [[15, 15]]
        #self.reference_points = [(6, 21)]
        #self.reference_points = cc[0:3]
        #self.reference_points = [(10, -10)]
        return super(DistanceFromCornersEdgeCostGenerator, self).register_points(points)

