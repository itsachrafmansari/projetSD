# Importing dependencies ________________________________________________________________________________________________
import time

import requests
from dotenv import load_dotenv
from pymongo import errors
from requests import Response

from course_extractor.app.db.models import CourseDocument
from course_extractor.app.storage.mongodb_storage import save_course_to_mongodb
from course_extractor.app.utils.file_utils import sanitize_filename
from course_extractor.app.utils.logger import log_message
from course_extractor.app.utils.url_utils import parameterized_url_generator

# Defining global variables and constants ______________________________________________________________________________
load_dotenv()  # take environment variables from .env

# Scribd API
API_BASE_URL = "https://www.scribd.com/search/query"
SEARCH_TERM = "cours de python"  # TODO: Change the search term according to our needs
LANGS = ["5"]  # 5 for French
FILE_TYPES = ["pdf"]
FILE_LENGTH = "1-3"  # Available options are "1-3", "4-100" or "100+"


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
        CourseDocument(
            f"{sanitize_filename(doc_data['title'])} ({doc_data["id"]}).pdf",
            "pdf",
            {
                "title": doc_data["title"],
                "source": doc_data["reader_url"],
                "pages": doc_data["pageCount"],
                "views": doc_data["views"],
            },
            {},
            []
        ) for doc_data in docs_data_list
    ]
    return processed_docs_data, json_response["page_count"], json_response["current_page"]


def scraper():
    # Fetching the list of Scribd file URLs ____________________________________________________________________________
    current_page = 1
    pages_count = None

    # Iterate through every API page and insert the results into the database
    while True:
        log_message(f"Scridb Data Fetching | Start of processing {current_page} / {pages_count}")
        start_time = time.time()

        page_response = requests.get(
            parameterized_url_generator(
                API_BASE_URL, query=SEARCH_TERM, num_pages=FILE_LENGTH, language=LANGS, filetype=FILE_TYPES,
                page=current_page
            )
        )
        processed_data, pages_count, current_page = process_scribd_docs_response(page_response)

        # Insert the new processed data into the database
        for document in processed_data:
            try:
                save_course_to_mongodb(document)
            except errors.DuplicateKeyError as e:
                log_message(f"Scridb Data Fetching | Caught the following error while inserting data to the database {e}")

        elapsed_time = time.time() - start_time
        log_message(f"Scridb Data Fetching | End of processing ({elapsed_time:.2f}s) {current_page} / {pages_count}")

        # Increment the page counter then check if all pages are parsed
        current_page += 1
        if pages_count is not None and current_page > pages_count:
            break

if __name__ == "__main__":
    scraper()
