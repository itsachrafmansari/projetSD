from bson import ObjectId

from course_extractor.app.db.connector import get_mongodb_connection
from course_extractor.app.db.models import CourseDocument


def save_course_to_mongodb(course_document: CourseDocument, collection: str = "python_courses") -> ObjectId:
    """
    Save a CourseDocument object to the `python_courses` collection in the `courses_db` database.

    Args:
        course_document (CourseDocument): The document to save.

    Returns:
        ObjectId: The ID of the inserted document.
        :param collection: Name of the target database collection.
    """
    # Get the MongoDB connection
    db = get_mongodb_connection()

    # Access the given collection (default is python_courses) in the `courses_db` database
    collection = db[collection]

    # Insert the document and return the inserted ID
    result = collection.insert_one(course_document.to_dict())
    return result.inserted_id