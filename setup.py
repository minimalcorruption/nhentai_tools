from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="nhentai_tools",
    version="1.0.0",
    description="A python library that allows you to interact with nhentai.net without API key",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="placeholder",
    author="minimalcorruption",
    author_email="placeholder",
    licence="MIT",
    classifiers=[

    ],
    install_requires=["requests >= 2.34.2", "beautifulsoup4 >= 4.15.0"],
    extras_require={
        "dev": ["twine >= 6.2.0"]
    }
)