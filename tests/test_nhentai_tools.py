from nhentai_tools import *
import pytest

def test_extract_title():
    assert(extract_title(655922)) == "[Mimonel]-W-Gal-to-Shuudengo-Hotel-Ecchi-|-åè¾£å¦¹ä¸æ²¡èµ¶ä¸æ«ç­è½¦çéåºè²è²â¥-(Blue-Archive)-[Chinese]-[æ¬¶æ¾æ±åç»]"

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