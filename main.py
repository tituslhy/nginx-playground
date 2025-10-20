#%%
import os
from dotenv import load_dotenv, find_dotenv

import chainlit as cl

from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.agent.workflow import (
    AgentWorkflow, 
    AgentStream, 
    ToolCallResult
)
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.tools.tavily_research import TavilyToolSpec

_ = load_dotenv(find_dotenv())
llm = OpenAI(model="gpt-4o-mini")
tavily_tool = TavilyToolSpec(api_key=os.getenv("TAVILY_API_KEY"))

# async def main():
#     agent = AgentWorkflow.from_tools_or_functions(
#         tavily_tool.to_tool_list(),
#         llm=llm,
#         system_prompt="You're a helpful assistant that can search the web for information."
#     )
#     context = Context(agent)
#     handler = agent.run(user_msg="What's the weather like in Singapore?", ctx=context)

#     # handle streaming output
#     async for event in handler.stream_events():
#         if isinstance(event, AgentStream):
#             print(event.delta, end="", flush=True)
#         elif isinstance(event, ToolCallResult):
#             print("Tool called: ", event.tool_name)  # the tool name
#             print("Arguments to the tool: ", event.tool_kwargs)  # the tool kwargs
#             print("Tool output: ", event.tool_output)  # the tool output            

#     # print final output
#     print(str(await handler))

#%%
@cl.on_chat_start
async def on_chat_start():
    agent = AgentWorkflow.from_tools_or_functions(
        tavily_tool.to_tool_list(),
        llm=llm,
        system_prompt="You're a helpful assistant that can search the web for information."
    )
    memory = ChatMemoryBuffer.from_defaults()
    cl.user_session.set("agent", agent)
    cl.user_session.set("context", Context(agent))
    cl.user_session.set("memory", memory)

@cl.on_message
async def on_message(message: cl.Message):
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
    await msg.send()
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
