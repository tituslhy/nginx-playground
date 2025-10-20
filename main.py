#%%
import socket
import os
from dotenv import load_dotenv, find_dotenv

import chainlit as cl
import logging

from src.on_chat_start import setup_agent
from src.on_message import invoke_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_container_info():
    """Gets unique information about the container."""

    hostname = socket.gethostname()
    # The hostname is often the most readable unique ID.
    # Docker Compose generates hostnames like 'projectname-servicename-N'
    # For example: 'my-project-chainlit-1'

    # You can also get the internal IP address like this:
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "N/A"

    # The container ID is also available in many environments via os.uname()
    # This is often the same as the short container ID you see with `docker ps`
    container_id = os.uname().nodename

    return f"Served by Container:\n- **Hostname:** `{hostname}`\n- **Internal IP:** `{ip_address}`\n- **Container ID:** `{container_id}`"

#%%
@cl.on_chat_start
async def on_chat_start():
    setup_agent()

@cl.on_message
async def on_message(message: cl.Message):
    
    container_info = await get_container_info()
    logger.info(f"Container Info: {container_info}")
    
    with cl.Step(name=container_info):
        response = await invoke_agent(message=message)
        logger.info(f"Agent Response: {response}")
