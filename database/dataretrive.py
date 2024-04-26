from pydantic import BaseModel, Field
from typing import List, Optional

from Mongo.connection import database


db = database('flashx')


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str


# If you had the QuizResponse model uncommented, it could look like this:
class QuizResponse(BaseModel):
    quiz: List[QuizQuestion]


class FlashcardTerm(BaseModel):
    term: str
    definition: str


class FlashcardResponse(BaseModel):
    flashcard: List[FlashcardTerm]


class SummaryResponse(BaseModel):
    summary_point: list


async def get_quiz_responses():
    quiz_questions = db.get_collection('quizzes_collection').find()  # Retrieve all documents from the collection
    quiz_questions_list = list(quiz_questions)  # Convert cursor to list
    quiz_questions_models = [QuizQuestion(**q) for q in quiz_questions_list]
    return quiz_questions_models


async def get_flash_responses():
    flash_questions = db.get_collection('flashcards_collection').find()  # Retrieve all documents from the collection
    flash_questions_list = list(flash_questions)  # Convert cursor to list
    # Convert each MongoDB document to a QuizQuestion instance
    flash_questions_models = [FlashcardTerm(**q) for q in flash_questions_list]
    return flash_questions_models


async def get_summary_responses():
    summary_points = db.get_collection('summaries_collection').find()  # Retrieve all documents from the collection
    summary_points_list = list(summary_points)  # Convert cursor to list
    summary_points_models = [SummaryResponse(**q) for q in summary_points_list]
    return summary_points_models
