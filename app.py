#%%
import socket
import os

import chainlit as cl
import logging
import httpx

from src.on_chat_start import setup_agent
from src.on_message import invoke_agent, invoke_guardrail
from utils.utils import get_container_info

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
)
logger = logging.getLogger(__name__)

GUARDRAIL_URL = "http://nginx_proxy:8080/guardrail"
#%%
@cl.on_chat_start
async def on_chat_start():
    setup_agent()
    logger.info("Agent setup complete")

@cl.on_message
async def on_message(message: cl.Message):
    response = invoke_guardrail(message=message)
    if "unsafe" in response['response']:
        await cl.Message(content=f"⚠️ Your message was flagged as unsafe by the guardrail model. Please modify your input and try again. Served by {response['served_by']}").send()
        logger.warning(f"Unsafe message detected: {message.content}")
        
    else:
        await cl.Message(content=f"⚠️ Your message has cleared the guardrail model. Proceeding to service query. Served by {response['served_by']}").send()
        container_info = get_container_info()
        logger.info(f"Container Info: {container_info}")
        await cl.Message(content=f"📦 {container_info}").send()
        response = await invoke_agent(message=message)
        logger.info(f"Agent Response: {response}")