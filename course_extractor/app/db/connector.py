from pymongo import MongoClient
from course_extractor.app.config.settings import MONGODB_URI


def get_mongodb_connection():
    """
    Connect to the MongoDB cluster and return the `courses_db` database.

    Returns:
        Database: The `courses_db` database object.
    """
    # Ensure MONGODB_URI is not None or empty
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not set in the environment variables.")

    # Connect to the MongoDB cluster
    client = MongoClient(MONGODB_URI)

    # Access the `courses_db` database
    db = client["courses_db"]
    return db