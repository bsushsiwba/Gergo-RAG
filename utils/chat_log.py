import logging
from datetime import datetime
from constants import DB_NAME, CHAT_LOGS_COLLECTION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def chat_log(client, question, answer, chat_id, question_id):
    """
    Logs the chat interaction into the Chat-Logs collection.

    Args:
        question (str): The question asked by the user.
        answer (str): The answer provided.
        chat_id (str): The unique chat session ID.
        referenced_question_id (str): The ID of the question.

    Returns:
        None
    """

    try:
        # Access the database and collection
        logging.info(
            f"Accessing database: {DB_NAME}, collection: {CHAT_LOGS_COLLECTION}."
        )
        db = client[DB_NAME]
        collection = db[CHAT_LOGS_COLLECTION]

        # Prepare the chat log entry
        log_entry = {
            "question": question,
            "answer": answer,
            "chat_id": chat_id,
            "refernced_question_id": question_id,
            "timestamp": datetime.utcnow(),
        }

        # Insert the log into the collection
        result = collection.insert_one(log_entry)
        if result.acknowledged:
            logging.info(f"Chat log successfully written with ID: {result.inserted_id}")
        else:
            logging.error("Failed to write chat log to the database.")

    except Exception as e:
        logging.error(f"An error occurred while logging chat: {e}")
