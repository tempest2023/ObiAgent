import os

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
    from openai import AsyncOpenAI, OpenAI  
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    response = client.chat.completions.create(
        model="gpt-4o-mini", # TODO: make this configurable
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def call_gemini(prompt: str, model: str = "gemini-2.0-flash-001") -> str:
    from google import genai
    client = genai.Client(api_key = os.environ.get("OPENAI_API_KEY", "your-api-key"))
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    import asyncio
    
    async def test():
        messages = [{"role": "user", "content": "Hello!"}]
        async for chunk in stream_llm(messages):
            print(chunk, end="", flush=True)
        print()
    
    asyncio.run(test()) 