from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

from utils.mongo_client import get_mongo_client
from utils.base_models import RateChatRequest
from constants import DB_NAME, REVIEW_QUESTIONS_COLLECTION, CHAT_LOGS_COLLECTION

router = APIRouter()


@router.post(
    "/rate_chat",
    summary="Review a chat log",
    description="Adds a chat log to the Review-Questions collection for further review.",
    responses={
        200: {
            "description": "Chat log successfully added to reviews.",
            "content": {
                "application/json": {
                    "example": {"detail": "Chat log reviewed successfully."}
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
                    "example": {"detail": "Failed to review chat log."}
                }
            },
        },
    },
    tags=["Review Chat"],
)
def rate_chat_endpoint(
    request: RateChatRequest, db_client: MongoClient = Depends(get_mongo_client)
):
    try:
        db = db_client[DB_NAME]
        chat_logs = db[CHAT_LOGS_COLLECTION]
        review_questions = db[REVIEW_QUESTIONS_COLLECTION]

        # Find the chat log by log_id
        print(request.log_id)
        chat_log = chat_logs.find_one({"_id": ObjectId(request.log_id)})
        if not chat_log:
            raise HTTPException(status_code=404, detail="Chat log not found.")

        # Prepare the review entry
        review_entry = {
            "log_id": request.log_id,
            "question": chat_log.get("question"),
            "answer": chat_log.get("answer"),
            "timestamp": datetime.utcnow(),
        }

        # Insert into Review-Questions collection
        review_questions.insert_one(review_entry)

        return {"detail": "Chat log reviewed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to review chat log.") from e
