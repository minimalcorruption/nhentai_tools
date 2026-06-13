import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
import time
import random

# Without headers you get a 403 status code (Forbidden)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

def time_logger(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}() completed in {int(end - start)} seconds.")
        return result
    return wrapper

def extract_server(gallery_id: int) -> str:
    """Extracts the server on which the supplied gallery's images are stored.

    Accepts ID of nhentai's gallery
    """
    first_page = requests.get(f"https://nhentai.net/g/{gallery_id}/1/", headers=HEADERS)

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
    
    Accepts ID of nhentai's gallery
    """
    gallery_url = f"https://nhentai.net/g/{gallery_id}"
    gallery_page = requests.get(gallery_url, headers=HEADERS)

    # Indicate blocked request
    if gallery_page.status_code == 403:
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

    Accepts ID of nhentai's gallery
    """
    gallery_url = f"https://nhentai.net/g/{gallery_id}"
    gallery_page = requests.get(gallery_url, headers=HEADERS)

    # Indicate blocked request
    if gallery_page.status_code == 403:
        return -1

    # It finds the first <img> tag with the "lazyload" class
    soup = BeautifulSoup(gallery_page.text, "html.parser")
    first_image = soup.find("img", {"class": "lazyload"})
    
    return first_image['alt'].replace(" ", "-")

def extract_tags(gallery_id: int) -> list[str]:
    """Extracts the gallery's tags and returns them as a list of strings.

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

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

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the container where the gallery's data is stored
    characters_container_regex = r"tag-container field-name svelte-.+"
    characters_container = soup.find_all("div", {"class": re.compile(characters_container_regex)})

    # Selects the tag where characters are stored
    characters_span_container = characters_container[1]

    # Finds the wrapper tags where characters are stored
    characters_span_regex = r"tags svelte-.+"
    characters_span = characters_span_container.find("span", {"class": re.compile(characters_span_regex)})

    # Finds all tags where characters are stored
    characters_regex = r"name svelte-.+"
    characters = characters_span.find_all("span", {"class": re.compile(characters_regex)})

    characters_extracted = []

    # Extracts characters from tags
    for character in characters:
        characters_extracted.append(character.get_text(strip=True))

    return characters_extracted

def extract_languages(gallery_id: int) -> list[str]:
    """Extracts the languages of the supplied gallery and returns them as a list.

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the container where the gallery's data is stored
    languages_container_regex = r"tag-container field-name svelte-.+"
    languages_container = soup.find_all("div", {"class": re.compile(languages_container_regex)})

    # Finds the wrapper tags where languages are stored
    languages_span_container = languages_container[5]

    # Finds the wrapper tags where languages are stored
    languages_span_regex = r"tags svelte-.+"
    languages_span = languages_span_container.find("span", {"class": re.compile(languages_span_regex)})

    # Finds all tags where languages are stored
    languages_regex = r"name svelte-.+"
    languages = languages_span.find_all("span", {"class": re.compile(languages_regex)})

    languages_extracted = []

    # Extracts languages from tags
    for language in languages:
        languages_extracted.append(language.get_text(strip=True))

    return languages_extracted

def extract_categories(gallery_id: int) -> list[str]:
    """Extracts the categories of the supplied gallery and returns them as a list.

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the container where the gallery's data is stored
    categories_container_regex = r"tag-container field-name svelte-.+"
    categories_container = soup.find_all("div", {"class": re.compile(categories_container_regex)})

    # Finds the wrapper tags where categories are stored
    categories_span_container = categories_container[6]

    # Finds the wrapper tags where categories are stored
    categories_span_regex = r"tags svelte-.+"
    categories_span = categories_span_container.find("span", {"class": re.compile(categories_span_regex)})

    # Finds all tags where categories are stored
    categories_regex = r"name svelte-.+"
    categories = categories_span.find_all("span", {"class": re.compile(categories_regex)})

    categories_extracted = []

    # Extracts categories from tags
    for category in categories:
        categories_extracted.append(category.get_text(strip=True))

    return categories_extracted

def extract_artists(gallery_id: int) -> list[str]:
    """Extracts the artists of the supplied gallery and returns them as a list.

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the container where the gallery's data is stored
    artists_container_regex = r"tag-container field-name svelte-.+"
    artists_container = soup.find_all("div", {"class": re.compile(artists_container_regex)})

    # Finds the wrapper tags where artists are stored
    artists_span_container = artists_container[3]

    # Finds the wrapper tags where artists are stored
    artists_span_regex = r"tags svelte-.+"
    artists_span = artists_span_container.find("span", {"class": re.compile(artists_span_regex)})

    # Finds all tags where artists are stored
    artists_regex = r"name svelte-.+"
    artists = artists_span.find_all("span", {"class": re.compile(artists_regex)})

    artists_extracted = []

    # Extracts artists from tags
    for artist in artists:
        artists_extracted.append(artist.get_text(strip=True))

    return artists_extracted

def extract_number_of_pages(gallery_id: int) -> int:
    """Extracts the total number of pages in the supplied gallery and returns it as an integer.

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the container where the gallery's data is stored
    pages_container_regex = r"tag-container field-name svelte-.+"
    pages_container = soup.find_all("div", {"class": re.compile(pages_container_regex)})

    # Finds the wrapper tags where the page counts are stored
    pages_span_container = pages_container[7]

    # Finds the wrapper tags where the page counts are stored
    pages_span_regex = r"tags svelte-.+"
    pages_span = pages_span_container.find("span", {"class": re.compile(pages_span_regex)})

    # Finds all tags where the page counts are stored
    pages_regex = r"name svelte-.+"
    pages = pages_span.find_all("span", {"class": re.compile(pages_regex)})

    return int(pages[0].get_text(strip=True))

def extract_parodies(gallery_id: int) -> list[str]:
    """Extracts the parodies from the supplied gallery and returns them as a list.

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the container where the gallery's data is stored
    parodies_container_regex = r"tag-container field-name svelte-.+"
    parodies_container = soup.find_all("div", {"class": re.compile(parodies_container_regex)})

    # Finds the wrapper tags where parodies are stored
    parodies_span_container = parodies_container[0]

    # Finds the wrapper tags where parodies are stored
    parodies_span_regex = r"tags svelte-.+"
    parodies_span = parodies_span_container.find("span", {"class": re.compile(parodies_span_regex)})

    # Finds all tags where parodies are stored
    parodies_regex = r"name svelte-.+"
    parodies = parodies_span.find_all("span", {"class": re.compile(parodies_regex)})

    parodies_extracted = []

    # Extracts parodies from tags
    for parody in parodies:
        parodies_extracted.append(parody.get_text(strip=True))

    return parodies_extracted

def extract_groups(gallery_id: int) -> list[str]:
    """Extracts the groups of supplied gallery and returns them as a list.

    Accepts ID of nhentai's gallery
    """
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    # Finds the container where the gallery's data is stored
    groups_container_regex = r"tag-container field-name svelte-.+"
    groups_container = soup.find_all("div", {"class": re.compile(groups_container_regex)})

    # Finds the wrapper tags where groups are stored
    groups_span_container = groups_container[4]

    # Finds the wrapper tags where groups are stored
    groups_span_regex = r"tags svelte-.+"
    groups_span = groups_span_container.find("span", {"class": re.compile(groups_span_regex)})

    # Finds all tags where groups are stored
    groups_regex = r"name svelte-.+"
    groups = groups_span.find_all("span", {"class": re.compile(groups_regex)})

    groups_extracted = []

    # Extracts groups from tags (Fixed loop variable typo conflict)
    for group in groups:
        groups_extracted.append(group.get_text(strip=True))

    return groups_extracted


def download(gallery_id: int, path: str="downloaded", metadata: bool=False):
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
    init_page = requests.get(f"https://nhentai.net/tag/{tag}?sort=popular-today", headers=HEADERS)

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
    init_page = requests.get(f"https://nhentai.net/artist/{artist}?sort=date", headers=HEADERS)

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
    init_page = requests.get(f"https://nhentai.net/character/{character}?sort=date", headers=HEADERS)

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
    init_page = requests.get(f"https://nhentai.net/parody/{parody}?sort=date", headers=HEADERS)

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

# Returns a pseudorandom gallery ID
def random_gallery():
    """Fetches the homepage to find the highest upload ID, then returns a pseudorandom ID within range.
    
    """
    nhentai_homepage = requests.get("https://nhentai.net/", headers=HEADERS)
    soup = BeautifulSoup(nhentai_homepage.text, "html.parser")

    # Isolating homepage main directory item container
    container = soup.find("div", {"class": "container index-container"})

    # Extracting the last uploaded card
    lang_regex = "gallery lang-\\w{2}"
    last_upload = container.find("div", {"class": re.compile(lang_regex)})
    
    # Matching out numeric structure to set maximum threshold
    last_upload_href = last_upload.find("a")['href']
    href_regex = r"\d+"
    last_upload_regex_match = re.search(href_regex, last_upload_href)

    last_upload_id = last_upload_regex_match.group(0)

    return random.randint(1, int(last_upload_id))

def extract_metadata(gallery_id: int) -> dict:
    """Extrcats all metadata from supplied gallery

    Accepts ID of nhentai's gallery
    """
    metadata = {"title": extract_title(gallery_id),
                "gallery id": gallery_id,
                 "parodies": extract_parodies(gallery_id),
                 "characters": extract_characters(gallery_id),
                 "tags": extract_tags(gallery_id),
                 "artists": extract_artists(gallery_id),
                 "groups": extract_groups(gallery_id),
                 "languages": extract_languages(gallery_id),
                 "categories": extract_categories(gallery_id)}
    
    return metadata

def embed_metadata(metadata: dict, path: str):
    """Writes compiled gallery metadata into a metadata.txt within downloads directory.

    Accepts metadata as dict from extract_metadata() and path as string
    """
    with open(f"{path}/metadata.txt", "w") as metadata_file:
        metadata_file.write(f"Title: {metadata['title']}\n")
        metadata_file.write(f"Gallery ID: {metadata['gallery id']}")
        metadata_file.write(f"Parodies: {metadata['parodies']}\n")
        metadata_file.write(f"Characters: {metadata['characters']}\n")
        metadata_file.write(f"Tags: {metadata['tags']}\n")
        metadata_file.write(f"Artists: {metadata['artists']}\n")
        metadata_file.write(f"Groups: {metadata['groups']}\n")
        metadata_file.write(f"Languages: {metadata['languages']}\n")
        metadata_file.write(f"Categories: {metadata['categories']}\n")