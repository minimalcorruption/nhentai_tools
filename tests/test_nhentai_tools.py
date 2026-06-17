from nhentai_tools import *
import pytest
import shutil

def test_extract_title():
    assert(extract_title(655922)) == "[Mimonel] W Gal to Shuudengo Hotel Ecchi | 双辣妹与没赶上末班车的酒店色色♥ (Blue Archive) [Chinese] [欶澜汉化组]".replace(" ", "-")

def test_extract_tags():
    assert(extract_tags(655922)) == ['big-breasts', 'sole-male', 'group', 'full-color', 'ffm-threesome', 'collar', 'tail', 'horns', 'gyaru', 'halo']

def test_extract_artists():
    assert(extract_artists(655922)) == ['mimonel']

def test_extract_characters():
    assert(extract_characters(655922)) == ['kirara-yozakura', 'erika-hatami']

def test_extract_parodies():
    assert(extract_parodies(655922)) == ['blue-archive']

def test_extract_groups():
    assert(extract_groups(655922)) == ['No groups']

def test_extract_languages():
    assert(extract_languages(655922)) == ['translated', 'chinese']

def test_extract_categories():
    assert(extract_categories(655922)) == ['doujinshi']

def test_extract_number_of_pages():
    assert(extract_number_of_pages(655922)) == 11

def test_artist_download():
    assert(artist_download(artist="fujitaka kinsei", metadata=True)) == True
    shutil.rmtree("fujitaka-kinsei")