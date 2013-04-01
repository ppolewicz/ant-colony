class Reality(object):
    def __init__(self, world, environment_parameters):
        self.world = world
        self.environment_parameters = environment_parameters
    def __repr__(self):
        return '%s\n%s' % (self.environment_parameters, self.world)

