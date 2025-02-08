from AutoRevise.course_extractor.app.db.connector import get_mongodb_connection
from AutoRevise.course_extractor.app.db.models import CourseDocument

def save_course_to_mongodb(course_document):
    db = get_mongodb_connection()
    collection = db["courses"]
    result = collection.insert_one(course_document.to_dict())
    return result.inserted_id