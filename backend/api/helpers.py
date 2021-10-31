import docker


def is_port_in_use(port: int) -> bool:
    """checks if a port is in use

    First step is to list all ports used by docker containers.
    If the port does not seem to be used in the first step, it tries to create a container bound to the port.

    Args:
        port (int): The port to check for usage
    Returns:
        bool: Whether or not the port is used
    """

    client = docker.from_env()
    used_ports = []
    for container in client.containers.list():
        for ports in container.ports.items():
            host_port_pairs = ports[1] or []
            for host_port_pair in host_port_pairs:
                host_port = int(host_port_pair["HostPort"])
                if host_port not in used_ports:
                    used_ports.append(host_port)

    if port in used_ports:
        return True

    try:
        container = client.containers.run("hello-world", ports={f"{port}/tcp": port}, detach=True)
    except docker.errors.APIError:
        return True

    try:
        container.kill()
    except docker.errors.APIError:
        pass

    return False
