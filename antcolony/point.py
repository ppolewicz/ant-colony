import math

class AbstractPoint(object):
    def __init__(self, coordinates, *args, **kwargs):
        self.coordinates = coordinates
    def is_anthill(self):
        return self.anthill
    def has_food(self):
        return self.food > 0
    def get_distance_to(self, other):
        return math.sqrt(sum([(self.coordinates[i] - other.coordinates[i])**2 for i in xrange(len(self.coordinates))]))
    def __hash__(self):
        return hash(self.coordinates)
    def __repr__(self):
        return '%s([%s])' % (self.__class__.__name__, ', '.join(map(str, self.coordinates)))

class Point(AbstractPoint):
    def __init__(self, coordinates, *args, **kwargs):
        self.anthill = False
        self.food = 0
        super(Point, self).__init__(coordinates, *args, **kwargs)

class AnthillPoint(AbstractPoint):
    def __init__(self, coordinates, *args, **kwargs):
        self.anthill = True
        self.food = 0
        super(AnthillPoint, self).__init__(coordinates, *args, **kwargs)

class FoodPoint(AbstractPoint):
    def __init__(self, coordinates, food, *args, **kwargs):
        self.anthill = False
        self.food = food
        super(FoodPoint, self).__init__(coordinates, *args, **kwargs)

