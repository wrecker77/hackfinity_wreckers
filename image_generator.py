import requests
from PIL import Image
from io import BytesIO



def generate_image(prompt: str,output_path: str = "output.png"):
    # api_key = "sk-HNjvk4RNypKy53WlENlv31YVMj66lcd7syc2NPjLDstjxvGZ"
    api_key= "sk-dNbSxU1nanUp1M11aS0a1JpOnwyE2WvLBhqgBmmNKKShMU7F"
    """
    Generate an image using Stability AI's Stable Diffusion Core API (correct Accept and multipart format).
    """

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*",  # ✅ Accept anything image-based
    }

    # Data must be passed in 'files' to make it multipart/form-data
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save(output_path)
        return output_path
    else:
        try:
            return f"Error {response.status_code}: {response.json()}"
        except:
            return f"Error {response.status_code}: {response.text}"




