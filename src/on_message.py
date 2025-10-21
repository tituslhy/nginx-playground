import chainlit as cl

from llama_index.core.agent.workflow import (
    AgentStream, 
    ToolCallResult
)
from llama_index.core.base.llms.types import (
    ChatMessage, 
    MessageRole
)

from ollama import AsyncClient

from utils.utils import get_container_info

async def invoke_guardrail(message: cl.Message) -> dict[str, str]:
    info = get_container_info()
    client = AsyncClient(host="http://nginx_proxy:8080/guardrail")
    response = await client.chat(
        model="llama-guard3",
        messages = [
            {
                'role': 'user',
                'content': message.content,
            }
        ]
    )
    return {
        "response": response.message.content,
        "served_by": info
    }
    

async def invoke_agent(message: cl.Message) -> str:
    agent = cl.user_session.get("agent")
    memory = cl.user_session.get("memory")
    context = cl.user_session.get("context")
    
    chat_history = memory.get() 
    msg = cl.Message(content="")
    
    handler = agent.run(
        user_msg=message.content,
        chat_history=chat_history,
        ctx=context
    )
    
    async for event in handler.stream_events():
        if isinstance(event, AgentStream):
            await msg.stream_token(event.delta)
        elif isinstance(event, ToolCallResult):
            with cl.Step(name=f"{event.tool_name} tool with arguments: {event.tool_kwargs}", type="tool"):
                continue       

    response = str(await handler)
    await msg.update()
    memory.put(
        ChatMessage(
            role = MessageRole.USER,
            content= message.content
        )
    )
    memory.put(
        ChatMessage(
            role = MessageRole.ASSISTANT,
            content = str(response)
        )
    )
    cl.user_session.set("memory", memory)
    return response