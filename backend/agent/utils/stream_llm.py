import os
from openai import AsyncOpenAI
from google import genai

async def stream_llm(messages):
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        temperature=0.7
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

def call_llm(prompt):    
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "your-api-key"))
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt)
    return (response.text)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        messages = [{"role": "user", "content": "Hello!"}]
        async for chunk in stream_llm(messages):
            print(chunk, end="", flush=True)
        print()
    
    asyncio.run(test()) 