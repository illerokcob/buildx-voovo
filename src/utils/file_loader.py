import glob
import json
import os
from pathlib import Path
import PyPDF2
from google import genai
from google.genai import types
import re

from utils.levenshteinDistance import levenshteinDistance

def loadPdfs(client: genai.Client, path: str):
    files = glob.glob(f"{path}*.pdf")
    uploaded_files = []
    for file in files:
        uploaded_files.append(client.files.upload(file=file))
    parts = []
    for uploaded_file in uploaded_files:
        parts.append(
            types.Part.from_uri(
                file_uri=uploaded_file.uri,
                mime_type=uploaded_file.mime_type,
            ))
    
    return parts


def saveJSON(dest: str, data: any):
    Path(os.path.dirname(dest)).mkdir(parents=True, exist_ok=True)
    with open(dest, "w") as file:
        print(json.dumps(data, indent=4), file=file) 

# Returns True if the subtopics matched the expectations
def saveResult(src: str, dest: str, res_data: dict):
    
    files = glob.glob(f"{src}/*.json")
    with open(files[0],"r") as file:
        src_data = json.load(file)
    
    src_subtopics = src_data.get("mainTopic").get("subTopics")
    src_data["mainTopic"]["team_name"] = "Bobókocka"

    res_subtopics = res_data.get("subTopics")
    for i in range(len(src_subtopics)):
        if levenshteinDistance(src_subtopics[i].get("title"), res_subtopics[i].get("title")) < 5: # check how different the subtopics are
            try:
                src_subtopics[i]["quizzes"] = res_subtopics[i].get("quizzes")
            except:
                return False
        else:
            print(f'Subtopic mismatch: {src_subtopics[i].get("title")} != {res_subtopics[i].get("title")}')
            return False
    
    
    saveJSON(dest, src_data)
        # the src_data is returned, because the quizzes are added to it and this way the mainTopic and the subTopic names are reserved like in the examples
    
    return True

def getSubtopics(path: str):
    files = glob.glob(f"{path}/*.json")
    with open(files[0],"r") as file:
        data = json.load(file)
    subtopics = []
    for subtopic in data.get("mainTopic").get("subTopics"):
        subtopics.append(subtopic.get("title"))
    parts = [
        types.Part.from_text(text=f"Only include these subtopics:\n{str(subtopics)}"),
        
        ]
    contentInfo = data.get("mainTopic").get("content_info")
    if contentInfo:
        parts.append(types.Part.from_text(text=str(contentInfo))),
    
    return parts

def getFileParts(client: genai.Client, path: str):
    parts = loadPdfs(client, path)
    parts += getSubtopics(path)
    return parts

def loadPrompt(promptName: str):
    path = os.path.join(os.environ.get("PROMPT_LOCATIONS"), promptName)
    with open(path, "r") as file:
        prompt = file.read()
    return types.Part.from_text(
                text=prompt
            )

# Reads the content_info from the json files
def readJsonContentInfoToString(path:str):
    files = glob.glob(f"{path}/*.json")
    with open(files[0],"r") as file:
        data = json.load(file)

    contentInfo = data.get("mainTopic").get("content_info")
    if contentInfo:
        return str(contentInfo)
    return ""

def readPdfToString(path: str):
    files = glob.glob(f"{path}*.pdf")
    text = ''
    for file in files:
        with open(file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Iterate through each page and extract text
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
    return text
