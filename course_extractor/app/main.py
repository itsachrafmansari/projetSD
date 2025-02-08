from AutoRevise.course_extractor.app.extractors.pdf_extractor import extract_text_and_images_from_pdf
from AutoRevise.course_extractor.app.storage.mongodb_storage import save_course_to_mongodb
from AutoRevise.course_extractor.app.db.models import CourseDocument
from AutoRevise.course_extractor.app.utils.logger import setup_logger
import os


logger = setup_logger()

def process_pdf(pdf_path):
    logger.info(f"Processing PDF: {pdf_path}")
    text, images = extract_text_and_images_from_pdf(pdf_path)
    course_doc = CourseDocument(
        file_name=os.path.basename(pdf_path),
        file_type="pdf",
        metadata={"title": "Introduction to Python", "author": "John Doe"},
        content={"text": text, "images": images},
        tags=["python", "programming"]
    )
    save_course_to_mongodb(course_doc)
    logger.info(f"Saved PDF to MongoDB: {pdf_path}")

if __name__ == "__main__":
    process_pdf("example.pdf")