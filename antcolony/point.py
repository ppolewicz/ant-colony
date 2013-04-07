import math

class AbstractPoint(object):
    JSON_KEY_COORDINATES = 'coordinates'
    JSON_KEY_IS_ANTHILL = 'is_anthill'
    def __init__(self, coordinates, *args, **kwargs):
        self.coordinates = coordinates
        self.edge_ends = set()
    def add_edge_end(self, edge):
        self.edge_ends.add(edge)
    def is_anthill(self):
        return self.anthill
    def has_food(self):
        return self.food > 0
    def get_distance_to(self, other):
        return math.sqrt(sum([(self.coordinates[i] - other.coordinates[i])**2 for i in xrange(len(self.coordinates))]))
    def get_edges(self):
        return [edge_end.edge for edge_end in self.edge_ends]
    def __hash__(self):
        return hash(self.coordinates)
    def __repr__(self):
        return '%s([%s])' % (self.__class__.__name__, ', '.join(map(str, self.coordinates)))
    def to_json(self):
        return {self.JSON_KEY_COORDINATES: self.coordinates, self.JSON_KEY_IS_ANTHILL: self.anthill}
    @classmethod
    def from_json(cls, json_point):
        return cls(tuple(json_point[cls.JSON_KEY_COORDINATES]))

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
    JSON_KEY_FOOD = 'food'
    def __init__(self, coordinates, food, *args, **kwargs):
        self.anthill = False
        self.food = food
        super(FoodPoint, self).__init__(coordinates, *args, **kwargs)
    def to_json(self):
        result = super(FoodPoint, self).to_json()
        result[self.JSON_KEY_FOOD] = self.food
        return result
    @classmethod
    def from_json(cls, json_point):
        return cls(tuple(json_point[cls.JSON_KEY_COORDINATES]), json_point[cls.JSON_KEY_FOOD])

