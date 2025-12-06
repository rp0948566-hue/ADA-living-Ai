import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from livekit.agents import function_tool

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# IMPORTANT: You need to set your image generation API key in the .env file.
# For example: IMAGE_API_KEY="your_api_key_here"
API_KEY = os.getenv("IMAGE_API_KEY")

# IMPORTANT: Replace this with the actual API endpoint for your image generation service.
# This is a placeholder and will not work without a real API endpoint.
API_URL = "https://api.example.com/v1/images/generations" 

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Directory to save the generated images
IMAGE_SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_images")


@function_tool
def generate_image_tool(prompt: str) -> dict:
    """
    Generates an image based on a text prompt using an external API.
    
    Args:
        prompt: The text prompt describing the image to generate.
        
    Returns:
        A dictionary with the result:
        - {'success': True, 'path': path_to_image} on success
        - {'success': False, 'error': error_message} on failure
    """
    if not API_KEY:
        return {"success": False, "error": "IMAGE_API_KEY is not set in the .env file."}

    if API_URL == "https://api.example.com/v1/images/generations":
        return {"success": False, "error": "The API_URL is a placeholder. Please configure it in Image-Generation/image_generator.py."}

    # Ensure the save directory exists
    os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

    # Sanitize the prompt to create a valid filename
    safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '_')).rstrip()
    filename = f"{safe_prompt[:50].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    save_path = os.path.join(IMAGE_SAVE_DIR, filename)

    # --- API Request Body ---
    # This is a common structure for image generation APIs (like DALL-E).
    # You may need to adjust this based on your chosen API's documentation.
    json_data = {
        "prompt": prompt,
        "n": 1,  # Number of images to generate
        "size": "1024x1024"  # Desired image size
    }

    try:
        print(f"🎨 Sending prompt to image generation API: '{prompt}'")
        response = requests.post(API_URL, headers=HEADERS, json=json_data, timeout=120)
        
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Assuming the API returns the image data directly in the response body
        # If it returns a URL, you'll need to make another request to download it.
        # Example for URL response:
        # image_url = response.json().get('data')[0].get('url')
        # image_data = requests.get(image_url).content

        image_data = response.content

        with open(save_path, "wb") as f:
            f.write(image_data)
            
        print(f"✅ Image successfully generated and saved to: {save_path}")
        return {"success": True, "path": save_path}

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {e}"
        print(f"❌ {error_message}")
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(f"❌ {error_message}")
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    # Example for testing the tool directly.
    # Make sure to set your IMAGE_API_KEY in a .env file in the project root.
    
    test_prompt = "A futuristic cityscape at sunset"
    result = generate_image_tool(test_prompt)
    
    if result["success"]:
        print(f"\nTest successful! Image at: {result['path']}")
    else:
        print(f"\nTest failed. Reason: {result['error']}")

    # Example of what happens if the API key is missing
    # old_key = os.environ.pop("IMAGE_API_KEY", None)
    # print("\n--- Testing with missing API key ---")
    # result_no_key = generate_image_tool(test_prompt)
    # print(f"Test result: {result_no_key}")
    # if old_key:
    #     os.environ["IMAGE_API_KEY"] = old_key
