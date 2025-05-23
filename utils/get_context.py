import logging


from constants import (
    DB_NAME,
    MULTILINGUAL_QUESTIONS_COLLECTION,
    MULTILINGUAL_QUESTIONS_INDEX,
    UNANSWERED_QUESTIONS_COLLECTION,
    UNANSWERED_QUESTIONS_INDEX,
    SCORE_THRESHOLD_MULTILINGUAL,
    SCORE_THRESHOLD_UNANSWERED,
)

# MongoDB Atlas Search parameters

SEARCH_PATH = "*"
SORT_ORDER = -1
LIMIT = 1

# Error codes
ERROR_CODE_NO_RESULTS = "ERR_NO_RESULTS"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def find_answer_in_knowledge_base(client, question):
    """Search for an exact match in the knowledge base."""
    result, error_code = fetch_top_result(
        client,
        question,
        MULTILINGUAL_QUESTIONS_COLLECTION,
        MULTILINGUAL_QUESTIONS_INDEX,
        SCORE_THRESHOLD_MULTILINGUAL,
    )
    if error_code:
        # adding to unanswered questions if not already present
        result, error_code = fetch_top_result(
            client,
            question,
            UNANSWERED_QUESTIONS_COLLECTION,
            UNANSWERED_QUESTIONS_INDEX,
            SCORE_THRESHOLD_UNANSWERED,
        )
        if result is None:
            unanswered_collection = client[DB_NAME][UNANSWERED_QUESTIONS_COLLECTION]
            document = {"question": question}
            unanswered_collection.insert_one(document)
            logging.info(f"Added question to unanswered questions: '{question}'")
            return ["", None]

        logging.info(f"Found question in unanswered questions Already: '{question}'")
        return ["", None]
    else:
        return result


def fetch_top_result(client, question, db_collection, db_index, score_threshold):
    """
    Fetches the top result for a question using MongoDB aggregation pipeline.

    Args:
        question (str): The question to search.

    Returns:
        tuple: (result, error_code)
            - result: [id, answer] if found, else None.
            - error_code: None if successful, or error code string.
    """

    try:
        # Access the database and collection
        logging.info(
            f"Accessing database: {DB_NAME}, collection: {MULTILINGUAL_QUESTIONS_COLLECTION}."
        )
        db = client[DB_NAME]
        collection = db[db_collection]

        # Define the aggregation pipeline
        pipeline = [
            {
                "$search": {
                    "index": db_index,
                    "text": {"query": question, "path": {"wildcard": SEARCH_PATH}},
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$match": {"score": {"$gt": score_threshold}}},
            {"$sort": {"score": SORT_ORDER}},
            {"$limit": LIMIT},
        ]

        # Log the query execution
        logging.info(f"Executing aggregation pipeline for question: '{question}'")
        results = list(collection.aggregate(pipeline))

        # Handle results
        if results:
            top_result = results[0]
            logging.info(f"Top result found with score: {top_result.get('score')}")
            return [str(top_result["_id"]), top_result.get("answer", None)], None
        else:
            logging.warning("No results found with a score above the threshold.")
            logging.info("Adding the question to unanswered questions.")

            return None, ERROR_CODE_NO_RESULTS

    except Exception as e:
        logging.error(f"An error occurred during query execution: {e}")
        return None, str(e)
