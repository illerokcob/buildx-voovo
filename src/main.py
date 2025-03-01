import os
from google import genai
from google.genai import types
from utils.file_loader import get_file_parts
from ai.generate import generate

def main():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    parts = get_file_parts(client, "/home/kissb/CodeLinux/buildx-voovo/inputs/Anatomy🫁/Anatomy🫁 - Accessory digestive organs/")
    generate(client, parts)

main()