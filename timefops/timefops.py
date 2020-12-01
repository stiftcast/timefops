"""Sorting files by time, made easy.
    Gets last access/creation/modification time from file(s) and/or folder(s),
    then either moves, copies or archives them to a new location, sorting them
    in new folders.  These folder names are created using a format string
    (in 'yyyy-mm-dd' format by default).
"""

import os
import sys
import collections
import shutil
import errno
import tarfile
import zipfile
import pyzipper
from datetime import datetime as dt
from ._logger import init_logging



class Timefops:
    def __init__(self, log_level, color=True, name=__name__):
        self.log = init_logging(log_level, name, color=color)
        self.num_warn = 0


    @staticmethod
    def find_mount_point(path):
        """This function returns the root for a directory."""
        path = os.path.abspath(path)
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return path


    @staticmethod
    def add_enumerate(f, num):
        """Seperates a path and adds 'num' in the right spot, used for renaming."""
        name, suffix = os.path.splitext(f)
        return f"{name}({num}){suffix}"


    def path_time_map(self, src, method, fmt, individual=False):
        """
        *args:
        src - list: list of paths.
        method - str: 'os.path' function to use (getatime, getctime, getmtime) .
        fmt - str: datetime format identitfier.

        **kwargs:
        individual - bool: changes how items in src are evaluated (literal).

        Maps the file/folder path to a time str, determined by the 'fmt' argument.

        Returns:
        { absolute_path: [acm]time of object (str; determined by 'fmt' arg) }
        """
        self.log.debug(f"format predicate -- {len(fmt)} levels, sample: " 
                       f"'{'/'.join(dt.now().strftime(x) for x in fmt)}'")

        if individual:
            return {os.path.abspath(x): '/'.join(dt.fromtimestamp(getattr(
                os.path, method)(x)).strftime(sub_fmt) for sub_fmt in fmt) 
                   for x in src}
        else:
            return {os.path.abspath(y): '/'.join(dt.fromtimestamp(getattr(
                os.path, method)(y)).strftime(sub_fmt) for sub_fmt in fmt)
                   for x in list((os.scandir(path) for path in src)) 
                      for sub_fmt in fmt for y in x}


    def _rename_duplicates(self, f):
        """
        *args:
        f - dict; (use the output of path_time_map())

        Will rename any files/folders (by enumerating) if there are any
        duplicates that fall under the same time string.

        Returns:
        dict - {absolute_path: basename (renamed using add_enumerate)}
        """
        basename_map = {x: os.path.basename(x) for x in f}

        filter_dict = collections.defaultdict(dict)
        for fn, date in f.items():
            filter_dict[os.path.basename(fn)].update({fn: date})

        to_rename = collections.defaultdict(
                lambda: collections.defaultdict(list))

        for key, val in filter_dict.items():
            if len(val) > 1:
                for date, occur in collections.Counter(val.values()).items():
                    if occur > 1:
                        for subk, subv in val.items():
                            if subv == date:
                                to_rename[subv][os.path.basename(subk)
                                        ].append(subk)

        for d, i in to_rename.items():
            for bn, p in i.items():
                self.log.debug(f"{len(p)} instances of '{bn}' --> "
                               f"{[os.path.relpath(x) for x in p]}")
                for k, v in enumerate(p):
                    if k > 0:
                        basename_map[v] = self.add_enumerate(
                                                os.path.basename(v), k)
                    else:
                        basename_map[v] = os.path.basename(v)

        return basename_map, to_rename


    def _recurse_zip_helper(self, zf, path, zippath):
        """Borrowed from the source module. Evaluates whether the path is 
        a file and can just be added, or if it is a directory and needs to be 
        recursivley run (zipfile does not already do this, for some reason)
        
        *args:
        zf - zipfile.Zipfile: zipfile object instance
        path - str: path to the file/directory 
        zippath - str: zip path (dir the path will be added under in the file)
        """
        try:
            if os.path.isfile(path):
                zf.write(path, arcname=zippath)
            elif os.path.isdir(path):
                if zippath:
                    zf.write(path, zippath)
                for nm in sorted(os.listdir(path)):
                    self._recurse_zip_helper(zf,
                             os.path.join(path, nm), os.path.join(zippath, nm))
        except PermissionError:
            self.num_warn += 1
            self.log.warning("Insufficient permissions to add: "
                            f"'{os.path.relpath(path)}', skipping.")


    def move(self, src, dst, method, fmt, individual=False, dry_run=False):
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
            if self.find_mount_point(path) != self.find_mount_point(dst):
                self.log.error("For transferring files to a different "
                               "filesystem, use the copy function.")
                sys.exit(1)

        file_time_map = self.path_time_map(src, f"get{method}", fmt,
                                           individual=individual)

        rename_map = self._rename_duplicates(file_time_map)[0]

        if dry_run:
            self.log.info(f"\nCreating directories based on {method}.\n")
            self.log.info("Item list:")

        # Move the associated items to the designated path.
        for n, (i, p) in enumerate(file_time_map.items(), 1):
            target_dir = os.path.join(dst, p)
            if not dry_run:
                os.makedirs(target_dir, exist_ok=True)
                try:
                    shutil.move(i, os.path.join(target_dir, rename_map.get(i)))
                    self.log.verbose("done moving: "
                                    f"{os.path.relpath(i)}")
                except PermissionError:
                    self.num_warn += 1
                    self.log.warning("Insufficient permissions "
                                    f"to move: '{os.path.relpath(i)}', "
                                    "skipping.")
            else:
                self.log.info("{}. {} --> {}".format(
                    n, os.path.relpath(i), os.path.join(target_dir,
                                                        rename_map.get(i))
                ))

        if dry_run:
            self.log.info(f"\n# of items to be moved: {len(file_time_map)}")
        else:
            self.log.success("contents moved -- finished with "
                            f"{self.num_warn} warning(s).")


    def copy(self, src, dst, method, fmt, individual=False, dry_run=False):
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

        file_time_map = self.path_time_map(src, f"get{method}", fmt,
                                           individual=individual)

        rename_map = self._rename_duplicates(file_time_map)[0]

        if dry_run:
            self.log.info(f"\nCreating directories based on {method}.\n")
            self.log.info("Item list:")

        # Copy the associated items to the designated path.
        for n, (i, p) in enumerate(file_time_map.items(), 1):
            target_dir = os.path.join(dst, p)
            if not dry_run:
                os.makedirs(target_dir, exist_ok=True)
                try:
                    shutil.copytree(i, os.path.join(target_dir,
                                                    rename_map.get(i)))
                    self.log.verbose(f"done copying: {os.path.relpath(i)}")
                except PermissionError:
                    self.num_warn += 1
                    self.log.warning("Insufficient permissions to copy the "
                                     f"directory: '{os.path.relpath(i)}', "
                                     "skipping.")
                except OSError as exc:
                    # If not a directory, copy the file(s)
                    if exc.errno == errno.ENOTDIR:
                        try:
                            shutil.copy2(i, os.path.join(target_dir,
                                                         rename_map.get(i)))
                            self.log.verbose(f"done copying: "
                                             f"{os.path.relpath(i)}")
                        except PermissionError:
                            self.num_warn += 1
                            self.log.warning("Insufficient permissions to copy "
                                            f"the file: '{os.path.relpath(i)}',"
                                             " skipping.")
            else:
                self.log.info("{}. {} --> {}".format(
                              n, os.path.relpath(i), os.path.join(target_dir,
                                                     rename_map.get(i))
                ))

        if dry_run:
            self.log.info(f"\n# of items to be copied: {len(file_time_map)}")
        else:
            self.log.success("contents copied -- finished with "
                            f"{self.num_warn} warning(s).")



    def archive(self, src, dst, method, fmt, cmp_sh="", individual=False,
                zip_file=False, to_stdout=False, aes_zip_create=(),
                dry_run=False):
        """
        *args:
        src - list: directories/filenames.
        dst - str: destination directory path.
        fmt - str: datetime format identitfier.

        **kwargs:
        cmp_sh - str (optional): compression shorthand (bz2, gz, xz).
        individual - bool: changes how items in src are evaluated (literal).
        zip_file - bool: decides whether to use zipfile or tarfile.
        to_stdout - bool: if True, prints binary output to stdout.
        dry_run - bool: whether to actually run, or just print expected results.


        Makes a tar archive containing the files/folders specified in 'src' 
        nested under folders by a date defined by the 'method' parameter
        (atime, ctime, mtime) and fmt (format identifier). This archive can be
        compressed by passing a valid compression method to 'cmp_sh'.
        """
        file_time_map = self.path_time_map(src, f"get{method}", fmt,
                                           individual=individual)

        rename_map = self._rename_duplicates(file_time_map) 

        if aes_zip_create:
            aes_zip_password, aes_encryption_lvl = aes_zip_create

        if not dry_run:
            # Put the associated items into either a tar archive or a zip file,
            # nesting the items under the designated path.
            if zip_file:
                if aes_zip_create:
                    with pyzipper.AESZipFile(sys.stdout.buffer \
                                             if to_stdout else dst,
                                             mode='x',
                                             compression={
                                                "bz2": pyzipper.ZIP_BZIP2,
                                                "xz" : pyzipper.ZIP_LZMA
                                                }.get(cmp_sh,
                                                    pyzipper.ZIP_STORED)) as az:
                        az.setpassword(bytes(aes_zip_password, "utf-8"))
                        az.setencryption(pyzipper.WZ_AES, 
                                         nbits=aes_encryption_lvl)
                        for i, p in file_time_map.items():
                            self._recurse_zip_helper(az, i, 
                                    os.path.join(p, rename_map[0].get(i)))
                            self.log.verbose("added: "
                                      f"{os.path.join(p,rename_map[0].get(i))}")

                        self.log.success("zip file created -- finished with "
                                        f"{self.num_warn} warning(s).")
                else:
                    with zipfile.ZipFile(sys.stdout.buffer \
                                         if to_stdout else dst,
                                         mode="x",
                                         compression={
                                             "bz2": zipfile.ZIP_BZIP2,
                                             "xz" : zipfile.ZIP_LZMA
                                             }.get(zipfile.ZIP_STORED)) as z:
                        for i, p in file_time_map.items():
                            self._recurse_zip_helper(z, i, 
                                    os.path.join(p, rename_map[0].get(i)))
                            self.log.verbose("added: "
                                      f"{os.path.join(p,rename_map[0].get(i))}")

                        self.log.success("zip file created -- finished with "
                                        f"{self.num_warn} warning(s).")
            else:
                with tarfile.open(dst, mode=f"x:{cmp_sh}" if cmp_sh else "x",
                                  fileobj=sys.stdout.buffer \
                                          if to_stdout else None) as t:
                    for i, p in file_time_map.items():
                        try:
                            t.add(i, arcname=os.path.join(
                                             p, rename_map[0].get(i)))
                            self.log.verbose(
                              f"added: {os.path.join(p, rename_map[0].get(i))}")
                        except PermissionError:
                            self.num_warn += 1
                            self.log.warning("Insufficient permissions to add: "
                                  f"'{os.path.relpath(i)}', skipping.")

                    self.log.success("tar archive created -- finished with "
                                    f"{self.num_warn} warning(s).")
        else:
            self.log.info(f"\nCreating directories based on {method}.\n")
            if to_stdout:
                self.log.info("writing to stdout...")
            else:
                self.log.info(f"writing to file: '{os.path.relpath(dst)}'")
            if cmp_sh:
                self.log.info(f"- using '{cmp_sh}' compression.")
            if zip_file and aes_zip_create:
                self.log.info("\nzip file using AES encryption "
                             f"({aes_encryption_lvl}-bit)")
            if zip_file and aes_zip_password:
                self.log.info("password-protection will be set.")
            self.log.info("\nItem list:")

            for n, (i, p) in enumerate(file_time_map.items(), 1):
                target_dir = os.path.join(dst, p)
                self.log.info("{}. {} --> {}".format(
                    n, os.path.relpath(i), os.path.relpath(os.path.join(
                        target_dir, rename_map[0].get(i)))
                ))
            self.log.info(f"\n# of items to be archived: {len(file_time_map)}")
