import os
from openai import AsyncOpenAI, OpenAI

async def stream_llm(messages):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    client = AsyncOpenAI(api_key=api_key)
    
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
    if not prompt:
        raise ValueError("Prompt cannot be empty")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def call_gemini(prompt: str, model: str = "gemini-2.0-flash-001") -> str:
    """
    Call the Gemini LLM using the google-genai SDK (2024+ API).

    Args:
        prompt (str): The prompt to send to Gemini.
        model (str): The Gemini model to use (default: "gemini-2.0-flash-001").

    Returns:
        str: The model's response as a string.

    Usage:
        Set the GEMINI_API_KEY environment variable before use.
        Example:
            response = call_gemini("Why is the sky blue?")
    """
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    client = genai.Client(api_key=api_key)
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