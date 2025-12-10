from pymongo import errors
from car_scraper.db.mongo_client import get_mongo_collection
import logging

logger = logging.getLogger(__name__)


def save_payload(api_json: dict):
    if not api_json:
        logger.warning("Empty payload. Skipping save.")
        return

    collection = get_mongo_collection()

    if collection is None:
        logger.warning("MongoDB connection is not available.")
        return

    try:
        unique_id = api_json.get("UniqueId")

        if unique_id:
            collection.update_one(
                {"UniqueId": unique_id},
                {"$set": api_json},
                upsert=True
            )
        else:
            collection.insert_one(api_json)

        logger.info(f"Ad successfully {'updated' if unique_id else 'inserted'} into MongoDB.")

    except errors.PyMongoError as e:
        logger.error(f"Error while saving to MongoDB: {e}")
