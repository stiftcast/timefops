#!/usr/bin/env python3

from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="timefops",
    url="https://github.com/stiftcast/timefops",
    author="stiftcast",
    author_email="stiftcast@gmail.com",
    version="0.1",
    license="GPLv3",
    description="A cross-platform module for file operations based on time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    test_suite="tests.my_test_suite",
    packages=["timefops"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: System :: Filesystems",
    ],
    entry_points={
        'console_scripts': [
            "atarchive = timefops.cli:atarchive",
            "atcopy = timefops.cli:atcopy",
            "atmove = timefops.cli:atmove",
            "ctarchive = timefops.cli:ctarchive",
            "ctcopy = timefops.cli:ctcopy",
            "ctmove = timefops.cli:ctmove",
            "mtarchive = timefops.cli:mtarchive",
            "mtcopy = timefops.cli:mtcopy",
            "mtmove = timefops.cli:mtmove",
        ],
    }
)
