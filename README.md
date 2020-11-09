# timefops
[![PyPI version fury.io](https://badge.fury.io/py/timefops.svg)](https://pypi.python.org/pypi/timefops/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/timefops.svg)](https://pypi.python.org/pypi/timefops)
[![PyPI license](https://img.shields.io/pypi/l/timefops.svg)](https://pypi.python.org/pypi/timefops/)

Performs file operations (moving, copying and archiving) on files/directories based on their access/change/modified times.

## Description
_timefops_ provides moving, copying and archiving capabilities for files/directories based on their access time, change time or modified time.

The interface contains nested sub-parsers where you'll be required to choose the time predicate and operation. Both the copying and moving functionality utilize Python's `shutil` module, whereas the`tarfile` and `zipfile` modules are both used for creating archives.

Platforms: Linux, Windows; compatibilty with Mac OS is unknown.

Python 3.7+ is required. 

## Installation
Using pipx (recommended):
```sh
pipx install timefops
```
Using pip:
```sh
pip3 install --user timefops
```
## Usage
Choosing the time predicate:

```
stiftcast@debian:~$ timefops -h
usage: timefops [-h] [-V] <time> ...

Operate on files/directories based on their access/change/modified times.

optional arguments:
  -h, --help     show this help message and exit
  -V, --version  print version number/info and exit

Time predicate:
  <time>
    atime        Perform operations based on last access-time.
    ctime        Perform operations based on last change-time.
    mtime        Perform operations based on last modification-time.
```
Choosing the operation:
```
stiftcast@debian:~$ timefops mtime -h
usage: timefops mtime [-h] [-V] <operation> ...

Perform operations based on last modification-time.

optional arguments:
  -h, --help     show this help message and exit
  -V, --version  print version number/info and exit

Operations:
  <operation>
    archive      Archive contents to a tarball or a zip file.
    copy         Copy contents to a different location.
    move         Move contents to a different location.
```

<br /> Options for `archive`:
```
optional arguments:
  -h, --help            show this help message and exit
  -V, --version         print version number/info and exit

General arguments:
  src                   Source directories/files.
  -a NAME, --archive NAME
                        Name for target archive.
  --to-stdout           Write tar archive or zip file to stdout instead of a
                        named file, emulates the '-' option of the tar and zip
                        executables.
  -z, --zipfile         Makes a zip file instead of a tar archive (GZ
                        compression is not available with this option)
  -c {bz2,gz,xz}, --compression {bz2,gz,xz}
                        Compression format for the archive.
  -f FORMAT [FORMAT ...], --format FORMAT [FORMAT ...]
                        Set folder name format (using Python's datetime
                        formatting directives). If there are multiple values
                        specifed, contents will get nested under the last
                        value.
  -i, --individual-items
                        Setting this flag will allow for specifying individual
                        source files and folders. The difference between
                        specifiying a source folder with this flag on is that
                        any folder(s) specified will not be traversed and
                        instead be treated as a standalone item.
  -v, --verbose         Set log level to verbose.
  -d, --debug           Set log level to debug (includes verbose).
  --no-color, --no-colour
                        Disable coloured logging output.
  --dry-run             Show results, but don't execute.

AES-Encrypted Zipfile options:
  Arguments for making a password-protected AES-Encrypted zip file. The
  -z/--zipfile flag is required for any of these to register, otherwise they
  will be ignored. Encrypting a zip file will not hide the directory
  structure, or encrypt any directories, but will encrypt individual files.

  --zip-password, -zp   Prompts for a password to encrypt zip folder contents
                        with.
  --zip-password-plaintext PASSWORD, -zP PASSWORD
                        Specify zip file password in plaintext, avoid this
                        option if possible.
  --zip-encryption {weak,medium,strong}, -ze {weak,medium,strong}
                        Set the strength of the AES encryption, if nothing is
                        specified, 'medium' is used by default.
```

Options for `copy` or `move`:
```
optional arguments:
  -h, --help            show this help message and exit
  -V, --version         print version number/info and exit

General arguments:
  src                   Source directories/files.
  -t TARGET_DIRECTORY, --target-directory TARGET_DIRECTORY
                        Destination directory.
  -f FORMAT [FORMAT ...], --format FORMAT [FORMAT ...]
                        Set folder name format (using Python's datetime
                        formatting directives). If there are multiple values
                        specifed, contents will get nested under the last
                        value.
  -i, --individual-items
                        Setting this flag will allow for specifying individual
                        source files and folders. The difference between
                        specifiying a source folder with this flag on is that
                        any folder(s) specified will not be traversed and
                        instead be treated as a standalone item.
  -v, --verbose         Set log level to verbose.
  -d, --debug           Set log level to debug (includes verbose).
  --no-color, --no-colour
                        Disable coloured logging output.
  --dry-run             Show results, but don't execute.
```
## Examples

The provided commands can either be used on their own, or with the `find` and `xargs` commands in tandem. The latter is the recommended method, due to find's powerful filtering options.<br />

#### Standalone
Traverse through multiple directories and copy the contents somewhere, sorted by access-time:
```sh
timefops atime copy dir1/ dir2/ dir3/ -t /dest/path
```
Archive all the files and folders specified as is into a .tar.bz2 archive, sorted by modified-time:
```sh
timefops mtime archive file1 dir1/ dir2/ file2 -i -a standalone_example -c bz2
```
#### <br />Using `find` and `xargs` 
Find files accessed within the last hour and move them somewhere into folders with the 12-hour time, sorted by accessed-time:
```sh
find ./ -type f -amin -60 -print0 | xargs -0 timefops atime move -f "%I:%M%p" -i -t /dest/path
```
Find all shell scripts and put them in a gzip-compressed tar archive, sorted by changed-time:
```sh
find ./ -type f -iname "*.sh" -print0 | xargs -0 timefops ctime archive -i -a ex_archive -c gz
```
Get directories that were modified between April 1, 2020 - April 30, 2020 and copy them somewhere, sorted by modified-time:
```sh
find ./ -type d -newermt 2020-04-01 ! -newermt 2020-04-30 -prune -print0 | \
xargs -0 timefops mtime copy -i -t /dest/path
```
Specify directories to be traversed (-i flag is omitted) and copy the contents inside to somewhere, sorted by modified-time:
```sh
find ./ -type d \( -iname 'pat1' -o -iname 'pat2' \) -prune -print0 | \
xargs -0 timefops mtime copy -t /dest/path
```
