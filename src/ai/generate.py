from time import sleep
from google import genai
from google.genai import types
from utils.file_loader import loadPrompt
import threading

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

def generate(client: genai.Client, parts, prompt: str):
    global running
    global requests
    if running:
        requests += 1
        with condition:
            condition.wait()
    else:
        running = True
        cooldown = threading.Thread(target=startCooldown,args=())
        cooldown.start()
    
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
            loadPrompt(prompt)
        ],
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return response.text


