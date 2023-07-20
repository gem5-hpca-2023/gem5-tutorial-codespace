from gem5.components.boards.test_board import TestBoard
from gem5.components.memory import HBM2Stack
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.random_generator import RandomGenerator
from gem5.components.cachehierarchies.classic.no_cache import NoCache


import m5
from m5.objects import Root

### TO COMPLETE HERE ###

# components
# memory = SingleChannelDDR3_1600("1GiB")
memory = HBM2Stack("1GiB")

# generator
generator = RandomGenerator(
    duration = "250us",
    rate = "40GB/s",
    num_cores = 1,
    max_addr = memory.get_size()
)

cache_hierarchy = NoCache()

# add to test board
board = TestBoard(
    clk_freq = "3GHz",
    generator = generator,
    memory = memory,
    cache_hierarchy = cache_hierarchy
)

# Setup the root and instantiate the simulation.
# This is boilerplate code, to be removed in future releaes of gem5.
root = Root(full_system=False, system=board)
board._pre_instantiate()
m5.instantiate()

# Start the traffic generator.
generator.start_traffic()
exit_event = m5.simulate()
