import glob
import json
from google import genai
from google.genai import types

def load_pdfs(client: genai.Client, path: str):
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

def get_subtopics(path: str):
    files = glob.glob(f"{path}*.json")
    with open(files[0],"r") as file:
        data = json.load(file)
    subtopics = []
    for subtopic in data.get("mainTopic").get("subTopics"):
        subtopics.append(subtopic.get("title"))
    return subtopics

def get_file_parts(client: genai.Client, path: str):
    parts = load_pdfs(client, path)
    parts.append(types.Part.from_text(text=f"Subtopics:\n{str(get_subtopics(path))}"))
    return parts
