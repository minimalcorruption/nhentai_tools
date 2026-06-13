import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
import time
import random

#Without headers you get 403 status code (Forbidden)
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

clear = lambda: print("\033[H\033[2J", end="")

#Finds server which contains requested gallery
def extract_server(gallery_id: int) -> str:
    first_page = requests.get(f"https://nhentai.net/g/{gallery_id}/1/", headers=HEADERS)

    soup = BeautifulSoup(first_page.text, "html.parser")

    section = soup.find("section", {"id": "image-container"})
    section_a = section.find("a")
    first_image = section_a.find("img")

    image_src = first_image['src']
    src_regex = r"https://i\d+\.nhentai\.net/"
    src_regex_match = re.search(src_regex, image_src)

    return src_regex_match.group(0)

#nhentai has 2 IDs - the one that officially referenced on page (https://nhentai.net/g/(99999) - id) and server side id under which images are stored.
#This function extracts server side id and returns it
def extract_gallery_server_id(gallery_id: int) -> int:
    gallery_url = f"https://nhentai.net/g/{gallery_id}"
    gallery_page = requests.get(gallery_url, headers=HEADERS)

    #Indicate blocked request
    if gallery_page.status_code == 403:
        return -1

    #It finds first <img> tag with "lazyload" class which contains info about gallery
    soup = BeautifulSoup(gallery_page.text, "html.parser")
    first_image = soup.find("img", {"class": "lazyload"})
    
    #Extracting server side id from "src" attribute using regex, checking it for invalid ID and returning it
    gallery_server_id_regex = re.compile(r"\d{2,}")
    try:
        gallery_server_id_match = gallery_server_id_regex.search(first_image['src'])
    except TypeError:
        return None
    
    return int(gallery_server_id_match.group(0))

#This function extracts gallery's title
def extract_title(gallery_id: int) -> str:
    gallery_url = f"https://nhentai.net/g/{gallery_id}"
    gallery_page = requests.get(gallery_url, headers=HEADERS)

    #Indicate blocked request
    if gallery_page.status_code == 403:
        return -1

    #It finds first <img> tag with "lazyload" class
    soup = BeautifulSoup(gallery_page.text, "html.parser")
    first_image = soup.find("img", {"class": "lazyload"})
    
    return first_image['alt'].replace(" ", "-")

def extract_tags(gallery_id: int) -> list[str]:
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    tag_class_regex = r"tagchip variant-pill state-normal svelte-.+"
    tags = soup.find_all("a", {"class": re.compile(tag_class_regex)})

    clean_tag_regex = r"/tag/([^/]+)/"
    clean_tags = []

    for tag in tags:
        match = re.search(clean_tag_regex, tag['href'])
        if match:
            clean_tags.append(match.group(1))

    return clean_tags

def extract_characters(gallery_id: int) -> list[str]:
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    characters_container_regex = r"tag-container field-name svelte-.+"
    characters_container = soup.find_all("div", {"class": re.compile(characters_container_regex)})

    characters_span_container = characters_container[1]

    characters_span_regex = r"tags svelte-.+"
    characters_span = characters_span_container.find("span", {"class": re.compile(characters_span_regex)})

    characters_regex = r"name svelte-.+"
    characters = characters_span.find_all("span", {"class": re.compile(characters_regex)})

    characters_extracted = []

    for character in characters:
        characters_extracted.append(character.get_text(strip=True))

    return characters_extracted

def extract_languages(gallery_id: int) -> list[str]:
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    languages_container_regex = r"tag-container field-name svelte-.+"
    languages_container = soup.find_all("div", {"class": re.compile(languages_container_regex)})

    languages_span_container = languages_container[5]

    languages_span_regex = r"tags svelte-.+"
    languages_span = languages_span_container.find("span", {"class": re.compile(languages_span_regex)})

    languages_regex = r"name svelte-.+"
    languages = languages_span.find_all("span", {"class": re.compile(languages_regex)})

    languages_extracted = []

    for language in languages:
        languages_extracted.append(language.get_text(strip=True))

    return languages_extracted

def extract_category(gallery_id: int) -> list[str]:
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    categories_container_regex = r"tag-container field-name svelte-.+"
    categories_container = soup.find_all("div", {"class": re.compile(categories_container_regex)})

    categories_span_container = categories_container[6]

    categories_span_regex = r"tags svelte-.+"
    categories_span = categories_span_container.find("span", {"class": re.compile(categories_span_regex)})

    categories_regex = r"name svelte-.+"
    categories = categories_span.find_all("span", {"class": re.compile(categories_regex)})

    categories_extracted = []

    for category in categories:
        categories_extracted.append(category.get_text(strip=True))

    return categories_extracted

def extract_artists(gallery_id: int) -> list[str]:
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    artists_container_regex = r"tag-container field-name svelte-.+"
    artists_container = soup.find_all("div", {"class": re.compile(artists_container_regex)})

    artists_span_container = artists_container[3]

    artists_span_regex = r"tags svelte-.+"
    artists_span = artists_span_container.find("span", {"class": re.compile(artists_span_regex)})

    artists_regex = r"name svelte-.+"
    artists = artists_span.find_all("span", {"class": re.compile(artists_regex)})

    artists_extracted = []

    for artist in artists:
        artists_extracted.append(artist.get_text(strip=True))

    return artists_extracted

def extract_number_of_pages(gallery_id: int) -> int:
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    pages_container_regex = r"tag-container field-name svelte-.+"
    pages_container = soup.find_all("div", {"class": re.compile(pages_container_regex)})

    pages_span_container = pages_container[7]

    pages_span_regex = r"tags svelte-.+"
    pages_span = pages_span_container.find("span", {"class": re.compile(pages_span_regex)})

    pages_regex = r"name svelte-.+"
    pages = pages_span.find_all("span", {"class": re.compile(pages_regex)})

    return pages[0].get_text(strip=True)

def extract_parodies(gallery_id: int) -> list[str]:
    gallery = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    soup = BeautifulSoup(gallery.text, "html.parser")

    parodies_container_regex = r"tag-container field-name svelte-.+"
    parodies_container = soup.find_all("div", {"class": re.compile(parodies_container_regex)})

    parodies_span_container = parodies_container[0]

    parodies_span_regex = r"tags svelte-.+"
    parodies_span = parodies_span_container.find("span", {"class": re.compile(parodies_span_regex)})

    parodies_regex = r"name svelte-.+"
    parodies = parodies_span.find_all("span", {"class": re.compile(parodies_regex)})

    parodies_extracted = []

    for parody in parodies:
        parodies_extracted.append(parody.get_text(strip=True))

    return parodies_extracted

@time_logger
def download(gallery_id: int, path: str="downloaded"):
    #Extracting gallery's data
    title = extract_title(gallery_id)
    server = extract_server(gallery_id)
    gallery_server_id = extract_gallery_server_id(gallery_id)

    path = f"{path}/{title}"
    
    #Checking if directory already exists and overrides it to avoid bugs  
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print("Error: Directory already exists, please delete it first.")
        print(f"Directory - {path}")
        return

    connectivity_check = 0
    page_counter = 1

    gallery_server_id = str(gallery_server_id)

    start = time.time()
    end = 0

    request = requests.Session()
    
    #Downloading images from server
    while connectivity_check == 0:
        current_image = f"{server}/galleries/{gallery_server_id}/{page_counter}.webp"
        current_image_jpg = f"{server}/galleries/{gallery_server_id}/{page_counter}.jpg"
        current_image_path = f"{path}/{page_counter}.webp"
        current_image_path_jpg = f"{path}/{page_counter}.jpg"
        current_request = request.get(current_image)
        current_request_jpg = request.get(current_image_jpg)
        
        #nhentai can have some parts of gallery in webp and some in jpg
        if current_request.status_code == 200:
            with open(current_image_path, 'wb') as image:
                image.write(current_request.content)
            page_counter += 1
        elif current_request_jpg.status_code == 200:
            with open(current_image_path_jpg, 'wb') as image:
                image.write(current_request_jpg.content)
            page_counter += 1
        #If status code for this page is different from 200 - there is no more pages
        else:
            end = time.time()
            connectivity_check = -1

    request.close()

@time_logger
def tag_download(tag: str):
    init_page = requests.get(f"https://nhentai.net/tag/{tag}?sort=popular-today", headers=HEADERS)

    soup = BeautifulSoup(init_page.text, "html.parser")

    tag_regex = r"last svelte-.+"

    tag_href = soup.find("a", {"class": re.compile(tag_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, tag_href).group(0)

    current_page = 1

    for current_page in range(1, int(last_page) + 1):
        tag_page = requests.get(f"https://nhentai.net/tag/{tag}?sort=popular-today&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(tag_page.text, "html.parser")

        tag_regex = "gallery lang-\\w{2}"

        galleries = soup.find_all("div", {"class": re.compile(tag_regex)})
        
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)

            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=tag)

@time_logger
def artist_download(artist: str):
    init_page = requests.get(f"https://nhentai.net/artist/{artist}?sort=date", headers=HEADERS)

    soup = BeautifulSoup(init_page.text, "html.parser")

    artist_regex = r"last svelte-.+"

    artist_href = soup.find("a", {"class": re.compile(artist_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, artist_href).group(0)

    current_page = 1


    for current_page in range(1, int(last_page) + 1):
        artist_page = requests.get(f"https://nhentai.net/artist/{artist}?sort=date&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(artist_page.text, "html.parser")

        artist_regex = "gallery lang-\\w{2}"

        galleries = soup.find_all("div", {"class": re.compile(artist_regex)})
        
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)

            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=artist)

@time_logger
def character_download(character: str):
    init_page = requests.get(f"https://nhentai.net/character/{character}?sort=date", headers=HEADERS)

    soup = BeautifulSoup(init_page.text, "html.parser")

    character_regex = r"last svelte-.+"

    character_href = soup.find("a", {"class": re.compile(character_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, character_href).group(0)

    current_page = 1


    for current_page in range(1, int(last_page) + 1):
        character_page = requests.get(f"https://nhentai.net/character/{character}?sort=date&page={current_page}", headers=HEADERS)

        soup = BeautifulSoup(character_page.text, "html.parser")

        character_regex = "gallery lang-\\w{2}"

        galleries = soup.find_all("div", {"class": re.compile(character_regex)})
        
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)

            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=character)

@time_logger
def parody_download(parody: str):
    init_page = requests.get(f"https://nhentai.net/parody/{parody}?sort=date", headers=request_headers)

    soup = BeautifulSoup(init_page.text, "html.parser")

    parody_regex = r"last svelte-.+"

    parody_href = soup.find("a", {"class": re.compile(parody_regex)})['href']

    last_page_regex = rf"\d+"
    last_page = re.search(last_page_regex, parody_href).group(0)

    current_page = 1


    for current_page in range(1, int(last_page) + 1):
        parody_page = requests.get(f"https://nhentai.net/parody/{parody}?sort=date&page={current_page}", headers=request_headers)

        soup = BeautifulSoup(parody_page.text, "html.parser")

        parody_regex = "gallery lang-\\w{2}"

        galleries = soup.find_all("div", {"class": re.compile(parody_regex)})
        
        for gallery in galleries:
            current_href = gallery.find("a")['href']
            href_regex = r"\d+"

            href_regex_match = re.search(href_regex, current_href)

            gallery_id = href_regex_match.group(0)

            download(int(gallery_id), path=parody)

#Returns a pseudorandom gallery ID
def random_gallery():
    nhentai_homepage = requests.get("https://nhentai.net/", headers=HEADERS)
    soup = BeautifulSoup(nhentai_homepage.text, "html.parser")

    container = soup.find("div", {"class": "container index-container"})

    lang_regex = "gallery lang-\\w{2}"
    last_upload = container.find("div", {"class": re.compile(lang_regex)})
    
    last_upload_href = last_upload.find("a")['href']
    href_regex = r"\d+"
    last_upload_regex_match = re.search(href_regex, last_upload_href)

    last_upload_id = last_upload_regex_match.group(0)

    return random.randint(1, int(last_upload_id))