#!/usr/bin/env python3

"""Sorting files by time, made easy.
    Gets last access/creation/modification time from file(s) and/or folder(s),
    then either moves, copies or archives them to a new location, sorting them
    in new folders.  These folder names are created using a format string
    (in 'yyyy-mm-dd' format by default).
"""

import os
import collections
import time
import shutil
import errno
import tarfile
from datetime import datetime


def find_mount_point(path):
    """This function returns the root for a directory."""
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)
    return path


def add_enumerate(f, num):
    """Seperates a path and adds 'num' in the right spot, used for renaming."""
    name, suffix = os.path.splitext(f)
    return "{}({}){}".format(name, num, suffix)


def path_time_map(src, method, fmt, individual=False):
    """
    *args:
    src - list: list of paths.
    method - str: 'os.path' function to use (getatime, getctime, getmtime) .
    fmt -str: datetime format identitfier.

    **kwargs:
    individual - bool: changes how items in src are evaluated (literal).

    Maps the file/folder path to a time str, determined by the 'fmt' argument.

    Returns:
    { absolute_path: [acm]time of object (str; determined by 'fmt' arg) }
    """
    if individual:
        return {os.path.abspath(x): datetime.strptime(time.ctime(getattr(
            os.path, method)(x)), "%a %b %d %H:%M:%S %Y").strftime(fmt)
                for x in src}
    else:
        return {os.path.abspath(y): datetime.strptime(time.ctime(getattr(
            os.path, method)(y)), "%a %b %d %H:%M:%S %Y").strftime(fmt)
                for x in list((os.scandir(path) for path in src)) for y in x}


def rename_duplicates(f):
    """
    *args:
    f - dict; (use the output of path_time_map())

    Will rename any files/folders (by enumerating) if there are any duplicates
    that fall under the same time string.

    Returns:
    dict - {absolute_path: basename (renamed using add_enumerate, if needed.)}
    """
    basename_map = {x: os.path.basename(x) for x in f}

    filter_dict = collections.defaultdict(dict)
    for fn, date in f.items():
        filter_dict[os.path.basename(fn)].update({fn: date})

    to_rename = collections.defaultdict(lambda: collections.defaultdict(list))
    for key, val in filter_dict.items():
        if len(val) > 1:
            for date, occur in collections.Counter(val.values()).items():
                if occur > 1:
                    for subk, subv in val.items():
                        if subv == date:
                            to_rename[subv][os.path.basename(subk)].append(subk)

    for d, i in to_rename.items():
        for bn, p in i.items():
            for k, v in enumerate(p):
                if k > 0:
                    basename_map[v] = add_enumerate(os.path.basename(v), k)
                else:
                    basename_map[v] = os.path.basename(v)

    return basename_map, to_rename


def move(src, dst, method, fmt, individual=False, dry_run=False):
    """
    *args:
    src - list: directories/filenames.
    dst - str: destination directory path.
    fmt - str: datetime format identitfier.

    **kwargs:
    cmp - str (optional): compression shorthand (bz2, gz, xz).
    individual - bool: changes how items in src are evaluated (literal).
    dry_run - bool: whether to actually run, or just print expected results.


    Moves files/folders & puts them in folders by a date defined by the
    method parameter (atime, ctime, mtime) and fmt (format identifier).

    This function will raise an Exception if the source and dest. paths are
    on different drives/filesystems, this was done as a precaution due to
    unexpected behaviour. To get around this, just use _copy() instead.
    """

    # Make sure moving is local only (all platforms)
    for path in src:
        if find_mount_point(path) != find_mount_point(dst):
            raise UserWarning("For transferring files to a different "
                              "filesystem, use the copy function.")

    file_time_map = path_time_map(src, "get{}".format(method), fmt,
                                  individual=individual)

    rename_map = rename_duplicates(file_time_map)[0]

    if dry_run:
        print("Creating directories based on {}.\n".format(method))
        print("# of items to be moved: {}\n".format(len(file_time_map)))
        print("Item list:")

    # Move the associated items to the designated path.
    for n, (i, p) in enumerate(file_time_map.items(), 1):
        target_dir = os.path.join(dst, p)
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)
            try:
                shutil.move(i, os.path.join(target_dir, rename_map.get(i)))
            except PermissionError:
                print("You dont have the proper permissions to move: '{}', "
                      "skipping.".format(i))
        else:
            print("{}. {} --> {}".format(
                n, os.path.relpath(i), os.path.join(target_dir,
                                                    rename_map.get(i))
            ))


def copy(src, dst, method, fmt, individual=False, dry_run=False):
    """
    *args:
    src - list: directories/filenames.
    dst - str: destination directory path.
    fmt - str: datetime format identitfier.

    **kwargs:
    cmp - str (optional): compression shorthand (bz2, gz, xz).
    individual - bool: changes how items in src are evaluated (literal).
    dry_run - bool: whether to actually run, or just print expected results.


    Copies files/folders & puts them in folders by last by a date defined by
    the method parameter (atime, ctime, mtime) and fmt (format identifier).
    """

    file_time_map = path_time_map(src, "get{}".format(method), fmt,
                                  individual=individual)

    rename_map = rename_duplicates(file_time_map)[0]

    if dry_run:
        print("Creating directories based on {}.\n".format(method))
        print("# of items to be copied: {}\n".format(len(file_time_map)))
        print("Item list:")

    # Copy the associated items to the designated path.
    for n, (i, p) in enumerate(file_time_map.items(), 1):
        target_dir = os.path.join(dst, p)
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)
            try:
                shutil.copytree(i, os.path.join(target_dir, rename_map.get(i)))
            except PermissionError:
                print("You dont have the proper permissions to copy the "
                      "directory: '{}', skipping.".format(os.path.relpath(i)))
            except OSError as exc:
                # If not a directory, copy the file(s)
                if exc.errno == errno.ENOTDIR:
                    try:
                        shutil.copy2(i, os.path.join(target_dir,
                                                     rename_map.get(i)))
                    except PermissionError:
                        print("You dont have the proper permissions to copy "
                              "the file: '{}', skipping."
                              .format(os.path.relpath(i))
                              )
        else:
            print("{}. {} --> {}".format(
                n, os.path.relpath(i), os.path.join(target_dir,
                                                    rename_map.get(i))
            ))


def archive(src, dst, method, fmt, cmp=None, individual=False, dry_run=False):
    """
    *args:
    src - list: directories/filenames.
    dst - str: destination directory path.
    fmt - str: datetime format identitfier.

    **kwargs:
    cmp - str (optional): compression shorthand (bz2, gz, xz).
    individual - bool: changes how items in src are evaluated (literal).
    dry_run - bool: whether to actually run, or just print expected results.


    Makes a tar archive containing the files/folders specified in 'src' nested
    under folders by a date defined by the 'method' parameter
    (atime, ctime, mtime) and fmt (format identifier). This archive can be
    compressed by passing a valid compression method to 'cmp'.
    """
    file_time_map = path_time_map(src, "get{}".format(method), fmt,
                                  individual=individual)

    rename_map = rename_duplicates(file_time_map)

    if not dry_run:
        with tarfile.open(dst, mode=f"x:{cmp}" if cmp else "x") as tar:
            # Put the associated items into a tar archive
            # nesting the items under the designated path.
            for i, p in file_time_map.items():
                try:
                    tar.add(i, arcname=os.path.join(p, rename_map[0].get(i)))
                except PermissionError:
                    print("You dont have the proper permissions to add: "
                          "'{}' to the archive, skipping.".format(i))
    else:
        print("Creating directories based on {}.\n".format(method))
        print("# of items to be archived: {}".format(len(file_time_map)),
              end='')
        if cmp:
            print("; using '{}' compression.".format(cmp), end='')
        print("\n\nItem list:")

        for n, (i, p) in enumerate(file_time_map.items(), 1):
            target_dir = os.path.join(dst, p)
            print("{}. {} --> {}".format(
                n, os.path.relpath(i), os.path.relpath(os.path.join(
                    target_dir, rename_map[0].get(i)))
            ))
