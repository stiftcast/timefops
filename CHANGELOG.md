# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## 0.3

### Added
* `-z/--zipfile` added with compression support for creating zip files.
* `--to-stdout` argument added for compressed tarballs and zip files.
* `-v/--verbose` and `-d/--debug` arguments added for more helpful output.
### Changed
* Verbose and debug information go to stdout, whereas warnings and errors now go to stderr.
### Fixed
* Now double-checks when archiving that the file does not exist already.
## 0.2

### Added
* Added new CLI, unifying all functionality into one binary.
