from gem5.components.boards.test_board import TestBoard
from gem5.components.memory.single_channel import SingleChannelDDR_1600
from gem5.components.processors.random_generator import RandomGenerator

import m5
from m5.objects import Root

### TO COMPLETE HERE ###

# Setup the root and instantiate the simulation.
# This is boilerplate code, to be removed in future releaes of gem5.
root = Root(full_system=False, system=board)
board._pre_instantiate()
m5.instantiate()

# Start the traffic generator.
board.start_traffic()
exit_event = m5.simulate()
