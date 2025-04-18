import base64
import io
import os

from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI


class GPTVisionClient:
    def __init__(self, model: str = "gpt-4o-mini"):
        # Load environment variables from .env file
        load_dotenv()

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def invoke(self, img: Image.Image, system_prompt: str) -> str:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()

        response = self.client.responses.create(
            model=self.model,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": system_prompt},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"}
                ]
            }]
        )
        return response.output_text
