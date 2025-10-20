from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.utils import get_container_info

from ollama import AsyncClient

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #specify this to be your frontend in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/guardrail")
async def check_query(query: str):
    client = AsyncClient(host="http://host.docker.internal:11434")
    response = await client.chat(
        model="llama-guard3",
        messages = [
            {
                'role': 'user',
                'content': query,
            }
        ]
    )
    container_info = get_container_info()
    return {
        "container_info": container_info,
        "response": response.message.content
    }