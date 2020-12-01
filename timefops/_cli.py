import argparse
import os
import sys
import getpass
import logging
from . import Timefops, __version__, TRANSLATIONS


def cli(argv):
    main_parser = argparse.ArgumentParser(
        description="Operate on files/directories based on their "
                    "access/change/modified times.",
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
                 "help='Archive contents to a tarball or a zip file.',"
                 "description='Archive contents to a tarball or a zip file, '"
                             "'sorted by '"
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
                "help='Move contents to a different location.',"
                "description='Move contents to a different location, '"
                      f"'sorted by {TRANSLATIONS.get(str(p).split('_')[0])}.')",
             globals(), dyn_opts)

    # arguments for archive operation.
    for arc_p in (dyn_opts["archive_ops_atime_parser"],
                  dyn_opts["archive_ops_ctime_parser"],
                  dyn_opts["archive_ops_mtime_parser"]):

        gen_arc_args = arc_p.add_argument_group("General arguments")
        bin_out_args = gen_arc_args.add_mutually_exclusive_group()
        

        arc_p.add_argument("-V", "--version",
                           action="version",
                           version=f"{__version__}",
                           help="print version number/info and exit")

        gen_arc_args.add_argument("src",
                                  type=str,
                                  nargs='+',
                                  help="Source directories/files.")

        bin_out_args.add_argument("-a", "--archive",
                                  type=str,
                                  dest='archive',
                                  default="",
                                  metavar="NAME",
                                  help="Name for target archive.")

        bin_out_args.add_argument("--to-stdout",
                                  action="store_true",
                                  help="Write tar archive or zip file to "
                                       "stdout instead of a named file, "
                                       "emulates the '-' option of "
                                       "the tar and zip executables.")

        gen_arc_args.add_argument("-z", "--zipfile",
                                  action="store_true",
                                  help="Makes a zip file instead of a "
                                       "tar archive (GZ compression "
                                       "is not available with this option)")

        gen_arc_args.add_argument("-c", "--compression",
                                  choices=("bz2", "gz", "xz"),
                                  type=str.lower,
                                  help="Compression format for the archive.")

        gen_arc_args.add_argument("-f", "--format",
                                  type=str,
                                  default=["%Y-%m-%d"],
                                  nargs="+",
                                  help="Set folder name format (using Python's "
                                       "datetime formatting directives). If "
                                       "there are multiple values specifed, "
                                       "contents will get nested under the "
                                       "last value.")

        gen_arc_args.add_argument("-i", "--individual-items",
                                  action="store_true",
                                  help="Setting this flag will allow for "
                                       "specifying individual source files and "
                                       "folders.  The difference between "
                                       "specifiying a source folder with this "
                                       "flag on is that any folder(s) specified"
                                       " will not be traversed and instead be "
                                       "treated as a standalone item.")

        gen_arc_args.add_argument("-v", "--verbose",
                                  action="store_const",
                                  const=int(logging.INFO - 5),
                                  default=logging.INFO,
                                  help="Set log level to verbose.")

        gen_arc_args.add_argument("-d", "--debug",
                                  action="store_const",
                                  const=logging.DEBUG,
                                  default=logging.INFO,
                                  help="Set log level to debug "
                                       "(includes verbose).")

        gen_arc_args.add_argument("--no-color", "--no-colour",
                                  action="store_false",
                                  help="Disable coloured logging output.")

        gen_arc_args.add_argument("--dry-run",
                                  action="store_true",
                                  help="Show results, but don't execute.")

        enc_zip = arc_p.add_argument_group("AES-Encrypted Zipfile options", 
                description="Arguments for making a password-protected "
                            "AES-Encrypted zip file. The -z/--zipfile "
                            "flag is required for any of these to "
                            "register, otherwise they will be ignored."
                            " Encrypting a zip file will not hide the "
                            "directory structure, or encrypt any directories, "
                            "but will encrypt individual files.")

        enc_passwd_args = enc_zip.add_mutually_exclusive_group()

        enc_passwd_args.add_argument("--zip-password", "-zp",
                             action="store_true",
                             help="Prompts for a password to encrypt zip "
                                  "folder contents with.")

        enc_passwd_args.add_argument("--zip-password-plaintext", "-zP",
                                     type=str,
                                     metavar="PASSWORD",
                                     help="Specify zip file password in "
                                          "plaintext, avoid this option "
                                          "if possible.")

        enc_zip.add_argument("--zip-encryption", "-ze",
                             choices=("weak", "medium", "strong"),
                             type=str.lower,
                             help="Set the strength of the AES encryption,"
                                  " if nothing is specified, 'medium' is "
                                  "used by default.")


    # arguments for copy/move operations.
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
                                 default=["%Y-%m-%d"],
                                 nargs="+",
                                 help="Set folder name format (using Python's "
                                       "datetime formatting directives). If "
                                       "there are multiple values specifed, "
                                       "contents will get nested under the "
                                       "last value.")

        gen_cm_args.add_argument("-i", "--individual-items",
                                 action="store_true",
                                 help="Setting this flag will allow for "
                                      "specifying individual source files and "
                                      "folders.  The difference between "
                                      "specifiying a source folder with this "
                                      "flag on is that any folder(s) specified "
                                      "will not be traversed and instead be "
                                      "treated as a standalone item.")

        gen_cm_args.add_argument("-v", "--verbose",
                                 action="store_const",
                                 const=int(logging.INFO - 5),
                                 default=logging.INFO,
                                 help="Set log level to verbose.")

        gen_cm_args.add_argument("-d", "--debug",
                                 action="store_const",
                                 const=logging.DEBUG,
                                 default=logging.INFO,
                                 help="Set log level to debug "
                                      "(includes verbose).")

        gen_cm_args.add_argument("--no-color", "--no-colour",
                                 action="store_false",
                                 help="Disable coloured logging output.")

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
        if opts.archive:
            if os.path.exists(opts.archive):
                parser.error(f"file '{opts.archive}' already exists.")

            if opts.zipfile:
                if opts.compression == "gz":
                    parser.error("'gz' compression not available with -z/--zipfile")
                if not opts.archive.endswith(".zip"):
                    opts.archive = opts.archive + ".zip"
            else:
                if not opts.compression and not opts.archive.endswith(".tar"):
                    opts.archive = opts.archive + ".tar"

                elif opts.compression and not opts.archive.endswith(
                        f".tar.{opts.compression}"):
                    opts.archive = opts.archive + f".tar.{opts.compression}"

            dir_tree = tuple(filter(None, os.path.split(opts.archive)))

            if len(dir_tree) > 1:
                # if the parent path doesn't exist...
                if not os.path.isdir(dir_tree[0]):
                    parser.error(f"cannot make file: '{opts.archive}'.")
            else:
                opts.archive = os.path.join(os.getcwd(), dir_tree[0])

            # Make sure the file doesn't exist after (possibly) adding suffix
            if os.path.isfile(opts.archive):
                parser.error(f"file '{opts.archive}' already exists.")

            if not os.access(os.path.dirname(opts.archive), os.W_OK | os.X_OK):
                parser.error("directory where archive is to be created is not "
                             "writable/executable, unable to make archive here.")
        elif opts.to_stdout:
            if not opts.compression and not opts.zipfile:
                parser.error("--to-stdout needs compression "
                        "(-c/--compression) when working with a tar archive")
            elif opts.zipfile and opts.compression == "gz":
                parser.error("'gz' compression not available with -z/--zipfile")
        else:
            parser.error("either one of -a/--archive or --to-stdout "
                         "is required.")

        if opts.zipfile:
            if opts.zip_encryption and not (opts.zip_password or \
                    opts.zip_password_plaintext):
                parser.error("To make an AES-encrypted zip file, make a "
                             "password with '-zp' or '-zP'.")
            elif opts.zip_password and not opts.dry_run:
                opts.zip_password = getpass.getpass("Enter a password: ")
            elif opts.zip_password_plaintext:
                opts.zip_password = opts.zip_password_plaintext

            enc_lvls = {"weak": 128, "medium": 192, "strong": 256}
            opts.zip_encryption = enc_lvls.get(opts.zip_encryption, 192)
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
    tfops = Timefops(min(args.debug, args.verbose), color=args.no_color)

    if args.operation == "archive":
        tfops.archive(args.src, args.archive, args.time, args.format,
                      individual=args.individual_items, cmp_sh=args.compression,
                      zip_file=args.zipfile, to_stdout=args.to_stdout, 
                      aes_zip_create=(args.zip_password, args.zip_encryption) \
                                     if args.zip_password \
                                     or args.zip_encryption else (),
                      dry_run=args.dry_run)

    elif args.operation == "copy":
        tfops.copy(args.src, args.target_directory, args.time, args.format,
             individual=args.individual_items, dry_run=args.dry_run)

    elif args.operation == "move":
        tfops.move(args.src, args.target_directory, args.time, args.format,
                   individual=args.individual_items, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
