# This file is used to initialize a simple databse schema and update the indexes to be used in the code
# It pauses the initial setup while the index is being created

import logging
import time
from constants import *


def check_and_create_db_schema(client):

    # Counter variable later used to add a 5 second delay if a table is created before creating indexes
    count = 0

    logging.basicConfig(level=logging.INFO)
    if DB_NAME not in client.list_database_names():
        logging.info("Database not found, creating database")
        db = client[DB_NAME]
        count += 1
    else:
        logging.info("Database found")
        db = client[DB_NAME]

    # Create collections if they don't exist
    if CHAT_LOGS_COLLECTION not in db.list_collection_names():
        logging.info("Chat Logs Collection not found, creating collection")
        db.create_collection(CHAT_LOGS_COLLECTION)
        db[CHAT_LOGS_COLLECTION].insert_one({"dummy": "dummy"})
        db[CHAT_LOGS_COLLECTION].delete_one({"dummy": "dummy"})
        count += 1
    else:
        logging.info("Chat Logs Collection found")

    if MULTILINGUAL_QUESTIONS_COLLECTION not in db.list_collection_names():
        logging.info("Multilingual Questions Collection not found, creating collection")
        db.create_collection(MULTILINGUAL_QUESTIONS_COLLECTION)
        db[MULTILINGUAL_QUESTIONS_COLLECTION].insert_one({"dummy": "dummy"})
        db[MULTILINGUAL_QUESTIONS_COLLECTION].delete_one({"dummy": "dummy"})
        count += 1
    else:
        logging.info("Multilingual Questions Collection found")

    if UNANSWERED_QUESTIONS_COLLECTION not in db.list_collection_names():
        logging.info("Unanswered Questions Collection not found, creating collection")
        db.create_collection(UNANSWERED_QUESTIONS_COLLECTION)
        db[UNANSWERED_QUESTIONS_COLLECTION].insert_one({"dummy": "dummy"})
        db[UNANSWERED_QUESTIONS_COLLECTION].delete_one({"dummy": "dummy"})
        count += 1
    else:
        logging.info("Unanswered Questions Collection found")

    if REVIEW_QUESTIONS_COLLECTION not in db.list_collection_names():
        logging.info("Review Questions Collection not found, creating collection")
        db.create_collection(REVIEW_QUESTIONS_COLLECTION)
        db[REVIEW_QUESTIONS_COLLECTION].insert_one({"dummy": "dummy"})
        db[REVIEW_QUESTIONS_COLLECTION].delete_one({"dummy": "dummy"})
        count += 1
    else:
        logging.info("Review Questions Collection found")

    logging.info("Database setup complete")

    # If any collection is created, wait for 5 seconds to let the indexes be created
    if count > 0:
        time.sleep(5)

    # check if index exists
    collection = db[MULTILINGUAL_QUESTIONS_COLLECTION]
    try:
        new_index_definition = {"mappings": {"dynamic": True}}

        collection.update_search_index(
            MULTILINGUAL_QUESTIONS_INDEX, new_index_definition
        )
        logging.info(f"Updated index {MULTILINGUAL_QUESTIONS_INDEX}")
    except:
        pass
    try:
        index = {
            "definition": {"mappings": {"dynamic": True}},
            "name": MULTILINGUAL_QUESTIONS_INDEX,
        }
        collection.create_search_index(index)
        logging.info(f"Created index {MULTILINGUAL_QUESTIONS_INDEX}")
    except:
        pass

    collection = db[UNANSWERED_QUESTIONS_COLLECTION]
    try:
        new_index_definition = {"mappings": {"dynamic": True}}

        collection.update_search_index(UNANSWERED_QUESTIONS_INDEX, new_index_definition)
        logging.info(f"Updated index {UNANSWERED_QUESTIONS_INDEX}")
    except:
        pass
    try:
        index = {
            "definition": {"mappings": {"dynamic": True}},
            "name": UNANSWERED_QUESTIONS_INDEX,
        }
        collection.create_search_index(index)
        logging.info(f"Created index {UNANSWERED_QUESTIONS_INDEX}")
    except:
        pass
