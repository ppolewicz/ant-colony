class Edge(object):
    def __init__(self, point_A, point_B, cost):
        self.a_end, self.b_end = sorted([point_A, point_B])
        self.cost = cost
        self.pheromone_on_a_end = 0
        self.pheromone_on_b_end = 0
    def __eq__(self, other):
        if self.a_end!=other.a_end:
            return False
        return self.b_end==other.b_end
    def __hash__(self):
        return hash((self.a_end, self.b_end))
    def __repr__(self):
        return 'Edge{%s <[%s]--[%s]> %s (%s)}' % (self.a_end, self.pheromone_on_a_end, self.pheromone_on_b_end, self.b_end, self.cost)

if __name__=='__main__':
    from pprint import pprint
    pprint(
        set(
            [
                Edge((1,), (2,), 5),
                Edge((1,), (2,), 5),
                Edge((1,), (2,), 6),
            ]
        )
    )

