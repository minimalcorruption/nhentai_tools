<div align="center">
  <img src="https://raw.githubusercontent.com/minimalcorruption/nhentai_tools/main/repo/ntools_logo.svg" width="200"/>
  <p>Unofficial Python library for interacting with nhentai.net without API key.</p>

  <!-- Badges -->

[![PyPI version](https://img.shields.io/pypi/v/nhentai_tools)](https://pypi.org/project/nhentai_tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

</div>

## Installation

```bash
pip install nhentai_tools
```

**nhentai tools requires python >= 3.9**

## Basic Usage

### Download gallery by ID

```python
from nhentai_tools import download

# Download gallery in gallery folder and embed metadata
download(1337, path="gallery", metadata=True)
# Downloaded files can be found in gallery/
```

### Mass download by tag, character, artist or parody

```python
from nhentai_tools import artist_download, character_download, tag_download, parody_download

# Download all galleries from artist and embed metadata
artist_download("coolsigma", True)
# Downloaded files can be found in coolsigma/

# Download all galleries with specified character and embed metadata
character_download("JetStream-Sam", True)
# Downloaded files can be found in JetStream-Sam/
```

The library has more mass download functions, please refer to [Downloading](https://github.com/minimalcorruption/nhentai_tools/wiki/Documentation#downloading)

### Working with metadata

```python
from nhentai_tools import extract_metadata, embed_metadata

# Extract metadata, return it as dict and save to "meta" variable
meta = extract_metadata(1337)

# Write metadata in metadata.txt file
embed_metadata(meta, path="metadata")
# File can be found in metadata/metadata.txt
```

## Documentation

Full documentation can be found on [wiki](https://github.com/minimalcorruption/nhentai_tools/wiki/Documentation)

## Building

```bash
# Required for building
pip install build

git clone https://github.com/minimalcorruption/nhentai_tools
cd nhentai_tools
python -m build

# Installing from local build
pip install .
```

## Important

**_This project is in beta, bugs are expected_<br>**
**_If something goes wrong, please open an issue_**
