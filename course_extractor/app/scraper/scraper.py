# Importing dependencies ________________________________________________________________________________________________
import os
import time
from datetime import datetime, UTC

import requests
from requests import Response
from dotenv import load_dotenv

from course_extractor.app.storage.database import AtlasClient
from course_extractor.app.utils.files import sanitize_filename
from course_extractor.app.utils.logging import log_message
from course_extractor.app.utils.urls import parameterized_url_generator

# Defining global variables and constants ______________________________________________________________________________
load_dotenv()  # take environment variables from .env

# Scribd API
API_BASE_URL = "https://www.scribd.com/search/query"
SEARCH_TERM = "cours de python"  # TODO: Change the search term according to our needs
LANGS = ["5"]  # 5 for French
FILE_TYPES = ["pdf"]
FILE_LENGTH = "4-100"  # Available options are "1-3", "4-100" or "100+"

# Mongodb SetUp
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
mongodb_client = AtlasClient(MONGODB_URI, MONGODB_DB_NAME)


# Defining necessary functions _________________________________________________________________________________________
def search_url_generator(search_term: str, page: int = 1):
    """Takes a search term and returns a URL with parameters"""

    return parameterized_url_generator(
        API_BASE_URL, query=search_term, num_pages=FILE_LENGTH, language=LANGS, filetype=FILE_TYPES, page=page
    )


def process_scribd_docs_response(response: Response):
    json_response = response.json()

    # Extract the list of documents data from the returned json response
    docs_data_list = json_response["results"]["documents"]["content"]["documents"]

    # Reconstruct a new list that contains only the fields we want
    processed_docs_data = [
        {
            "_id": doc_data["id"],
            "file_name": f"{sanitize_filename(doc_data['title'])} ({doc_data["id"]}).pdf",
            "file_type": "pdf",
            "metadata": {
                "title": doc_data["title"],
                "source": doc_data["reader_url"],
                "pages": doc_data["pageCount"],
                "views": doc_data["views"],
            },
            "creation_date": datetime.now(UTC)
        } for doc_data in docs_data_list
    ]
    return processed_docs_data, json_response["page_count"], json_response["current_page"]


def scraper():
    # Fetching the list of Scribd file URLs ____________________________________________________________________________
    current_page = 1
    pages_count = None

    # Iterate through every API page and insert the results into the database
    while True:
        log_message(f"API Scraping | Start of processing page {current_page} / {pages_count}")
        start_time = time.time()

        page_response = requests.get(
            parameterized_url_generator(
                API_BASE_URL, query=SEARCH_TERM, num_pages=FILE_LENGTH, language=LANGS, filetype=FILE_TYPES,
                page=current_page
            )
        )
        processed_data, pages_count, current_page = process_scribd_docs_response(page_response)

        # Insert the new processed data into the database
        mongodb_client.insert_many(MONGODB_COLLECTION_NAME, processed_data, ignore_duplicates=True)

        elapsed_time = time.time() - start_time
        log_message(f"API Scraping | End of processing page ({elapsed_time:.2f}s) {current_page} / {pages_count}")

        # Increment the page counter then check if all pages are parsed
        current_page += 1
        if pages_count is not None and current_page > pages_count:
            break


if __name__ == "__main__":
    scraper()
