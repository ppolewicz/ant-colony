class AbstractQueen(object):
    def spawn_ants(self, amount_of_ants):
        raise NotImplementedError()
    def get_name(self):
        raise NotImplementedError()

class BasicQueen(AbstractQueen):
    def __init__(self, ant_class):
        self._ant_class = ant_class
    def spawn_ants(self, amount_of_ants):
        return [self._ant_class] * amount_of_ants
    def get_name(self):
        return '%s-%s' % (self.__class__.__name__, self._ant_class.__name__)

