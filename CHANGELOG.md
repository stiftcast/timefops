# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## 0.3

### Added
* `-z/--zipfile` added with compression support for creating zip files.
* `--zip-encryption/-ze` added for optional AES encryption of zip files.
* `--zip-password/-zp` and `--zip-password-plaintext/-zP` for setting password of AES encrypted zip files.
* `--to-stdout` argument added for compressed tarballs and zip files.
* `-v/--verbose` and `-d/--debug` arguments added for more helpful output.
* `--no-color/--no-colour` argument added for disabling coloured log output.
### Changed
* [colorama](https://pypi.org/project/colorama/) and [pyzipper](https://pypi.org/project/pyzipper/) have both been made dependencies.
* `-f/--format` argument now accepts multiple values, making it possible to place contents under nested folders.
### Fixed
* Now double-checks when archiving that the file does not exist already.
## 0.2

### Added
* Added new CLI, unifying all functionality into one binary.
