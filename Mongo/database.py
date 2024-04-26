from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from .connection import database

db = database('flashx')


def store_quiz_response(quiz_response: dict | list):
    for question in quiz_response:
        try:
            db.get_collection('quizzes_collection').insert_one(question)
            print("Quiz response stored successfully.")
        except ValidationError as e:
            print(f"Error processing quiz response: {e}")


def store_flashcard_response(flashcard_response: dict | list):
    for term in flashcard_response:
        try:
            db.get_collection('flashcards_collection').insert_one(term)
            print("Flash response stored successfully.")
        except DuplicateKeyError as e:
            pass
        except ValidationError as e:
            print(f"Error processing quiz response: {e}")


def store_summary_response(summary_response: dict | list):
    for point in summary_response:
        try:
            db.get_collection('summaries_collection').insert_one(point)
            print("Point response stored successfully.")
        except DuplicateKeyError as e:
            pass
        except ValidationError as e:
            print(f"Error processing quiz response: {e}")

