import os
from google import genai
from google.genai import types
from ai.process_queue import addRequest
from utils.file_loader import getFileParts
from ai.generate import generate
from utils.file_loader import saveResult


topics = [
    "Accessory digestive organs",
    "Alimentary canal organs",
    "Anti Inflammatory Drugs",
    "Antimicrobials",
    "Connective Tissue",
    "Epithelium",
    "Esophagus",
    "Histology of the peripheral nervous system",
    "Hypersensitivies and autoimmune diseases",
    "Kidney",
    "Lipid Lowering Drugs",
    "Medical Histology",
    "Oral Cavity and Salivary Glands",
    "Phagocytic Cells",
    "Skin and Glands",
    "Transplantation",
    "Vasoactive Drugs for hypertension",
    "VDJ recombination",
    "Acute coronary syndromes",
    "Hypertension",
    "Fibroids",
    "Placenta",
    "Mitral stenosis",
    "Aortic regurgitation",
    "Trophoblastic neoplasia",
    "Cervical neoplasia",
    "Aortic stenosis",
    "Chronic coronary artery disease",
    "Female pelvic anatomy",
    "Ovarian pathology",
]

inputPath = os.environ.get("INPUT_PATH")
outputPath = os.environ.get("OUTPUT_PATH")


def handleTopic(client: genai.Client, path: str, depth:int = 0):

    fullPath = os.path.join(inputPath, path)
    mainTopicName = os.path.basename(os.path.normpath(fullPath))
    if mainTopicName.split(" - ")[1] not in topics:
        return
    outPath, _ = os.path.split(os.path.normpath(os.path.join(outputPath, path)))
    resultPath = os.path.join(outPath, f"{mainTopicName}.json")
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
