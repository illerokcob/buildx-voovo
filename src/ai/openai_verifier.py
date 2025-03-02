import os
import threading
from time import sleep
from openai import OpenAI

from utils.file_loader import loadPrompt, readJsonContentInfoToString, readPdfToString

# Create an OpenAI client with your API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

condition = threading.Condition()

MIN_DELAY_MS = 6000 # Minimum waiting time between starting new requests

running = False
requests = 0

def startCooldown():
    global running
    global requests
    while requests > 0:
        sleep(MIN_DELAY_MS * 0.001)
        with condition:
            condition.notify(1)
            requests -= 1
    running = False
    with condition:
        condition.notifyAll()

def generateVerification(aiResponse: str, path: str):
    global running
    global requests
    requests += 1
    
    if running:
        with condition:
            condition.wait()
    else:
        running = True
        cooldown = threading.Thread(target=startCooldown,args=())
        cooldown.start()

    contentInfo = readJsonContentInfoToString(path)

    pdfContent = readPdfToString(path)
    # Generate a chat response
    response = client.chat.completions.create(
        model="gpt-4.5-preview",
        messages=[
            {"role": "user", "content": pdfContent},
            {"role": "user", "content": f"Content info: {contentInfo}"},
            {"role": "user", "content": loadPrompt("openai_verification_prompt.txt").text},
            {"role": "user", "content": aiResponse},
        ]
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content
