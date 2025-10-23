import os
import socket
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
)
logger = logging.getLogger(__name__)

def get_container_info() -> str:
    """Gets unique information about the container."""
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "N/A"
    container_id = os.uname().nodename
    return f"Served by Container:\n- **Hostname:** `{hostname}`\n- **Internal IP:** `{ip_address}`\n- **Container ID:** `{container_id}`"

def get_secret(name: str):
    if name in os.environ:
        return os.environ[name]
    secret_path = Path(f"/run/secrets/{name}")
    if secret_path.exists():
        return secret_path.read_text().strip()
    return None

def get_secrets():
    secrets = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    for secret in secrets:
        if os.getenv(secret) is None:
            value = get_secret(secret)
            if value:
                os.environ[secret] = value
                logging.info(f"Loaded secret {secret} from file.")
            else:
                logging.warning(f"Secret {secret} not found in environment or file.")