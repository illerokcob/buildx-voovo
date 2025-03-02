import json
import re

DATA_FIELDS = [
    "options",
    "question-complexity",
    "answer-complexity",
    "knowledge"
]
def devideStats(data: dict, num: float):
    for field in DATA_FIELDS:
        data[field] /= num

def addStats(data0: dict, data1: dict):
    for field in DATA_FIELDS:
        data0[field] += data1[field]
    

def evalReview(review: str):
    regex = r"```json(.*)```"
    json_string = re.findall(regex,review,re.DOTALL)
    data = json.loads(json_string[0])
        
    count = 0
    
    collectedData = dict()
    for field in DATA_FIELDS:
        collectedData[field] = 0.0
    
    for subtopic in data.get("subTopics"):
        for quiz in subtopic.get("quizzes"):
            try:
                tempData = dict()
                for field in DATA_FIELDS:
                    tempData[field] = quiz.get(field)
                addStats(collectedData, tempData)
                count += 1
            except:
                ""
    if count != 0:
        devideStats(collectedData, count)
        
        return collectedData
    else:
        return dict()
