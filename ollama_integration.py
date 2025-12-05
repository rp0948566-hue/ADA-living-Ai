import httpx
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def generate_response(prompt):
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "model": "qwen2:latest",
                "prompt": prompt,
                "stream": False 
            }
            response = await client.post(OLLAMA_API_URL, json=data, timeout=60.0)
            response.raise_for_status()

            response_json = response.json()
            return response_json.get("response", "").strip()

    except httpx.RequestError as e:
        return f"Error communicating with Ollama: {e}"
    except json.JSONDecodeError:
        return "Error decoding Ollama's response. It might be malformed."

async def main():
    # Example usage
    prompt = "Hello, who are you?"
    response = await generate_response(prompt)
    print(f"User: {prompt}")
    print(f"AI: {response}")

    prompt = "What is the capital of France?"
    response = await generate_response(prompt)
    print(f"User: {prompt}")
    print(f"AI: {response}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
