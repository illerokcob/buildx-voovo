import glob
import json
import os
from google import genai
from google.genai import types
import re

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

# Returns True if the subtopics matched the expectations
def saveResult(src: str, dest: str, aiResponse: str):
    regex = r"```json(.*)```"
    json_string = re.findall(regex,aiResponse,re.DOTALL)
    res_data = json.loads(json_string[0])
    
    files = glob.glob(f"{src}*.json")
    with open(files[0],"r") as file:
        src_data = json.load(file)
    
    src_subtopics = src_data.get("mainTopic").get("subTopics")
    res_subtopics = res_data.get("subTopics")
    for i in range(len(src_subtopics)):
        if src_subtopics[i].get("title") != res_subtopics[i].get("title"):
            return False
    
    src_data.get("mainTopic")["subTopics"] = res_subtopics
    
    with open(dest, mode="w") as file:
        print(json.dumps(src_data, indent=4), file=file)
    
    return True

def getSubtopics(path: str):
    files = glob.glob(f"{path}*.json")
    with open(files[0],"r") as file:
        data = json.load(file)
    subtopics = []
    for subtopic in data.get("mainTopic").get("subTopics"):
        subtopics.append(subtopic.get("title"))
    parts = [
        types.Part.from_text(text=f"Subtopics:\n{str(subtopics)}"),
        
        ]
    contentInfo = data.get("mainTopic").get("content_info")
    if contentInfo:
        parts.append(types.Part.from_text(text=str(contentInfo))),
    
    return parts

def getFileParts(client: genai.Client, path: str):
    parts = loadPdfs(client, path)
    parts += getSubtopics(path)
    return parts

def loadPrompt(prompName: str):
    path = os.environ.get("PROMPT_LOCATIONS") + prompName
    with open(path, "r") as file:
        prompt = file.read()
    return prompt