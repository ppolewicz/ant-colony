import random

class AbstractAnt(object):
    def __init__(self, world_parameters):
        self.world_parameters = world_parameters
        self.food = 0
    def tick(self, current_point):
        """
           returns the result of Ant's decision process.
           returns two element tuple
           first element is the target point
           second element is a number representing the amount of pheromone dropped on the way to the target
           the amount of pheromone has to be within the world's limits
        """
        raise NotImplementedError()
    @classmethod
    def weighted_choice(cls, choice_dict):
        """
            returns roulette winner and a set of rejected choices
        """
        total = sum(v for k, v in choice_dict.iteritems())
        mark = random.uniform(0, total)
        upto = 0
        choice_dict_sorted = sorted(choice_dict)
        for k in choice_dict_sorted:
            v = choice_dict[k]
            upto += v
            if upto >= mark:
                winner = k
                break
        return winner, set(choice_dict_sorted) - set([winner])

class PurelyRandomAnt(AbstractAnt):
    """ ant that selects edges randomly. Very inefficient (unless very lucky). """
    def tick(self, current_point):
        choices = current_point.get_edges()
        target = random.choice(choices)
        return target, self.world_parameters.max_pheromone_dropped_by_ant


if __name__=='__main__':
    # test of random distribution of AbstractAnt.weighted_choice
    # takes a moment to execute
    total = 1000000
    result = {}
    for x in xrange(total):
        k, rest = AbstractAnt.weighted_choice({y: 0.1234 for y in xrange(40)})
        result[k] = result.get(k, 0) + 1
    for k, v in sorted(result.iteritems()):
        print '%s: %.3f%%' % (k, v*100.0/total)


