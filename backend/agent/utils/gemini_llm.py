import os
from google import genai
from google.genai import types

# Initialize the Gemini client using the API key from the environment
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Call the Gemini LLM using the latest google-genai SDK.

    Args:
        prompt (str): The prompt to send to Gemini.
        model (str): The Gemini model to use (default: "gemini-2.5-flash").

    Returns:
        str: The model's text response.
    """
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

# Example usage
if __name__ == "__main__":
    prompt = "Explain the difference between AI and machine learning."
    print(call_gemini(prompt)) 