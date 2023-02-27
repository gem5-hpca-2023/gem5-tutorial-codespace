from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.resources.looppoint import LooppointCsvLoader
from pathlib import Path
from gem5.simulate.exit_event_generators import (
    looppoint_save_checkpoint_generator,
)

requires(isa_required=ISA.X86)

# When taking a checkpoint, the cache state is not saved, so the cache
# hierarchy can be changed completely when restoring from a checkpoint.
# By using NoCache() to take checkpoints, it can slightly improve the
# performance when running in atomic mode, and it will not put any restrictions
# on what people can do with the checkpoints.
cache_hierarchy = NoCache()


# Using simple memory to take checkpoints might slightly imporve the
# performance in atomic mode. The memory structure can be changed when
# restoring from a checkpoint, but the size of the memory must be equal or
# greater to that taken when creating the checkpoint.
memory = SingleChannelDDR3_1600(size="2GB")

processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC,
    isa=ISA.X86,
    # LoopPoint can work with multicore workloads
    num_cores=9,
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Here we load the Pinpoint Looppoints CSV workload with the target binary and
# input arguments.
board.set_se_looppoint_workload(
    binary=obtain_resource("x86-matrix-multiply-omp"),
    arguments=[100, 8],
    looppoint=LooppointCsvLoader(
        pinpoints_file="materials/looppoints/refs/looppoint-pinpoints.csv"
    ),
)

# Here we specify where this script should output the checkpoints.
dir = Path("checkpoint_outputs")
dir.mkdir(exist_ok=True)

# This code ensures that when a looppoint region begins (inclusive of warmup)
# a checkpoint will be taken. It also updates our looppoint data structure.
simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.SIMPOINT_BEGIN: looppoint_save_checkpoint_generator(
            checkpoint_dir=dir,
            looppoint=board.get_looppoint(),
            # True if the relative PC count pairs should be updated during the
            # simulation. Default as True.
            update_relatives=True,
            # True if the simulation loop should exit after all the PC count
            # pairs in the LoopPoint data file have been encountered. Default
            # as True.
            exit_when_empty=True,
        )
    },
)

simulator.run()

# Output the JSON file. To be used when restoring.
board.get_looppoint().output_json_file("looppoint.json")
