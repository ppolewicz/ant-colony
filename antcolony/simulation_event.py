class AbstractSimulationEvent(object):
    def process_start(self):
        return frozenset()
    def process_end(self, world, stats):
        return frozenset()
    def __cmp__(self, other):
        return self.end_time - other.end_time

