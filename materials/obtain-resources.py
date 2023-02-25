from gem5.resources.resource import obtain_resource

resource = obtain_resource("riscv-disk-img")

print(f"The resource is available at {resource.get_local_path()}")
