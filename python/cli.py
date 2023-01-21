import argparse
import io
import json
import multiprocessing as mp
import pathlib
import traceback
import warnings
from datetime import datetime

import app
import language
from tqdm.auto import tqdm

CLI_HELP = """Translates or transliterates Lang.dat files of Spacer Rangers
2/HD game. Default behavior is transliteration as it doesn't require access to
DeepL.com api. If you want to translate. Read README.md to find out what needs
to be done."""

def _get_args():

    parser = argparse.ArgumentParser(
        description=CLI_HELP)

    subparsers = parser.add_subparsers(help="Available")

    parser_show = subparsers.add_parser("show",help="Reads Lang.dat and prints it as json to stdout")
    parser_show.set_defaults(func=command_show)
    parser_show.add_argument("file",help ="Path to Lang.dat file")

    parser_transl = subparsers.add_parser(
        "transl_dat",                               
        help="Translate signle dat file Lang.Dat.transl in the same folder")
    _add_transl_argument(parser_transl)
    parser_transl.add_argument("file",help="Dat file to translate")
    parser_transl.add_argument(
        "--stdout", help="Prints result to stdout, not to a file", action="store_true"
    )

    parser_transl.set_defaults(func=command_transl_dat)

    parser_transl_mod = subparsers.add_parser(
        "transl_mod",
        help="Translates ModuleInfo.txt and CFG/Rus/Lang.Dat in a mod folder")
    _add_transl_argument(parser_transl_mod)
    parser_transl_mod.add_argument("folder",help = "Path to a mod folder")
    parser_transl_mod.set_defaults(func=command_transl_mod)

    parser_transl_all_mods = subparsers.add_parser(
        "transl_all_mods",
        help = "Translates all mods in Space Ranger/Mods folder")

    _add_transl_argument(parser_transl_all_mods)
    parser_transl_all_mods.add_argument("folder", help='Path to Mods folder')
    parser_transl_all_mods.set_defaults(func=command_transl_all_mods)
    return parser.parse_args()


def _add_transl_argument(parser):

    parser.add_argument(
        "--translate",
        help="Uses translation instead of translition. Requires DeepL account",
        action="store_true",
    )


def command_transl_mod(args):
    transl_func = _resolve_transl_func(args)
    folder_path = pathlib.Path(args.folder)

    app.translate_mod(folder_path, transl_func, notify_progress=True)


def command_show(args):
    file_path = pathlib.Path(args.file)
    app.show_dat(file_path)


def command_transl_dat(args):
    transl_func = _resolve_transl_func(args)
    dat_file_path = pathlib.Path(args.file)
    dat_file_path_out = pathlib.Path(str(dat_file_path) + ".transl")
    app.transl_dat_file(
        dat_file_path,
        dat_file_path_out,
        transl_func,
        stdout=args.stdout,
        notify_progress=True,
    )


def _process_one_mod(params):
    mod_folder, transl_func = params
    mod_name = f"{mod_folder.parent.name}/{mod_folder.name}"
    # print("Processing: ", mod_name)
    try:
        app.translate_mod(mod_folder, transl_func)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"ERROR while processing {mod_name}:", e, tb)


def command_transl_all_mods(args):
    folder_path = pathlib.Path(args.folder)

    folders = [x for x in folder_path.glob("*/*") if x.is_dir()]
    if len(folders) == 0:
        warnings.warn("No folders found in {str(folder_path)}")
    params = [(x, _resolve_transl_func(args)) for x in folders]
    total = len(params)
    with mp.Pool() as pool:
        list(tqdm(pool.imap(_process_one_mod, params), total=total))


def _resolve_transl_func(args):
    if args.translate:
        return language.TranslatorOptimizer()
    else:
        return language.translit


if __name__ == "__main__":
    args = _get_args()
    args.func(args)
