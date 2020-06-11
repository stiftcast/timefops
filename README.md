# timefops
Performs file operations (moving, copying and archiving) on files/directories based on their access/change/modified dates.

## Description
This program will provide a total of 9 commands, which will provide moving, copying and archiving capabilities for files/directories based on their access time, change time or modified time.

`[acm]tmove` - Move files/dirs based on the date last accessed/created/modified.<br />
`[acm]tcopy` - Copy files/dirs based on the date last accessed/created/modified.<br />
`[acm]tarchive` - Archive files/dirs based on the date last accessed/created/modified.<br />

Both the copying and moving functionality utilize Python's `shutil` module, whereas the `tarfile` module is used for creating tar archives.

Tested & confirmed working on Linux and Windows platforms, compatibility with Mac OS is unknown.

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
For `[acm]tcopy` or `[acm]tmove`:
```
positional arguments:
src                   Source directories/files.

optional arguments:
-h, --help            show this help message and exit
-t TARGET_DIRECTORY, --target-directory TARGET_DIRECTORY
                    Destination directory.
-f FORMAT, --format FORMAT
                    Set folder name format (using Python's datetime
                    formatting directives).
-i, --individual-items
                    Setting this flag will allow for specifying individual
                    source files and folders. The difference between
                    specifiying a source folder with this flag on is that
                    any folder(s) specified will not be traversed and
                    instead be treated as a standalone item.
--dry-run             Show results, but don't execute.
-v, --version         Display licence/version info and exit.
```
<br /> For `[acm]tarchive`:
```
positional arguments:
src                   Source directories/files.

optional arguments:
-h, --help            show this help message and exit
-a ARCHIVE, --archive ARCHIVE
                    Name for target archive.
-c {bz2,gz,xz}, --compression {bz2,gz,xz}
                    Compression format for the archive.
-f FORMAT, --format FORMAT
                    Set folder name format (using Python's datetime
                    formatting directives).
-i, --individual-items
                    Setting this flag will allow for specifying individual
                    source files and folders. The difference between
                    specifiying a source folder with this flag on is that
                    any folder(s) specified will not be traversed and
                    instead be treated as a standalone item.
--dry-run             Show results, but don't execute.
-v, --version         Display licence/version info and exit.
```
## Examples

### API
```python
import timefops

# For archiving:
timefops.archive([list_of_dirs], dest_dir, "atime", "%Y-%m-%d", cmp="gz", individual=False, dry_run=False)

# For copying:
timefops.copy([list_of_dirs], dest_dir, "ctime", "%Y-%m-%d", individual=False, dry_run=False)

# For moving:
timefops.move([list_of_dirs], dest_dir, "mtime", "%Y-%m-%d", individual=False, dry_run=False)

# NOTE: if individual=True, then the iterable [list_of_dirs] can also contain paths to files.
```
### CLI
The provided commands can either be used on their own, or with the `find` and `xargs` commands in tandem. The latter is the recommended method, due to find's powerful filtering options.<br />

#### Standalone
Traverse through multiple directories and copy the contents somewhere, sorted by access date:
```sh
atcopy dir1/ dir2/ dir3/ -t /dest/path
```
Archive all the files and folders specified as is into a .tar.bz2 archive, sorted by modified date:
```sh
mtarchive file1 dir1/ dir2/ file2 -i -a standalone_example -c bz2
```
#### <br />Using `find` and `xargs` 
Find files accessed within the last hour and move them somewhere into folders with the 12-hour time, sorted by accessed date:
```sh
find ./ -type f -amin -60 -print0 | xargs -0 atmove -f "%I:%M%p" -i -t /dest/path
```
Find all shell scripts and put them in a gzip-compressed tar archive, sorted by changed date:
```sh
find ./ -type f -iname "*.sh" -print0 | xargs -0 ctarchive -i -a ex_archive -c gz
```
Get directories that were modified between April 1, 2020 - April 30, 2020 and copy them somewhere, sorted by modified date:
```sh
find ./ -type d -newermt 2020-04-01 ! -newermt 2020-04-30 -prune -print0 | xargs -0 mtcopy -i -t /dest/path
```
Specify directories to be traversed (-i flag is omitted) and copy the contents inside to somewhere, sorted by modified date:
```sh
find ./ -type d \( -iname 'pat1' -o -iname 'pat2' \) -prune -print0 | xargs -0 mtcopy -t /dest/path
```
