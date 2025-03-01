import os
from google import genai
from google.genai import types
from ai.process_queue import addRequest
from utils.file_loader import getFileParts
from ai.generate import generate
from utils.file_loader import saveResult


inputPath = os.environ.get("INPUT_PATH")
outputPath = os.environ.get("OUTPUT_PATH")


def handleTopic(client: genai.Client, path: str, depth:int = 0):

    fullPath = os.path.join(inputPath, path)
    mainTopicName = os.path.basename(os.path.normpath(fullPath))
    
    resultPath = os.path.join(outputPath, path, f"{mainTopicName}.json")
    addRequest(client, fullPath, resultPath, mainTopicName, depth)


def processFolderRecursive(client: genai.Client,path: str, depth: int = 0, maxDepth = 10):
    fullPath = os.path.join(inputPath, path)

    entries = os.listdir(fullPath)
    
    isBranch = True
    for entry in entries:
        if os.path.isdir(os.path.join(fullPath, entry)):
            isBranch = False
            if depth < maxDepth:
                processFolderRecursive(client, os.path.join(path, entry), depth = depth + 1, maxDepth = maxDepth)
    if isBranch:
        handleTopic(client, path, depth)

def main():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")
    )

    if not os.path.isdir(inputPath):
        print(f"The path '{inputPath}' is not a valid directory.")
        return

    processFolderRecursive(client,"")


main()
