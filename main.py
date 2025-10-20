#%%
import socket
import os

import chainlit as cl
import logging

from src.on_chat_start import setup_agent
from src.on_message import invoke_agent

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

#%%
@cl.on_chat_start
async def on_chat_start():
    setup_agent()
    logger.info("Agent setup complete")

@cl.on_message
async def on_message(message: cl.Message):
    
    container_info = get_container_info()
    logger.info(f"Container Info: {container_info}")
    await cl.Message(name=f"📦 {container_info}").send()
    response = await invoke_agent(message=message)
    logger.info(f"Agent Response: {response}")