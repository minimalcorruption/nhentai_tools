import requests

from nhentai_tools.utils import HEADERS
from nhentai_tools.extraction import *

from nhentai_tools.exceptions import *

def extract_metadata(gallery_id: int) -> dict:
    """Extrcats all metadata from supplied gallery

    Accepts ID of nhentai's gallery
    """

    #Check if gallery exists and request status
    response = requests.get(f"https://nhentai.net/g/{gallery_id}/", headers=HEADERS)

    if response.status_code == 404:
        raise GalleryNotFoundError("Gallery not found.")
    
    if response.status_code == 403:
        raise RequestBlockedError("Request was blocked by nhentai.")

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
        metadata_file.write(f"Gallery ID: {metadata['gallery id']}\n")
        metadata_file.write(f"Parodies: {metadata['parodies']}\n")
        metadata_file.write(f"Characters: {metadata['characters']}\n")
        metadata_file.write(f"Tags: {metadata['tags']}\n")
        metadata_file.write(f"Artists: {metadata['artists']}\n")
        metadata_file.write(f"Groups: {metadata['groups']}\n")
        metadata_file.write(f"Languages: {metadata['languages']}\n")
        metadata_file.write(f"Categories: {metadata['categories']}\n")