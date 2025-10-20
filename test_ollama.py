#%%
from ollama import AsyncClient

async def main(query: str):
    client = AsyncClient(host="http://localhost:11434")
    response = await client.chat(
        model="llama-guard3",
        messages = [
            {
                'role': 'user',
                'content': query,
            }
        ]
    )
    return response.message.content
# %%
