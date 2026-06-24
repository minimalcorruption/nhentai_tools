import requests
from bs4 import BeautifulSoup
import re

from nhentai_tools.utils import HEADERS

from exceptions import *

def _extract(gallery_id: int, value: str) -> list[str]:
    """Shared worker for metadata extraction

    Accepts gallery's ID as int and value that need to be extracted\n
    Returns data as list of strings
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)
    
    #Check if gallery exists
    if gallery.status_code == 404:
        raise GalleryNotFoundError('Gallery not found.')
    
    # Indicate blocked request
    if gallery.status_code == 403:
        raise RequestBlockedError("Request was blocked by nehntai.")
    
    value_plural = ""

    if value.endswith('y'):
        value_plural = value[:-1] + "ies"
    else:
        value_plural = value + 's'

    soup = BeautifulSoup(gallery.text, "html.parser")

    page_text = soup.find(string=re.compile(rf"{value_plural.capitalize()}:")) # Languages
    
    #Finds tag that languages
    tag_regex = r"tag-container"
    
    # Checks if languages are present
    try:
        page_container = page_text.find_parent("div", {"class": re.compile(tag_regex)})
    except AttributeError:
        return [f"No {value_plural}"]

    regex = r"tagchip variant-pill state-normal svelte-.+"

    page_content = page_container.find_all("a", {"class": re.compile(regex)})

    extracted = []

    # Iterates through languages and appends languages_extracted
    for content in page_content:
        page_href = content['href']
        
        content_regex = rf"/{value}/(.+)/"
        content_match = re.search(content_regex, page_href)

        extracted.append(content_match.group(1)) 

    return extracted


def extract_server(gallery_id: int) -> str:
    """Extracts the server on which the supplied gallery's images are stored.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    first_page = requests.get(f"https://nhentai.net/g/{gallery_id}/1/", headers=HEADERS)

    #Check if gallery exists
    if first_page.status_code == 404:
        print("Gallery not found.")
        return -1
    
    #Check if request was blocked
    if first_page.status_code == 403:
        print("Request was blocked by nhentai.")
        return -1

    soup = BeautifulSoup(first_page.text, "html.parser")

    # Finds the HTML tag which stores the server address of the first image
    section = soup.find("section", {"id": "image-container"})
    section_a = section.find("a")
    first_image = section_a.find("img")

    # Finds the server in the src attribute
    image_src = first_image['src']
    src_regex = r"https://i\d+\.nhentai\.net/"
    src_regex_match = re.search(src_regex, image_src)

    return src_regex_match.group(0)

def extract_gallery_server_id(gallery_id: int) -> int:
    """Extracts the server side ID of the supplied gallery and returns it.
    nhentai's galleries have 2 IDs - the one officially referenced on the page (https://nhentai.net/g/99999 - ID) and the server side ID under which images are stored.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery_url = f"https://nhentai.net/g/{gallery_id}"
    gallery_page = requests.get(gallery_url, headers=HEADERS)

    #Check if gallery exists
    if gallery_page.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery_page.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    # It finds the first <img> tag with the "lazyload" class which contains info about the gallery
    soup = BeautifulSoup(gallery_page.text, "html.parser")
    first_image = soup.find("img", {"class": "lazyload"})
    
    # Extracting the server side ID from the "src" attribute using regex, checking it for an invalid ID and returning it
    gallery_server_id_regex = re.compile(r"\d{2,}")
    try:
        gallery_server_id_match = gallery_server_id_regex.search(first_image['src'])
    except TypeError:
        return None
    
    return int(gallery_server_id_match.group(0))

def extract_title(gallery_id: int) -> str:
    gallery_url = f"https://nhentai.net/g/{gallery_id}"
    gallery_page = requests.get(gallery_url, headers=HEADERS)
    gallery_page.encoding = 'utf-8'

    if gallery_page.status_code == 404:
        return -1
    if gallery_page.status_code == 403:
        return -1

    soup = BeautifulSoup(gallery_page.text, "html.parser")

    # Find tag that contains title
    cover = soup.find("div", {"id": "cover"})
    first_image = cover.find("img")

    if first_image is None:
        return -1

    return first_image['alt'].replace(" ", "-")

def extract_number_of_pages(gallery_id: int) -> int:
    """Extracts the total number of pages in the supplied gallery and returns it as an integer.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    # Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")

    pages_text = soup.find(string=re.compile(r"Pages:"))
    
    #Finds tag that contains number of pages
    tag_regex = r"tag-container"
    pages_container = pages_text.find_parent("div", {"class": re.compile(tag_regex)})
    
    span_regex = r"^name"
    pages_span = pages_container.find("span", {"class": re.compile(span_regex)})

    return int(pages_span.get_text(strip=True))

def extract_tags(gallery_id: int) -> list[str]:
    """Extracts the gallery's tags and returns them as a list of strings.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    return _extract(gallery_id, value="tag")

def extract_characters(gallery_id: int) -> list[str]:
    """Extracts the characters featured in the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    return _extract(gallery_id, value="character")

def extract_languages(gallery_id: int) -> list[str]:
    """Extracts the languages of the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    return _extract(gallery_id, value="language")


def extract_categories(gallery_id: int) -> list[str]:
    """Extracts the categories of the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    return _extract(gallery_id, value="category")

def extract_artists(gallery_id: int) -> list[str]:
    """Extracts the artists of the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    return _extract(gallery_id, value="artist")
    
def extract_parodies(gallery_id: int) -> list[str]:
    """Extracts the parodies from the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    return _extract(gallery_id, value="parody")

def extract_groups(gallery_id: int) -> list[str]:
    """Extracts the groups of supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    return _extract(gallery_id, value="group")