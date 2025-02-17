from AutoRevise.course_extractor.app.db.connector import get_mongodb_connection
from AutoRevise.course_extractor.app.db.models import CourseDocument

def save_courses_to_mongodb(course_documents):
    """
    Save multiple CourseDocument objects to the `python_courses` collection in the `courses_db` database.

    Args:
        course_documents (list[CourseDocument]): The list of documents to save.

    Returns:
        list[ObjectId]: The list of inserted document IDs.
    """
    # Get the MongoDB connection
    db = get_mongodb_connection()

    # Access the `python_courses` collection in the `courses_db` database
    collection = db["python_courses"]

    # Convertir chaque objet en dictionnaire
    documents = [doc.to_dict() for doc in course_documents]

    # Insérer tous les documents en une seule opération
    if documents:
        result = collection.insert_many(documents)
        return result.inserted_ids
    return []
