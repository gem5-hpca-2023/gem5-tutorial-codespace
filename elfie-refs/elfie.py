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
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.resources.elfie import PcCountPair, ELFieInfo
from gem5.resources.workload import CustomWorkload
from m5.stats import reset, dump

requires(isa_required=ISA.X86)


cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32kB",
    l1i_size="32kB",
    l2_size="256kB",
)

memory = DualChannelDDR4_2400()

processor = SimpleProcessor(
    cpu_type=CPUTypes.TIMING,
    isa=ISA.X86,
    num_cores=8,
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

workload = CustomWorkload(
    function = "set_se_elfie_workload",
    parameters = {
        "elfie": BinaryResource("cactuBSSN-s.1_1_globalr2/cactuBSSN-s.1_1_globalr2.sim.elfie"),
        "elfie_info": ELFieInfo(PcCountPair(0x6ffed1, 1), PcCountPair(0x6c830f, 6479283)),
    }
)

# Note: it could be useful to go to the beginning in atomic mode instead of timing
board.set_workload(workload)

def gen():
    print("Hit beginning of the region.")
    reset()
    print ("Running the region.")
    yield False
    dump()
    yield True

simulator = Simulator(
    board = board,
    on_exit_event={ExitEvent.SIMPOINT_BEGIN: gen()},
)

simulator.run()
