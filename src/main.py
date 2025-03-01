import os
from google import genai
from google.genai import types
from utils.file_loader import getFileParts
from ai.generate import generate
from utils.file_loader import saveResult

def main():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    path = "/home/kissb/CodeLinux/buildx-voovo/inputs/Anatomy🫁/Anatomy🫁 - Accessory digestive organs/"
    
    parts = getFileParts(client, path)
    result = generate(client, parts)
    print(saveResult(path, "test.json", result))

main()