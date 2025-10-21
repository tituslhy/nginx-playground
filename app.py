#%%
import chainlit as cl
import logging

from src.on_chat_start import setup_agent
from src.on_message import invoke_agent
from utils.utils import get_container_info

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
)
logger = logging.getLogger(__name__)

#%%
@cl.on_chat_start
async def on_chat_start():
    setup_agent()
    logger.info("Agent setup complete")

@cl.on_message
async def on_message(message: cl.Message):
    
    # Get container serving info
    container_info = get_container_info()
    logger.info(f"Container Info: {container_info}")
    await cl.Message(content=f"📦 {container_info}").send()
    
    # Invoke agent
    response = await invoke_agent(message=message)
    logger.info(f"Agent Response: {response}")