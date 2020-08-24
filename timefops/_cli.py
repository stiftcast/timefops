import argparse
import os
import sys
from . import __version__, archive, copy, move


TRANSLATIONS = {"atime": "access-time",
                "ctime": "change-time",
                "mtime": "modified-time"}


def cli(argv):
    main_parser = argparse.ArgumentParser(
        description="Operate on files/directories based on their "
                    "access/change/modified dates.",
        formatter_class=argparse.RawTextHelpFormatter)

    main_parser.add_argument("-V", "--version",
                             action="version",
                             version=f"{__version__}",
                             help="print version number/info and exit")

    sub_parsers = main_parser.add_subparsers(
        title="Time predicate",
        dest="time",
        metavar="<time>",
        required=True)

    atime_parser = sub_parsers.add_parser(
        "atime",
        help="Perform operations based on last access-time.",
        description="Perform operations based on last access-time.")

    ctime_parser = sub_parsers.add_parser(
        "ctime",
        help="Perform operations based on last change-time.",
        description="Perform operations based on last change-time.")

    mtime_parser = sub_parsers.add_parser(
        "mtime",
        help="Perform operations based on last modification-time.",
        description="Perform operations based on last modification-time.")

    dyn_opts = locals()
    
    for p in ('atime_parser', 'ctime_parser', 'mtime_parser'):
        
        exec(f"{p}.add_argument('-V', '--version', action='version',"
             "version=f'{__version__}', "
             "help='print version number/info and exit')",
             globals(), dyn_opts)
        
        exec(f"ops_{p} = {p}.add_subparsers("
                 "title='Operations', dest='operation', metavar='<operation>', "
                 "required=True)",
             globals(), dyn_opts)
        
        exec(f"archive_ops_{p} = ops_{p}.add_parser("
                 "'archive',"
                 "help='Archive contents to a tarball, with '"
                      "'optional compression.',"
                 "description='Archive contents to a tarball '"
                             "'(w/ opt. compression), sorted by '"
                            f"'{TRANSLATIONS.get(str(p).split('_')[0])}.')",
             globals(), dyn_opts)

        exec(f"copy_ops_{p} = ops_{p}.add_parser("
                 "'copy',"
                 "help='Copy contents to a different location.',"
                 "description='Copy contents to a different location, sorted '"
                            f"'by {TRANSLATIONS.get(str(p).split('_')[0])}.')",
             globals(), dyn_opts)

        exec(f"move_ops_{p} = ops_{p}.add_parser("
                "'move',"
                "help='Move contents to a different (local) location.',"
                "description='Move contents to a different (local) location, '"
                      f"'sorted by {TRANSLATIONS.get(str(p).split('_')[0])}.')",
             globals(), dyn_opts)
          
    # base arguments for archive operation.
    for arc_p in (dyn_opts["archive_ops_atime_parser"],
                  dyn_opts["archive_ops_ctime_parser"],
                  dyn_opts["archive_ops_mtime_parser"]):

        gen_arc_args = arc_p.add_argument_group("General arguments")


        arc_p.add_argument("-V", "--version",
                           action="version",
                           version=f"{__version__}",
                           help="print version number/info and exit")
        
        gen_arc_args.add_argument("src",
                                  type=str,
                                  nargs='+',
                                  help="Source directories/files.")
        
        gen_arc_args.add_argument("-a", "--archive",
                                  type=str,
                                  dest='archive',
                                  required=True,
                                  help="Name for target archive.")

        gen_arc_args.add_argument("-c", "--compression",
                                  choices=("bz2", "gz", "xz"),
                                  type=str.lower,
                                  help="Compression format for the archive.")

        gen_arc_args.add_argument("-f", "--format",
                                  type=str,
                                  default="%Y-%m-%d",
                                  help="Set folder name format (using Python's "
                                       "datetime formatting directives).")

        gen_arc_args.add_argument("-i", "--individual-items",
                                  action="store_true",
                                  help="Setting this flag will allow for "
                                       "specifying individual source files and "
                                       "folders.  The difference between "
                                       "specifiying a source folder with this "
                                       "flag on is that any folder(s) specified"
                                       " will not be traversed and instead be "
                                       "treated as a standalone item.")

        gen_arc_args.add_argument("--dry-run",
                                  action="store_true",
                                  help="Show results, but don't execute.")


    # base arguments for copy/move operations.
    for cm_p in (dyn_opts["copy_ops_atime_parser"],
                 dyn_opts["copy_ops_ctime_parser"],
                 dyn_opts["copy_ops_mtime_parser"],
                 dyn_opts["move_ops_atime_parser"],
                 dyn_opts["move_ops_ctime_parser"],
                 dyn_opts["move_ops_mtime_parser"]):

        gen_cm_args = cm_p.add_argument_group("General arguments")


        cm_p.add_argument("-V", "--version",
                          action="version",
                          version=f"{__version__}",
                          help="print version number/info and exit")

        gen_cm_args.add_argument("src",
                                 type=str,
                                 nargs='+',
                                 help="Source directories/files.")
        
        gen_cm_args.add_argument("-t", "--target-directory",
                                 type=str,
                                 required=True,
                                 help="Destination directory.")

        gen_cm_args.add_argument("-f", "--format",
                                 type=str,
                                 default="%Y-%m-%d",
                                 help="Set folder name format (using Python's "
                                      "datetime formatting directives).")

        gen_cm_args.add_argument("-i", "--individual-items",
                                 action="store_true",
                                 help="Setting this flag will allow for "
                                      "specifying individual source files and "
                                      "folders.  The difference between "
                                      "specifiying a source folder with this "
                                      "flag on is that any folder(s) specified "
                                      "will not be traversed and instead be "
                                      "treated as a standalone item.")

        gen_cm_args.add_argument("--dry-run",
                                 action="store_true",
                                 help="Show results, but don't execute.")

        
    opts = main_parser.parse_args(argv)

    parser = dyn_opts[f"{opts.operation}_ops_{opts.time}_parser"]

    for path in opts.src:
        if opts.individual_items:
            if not os.path.exists(path):
                parser.error(f"src path '{path}' not understood/does "
                             "not exist.")
        else:
            if not os.path.isdir(path):
                parser.error(f"src dir '{path}' not understood/does not exist;"
                             " use '-i' if entry is a file.")

            # directories specified without using '-i' will be traversed.
            elif not os.access(path, os.R_OK | os.X_OK):
                parser.error(f"src dir '{path}' is unable to be traversed.")

    if opts.operation == "archive":
        if not opts.compression and not opts.archive.endswith(".tar"):
            opts.archive = opts.archive + ".tar"

        elif opts.compression and not opts.archive.endswith(
                ".tar.{}".format(opts.compression)):
            opts.archive = opts.archive + f".tar.{opts.compression}"

        dir_tree = tuple(filter(None, os.path.split(opts.archive)))

        if len(dir_tree) > 1:
            # if the parent path doesn't exist...
            if not os.path.isdir(dir_tree[0]):
                parser.error(f"cannot make file: '{opts.archive}'.")
        else:
            opts.archive = os.path.join(os.getcwd(), dir_tree[0])

        if os.path.isfile(opts.archive):
            raise parser.error(f"file '{opts.archive}' already exists.")

        if not os.access(os.path.dirname(opts.archive), os.W_OK | os.X_OK):
            parser.error("directory where archive is to be created is not "
                         "writable/executable, unable to make archive here.")
    else:

        if not os.path.isdir(opts.target_directory):
            parser.error(f"dest. directory '{opts.target_directory}' not "
                         "understood/does not exist.")
        elif not os.access(opts.target_directory, os.W_OK | os.X_OK):
            parser.error("dest. directory is not writable/executable, "
                         "unable to transfer items here.")
    return opts


def main():
    args = cli(sys.argv[1::])

    if args.operation == "archive":
        archive(args.src, args.archive, args.time, args.format,
                individual=args.individual_items, cmp=args.compression,
                dry_run=args.dry_run)
        
    elif args.operation == "copy":
        copy(args.src, args.target_directory, args.time, args.format,
             individual=args.individual_items, dry_run=args.dry_run)

    elif args.operation == "move":
        try:
            move(args.src, args.target_directory, args.time, args.format,
             individual=args.individual_items, dry_run=args.dry_run)
        except UserWarning as err:
            print(err)
