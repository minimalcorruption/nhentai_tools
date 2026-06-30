import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random

from nhentai_tools.extraction import *
from nhentai_tools.metadata import *

from nhentai_tools.exceptions import *


def _mass_download(category: str, name: str, metadata: bool) -> bool:
    name_formatted = name.replace(" ", "-")

    init_page = requests.get(f"https://nhentai.net/{category}/{name_formatted}?sort=date", headers=HEADERS)

    #Check if gallery exists
    if init_page.status_code == 404:
        raise GalleryNotFoundError(f"{category.capitalize()} not found.")
    
    # Indicate blocked request
    if init_page.status_code == 403:
        raise RequestBlockedError("Request was blocked by nhentai.")

    soup = BeautifulSoup(init_page.text, "html.parser")

    last_page = ""

    # Finding pagination controls to determine the last page
    try:    
        category_regex = r"last svelte-.+"
        category_href = soup.find("a", {"class": re.compile(category_regex)})['href']
        last_page_regex = rf"\d+"
        last_page = re.search(last_page_regex, category_href).group(0)
    except TypeError:
        last_page = "1"


    # Iterating through all pages of the specified category
    for current_page in range(1, int(last_page) + 1):
        category_page = requests.get(f"https://nhentai.net/{category}/{name_formatted}?sort=date&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(category_page.text, "html.parser")

        # Parsing list of galleries on the current page
        tag_regex = "gallery lang-\\w{2}"
        galleries = soup.find_all("div", {"class": re.compile(tag_regex)})
        
        # Extracting IDs and passing them into the central download worker
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)
            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=name_formatted, metadata=metadata)

        # Sleep to avoid rate limit
        time.sleep(random.randint(15, 50))
    
    return True


def download(gallery_id: int, path: str="downloaded", metadata: bool=False) -> bool:
    """Downloads all images from the requested gallery into specified path and optionally saves metadata.

    Accepts:
    ID of nhentai's gallery, Destination directory path, which defaults to downloaded unless specified and Metadata flag, which default to False unless specified
    """
    # Extracting gallery's data
    title = extract_title(gallery_id)
    server = extract_server(gallery_id)
    gallery_server_id = extract_gallery_server_id(gallery_id)

    path = f"{path}/{title}"
    
    # Checking if directory already exists and exits to avoid bugs  
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print("Error: Directory already exists, please delete it first.")
        print(f"Directory - {path}")
        return False

    page_counter = 1

    gallery_number_of_pages = extract_number_of_pages(gallery_id)

    request = requests.Session()
    
    # Downloading images from server
    while page_counter <= gallery_number_of_pages:
        current_image = f"{server}/galleries/{gallery_server_id}/{page_counter}.webp"
        current_image_jpg = f"{server}/galleries/{gallery_server_id}/{page_counter}.jpg"
        current_image_path = f"{path}/{page_counter}.webp"
        current_image_path_jpg = f"{path}/{page_counter}.jpg"
        current_request = request.get(current_image)
        
        # nhentai can have some parts of gallery in webp and some in jpg
        if current_request.status_code == 200:
            with open(current_image_path, 'wb') as image:
                image.write(current_request.content)
        else:
            current_request_jpg = request.get(current_image_jpg)
            with open(current_image_path_jpg, 'wb') as image:
                image.write(current_request_jpg.content)

        page_counter += 1
    
    # Checks if metadata embedding is requested
    if metadata:
        embed_metadata(extract_metadata(gallery_id), path)

    request.close()

    return True


def tag_download(tag: str, metadata: bool=False):
    """Scrapes and downloads all galleries under specified tag sorted by date.

    Accepts:
    Tag as string and Metadata flag
    """
    return _mass_download(category="tag", name=tag, metadata=metadata)


def artist_download(artist: str, metadata: bool=False):
    """Scrapes and downloads all galleries associated from a specified artist sorted by date.

    Accepts: 
    Artist's name as string and Metadata flag
    """
    return _mass_download(category="artist", name=artist, metadata=metadata)


def character_download(character: str, metadata: bool=False):
    """Scrapes and downloads all galleries featuring a specified character sorted by date.

    Accepts:
    Character's name as string and Metadata flag
    """
    return _mass_download(category="character", name=character, metadata=metadata)

def parody_download(parody: str, metadata: bool=False):
    """Scrapes and downloads all galleries under a specific parody sorted by date.

    Accepts:
    Parody as string and Metadata flag
    """
    return _mass_download(category="parody", name=parody, metadata=metadata)
