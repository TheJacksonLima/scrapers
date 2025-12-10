from functools import lru_cache
from pymongo import MongoClient, errors
from car_scraper.utils.config import settings
import logging

logger = logging.getLogger(__name__)


@lru_cache()
def get_mongo_collection():
    try:
        client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client[settings.MONGO_CLIENT]
        collection = db[settings.MONGO_COLLECTION]

        client.server_info()
        return collection
    except errors.ServerSelectionTimeoutError as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None
