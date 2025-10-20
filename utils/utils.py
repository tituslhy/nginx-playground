import os
import socket

def get_container_info() -> str:
    """Gets unique information about the container."""
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "N/A"
    container_id = os.uname().nodename
    return f"Served by Container:\n- **Hostname:** `{hostname}`\n- **Internal IP:** `{ip_address}`\n- **Container ID:** `{container_id}`"