class AbstractSimulationEvent(object):
    def process_start(self):
        return frozenset()
    def process_end(self, world, stats):
        return frozenset()

