from fastapi import Query, Depends, APIRouter
from datetime import datetime, timedelta
from utils.mongo_client import get_mongo_client
from typing import List, Optional
from pymongo import MongoClient
from constants import DB_NAME, CHAT_LOGS_COLLECTION

router = APIRouter()


@router.get(
    "/get_chat_logs",
    summary="Retrieve chat logs from the past X hours or all",
    description=(
        "Fetches chat logs stored in the MongoDB database under the defined database and `Chat-Logs` collection. "
        "If the `hours` query parameter is provided, only logs from the past `hours` number of hours are returned. "
        "Otherwise, all chat logs are fetched."
    ),
    responses={
        200: {
            "description": (
                "A list of chat logs filtered by the past `hours` parameter or all logs if no parameter is provided:\n\n"
                "- **_id**: Unique identifier for the chat log.\n"
                "- **question**: The user's question submitted to the system.\n"
                "- **answer**: The system's response to the user's question.\n"
                "- **chat_id**: Unique identifier for the chat session.\n"
                "- **question_id**: Unique identifier for the specific question in the session.\n"
                "- **timestamp**: ISO 8601 formatted timestamp indicating when the log entry was created."
            ),
            "content": {
                "application/json": {
                    "example": [
                        {
                            "_id": "677ffbb35808278eec558ccb",
                            "question": "Mi a jelentősége a szerepköröknek?",
                            "answer": "Az keretrendszerben kialakított szerepkörök igazodnak a később kielekításra kerülő szabályozókhoz, ahol ezen szerepkörök kerülnek megjelenítésre.",
                            "chat_id": "b37e6182-8b0b-4a82-9d10-d7f6ddc52fd3",
                            "question_id": "677ec97711172d691541fa4c",
                            "timestamp": "2025-01-09T16:39:15.658000",
                        }
                    ]
                }
            },
        },
        422: {
            "description": "Validation error for hours parameter",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "greater_than_equal",
                                "loc": ["query", "hours"],
                                "msg": "Input should be greater than or equal to 1",
                                "input": "0",
                                "ctx": {"ge": 1},
                                "url": "https://errors.pydantic.dev/2.9/v/greater_than_equal",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Database connection failed"}
                }
            },
        },
    },
    tags=["Get Chat Logs"],
)
def get_chat_logs(
    hours: Optional[int] = Query(
        None,
        description="Filter logs from the past `hours` hours. If not provided, all logs are returned.",
        ge=1,
        le=168,  # Limit to 1 week (168 hours)
    ),
    db_client: MongoClient = Depends(get_mongo_client),
):
    db = db_client[DB_NAME]
    collection = db[CHAT_LOGS_COLLECTION]

    query = {}
    if hours is not None:
        # Calculate the datetime for the past `hours`
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query["timestamp"] = {"$gte": time_threshold}

    logs = list(collection.find(query))

    # Convert MongoDB object IDs to strings and prepare the JSON response
    json_logs = []
    for log in logs:
        log["_id"] = str(log["_id"])
        json_logs.append(log)
    return json_logs
