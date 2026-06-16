import requests
from bs4 import BeautifulSoup
import re

from utils import HEADERS


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
    """Extracts the title of the supplied gallery and returns it, returns -1 if the request was blocked.
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

    # It finds the first <img> tag with the "lazyload" class
    soup = BeautifulSoup(gallery_page.text, "html.parser")
    first_image = soup.find("img", {"class": "lazyload"})
    
    return first_image['alt'].replace(" ", "-")

def extract_tags(gallery_id: int) -> list[str]:
    """Extracts the gallery's tags and returns them as a list of strings.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    #Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the wrapper where tags are stored
    tag_class_regex = r"tagchip variant-pill state-normal svelte-.+"
    tags = soup.find_all("a", {"class": re.compile(tag_class_regex)})

    # Extracts tags
    clean_tag_regex = r"/tag/([^/]+)/"
    clean_tags = []

    for tag in tags:
        match = re.search(clean_tag_regex, tag['href'])
        if match:
            clean_tags.append(match.group(1))

    return clean_tags

def extract_characters(gallery_id: int) -> list[str]:
    """Extracts the characters featured in the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    #Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")

    characters_text = soup.find(string=re.compile(r"Characters:"))
    
    #Finds tag that characters
    tag_regex = r"tag-container"
    
    # Checks if characters are present
    try:
        characters_container = characters_text.find_parent("div", {"class": re.compile(tag_regex)})
    except AttributeError:
        return ["No characters"]

    regex = r"tagchip variant-pill state-normal svelte-.+"

    characters = characters_container.find_all("a", {"class": re.compile(regex)})

    characters_extracted = []

    # Iterates through characters and appends characters_extracted
    for parody in characters:
        page_href = parody['href']
        
        parody_regex = r"/character/(.+)/"
        parody_match = re.search(parody_regex, page_href)

        characters_extracted.append(parody_match.group(1)) 

    return characters_extracted

def extract_languages(gallery_id: int) -> list[str]:
    """Extracts the languages of the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    #Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")

    languages_text = soup.find(string=re.compile(r"Languages:"))
    
    #Finds tag that languages
    tag_regex = r"tag-container"
    
    # Checks if languages are present
    try:
        languages_container = languages_text.find_parent("div", {"class": re.compile(tag_regex)})
    except AttributeError:
        return ["No languages"]

    regex = r"tagchip variant-pill state-normal svelte-.+"

    languages = languages_container.find_all("a", {"class": re.compile(regex)})

    languages_extracted = []

    # Iterates through languages and appends languages_extracted
    for parody in languages:
        page_href = parody['href']
        
        parody_regex = r"/language/(.+)/"
        parody_match = re.search(parody_regex, page_href)

        languages_extracted.append(parody_match.group(1)) 

    return languages_extracted

def extract_categories(gallery_id: int) -> list[str]:
    """Extracts the categories of the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)
    
    #Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")

    categories_text = soup.find(string=re.compile(r"Categories:"))
    
    #Finds tag that categories
    tag_regex = r"tag-container"
    
    # Checks if categories are present
    try:
        categories_container = categories_text.find_parent("div", {"class": re.compile(tag_regex)})
    except AttributeError:
        return ["No categories"]

    regex = r"tagchip variant-pill state-normal svelte-.+"

    categories = categories_container.find_all("a", {"class": re.compile(regex)})

    categories_extracted = []

    # Iterates through categories and appends categories_extracted
    for parody in categories:
        page_href = parody['href']
        
        parody_regex = r"/category/(.+)/"
        parody_match = re.search(parody_regex, page_href)

        categories_extracted.append(parody_match.group(1)) 

     
    return categories_extracted

def extract_artists(gallery_id: int) -> list[str]:
    """Extracts the artists of the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    #Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")
   
    artists_text = soup.find(string=re.compile(r"Artists:"))
    
    #Finds tag that artists
    tag_regex = r"tag-container"
    
    # Checks if artists are present
    try:
        artists_container = artists_text.find_parent("div", {"class": re.compile(tag_regex)})
    except AttributeError:
        return ["No artists"]

    regex = r"tagchip variant-pill state-normal svelte-.+"

    artists = artists_container.find_all("a", {"class": re.compile(regex)})

    artists_extracted = []

    # Iterates through artists and appends artists_extracted
    for parody in artists:
        page_href = parody['href']
        
        parody_regex = r"/artist/(.+)/"
        parody_match = re.search(parody_regex, page_href)

        artists_extracted.append(parody_match.group(1)) 

     
    return artists_extracted

def extract_number_of_pages(gallery_id: int) -> int:
    """Extracts the total number of pages in the supplied gallery and returns it as an integer.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    #Check if gallery exists
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


def extract_parodies(gallery_id: int) -> list[str]:
    """Extracts the parodies from the supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    #Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")

    parodies_text = soup.find(string=re.compile(r"Parodies:"))
    
    #Finds tag that parodies
    tag_regex = r"tag-container"
    
    # Checks if parodies are present
    try:
        parodies_container = parodies_text.find_parent("div", {"class": re.compile(tag_regex)})
    except AttributeError:
        return ["No Parodies"]

    regex = r"tagchip variant-pill state-normal svelte-.+"

    parodies = parodies_container.find_all("a", {"class": re.compile(regex)})

    parodies_extracted = []

    # Iterates through parodies and appends parodies_extracted
    for parody in parodies:
        page_href = parody['href']
        
        parody_regex = r"/parody/(.+)/"
        parody_match = re.search(parody_regex, page_href)

        parodies_extracted.append(parody_match.group(1)) 

     
    return parodies_extracted

def extract_groups(gallery_id: int) -> list[str]:
    """Extracts the groups of supplied gallery and returns them as a list.
    In case of errors returns int(-1)

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    #Check if gallery exists
    if gallery.status_code == 404:
        print("Gallery not found.")
        return -1
    
    # Indicate blocked request
    if gallery.status_code == 403:
        print("Request was blocked by nehntai.")
        return -1

    soup = BeautifulSoup(gallery.text, "html.parser")

    groups_text = soup.find(string=re.compile(r"Groups:"))
    
    #Finds tag that groups
    tag_regex = r"tag-container"
    
    # Checks if groups are present
    try:
        groups_container = groups_text.find_parent("div", {"class": re.compile(tag_regex)})
    except AttributeError:
        return ["No groups"]

    regex = r"tagchip variant-pill state-normal svelte-.+"

    groups = groups_container.find_all("a", {"class": re.compile(regex)})

    groups_extracted = []

    # Iterates through groups and appends groups_extracted
    for parody in groups:
        page_href = parody['href']
        
        parody_regex = r"/group/(.+)/"
        parody_match = re.search(parody_regex, page_href)

        groups_extracted.append(parody_match.group(1)) 

     
    return groups_extracted
