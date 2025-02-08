from datetime import datetime
from bson import ObjectId

class CourseDocument:
    def __init__(self, file_name, file_type, metadata, content, tags):
        self.file_name = file_name
        self.file_type = file_type
        self.metadata = metadata
        self.content = content
        self.tags = tags
        self.upload_date = datetime.utcnow()

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "file_type": self.file_type,
            "metadata": self.metadata,
            "content": self.content,
            "tags": self.tags,
            "upload_date": self.upload_date
        }