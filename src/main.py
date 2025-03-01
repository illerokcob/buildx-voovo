import os
from google import genai
from google.genai import types
from utils.file_loader import getFileParts
from ai.generate import generate
from utils.file_loader import saveResult


input_path = os.environ.get("INPUT_PATH")
output_path = os.environ.get("OUTPUT_PATH")


def handle_topic(client: genai.Client, path: str):
    main_topic_name = os.path.basename(path)
    head, tail = os.path.split(path)
    course_name = os.path.basename(head)

    result_path = os.path.join(output_path, course_name, f"{main_topic_name}.json")

    parts = getFileParts(client, path)
    result = generate(client, parts)

    #print(saveResult(path, result_path, result))
    saveResult(path, result_path, result)

def main():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")
    )

    if not os.path.isdir(input_path):
        print(f"The path '{input_path}' is not a valid directory.")
        return

    entries = os.listdir(input_path)
    for entry in entries:
        full_path = os.path.join(input_path, entry)
        if os.path.isdir(full_path):
            print(f"Processing course collection: {full_path}")
            entries_lvl2 = os.listdir(full_path)
            for entry_lvl2 in entries_lvl2:
                full_path_lvl2 = os.path.join(full_path, entry_lvl2)
                if os.path.isdir(full_path_lvl2):
                    print(f" Processing main topic: {full_path_lvl2}", end='', flush=True)
                    handle_topic(client, full_path_lvl2)
                    print(" ✅");


main()
