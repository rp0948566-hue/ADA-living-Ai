import requests
import os
from dotenv import load_dotenv
from livekit.agents import function_tool
import asyncio

load_dotenv()

# Stability AI API key — set STABILITY_API_KEY in .env (no key is bundled here).
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")


def generate_image_sync(prompt: str, save_path: str = "generated_image.png") -> str:
    """Non-interactive variant for pipelines (e.g. the website builder) —
    same Stability AI call, but never pops up a fullscreen preview window."""
    if not STABILITY_API_KEY:
        return "❌ STABILITY_API_KEY not set in .env."
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {"Authorization": f"Bearer {STABILITY_API_KEY}", "Content-Type": "application/json"}
    data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 10,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 40,
    }
    resp = requests.post(url, headers=headers, json=data, timeout=90)
    if resp.status_code != 200:
        return f"❌ Stability AI error {resp.status_code}: {resp.text[:300]}"
    result = resp.json()
    artifacts = result.get("artifacts") or []
    if not artifacts:
        return "❌ No image returned by Stability AI."
    import base64
    img_data = base64.b64decode(artifacts[0]["base64"])
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(img_data)
    return f"✅ Image saved to {save_path}"

@function_tool
async def generate_image_stability(prompt: str, save_path: str = "generated_image.png") -> str:
    """
    Generate a high-quality image from a text prompt using Stability AI's API.
    Save the image to the specified path.
    """
    if not STABILITY_API_KEY:
        return "API key not found. Please set STABILITY_API_KEY in your .env file."

    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 10,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 50
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    result = response.json()
    if "artifacts" not in result or not result["artifacts"]:
        return "No image generated."
    image_base64 = result["artifacts"][0]["base64"]
    import base64
    img_data = base64.b64decode(image_base64)
    with open(save_path, "wb") as handler:
        handler.write(img_data)
    # Automatically open the image in full screen popup
    try:
        from PIL import Image, ImageTk
        import tkinter as tk
        def show_fullscreen(img_path):
            root = tk.Tk()
            root.attributes('-fullscreen', True)
            root.configure(background='black')
            img = Image.open(img_path)
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            img = img.resize((screen_width, screen_height), Image.ANTIALIAS)
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(root, image=tk_img, bg='black')
            label.pack(expand=True)
            root.bind('<Escape>', lambda e: root.destroy())
            root.mainloop()
        show_fullscreen(save_path)
    except Exception as e:
        import platform
        import subprocess
        if platform.system() == "Windows":
            os.startfile(save_path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", save_path])
        else:
            subprocess.call(["xdg-open", save_path])
    return f"High-quality image generated and saved to {save_path}"

def enhance_image(image_path: str, save_path: str = "enhanced_image.png") -> str:
    """
    Enhance the quality of an image using Stability AI's upscaling endpoint.
    """
    if not STABILITY_API_KEY:
        return "API key not found. Please set STABILITY_API_KEY in your .env file."
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image/upscale"
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }
    with open(image_path, "rb") as img_file:
        files = {"image": img_file}
        response = requests.post(url, headers=headers, files=files)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    result = response.json()
    if "artifacts" not in result or not result["artifacts"]:
        return "No enhanced image returned."
    image_base64 = result["artifacts"][0]["base64"]
    import base64
    img_data = base64.b64decode(image_base64)
    with open(save_path, "wb") as handler:
        handler.write(img_data)
    # Automatically open the enhanced image in full screen popup
    try:
        from PIL import Image, ImageTk
        import tkinter as tk
        def show_fullscreen(img_path):
            root = tk.Tk()
            root.attributes('-fullscreen', True)
            root.configure(background='black')
            img = Image.open(img_path)
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            img = img.resize((screen_width, screen_height), Image.ANTIALIAS)
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(root, image=tk_img, bg='black')
            label.pack(expand=True)
            root.bind('<Escape>', lambda e: root.destroy())
            root.mainloop()
        show_fullscreen(save_path)
    except Exception as e:
        import platform
        import subprocess
        if platform.system() == "Windows":
            os.startfile(save_path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", save_path])
        else:
            subprocess.call(["xdg-open", save_path])
    return f"Enhanced image saved to {save_path}"

if __name__ == "__main__":
    prompt = input("Enter your image prompt: ")
    result = asyncio.run(generate_image_stability(prompt))
    print(result)
    if "saved to" in result:
        enhance = input("Do you want to enhance the image quality? (y/n): ")
        if enhance.lower() == "y":
            image_path = "generated_image.png"
            print(enhance_image(image_path))
