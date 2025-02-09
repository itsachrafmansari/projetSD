import os

from AutoRevise.course_extractor.app.db.models import CourseDocument
from AutoRevise.course_extractor.app.extractors.pdf_extractor import extract_text_from_pdf, download_pdf
from AutoRevise.course_extractor.app.storage.mongodb_storage import save_course_to_mongodb


# Example usage
pdf_path = "downloads/cours-python.pdf"
text = extract_text_from_pdf(pdf_path)
url = "https://urfist.pages.math.unistra.fr/cours-python/cours-python.pdf"
downloaded_pdf = download_pdf(url, "downloads")
# Example data
file_name = os.path.basename(url),
file_type = "pdf"
metadata = {
    "title": "Introduction to Python",
    "source": url
}
content = {
    "text": text
}
tags = ["python", "programming"]

# Create a CourseDocument
course_doc = CourseDocument(file_name, file_type, metadata, content, tags)

# Save the document to MongoDB
inserted_id = save_course_to_mongodb(course_doc)
print(f"Document saved with ID: {inserted_id}")