from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from datetime import datetime

from utils.mongo_client import get_mongo_client
from utils.base_models import MultilingualQuestionRequest
from utils.translation import translate_to_all_languages
from utils.databse_schema import update_index
from constants import *

router = APIRouter()


@router.post(
    "/add_multilingual_question",
    summary="Create a multilingual question",
    description="Accepts questions and answers in English, Hungarian, and German, translates them to all three languages, and stores them in the multilingual questions collection.",
    responses={
        201: {
            "description": "Multilingual question created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Multilingual question created successfully.",
                        "id": "generated_id",
                    }
                }
            },
        },
        400: {
            "description": "Invalid input.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "At least one pair of question and answer must be provided in the same language."
                    }
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to create multilingual question."}
                }
            },
        },
    },
    tags=["Multilingual Questions"],
)
def create_multilingual_question(
    request: MultilingualQuestionRequest,
    client: MongoClient = Depends(get_mongo_client),
):
    try:
        # Validate that at least one language pair is provided
        request.validate_languages()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    try:
        db = client[DB_NAME]
        multilingual_questions = db[MULTILINGUAL_QUESTIONS_COLLECTION]

        # Prepare data for translation
        data = request.dict()
        translations = translate_to_all_languages(data)

        # Prepare the document to insert
        document_en = {
            "question": translations.get("en_question"),
            "answer": translations.get("en_answer"),
            "references": request.references or [],
            "timestamp": datetime.utcnow(),
        }

        document_hu = {
            "question": translations.get("hu_question"),
            "answer": translations.get("hu_answer"),
            "references": request.references or [],
            "timestamp": datetime.utcnow(),
        }

        document_de = {
            "question": translations.get("de_question"),
            "answer": translations.get("de_answer"),
            "references": request.references or [],
            "timestamp": datetime.utcnow(),
        }

        inserted_en = multilingual_questions.insert_one(document_en)
        inserted_hu = multilingual_questions.insert_one(document_hu)
        inserted_de = multilingual_questions.insert_one(document_de)

        # update the index of the collection
        update_index(multilingual_questions, MULTILINGUAL_QUESTIONS_INDEX)

        return {
            "detail": "Multilingual question created successfully.",
            "en_id": str(inserted_en.inserted_id),
            "hu_id": str(inserted_hu.inserted_id),
            "de_id": str(inserted_de.inserted_id),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to create multilingual question."
        ) from e
