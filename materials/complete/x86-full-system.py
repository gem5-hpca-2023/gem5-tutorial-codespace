from gem5.utils.requires import requires
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.coherence_protocol import CoherenceProtocol
from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes
from gem5.resources.workload import Workload
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

# This runs a check to ensure the gem5 binary is compiled to X86 and supports
# the MESI Two Level coherence protocol.
requires(
    isa_required=ISA.X86,
    coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
)

# Here we setup a MESI Two Level Cache Hierarchy.
cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32KiB",
    l1d_assoc=8,
    l1i_size="32KiB",
    l1i_assoc=8,
    l2_size="256kB",
    l2_assoc=16,
    num_l2_banks=1,
)

# Setup the system memory.
# Note, by default DDR3_1600 defaults to a size of 8GiB. However, a current
# limitation with the X86 board is it can only accept memory systems up to 3GB.
# As such, we must fix the size.
memory = SingleChannelDDR3_1600("2GiB")

# Here we setup the processor. This is a special switchable processor in which
# a starting core type and a switch core type must be specified. Once a
# configuration is instantiated a user may call `processor.switch()` to switch
# from the starting core types to the switch core types. In this simulation
# we start with TIMING cores to simulate the OS boot, then switch to the O3
# cores for the command we wish to run after boot.
processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.TIMING,
    switch_core_type=CPUTypes.O3,
    num_cores=2,
    isa=ISA.X86,
)

# Here we setup the board. The X86Board allows for Full-System X86 simulations.
board = X86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# This is the command to run after the system has booted. The first `m5 exit`
# will stop the simulation so we can switch the CPU cores from KVM to timing
# and continue the simulation to run the echo command, sleep for a second,
# then, again, call `m5 exit` to terminate the simulation. After simulation
# has ended you may inspect `m5out/system.pc.com_1.device` to see the echo
# output.
command = (
    "m5 exit;"
    + "echo 'This is running on Timing O3 cores.';"
    + "sleep 1;"
    + "m5 exit;"
)

# Here we set the workload. If we look up
# http://resources.gem5.org/resources.json we can see the following entry for
# the workload "x86-ubuntu-18.04-boot":
# ```
# {
#      "type" : "workload",
#      "name" : "x86-ubuntu-18.04-boot",
#      "documentation" : "A full boot of Ubuntu 18.04 with Linux 5.4.49 for
#                         X86. It runs an `m5 exit` command when the boot is
#                         completed unless the readfile is specified. If
#                         specified the readfile will be executed after
#                         booting.",
#      "function": "set_kernel_disk_workload",
#      "resources" : {
#          "kernel" : "x86-linux-kernel-5.4.49",
#          "disk_image":"x86-ubuntu-18.04-img"
#      },
#      "additional_params" : {}
# },
# ```
workload = Workload("x86-ubuntu-18.04-boot")

# We want to ammend this workload slightly to carry out a script when the OS
# boot is complete. The script immediately exits the simulation loop then,
# when re-entered, will print "This is running on Timing CPU cores." before
# sleeping for 1 simulated second then exiting the simulation loop again.
#
# We set this to the "readfile_contents" parameter. This parameter allows for
# the setting of the contents of the readfile. The readfile is executed by this
# resource when the OS is booted.
command = (
    "m5 exit;"
    + "echo 'This is running on O3 CPU cores.';"
    + "sleep 1;"
    + "m5 exit;"
)

workload.set_parameter("readfile_contents", command)

board.set_workload(workload)

simulator = Simulator(
    board=board,
    on_exit_event={
        # Here we want override the default behavior for the first m5 exit
        # exit event. Instead of exiting the simulator, we just want to
        # switch the processor. The 2nd 'm5 exit' after will revert to using
        # default behavior where the simulator run will exit.
        ExitEvent.EXIT: (func() for func in [processor.switch]),
    },
)
simulator.run()
