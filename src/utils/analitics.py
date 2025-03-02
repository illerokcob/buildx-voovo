import json
import re

DATA_FIELDS = [
    "options",
    "question-complexity",
    "answer-complexity",
    "knowledge"
]

FIELD_WEIGHTS = {
    "options": 2,
    "question-complexity": 2,
    "answer-complexity": 2,
    "knowledge": 2
}

def devideStats(data: dict, num: float):
    for field in DATA_FIELDS:
        data[field] /= num

def addStats(data0: dict, data1: dict):
    for field in DATA_FIELDS:
        data0[field] += data1[field]
        
def stringToDict(review: str):
    regex = r"```json(.*)```"
    json_string = re.findall(regex,review,re.DOTALL)
    if len(json_string) == 0:
        return json.loads(review)
    return json.loads(json_string[0])

def evalQuestion(data: dict):
    value = 0.0
    for field in DATA_FIELDS:
        value += data[field] * FIELD_WEIGHTS[field]
    return value
    

def evalReview(data: dict):       
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



def filterBetter(result: dict, correctedResult: dict, review: dict, correctedReview: dict):
    originalSubts = result.get("subTopics")
    correctedSubts = correctedResult.get("subTopics")
    reviewSubts = review.get("subTopics")
    corrReviewSubts = correctedReview.get("subTopics")
    
    for i in range(min(len(originalSubts),len(correctedSubts),len(reviewSubts),len(corrReviewSubts))):
        quizzes = originalSubts[i].get("quizzes")
        correctedQuizzes = correctedSubts[i].get("quizzes")
        reviewQuizzes = reviewSubts[i].get("quizzes")
        correctedReviewQuizzes = corrReviewSubts[i].get("quizzes")
        for j in range(min(len(quizzes),len(correctedQuizzes),len(reviewQuizzes),len(correctedReviewQuizzes))):
            original = evalQuestion(reviewQuizzes[j])
            revised = evalQuestion(correctedReviewQuizzes[j])
            if original > revised:
                correctedQuizzes[j] = quizzes[j]
                correctedReviewQuizzes[j] = reviewQuizzes[j]
            
    
    return correctedResult