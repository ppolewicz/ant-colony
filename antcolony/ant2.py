import random

from ant import AbstractAnt
from util import avg

import os.path
from pprint import pprint

class AntMode(object):
    RETURNING_WITH_FOOD = 1001
    RETURNING_WITHOUT_FOOD = 1002
    EXPLORING = 1003

class BasicAnt(AbstractAnt, AntMode):
    EXPLORING_PHEROMONE_FRACTION = 0.0
    FOOD_PHEROMONE_FRACTION = 1.0
    #DEFAULT_EDGE_ATTRACTIVENESS = 1.0
    CHANCE_OF_IGNORING_AN_IGNORED_POINT = 0.1
    CHANCE_OF_IGNORING_ROULETTE = 0.02
    LENGTH_PENALTY_EXPONENT = 5 #1.5
    SNIFF_EXPONENT = 1
    def __init__(self, world_parameters):
        super(BasicAnt, self).__init__(world_parameters)
        self.path_to_home = []
        self.mode = self.EXPLORING
        self.cost = None
        self.resets = 0
        self.ignored_points = set()
        assert self.world_parameters.min_pheromone_dropped_by_ant == 0, 'this ant doesn\'t support this environment'
    def _is_coming_home(self):
        return self.mode in (self.RETURNING_WITHOUT_FOOD, self.RETURNING_WITH_FOOD)
    def _pick_edge(self, next_edge):
        amount_of_pheromone = 0
        if self.mode == self.RETURNING_WITHOUT_FOOD:
            amount_of_pheromone = 0
        else:
            maax = self.world_parameters.max_pheromone_dropped_by_ant
            miin = self.world_parameters.min_pheromone_dropped_by_ant
            variable_amount = (maax - miin)
            if self.mode == self.RETURNING_WITH_FOOD:
                amount_of_pheromone = miin + variable_amount * self.FOOD_PHEROMONE_FRACTION / (self.cost**self.LENGTH_PENALTY_EXPONENT) * self._world_size()
                amount_of_pheromone = min(amount_of_pheromone, maax) # floating point rounding errors breaks stuff
                mode='returning with food'
            elif self.mode == self.EXPLORING:
                amount_of_pheromone = miin + variable_amount * self.EXPLORING_PHEROMONE_FRACTION * self._world_size()
                mode='exploring'
            else:
                assert False, 'Unknown ant operation mode'
            if amount_of_pheromone < 0 or amount_of_pheromone > 1.0:
                print 'amount_of_pheromone', repr(amount_of_pheromone)
                print 'miin', miin
                print 'mode:', mode
                print 'self.cost', self.cost
                print 'coefficient', self.cost**self.LENGTH_PENALTY_EXPONENT
                assert False

        return next_edge, amount_of_pheromone
    def _world_size(self):
        #return self.world_parameters.num_edges
        return 1
        #return self.world_parameters.num_points
    def _return_home(self, current_point):
        next_edge = self.path_to_home.pop()
        return self._pick_edge(next_edge)
    def tick(self, current_point):
        #print 'has %s food, current_point: %s' % (self.food, current_point)
        if current_point.is_anthill():
            self.path_to_home = [] # if We happen to stumble upon the anthill, We reset the path
            self.mode = self.EXPLORING
        elif self.food and self.mode!=self.RETURNING_WITH_FOOD:
            #print 'found food after %s moves, %s minutes, going home' % (len(self.path_to_home), sum([edge.cost for edge in self.path_to_home]))
            self.mode = self.RETURNING_WITH_FOOD
            self.cost = sum([edge.cost for edge in self.path_to_home])
        if self._is_coming_home():
            choice = self._return_home(current_point)
            #if os.path.isfile('/tmp/ant'):
            #    print 'back home: %s, %s' % choice
            #    raw_input()
            return choice
        candidates = set(current_point.get_edges()) - set(self.path_to_home) # We don't want to go the way We came already
        if not candidates: # We have reached a dead end
            #print 'We have reached a dead end'
            self.resets += len(self.path_to_home)
            self.mode = self.RETURNING_WITHOUT_FOOD
            return self._return_home(current_point) # let's just start over
        candidates_filtered_by_rejected = self._filter_candidates(candidates, current_point)
        if len(candidates)!=len(candidates_filtered_by_rejected): # something would be filtered
            if self.CHANCE_OF_IGNORING_AN_IGNORED_POINT > 0 and self.CHANCE_OF_IGNORING_AN_IGNORED_POINT >= random.uniform(0, 1): # We have decided to use filter
                if candidates_filtered_by_rejected: # We have a choice that was not filtered
                    #print "We choose a filtered choice"
                    candidates = candidates_filtered_by_rejected
                else:
                    #print "We don't have a choice that was not filtered"
                    pass
        if self.CHANCE_OF_IGNORING_ROULETTE >= random.uniform(0, 1):
            roulette = {edge: 1 for edge in candidates}
        else:
            roulette = {}
            for edge in candidates:
                roulette[edge] = self._get_edge_attractiveness(edge, current_point)
        next_edge, rejected_choices = self.weighted_choice(roulette, weight_exponent=self.SNIFF_EXPONENT)
        self.ignored_points.update([candidate.get_other_end_by_point(current_point).point for candidate in rejected_choices])
        self._remember_way_home(next_edge, current_point)
        choice = self._pick_edge(next_edge)
        if os.path.isfile('/tmp/ant'):
            pprint(roulette)
            #print 'choice: %s, %s' % choice
            #raw_input()
            pass
        return choice
    def _filter_candidates(self, candidates, current_point):
        result = set()
        for candidate in candidates:
            if candidate.get_other_end_by_point(current_point).point not in self.ignored_points:
                result.add(candidate)
        return result
    def _get_edge_attractiveness(self, edge, current_point):
        end = edge.get_end_by_point(current_point)
        if end.pheromone_level == 0:
            #return self.DEFAULT_EDGE_ATTRACTIVENESS
            return avg([edge_end.pheromone_level for edge_end in current_point.edge_ends])
        return end.pheromone_level #/ edge.cost # if We divide attractiveness by cost, We are more likely to end up in local optimum
    def _iterate_over_remembered_points(self):
        a = self.path_to_home[0].a_end.point
        b = self.path_to_home[0].b_end.point
        if a.is_anthill():
            old_connect = a
        elif b.is_anthill():
            old_connect = b
        else:
            assert False
        i = 0
        while i < len(self.path_to_home)-1:
            new_connect = self.path_to_home[i].get_other_end_by_point(old_connect).point
            yield new_connect
            old_connect = new_connect
            i += 1
    def _remember_way_home(self, next_edge, current_point):
        self.path_to_home.append(next_edge) # We'll come back the same way we got here

class PathShorteningBehavior(BasicAnt):
    def _remember_way_home(self, next_edge, current_point):
        super(PathShorteningBehavior, self)._remember_way_home(next_edge, current_point)

        target_point = next_edge.get_other_end_by_point(current_point).point
        for i, point in enumerate(self._iterate_over_remembered_points()):
            new_connect = point
            if new_connect==target_point: # We currently plan to go somewhere We have already been, like abcdb
                # the points that We have visited obviously have no food on
                # them, so it'd be good to avoid them in the future

                # this is a bit inefficient and a bit too eager, but the implementation is simple
                for edge in self.path_to_home[i+1:]:
                    self.ignored_points.add(edge.a_end.point)
                    self.ignored_points.add(edge.b_end.point)

                # let's not do the same loop on a return trip
                self.path_to_home = self.path_to_home[:i+1]

                # as we search for cycles on every move, only one may be detected. No point in looking further.
                break

class ShortcutBehavior(BasicAnt):
    def _return_home(self, current_point):
        # try to find a shortcut
        candidates = {}
        for edge in current_point.get_edges():
            candidates[edge.get_other_end_by_point(current_point).point] = edge
        for i, remembered_point in list(enumerate(self._iterate_over_remembered_points()))[:-1]:
            for candidate_point in candidates:
                candidate_edge = candidates[candidate_point]
                if remembered_point==candidate_point: # shortcut found, but is it worth taking?
                    if candidate_edge.cost < sum([edge.cost for edge in self.path_to_home[i:]]): # yes
                        #print 'bad edge:', self.path_to_home[-1]
                        #print 'better edge:', candidate_edge
                        #print 'self.cost:', self.cost
                        #print 'edges that We cut off:'
                        #pprint(self.path_to_home[i+1:])
                        #print 'all edges on path home:'
                        #pprint(self.path_to_home)
                        saved_cost = sum([edge.cost for edge in self.path_to_home[i+1:]])
                        #print 'saved_cost:', saved_cost
                        #print 'self.cost:', self.cost
                        if self.cost is not None:
                            self.cost -= saved_cost # self.cost is None if we are returning without food
                        self.path_to_home = self.path_to_home[:i+1]
                        return self._pick_edge(candidate_edge)

        # shortcut not found, we'll return the way we came here
        return super(ShortcutBehavior, self)._return_home(current_point)

class PathShorteningAnt(PathShorteningBehavior, BasicAnt):
    """ ant that eagerly eliminates cycles in it's return path """
    pass

class ShortcutAnt(ShortcutBehavior, BasicAnt):
    """ ant that tries to find a shortcut to anthill """
    pass

class AdvancedAnt(ShortcutBehavior, PathShorteningBehavior, BasicAnt):
    pass

class AdvancedQuadraticAnt(AdvancedAnt):
    """ ant that squares pheromone before using roulette """
    SNIFF_EXPONENT = 2

class AdvancedRootAnt(AdvancedAnt):
    """ ant that square roots pheromone before using roulette """
    SNIFF_EXPONENT = 0.5

class AdvancedBadLuckAnt(AdvancedAnt):
    """ ant that picks a random candidate edge instead of using roulette """
    CHANCE_OF_IGNORING_ROULETTE = 1

class AdvancedIgnorantAnt(AdvancedAnt):
    """ ant that doesn't ignore a point which was rejected previously """
    CHANCE_OF_IGNORING_AN_IGNORED_POINT = 1

class LinearPenaltyAnt(AdvancedAnt):
    """ ant that applies only proportional length coefficient pheromone drop (instead of exponent) """
    LENGTH_PENALTY_EXPONENT = 1

class HalfLengthPenaltyExponent(AdvancedAnt):
    LENGTH_PENALTY_EXPONENT = 0.5

