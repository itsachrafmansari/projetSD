from datetime import datetime


class CourseDocument:
    def __init__(self, file_name, file_type, metadata, content, tags):
        """
        Initialize a CourseDocument object.

        Args:
            file_name (str): Name of the file.
            file_type (str): Type of the file (e.g., "pdf").
            metadata (dict): Metadata about the document.
            content (dict): Content of the document (e.g., extracted text).
            tags (list): List of tags for categorization.
        """
        self.file_name = file_name
        self.file_type = file_type
        self.metadata = metadata
        self.content = content
        self.tags = tags
        self.upload_date = datetime.utcnow()

    def to_dict(self):
        """
        Convert the CourseDocument object to a dictionary for MongoDB storage.

        Returns:
            dict: A dictionary representation of the document.
        """
        return {
            "file_name": self.file_name,
            "file_type": self.file_type,
            "metadata": self.metadata,
            "content": self.content,
            "tags": self.tags,
            "upload_date": self.upload_date
        }