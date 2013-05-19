from collections import deque
import copy

from util import avg

class TripStats(object):
    def __init__(self):
        self.food_found_after = 0, 0
        self.total_cost = 0
        self.total_moves = 0
        self.visited = deque()
    def reset_route(self):
        self.visited = deque()
    def food_found(self):
        self.food_found_after = self.total_moves, self.total_cost
    def normal_move(self, cost):
        self.total_moves += 1
        self.total_cost += cost
    def edge_visited(self, edge):
        self.visited.append(edge)
    def back_home(self):
        pass

class QueenStats(object):
    def __init__(self, reality, number_of_ants):
        self.reality = reality
        self.food_discovered = 0
        self.moves_leading_to_food_being_found = 0
        self.number_of_ants = number_of_ants
        self.best_finding_cost = 999999999
        self.last_cost = 0
        self.last_route = []
        self.last_results = deque(maxlen=50)
    def food_found(self, trip_stats):
        self.food_discovered += 1
        moves_leading_to_food_being_found, last_cost = trip_stats.food_found_after
        self.last_cost = last_cost
        self.moves_leading_to_food_being_found += moves_leading_to_food_being_found
        self.best_finding_cost = min(self.best_finding_cost, last_cost)
        self.last_route = copy.copy(trip_stats.visited)
        self.last_results.append(trip_stats.food_found_after)
    def present(self):
        # averages are usually heavily biased by the few initial food findings
        #avg_cost = (self.reality.world.elapsed_time*self.number_of_ants)/self.food_discovered
        #avg_moves = self.moves_leading_to_food_being_found/self.food_discovered

        fl_avg_cost = avg([cost for moves, cost in self.last_results])
        fl_avg_moves = avg([moves for moves, cost in self.last_results])
        avg_pheromone = self.reality.world.get_average_pheromone_level()
        max_pheromone = self.reality.world.get_max_pheromone_level()
        print 'found: %d, best: %.3f, avg.ph.: %.3f, max.ph.: %.3f [%.3f], fl.avg.moves: %d, fl.avg.cost: %.3f, last_cost: %s, world.time: %d' % (
            self.food_discovered,
            self.best_finding_cost,
            avg_pheromone,
            max_pheromone,
            max_pheromone/(avg_pheromone or 1),
            fl_avg_moves,
            fl_avg_cost,
            self.last_cost,
            self.reality.world.elapsed_time,
        )

