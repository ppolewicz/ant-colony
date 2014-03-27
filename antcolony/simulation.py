import heapq

class AbstractSimulation(object):
    def __init__(self, reality, antmoves, stats):
        self.reality = reality
        self.antmoves = antmoves
        heapq.heapify(antmoves)
        self.stats = stats
        self.ticks = 0
    def tick(self):
        ant_move = heapq.heappop(self.antmoves)
        self.reality.world.elapsed_time = ant_move.end_time # simulation is now at the point of ant_move.ant arriving at ant_move.destination
        new_antmove, changed_items_end = ant_move.process_end(self.reality, self.stats)
        assert not self.reality.world.elapsed_time > ant_move.end_time
        changed_items_start = new_antmove.process_start()
        assert changed_items_start is not None, new_antmove
        heapq.heappush(self.antmoves, new_antmove)
        self.ticks += 1
        return changed_items_start & changed_items_end, self.stats

class TickStepSimulation(AbstractSimulation):
    def advance(self):
        if self.reality.is_resolved():
            return [], True, None
        tick_changed_items, stats = self.tick()
        print 'ticks: %d, food_discovered: %d' % (self.ticks, stats.food_discovered)
        return tick_changed_items, False, stats.last_route

class MultiSpawnStepSimulation(AbstractSimulation):
    def __init__(self, reality, *args, **kwargs):
        super(MultiSpawnStepSimulation, self).__init__(reality, *args, **kwargs)
        self.spawn_amount = 50
        self.anthills = reality.world.get_anthills()
    def advance(self):
        if self.reality.is_resolved():
            return [], True, None
        anthill_food_pre_tick = sum([anthill.food for anthill in self.anthills])
        changed_items = set()
        amount = 0
        while amount <= self.spawn_amount:
            tick_changed_items, stats = self.tick()
            changed_items.update(tick_changed_items)
            anthill_food_post_tick = sum([anthill.food for anthill in self.anthills])
            if anthill_food_post_tick != anthill_food_pre_tick+amount:
                if self.reality.is_resolved():
                    break
                amount += 1
        return changed_items, False, stats.last_route

class SpawnStepSimulation(MultiSpawnStepSimulation):
    def __init__(self, reality, *args, **kwargs):
        super(SpawnStepSimulation, self).__init__(reality, *args, **kwargs)
        self.spawn_amount = 1

class LastSpawnStepSimulation(MultiSpawnStepSimulation):
    def __init__(self, reality, *args, **kwargs):
        super(LastSpawnStepSimulation, self).__init__(reality, *args, **kwargs)
        self.spawn_amount = reality.world.get_total_food()

