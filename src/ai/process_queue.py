import json
import os
import threading
import traceback
from google import genai
from google.genai import types
from ai.openai_verifier import generateVerification
from utils.analitics import evalReview, filterBetter, stringToDict
from utils.file_loader import getFileParts, loadPdfs, saveJSON
from ai.generate import generate
from utils.file_loader import saveResult
import time

ENABLE_OPENAI = True

threadFinishedEvent = threading.Event()
runningThreads = 0
MAX_THREADS = 100

MIN_DELAY_MS = 10 # Minimum waiting time between starting new threads
delayEvent = threading.Event()
delayEvent.set()

ANALYTICS_PATH = os.environ.get("ANALYTICS_PATH")
FIRST_ITER_OUTPUT_PATH = os.environ.get("FIRST_ITER_OUTPUT_PATH")

def topicWorker(client, srcPath, resPath, topic):
    global runningThreads, ANALYTICS_PATH, FIRST_ITER_OUTPUT_PATH
    prefix = f"Main topic: '{topic}'"

    analitics = dict()
    try:
        print(f"{prefix} 0/3")
        parts = getFileParts(client, srcPath)
        result = stringToDict(generate(client, parts, "default_prompt.txt"))
        try:
            if FIRST_ITER_OUTPUT_PATH:
                saveResult(srcPath, os.path.join(FIRST_ITER_OUTPUT_PATH,f"{topic} - first iter.json"), result)
        except:
            ""
        print(f"{prefix} 1/3")
        
        verificationParts = loadPdfs(client, srcPath)
        verificationParts.append(types.Part.from_text(text=str(result)))
        if ENABLE_OPENAI:
            review = stringToDict(generateVerification(json.dumps(result, indent=4),srcPath))
        else:
            review = stringToDict(generate(client, verificationParts, "openai_verification_prompt.txt"))
        analitics["original"] = evalReview(review)
        print(f"{prefix} 2/3")

        parts.append(types.Part.from_text(text=str(result)))
        parts.append(types.Part.from_text(text=str(review)))
        correctedResult = stringToDict(generate(client, parts, "correction_prompt.txt"))
        
        verificationParts = loadPdfs(client, srcPath)
        verificationParts.append(types.Part.from_text(text=str(correctedResult)))
        if ENABLE_OPENAI:
            correctedReview = stringToDict(generateVerification(json.dumps(correctedResult, indent=4),srcPath))
        else:
            correctedReview = stringToDict(generate(client, verificationParts, "openai_verification_prompt.txt"))
        analitics["revised"] = evalReview(correctedReview)
        
        correctedResult = filterBetter(result, correctedResult, review, correctedReview)
        analitics["final"] = evalReview(correctedReview)

        if ANALYTICS_PATH:
            saveJSON(os.path.join(ANALYTICS_PATH,f"{topic} - stats.json"),analitics)
                    
        if saveResult(srcPath, resPath, correctedResult):
            print(f"{prefix} ✅")
        else:
            print(f"{prefix} ❌")

    except Exception as e:
        print(f"{prefix} ❌❌❌")
        
        if str(e).startswith("429") or str(e).startswith("503") or str(e).startswith("502"):
            print("Out of resource, waiting 30 seconds")
            time.sleep(30)
            addRequest(client, srcPath, resPath, topic)
        else:
            print(e)
            print("❌❌❌ Cannot resolve ❌❌❌")
            print(traceback.format_exc())

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