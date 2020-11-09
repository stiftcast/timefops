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
    version="0.3",
    license="GPLv3",
    description="A cross-platform module for file operations based on time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    test_suite="tests.my_test_suite",
    packages=["timefops"],
    install_requires=["colorama", "pyzipper"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: System :: Archiving :: Compression",
        "Topic :: System :: Filesystems",
    ],
    entry_points={
        "console_scripts": [
            "timefops = timefops._cli:main",
        ],
    },
)
