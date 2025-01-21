# This file contains all teh routes that can be used to delete documents from the database

# routers/review_chat.py

from fastapi import APIRouter, HTTPException
from bson import ObjectId

from utils.mongo_client import get_mongo_client
from constants import *

router = APIRouter()


@router.delete(
    "/review_questions/{id}",
    summary="Delete a review question",
    description="Delete a specific review question by ID.",
    responses={
        200: {
            "description": "Review question deleted successfully.",
            "content": {
                "application/json": {
                    "example": {"detail": "Review question deleted successfully."}
                }
            },
        },
        404: {
            "description": "Review question not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Review question not found."}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to delete review question."}
                }
            },
        },
    },
    tags=["Delete Documents"],
)
def delete_review_question(id: str):
    try:
        db_client = get_mongo_client()
        db = db_client[DB_NAME]
        review_questions = db[REVIEW_QUESTIONS_COLLECTION]

        result = review_questions.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Review question not found.")

        return {"detail": "Review question deleted successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to delete review question."
        ) from e


@router.delete(
    "/chat_logs/{id}",
    summary="Delete a chat log",
    description="Delete a specific chat log by ID.",
    responses={
        200: {
            "description": "Chat log deleted successfully.",
            "content": {
                "application/json": {
                    "example": {"detail": "Chat log deleted successfully."}
                }
            },
        },
        404: {
            "description": "Chat log not found.",
            "content": {
                "application/json": {"example": {"detail": "Chat log not found."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to delete chat log."}
                }
            },
        },
    },
    tags=["Delete Documents"],
)
def delete_chat_log(id: str):
    try:
        db_client = get_mongo_client()
        db = db_client[DB_NAME]
        chat_logs = db[CHAT_LOGS_COLLECTION]

        result = chat_logs.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat log not found.")

        return {"detail": "Chat log deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete chat log.") from e


@router.delete(
    "/multilingual_questions/{id}",
    summary="Delete a multilingual question",
    description="Delete a specific multilingual question by ID.",
    responses={
        200: {
            "description": "Multilingual question deleted successfully.",
            "content": {
                "application/json": {
                    "example": {"detail": "Multilingual question deleted successfully."}
                }
            },
        },
        404: {
            "description": "Multilingual question not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Multilingual question not found."}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to delete multilingual question."}
                }
            },
        },
    },
    tags=["Delete Documents"],
)
def delete_multilingual_question(id: str):
    try:
        db_client = get_mongo_client()
        db = db_client[DB_NAME]
        multilingual_questions = db[MULTILINGUAL_QUESTIONS_COLLECTION]

        result = multilingual_questions.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Multilingual question not found."
            )

        return {"detail": "Multilingual question deleted successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to delete multilingual question."
        ) from e


@router.delete(
    "/unanswered_questions/{id}",
    summary="Delete an unanswered question",
    description="Delete a specific unanswered question by ID.",
    responses={
        200: {
            "description": "Unanswered question deleted successfully.",
            "content": {
                "application/json": {
                    "example": {"detail": "Unanswered question deleted successfully."}
                }
            },
        },
        404: {
            "description": "Unanswered question not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Unanswered question not found."}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to delete unanswered question."}
                }
            },
        },
    },
    tags=["Delete Documents"],
)
def delete_unanswered_question(id: str):
    try:
        db_client = get_mongo_client()
        db = db_client[DB_NAME]
        unanswered_questions = db[UNANSWERED_QUESTIONS_COLLECTION]

        result = unanswered_questions.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Unanswered question not found."
            )

        return {"detail": "Unanswered question deleted successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to delete unanswered question."
        ) from e
