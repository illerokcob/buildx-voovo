import os
from openai import OpenAI

from utils.file_loader import loadPrompt, readJsonContentInfoToString, readPdfToString

# Create an OpenAI client with your API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generateVerification(aiResponse: str, path: str):
    
    contentInfo = readJsonContentInfoToString(path)

    pdfContent = readPdfToString(path)
    # Generate a chat response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": pdfContent},
            {"role": "user", "content": f"Content info: {contentInfo}"},
            {"role": "user", "content": loadPrompt("openai_verification_prompt.txt").text},
            {"role": "user", "content": aiResponse},
        ]
    )
    return response.choices[0].message.content
