import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

MONGODB_URI = os.getenv("MONGODB_URI")
