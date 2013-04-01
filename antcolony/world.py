class World(object):
    def __init__(self, points, edges):
        self.points = points
        self.edges = edges
    def get_anthill(self):
        for point in self.points:
            if point.is_anthill():
                return point
    def __repr__(self):
        return 'World:\n    ' + '\n    '.join(map(str, self.edges))

