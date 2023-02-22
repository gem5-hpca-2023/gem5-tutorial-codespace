from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory.single_channel import SingleChannelDDR_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator

# Obtain the components.
cache_hierarchy = NoCache
memory = SingleChannelDDR_1600("1GiB")
processor = SimpleProcessor(cpu_type=CPUTypes.Atomic, num_cores=1)

# Add them to the board.
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Obtain a binary to run via gem5-resources.
binary = obtain_resource("x86-hello64-static")
board.set_se_binary_workload(binary)

# Setup the simulator and run the simulation.
simulator = Simulator(board=board)
simulator.run()
