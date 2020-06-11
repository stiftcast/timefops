import timefops as tf
import os
import sys
import argparse


AUTHOR = "stiftcast"
LICENCE = "GPLv3"
VERSION = "0.1.0"


def arguments(name, argv, archive=False):
    parser = argparse.ArgumentParser(name)

    parser.add_argument("src",
                        type=str,
                        nargs='+',
                        help="Source directories/files.")

    if not archive:
        parser.add_argument("-t", "--target-directory",
                            type=str,
                            required=True,
                            help="Destination directory.")

    else:
        parser.add_argument("-a", "--archive",
                            type=str,
                            required=True,
                            help="Name for target archive.")

        parser.add_argument("-c", "--compression",
                            choices=("bz2", "gz", "xz"),
                            help="Compression format for the archive.")

    parser.add_argument("-f", "--format",
                        type=str,
                        default="%Y-%m-%d",
                        help="Set folder name format (using Python's datetime "
                             "formatting directives).")

    parser.add_argument("-i", "--individual-items",
                        action="store_true",
                        help="Setting this flag will allow for specifying "
                             "individual source files and folders.  The "
                             "difference between specifiying a source folder "
                             "with this flag on is that any folder(s) specified"
                             " will not be traversed and instead be treated "
                             "as a standalone item.")

    parser.add_argument("--dry-run",
                        action="store_true",
                        help="Show results, but don't execute.")

    parser.add_argument("-v", "--version",
                        action="store_true",
                        help="Display licence/version info and exit.")

    opts = parser.parse_args(argv)

    # Run preliminary checks, raising an error if necessary.

    if opts.version:
        print("Author: {}\nLicence: {}\nVersion: {}"
              .format(AUTHOR, LICENCE, VERSION))
        sys.exit(0)

    for path in opts.src:
        if opts.individual_items:
            if not os.path.exists(path):
                parser.error("source path: '{}' could not be understood, "
                             "or does not exist.".format(path))
        else:
            if not os.path.isdir(path):
                parser.error("source dir: '{}' could not be understood, or "
                             "does not exist; use '-i' if entry is a file."
                             .format(path))

            # directories specified without using '-i' will be traversed.
            elif not os.access(path, os.R_OK | os.X_OK):
                parser.error("source dir: '{}' is unable to be traversed."
                             .format(path))

    if archive:
        if not opts.compression and not opts.archive.endswith(".tar"):
            opts.archive = opts.archive + ".tar"

        elif opts.compression and not opts.archive.endswith(
                ".tar.{}".format(opts.compression)):
            opts.archive = opts.archive + ".tar.{}".format(opts.compression)

        dir_tree = tuple(filter(None, os.path.split(opts.archive)))

        if len(dir_tree) > 1:
            # if the parent path doesn't exist...
            if not os.path.isdir(dir_tree[0]):
                parser.error("couldn't make file: '{}'.".format(opts.archive))
        else:
            opts.archive = os.path.join(os.getcwd(), dir_tree[0])

        if os.path.isfile(opts.archive):
            parser.error("file '{}' already exists.".format(opts.archive))

        if not os.access(os.path.dirname(opts.archive), os.W_OK | os.X_OK):
            parser.error("directory where archive is to be created is not "
                         "writable/executable, unable to make archive here.")
    else:

        if not os.path.isdir(opts.target_directory):
            parser.error("dest. directory: '{}' could not be understood, or "
                         "does not exist.".format(opts.target_directory))
        elif not os.access(opts.target_directory, os.W_OK | os.X_OK):
            parser.error("dest. directory is not writable/executable, "
                         "unable to transfer items here.")
    return opts


def archive(mode):
    def inner_archive():
        args = arguments("{}archive".format(mode[0:2]),
                         sys.argv[1::],
                         archive=True)
        tf.archive(args.src,
                   args.archive,
                   mode,
                   args.format,
                   individual=args.individual_items,
                   cmp=args.compression,
                   dry_run=args.dry_run)

    return inner_archive


def copy(mode):
    def inner_copy():
        args = arguments("{}copy".format(mode[0:2]),
                         sys.argv[1::])
        tf.copy(args.src,
                args.target_directory,
                mode,
                args.format,
                individual=args.individual_items,
                dry_run=args.dry_run)

    return inner_copy


def move(mode):
    def inner_move():
        args = arguments("{}move".format(mode[0:2]),
                         sys.argv[1::])
        try:
            tf.move(args.src,
                    args.target_directory,
                    mode,
                    args.format,
                    individual=args.individual_items,
                    dry_run=args.dry_run)
        except UserWarning as err:
            print(err)

    return inner_move


atarchive = archive("atime")
atcopy = copy("atime")
atmove = move("atime")

ctarchive = archive("ctime")
ctcopy = copy("ctime")
ctmove = move("ctime")

mtarchive = archive("mtime")
mtcopy = copy("mtime")
mtmove = move("mtime")
