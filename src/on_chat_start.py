import chainlit as cl

import os
from dotenv import load_dotenv, find_dotenv

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.tools.tavily_research import TavilyToolSpec

from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from phoenix.otel import register

_ = load_dotenv(find_dotenv())

def setup_agent():
    llm = OpenAI(model="gpt-4o-mini")
    tavily_tool = TavilyToolSpec(api_key=os.getenv("TAVILY_API_KEY"))
    agent = AgentWorkflow.from_tools_or_functions(
        tavily_tool.to_tool_list(),
        llm=llm,
        system_prompt="You're a helpful assistant that can search the web for information."
    )
    memory = ChatMemoryBuffer.from_defaults()
    cl.user_session.set("agent", agent)
    cl.user_session.set("context", Context(agent))
    cl.user_session.set("memory", memory)
    
    ## Setup tracing
    tracer_provider = register(
        endpoint="http://phoenix:4317"
    )
    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)