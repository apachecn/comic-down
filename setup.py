#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import setuptools
import ComicDown

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requires = fh.read().splitlines()

setuptools.setup(
    name="ComicDown",
    version=ComicDown.__version__,
    url="https://github.com/apachecn/comic-down",
    author=ComicDown.__author__,
    author_email=ComicDown.__email__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: Other/Proprietary License",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Utilities",
    ],
    description="ComicDown，漫画批量下载工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "ebook",
        "comic",
        "epub",
        "crawler",
        "爬虫",
        "电子书",
        "漫画",
    ],
    install_requires=install_requires,
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            "dl-comic=ComicDown.__main__:main",
        ],
    },
    packages=setuptools.find_packages(),
)
