import base64
import os
from google import genai
from google.genai import types

from utils.file_loader import loadPrompt


def generate(client: genai.Client, parts):

    model = "gemini-2.0-flash-thinking-exp-01-21"
    contents = [
        types.Content(
            role="user",
            parts=[
                *parts,
            ],
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=64,
        max_output_tokens=65536,
        response_mime_type="text/plain",
        system_instruction=[
            loadPrompt("default_prompt.txt")
        ],
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    
    
    return response.text
