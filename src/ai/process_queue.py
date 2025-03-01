import threading
from google import genai
from google.genai import types
from utils.file_loader import getFileParts
from ai.generate import generate
from utils.file_loader import saveResult
import time


threadFinishedEvent = threading.Event()
runningThreads = 0
MAX_THREADS = 20

MIN_DELAY_MS = 6000 # Minimum waiting time between starting new requests
delayEvent = threading.Event()
delayEvent.set()

def topicWorker(client, srcPath, resPath, topic):
    global runningThreads
    prefix = f"Main topic: '{topic}'"


    try:
        parts = getFileParts(client, srcPath)
        result = generate(client, parts)
        
        # Update line by overwriting it
        if saveResult(srcPath, resPath, result):
            print(f"{prefix} ✅")
        else:
            print(f"{prefix} ❌")

    except Exception as e:
        print(f"{prefix} ❌❌❌")
        
        if str(e).startswith("429"):
            print("Out of resource, waiting 30 seconds")
            time.sleep(30)
            addRequest(client, srcPath, resPath, topic)
        else:
            print(e)
            print("❌❌❌ Cannot resolve ❌❌❌")

    threadFinishedEvent.set()
    runningThreads -= 1

def delay():
    delayEvent.clear()
    time.sleep(MIN_DELAY_MS * 0.001)
    delayEvent.set()

def addRequest(client: genai.Client, srcPath: str, resPath: str, topic: str, depth: int = 0):
    global runningThreads
    
    delayEvent.wait()
    delayThread = threading.Thread(target=delay,args=())
    delayThread.start()
        
    if runningThreads >= MAX_THREADS:
        threadFinishedEvent.wait()
    runningThreads += 1
    if runningThreads >= MAX_THREADS:
        threadFinishedEvent.clear()
    thread = threading.Thread(target=topicWorker, args=(client, srcPath, resPath, topic))
    thread.start()