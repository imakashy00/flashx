from pydantic import BaseModel
from pymongo import MongoClient


class Response(BaseModel):
    quizzes: list = []
    flashcards: list = []
    summaries: list = []
