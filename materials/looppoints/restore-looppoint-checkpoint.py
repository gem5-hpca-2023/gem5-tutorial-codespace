import argparse

from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.resources.looppoint import LooppointJsonLoader
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from m5.stats import reset, dump
from pathlib import Path

requires(isa_required=ISA.X86)

parser = argparse.ArgumentParser(description="An restore checkpoint script.")

parser.add_argument(
    "--region",
    type=str,
    required=False,
    choices=("1", "2", "3"),
    default="1",
    help="The checkpoint region to restore from.",
)
args = parser.parse_args()

# The cache hierarchy can be different from the cache hierarchy used in taking
# the checkpoints
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32kB",
    l1i_size="32kB",
    l2_size="256kB",
)

# The memory structure can be different from the memory structure used in
# taking the checkpoints, but the size of the memory must be equal or larger.
memory = DualChannelDDR4_2400(size="2GB")

processor = SimpleProcessor(
    cpu_type=CPUTypes.TIMING,
    isa=ISA.X86,
    # The number of cores must be equal or greater than that used when taking
    # the checkpoint.
    num_cores=9,
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Load the Looppoint JSON here and specify the region and the corresponding
# checkpoint
board.set_se_looppoint_workload(
    binary=obtain_resource("x86-matrix-multiply-omp"),
    looppoint=LooppointJsonLoader(
        looppoint_file=Path("materials/looppoints/refs/looppoint.json"),
        region_id=args.region,
    ),
    checkpoint=Path(
        f"materials/looppoints/refs/region-{args.region}-checkpoint"
    ),
)

# This generator will dump the stats and exit the simulation loop when the
# simulation region reaches its end. In the case there is a warmup interval,
# the simulation stats are reset after the warmup is complete.
def reset_and_dump():
    if len(board.get_looppoint().get_targets()) > 1:
        print("Warmup region ended. Resetting stats.")
        reset()
        yield False
    print("Region ended. Dumping stats.")
    dump()
    yield True


simulator = Simulator(
    board=board,
    on_exit_event={ExitEvent.SIMPOINT_BEGIN: reset_and_dump()},
)

simulator.run()
