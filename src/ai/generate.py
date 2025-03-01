import base64
import os
from google import genai
from google.genai import types


def generate(client: genai.Client, parts):

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
            types.Part.from_text(
                text="""Your task is to generate a quiz from the provided pdfs. Separate the quiestions based on the given subtopics. Each question should have 1 good and 4 wrong options.
                    Make sure to use the reference materials and make the questions as technical as possible, so no obvious answers, also no short answers, make them complicated.
                    Each subtopic should have 3-14 questions based on the length and contents of the topic.
                    Output the quiz in json format like this:
                    "subTopics": [
                    {
                        "title": "The Nose and its Adjacent Structures",
                        "quizzes": [
                        {
                            "question": "What are the primary functions of the respiratory system?",
                            "goodAnswer": "To provide oxygen to body tissues for cellular respiration, remove carbon dioxide as a waste product, and help maintain acid-base balance.",
                            "wrongAnswer_1": "To regulate blood circulation, store excess oxygen in the lungs, and break down carbon dioxide into nitrogen and water.",
                            "wrongAnswer_2": "To filter toxins from the bloodstream, transport oxygen directly to muscles, and stabilize body temperature.",
                            "wrongAnswer_3": "To produce enzymes for digestion, absorb nutrients from inhaled air, and control the pH of stomach fluids.",
                            "wrongAnswer_4": "To generate red blood cells and to store carbon dioxide for later use."
                        },"""
            ),
        ],
    )
    result = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        result = result + chunk.text
        print(chunk.text, end="")
    return result
