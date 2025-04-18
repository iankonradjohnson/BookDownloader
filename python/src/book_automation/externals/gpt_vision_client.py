import base64
import io
from typing import Dict, Any

import openai
from PIL import Image


class GPTVisionClient:
    """
    Generic wrapper for GPT-4o Vision calls.
    Use the `invoke` method to send any prompt and image.

    Example:
        client = GPTVisionClient(model="gpt-4o-vision-mini")
        response = client.invoke(image, system_prompt)
    """

    def __init__(self, model: str = "gpt-4o-vision-mini"):
        self.model = model

    def invoke(self, img: Image.Image, system_prompt: str) -> Dict[str, Any]:
        """
        Send an image and system prompt to GPT-4o Vision, returning parsed JSON.

        Args:
            img: PIL Image to send
            system_prompt: string for the system role instruction

        Returns:
            Parsed JSON response (via response.choices[0].message.json())
        """
        # encode image as base64 data URL
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]}
        ]

        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=0,
            response_format="json"
        )
        return resp.choices[0].message.json()
