import json
import math
from dotenv import load_dotenv
import os
from .extract_text import extract_text_from_pdf, split_into_chunks
import google.generativeai as genai
from Mongo.database import store_summary_response, store_quiz_response, store_flashcard_response


load_dotenv()


Api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=Api_key)

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

quizz_prompt = """
    Your task is to generate quiz based on the given content.
    important: Generate the questions related to the topics in pdf not about the data about the file.
    I am giving you a content in \"<CONTEXT>\". You need to generate exactly \"<QUESTION_COUNT>\" questions
    under the key \"quiz\" in JSON format. Each question should have the following
    format:
    {
        \"question\": \"<QUESTION>\",
        \"options\": [\"<OPTION1>\", \"<OPTION2>\", \"<OPTION3>\", \"<OPTION4>\"],
        \"answer\": \"<ANSWER>\"
    }
    Generate the options for the given question very similar to the correct answer.
    Generate \"<QUESTION_COUNT>\" important questions about the \"CONTEXT\"
    very important: You should provide response with proper format such that it should be easy to extract
    the question programmatically in python. Enclosed it within 3 backticks.
    Apply double quotes to json data not single quotes. 
    send data so that text from the it can be extracted 
    important: avoid using quotes in json values

"""
flash_prompt = """
your task is to generate flash cards having question and answer on given content.
I am giving you a content in \"<CONTEXT>\". You need to generate exactly <QUESTION_COUNT> questions
    in JSON format under a key \"flash\". Each question should have the following
    format:
    {
        \"term\": \"<Term>\",
        \"answer\": \"<DESCRIPTION on the term>\"
    }
    important:Generate the questions related to the topics in pdf not about the data about the file or author or book.
    Generate \"<QUESTION_COUNT>\" important questions about the \"CONTEXT\"
    very important: You should provide response with proper format such that it should be easy to extract
    the question and answer programmatically in python. Enclosed it within 3 backticks.
    Apply double quotes to json data not single quotes.
    send data so that text from the it can be extracted 
    important: avoid using quotes in json values and Avoid escape characters in json values

"""
summary_prompt = """
your task is to generate summary of most topics in points.
I am giving you a content in \"<CONTEXT>\". You need to generate exactly \"<SUMMARY_POINTS>\" points
    in JSON format under a key \"summary\". Points should should have the following
    format:
    {
         \"point\":\"<POINT>\",    
        
    }
    There should be only one key
    Generate \"<SUMMARY_POINTS>\" important points about the \"CONTEXT\"
    important:Generate the points related to the topics in pdf not about the data about the file or author or book.
    very important: You should provide response with proper json format such that it should be easy to extract
    the points programmatically in python. Enclosed it within 3 backticks.
    Apply double quotes to json data not single quotes.
    send data so that text from the it can be extracted 
    important: avoid using quotes in json values
"""


def read_pdf(user_input):
    print("Reading PDF...")
    text = extract_text_from_pdf(user_input)
    return split_into_chunks(text)


#Generate Flashcards //////////////////////////////////////////////////////////////////

def generate_flash(tokens, flag, questions):
    global flash_prompt
    flash_array = []
    if flag:
        for token in tokens:
            ques_per_token_count = str(math.ceil(int(questions) / len(tokens)))
            flash_prompt = flash_prompt.replace("<CONTEXT>", token).replace("<QUESTION_COUNT>", ques_per_token_count)
            response = model.generate_content(flash_prompt)
            response = response.text.strip('```json')
            flash_json = json.loads(response)
            for ques in flash_json.get('flash'):
                flash_array.append(ques)
        store_flashcard_response(flash_array)
    else:
        flash_prompt = flash_prompt.replace("<CONTEXT>", tokens).replace("<QUESTION_COUNT>", str(questions))
        response = model.generate_content(flash_prompt)
        response = response.text.strip('```json')
        flash_json = json.loads(response)
        for term in flash_json.get('flash'):
            flash_array.append(term)
    store_flashcard_response(flash_array)


# Generate quizzes////////////////////////////////
def generate_quizz(tokens, flag, questions):
    global quizz_prompt
    quiz_array = []
    if flag:
        for token in tokens:
            ques_per_token_count = str(math.ceil(int(questions) / len(tokens)))
            quizz_prompt = quizz_prompt.replace("<CONTEXT>", token).replace("<QUESTION_COUNT>", ques_per_token_count)
            response = model.generate_content(quizz_prompt)
            response = response.text.strip('```json')
            quiz_json = json.loads(response)
            print(quiz_json)
            for ques in quiz_json.get('quiz'):
                quiz_array.append(ques)
        store_quiz_response(quiz_array)
        # //////////////////////////////////////////////////////////////////////////////
    else:
        print("generating")
        quizz_prompt = quizz_prompt.replace("<CONTEXT>", tokens).replace("<QUESTION_COUNT>", str(questions))
        response = model.generate_content(quizz_prompt)
        response = response.text.strip('```json')
        quiz_json = json.loads(response)
        for ques in quiz_json.get('quiz'):
            quiz_array.append(ques)
    store_quiz_response(quiz_array)


def generate_summary(tokens, flag, questions):
    global summary_prompt
    summ_array = []
    if flag:
        for token in tokens:
            ques_per_token_count = str(math.ceil(int(questions) / len(tokens)))
            summary_prompt = summary_prompt.replace("<CONTEXT>", token).replace("<SUMMARY_POINTS>",
                                                                                ques_per_token_count)
            response = model.generate_content(summary_prompt)
            response = response.text.strip('```json')
            summ_json = json.loads(response)
            for point in summ_json.get('summary'):
                summ_array.append(point)
        store_summary_response(summ_array)
    else:
        summary_prompt = summary_prompt.replace("<CONTEXT>", tokens).replace("<SUMMARY_POINTS>", str(questions))
        response = model.generate_content(summary_prompt)
        response = response.text.strip('```json')
        summ_json = json.loads(response)
        for point in summ_json.get('summary'):
            summ_array.append(point)
    store_summary_response(summ_array)



