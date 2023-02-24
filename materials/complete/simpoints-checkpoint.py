from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource, SimpointResource
from pathlib import Path
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.simulate.exit_event_generators import (
    save_checkpoint_generator,
)

requires(isa_required=ISA.X86)

# Setup the components.
cache_hierarchy = NoCache()
memory = SingleChannelDDR3_1600(size="2GB")
processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC,
    isa=ISA.X86,
    # SimPoints only works with one core
    num_cores=1,
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Setup the Simpoints workload
board.set_se_simpoint_workload(
    binary=obtain_resource("x86-print-this"),
    arguments=["print this", 15000],
    simpoint=SimpointResource(
        simpoint_interval=1000000,
        simpoint_list=[2, 3, 4, 15],
        weight_list=[0.1, 0.2, 0.4, 0.3],
        warmup_interval=1000000,
    ),
)

dir = Path("simpoint-checkpoint-dir")
dir.mkdir(exist_ok=True)

# Here we use the Simpoints generator to take the checkpoints.
# When a Simpoint region, or warmup region, begins, a checkpoint is generated.
simulator = Simulator(
    board=board,
    on_exit_event={ExitEvent.SIMPOINT_BEGIN: save_checkpoint_generator(dir)},
)

simulator.run()
