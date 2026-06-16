import requests
from bs4 import BeautifulSoup
import re
import os

from extraction import *
from metadata import *


def download(gallery_id: int, path: str="downloaded", metadata: bool=False):
    """Downloads all images from the requested gallery into specified path and optionally saves metadata.

    Accepts:
    ID of nhentai's gallery, Destination directory path, which defaults to downloaded unless specified and Metadata flag, which default to False unless specified
    """
    # Extracting gallery's data
    title = extract_title(gallery_id)
    server = extract_server(gallery_id)
    gallery_server_id = extract_gallery_server_id(gallery_id)

    if type(server) == int:
        print("Gallery not found or request was blocked by nhentai.")
        return

    path = f"{path}/{title}"
    
    # Checking if directory already exists and exits to avoid bugs  
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print("Error: Directory already exists, please delete it first.")
        print(f"Directory - {path}")
        return

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


def tag_download(tag: str, metadata: bool=False):
    """Scrapes and downloads all galleries under specified tag sorted by today's popularity.

    Accepts:
    Tag as string and Metadata flag
    """
    tag = tag.replace(" ", "-")

    init_page = requests.get(f"https://nhentai.net/tag/{tag}?sort=popular-today", headers=HEADERS)

    #Check if gallery exists
    if init_page.status_code == 404:
        print("Tag not found.")
        return
    
    # Indicate blocked request
    if init_page.status_code == 403:
        print("Request was blocked by nhentai.")
        return

    soup = BeautifulSoup(init_page.text, "html.parser")

    # Finding pagination controls to determine the last page
    tag_regex = r"last svelte-.+"
    tag_href = soup.find("a", {"class": re.compile(tag_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, tag_href).group(0)

    # Iterating through all pages of the specific tag
    for current_page in range(1, int(last_page) + 1):
        tag_page = requests.get(f"https://nhentai.net/tag/{tag}?sort=popular-today&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(tag_page.text, "html.parser")

        # Parsing list of galleries on the current page
        tag_regex = "gallery lang-\\w{2}"
        galleries = soup.find_all("div", {"class": re.compile(tag_regex)})
        
        # Extracting IDs and passing them into the central download worker
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)
            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=tag, metadata=metadata)


def artist_download(artist: str, metadata: bool=False):
    """Scrapes and downloads all galleries associated from a specified artist sorted by date.

    Accepts: 
    Artist's name as string and Metadata flag
    """
    artist = artist.replace(" ", "-")
    
    init_page = requests.get(f"https://nhentai.net/artist/{artist}?sort=date", headers=HEADERS)

    #Check if gallery exists
    if init_page.status_code == 404:
        print("Artist not found.")
        return
    
    # Indicate blocked request
    if init_page.status_code == 403:
        print("Request was blocked by nhentai.")
        return

    soup = BeautifulSoup(init_page.text, "html.parser")

    # Finding pagination controls to determine the last page
    artist_regex = r"last svelte-.+"
    artist_href = soup.find("a", {"class": re.compile(artist_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, artist_href).group(0)

    # Iterating through all pages of the artist's library
    for current_page in range(1, int(last_page) + 1):
        artist_page = requests.get(f"https://nhentai.net/artist/{artist}?sort=date&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(artist_page.text, "html.parser")

        # Parsing list of galleries on the current page
        artist_regex = "gallery lang-\\w{2}"
        galleries = soup.find_all("div", {"class": re.compile(artist_regex)})
        
        # Extracting IDs and downloading
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)
            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=artist, metadata=metadata)


def character_download(character: str, metadata: bool=False):
    """Scrapes and downloads all galleries featuring a specified character sorted by date.

    Accepts:
    Character's name as string and Metadata flag
    """
    character = character.replace(" ", "-")
    
    init_page = requests.get(f"https://nhentai.net/character/{character}?sort=date", headers=HEADERS)

    #Check if gallery exists
    if init_page.status_code == 404:
        print("Character not found.")
        return
    
    # Indicate blocked request
    if init_page.status_code == 403:
        print("Request was blocked by nhentai.")
        return

    soup = BeautifulSoup(init_page.text, "html.parser")

    # Finding pagination controls to determine the last page
    character_regex = r"last svelte-.+"
    character_href = soup.find("a", {"class": re.compile(character_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, character_href).group(0)

    # Iterating through all pages containing the character
    for current_page in range(1, int(last_page) + 1):
        character_page = requests.get(f"https://nhentai.net/character/{character}?sort=date&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(character_page.text, "html.parser")

        # Parsing list of galleries on the current page
        character_regex = "gallery lang-\\w{2}"
        galleries = soup.find_all("div", {"class": re.compile(character_regex)})
        
        # Extracting IDs and downloading
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)
            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=character, metadata=metadata)


def parody_download(parody: str, metadata: bool=False):
    """Scrapes and downloads all galleries under a specific parody sorted by date.

    Accepts:
    Parody as string and Metadata flag
    """
    parody = parody.replace(" ", "-")
    
    init_page = requests.get(f"https://nhentai.net/parody/{parody}?sort=date", headers=HEADERS)

    #Check if gallery exists
    if init_page.status_code == 404:
        print("Parody not found.")
        return
    
    # Indicate blocked request
    if init_page.status_code == 403:
        print("Request was blocked by nhentai.")
        return

    soup = BeautifulSoup(init_page.text, "html.parser")

    # Finding pagination controls to determine the last page
    parody_regex = r"last svelte-.+"
    parody_href = soup.find("a", {"class": re.compile(parody_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, parody_href).group(0)

    # Iterating through all pages containing the parody category
    for current_page in range(1, int(last_page) + 1):
        parody_page = requests.get(f"https://nhentai.net/parody/{parody}?sort=date&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(parody_page.text, "html.parser")

        # Parsing list of galleries on the current page
        parody_regex = "gallery lang-\\w{2}"
        galleries = soup.find_all("div", {"class": re.compile(parody_regex)})
        
        # Extracting IDs and downloading
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)
            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=parody, metadata=metadata)