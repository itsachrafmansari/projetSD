# Importing dependencies ________________________________________________________________________________________________
import os
import re
import time
from urllib.parse import unquote

import requests
from dotenv import load_dotenv
from pymongo import errors
from requests import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils import parameterized_url_generator, sanitize_filename, rename_file, log_message, ensure_folder_exists
from databases import AtlasClient

# Defining global variables and constants ______________________________________________________________________________
load_dotenv()  # take environment variables from .env

# Scribd API
API_BASE_URL = "https://www.scribd.com/search/query"
SEARCH_TERM = "TD"  # TODO: Change the search term according to our needs
LANGS = ["5"]  # 5 for French
FILE_TYPES = ["pdf"]
FILE_LENGTH = "1-3"  # Available options are "1-3", "4-100" or "100+"

# MongoDB Atlas
MONGODB_ATLAS_URI = os.getenv("MONGODB_ATLAS_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
db_client = AtlasClient(MONGODB_ATLAS_URI, MONGODB_DB_NAME)

# Check the download folder
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")
ensure_folder_exists(DOWNLOAD_PATH)

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_PATH,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})


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

    # Reconstruct a new list that contains only the fields w want
    processed_docs_data = [{
        "_id": doc_data["id"],
        "title": doc_data["title"],
        "filename": f"{sanitize_filename(doc_data['title'])} ({doc_data["id"]}).pdf",
        "url": doc_data["reader_url"],
        "pages": doc_data["pageCount"],
        "views": doc_data["views"],
    } for doc_data in docs_data_list]

    return processed_docs_data, json_response["page_count"], json_response["current_page"]


def main():
    # Install the chrome driver if necessary then initiate it __________________________________________________________
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

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
        try:
            db_client.insert_many(MONGODB_COLLECTION_NAME, processed_data)
        except errors.BulkWriteError as e:
            log_message(f"Scridb Data Fetching | Caught the following error while running the Data fetching loop {e}")

        elapsed_time = time.time() - start_time
        log_message(f"Scridb Data Fetching | End of processing ({elapsed_time:.2f}s) {current_page} / {pages_count}")

        # Increment the page counter then check if all pages are parsed
        current_page += 1
        if pages_count is not None and current_page > pages_count:
            break

    # Downloading the pdf files ________________________________________________________________________________________
    # Fetch all the documents data stored in the database
    log_message("Database Data fetching | Start of the fetching process")
    docs = db_client.get_items_from(MONGODB_COLLECTION_NAME)
    log_message("Database Data fetching | Start of the fetching process")

    for idx, doc in enumerate(docs[:5]):
        _id = doc["_id"]
        url = doc["url"]
        title = doc["title"]
        filename = doc["filename"]

        # Log the start of the document downloading process
        log_message(f"PDFs Downloading | Start of processing {idx + 1}/{len(docs)}: {url}")
        start_time = time.time()

        # Get the pdf display page using https://ilide.info/
        driver.get(
            parameterized_url_generator(
                "https://ilide.info/docgeneratev2",
                fileurl=f"https://scribd.vdownloaders.com/pdownload/{_id}/{title}",
                title=title, utm_source="scrfree", utm_medium="queue",
                utm_campaign="dl"
            )
        )

        # Extract the pdf viewer page URL from the current page
        pdf_viewer_page_url = ""
        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and src.startswith("https://ilide.info/viewer/web/viewer.html?file="):
                pdf_viewer_page_url = src
                break

        # Redirect to the pdf viewer page
        log_message(f"PDFs Downloading | Redirecting to {pdf_viewer_page_url}")
        driver.get(pdf_viewer_page_url)

        # Click on the download button
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "download"))
        )
        download_button.click()

        # Extract the original download filename from the pdf viewer page URL
        decoded_pdf_viewer_page_url = unquote(pdf_viewer_page_url)
        download_filename = re.search(
            r"https://ilide\.info/docdownloadv2-([^?]+)",
            decoded_pdf_viewer_page_url
        ).group(1)

        if download_filename:  # Only rename the downloaded file if the original filename was extracted successfully
            download_filename = f"ilide.info-{download_filename}.pdf"
            log_message(f"PDFs Downloading | Extracted download filename : {download_filename}")

            # Wait for file download to complete
            while download_filename not in os.listdir(DOWNLOAD_PATH):
                log_message("PDFs Downloading | File not found yet, waiting...")
                time.sleep(5)  # Check every 5 seconds

            rename_file(os.path.join(DOWNLOAD_PATH, download_filename), os.path.join(DOWNLOAD_PATH, filename))
            log_message(f"PDFs Downloading | Renamed file '{download_filename}' to '{filename}'")

        elapsed_time = time.time() - start_time
        log_message(f"PDFs Downloading | End of processing ({elapsed_time:.2f}s) {idx + 1}/{len(docs)}: {url}")

    driver.quit()


if __name__ == "__main__":
    main()
