from AutoRevise.course_extractor.app.db.connector import get_mongodb_connection
from AutoRevise.course_extractor.app.db.models import CourseDocument


def save_course_to_mongodb(course_document):
    """
    Save a CourseDocument object to the `python_courses` collection in the `courses_db` database.

    Args:
        course_document (CourseDocument): The document to save.

    Returns:
        ObjectId: The ID of the inserted document.
    """
    # Get the MongoDB connection
    db = get_mongodb_connection()

    # Access the `python_courses` collection in the `courses_db` database
    collection = db["python_courses"]

    # Insert the document and return the inserted ID
    result = collection.insert_one(course_document.to_dict())
    return result.inserted_id