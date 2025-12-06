import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

# API key for Ollama (for jock tone analysis)
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')

# Ollama API endpoint (assuming local Ollama server)
OLLAMA_URL = 'http://localhost:11434/api/generate'

class JockToneAnalyzer:
    def __init__(self):
        self.api_key = OLLAMA_API_KEY
        self.url = OLLAMA_URL
        self._session = aiohttp.ClientSession()

    async def analyze_tone(self, user_input):
        """Analyze the tone of user input using Ollama asynchronously"""
        prompt = f"Analyze the tone of this message and respond appropriately as an AI assistant named Jock: '{user_input}'"

        payload = {
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with self._session.post(self.url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('response', 'Unable to analyze tone.')
                else:
                    return f"Error analyzing tone: {response.status}"
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    async def generate_response(self, user_input):
        """Generate an AI response based on user input and tone asynchronously"""
        prompt = f"As Jock, an AI assistant that understands human tone, respond to: '{user_input}'"

        payload = {
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with self._session.post(self.url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('response', 'Unable to generate response.')
                else:
                    return f"Error generating response: {response.status}"
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

# Global instance
jock_analyzer = JockToneAnalyzer()

async def analyze_user_tone(user_input):
    """Function to analyze user tone"""
    return await jock_analyzer.analyze_tone(user_input)

async def generate_jock_response(user_input):
    """Function to generate AI response"""
    return await jock_analyzer.generate_response(user_input)

