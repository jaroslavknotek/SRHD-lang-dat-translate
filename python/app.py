import io
import json
import pathlib
import shutil
import traceback
import warnings
from datetime import datetime

import chardet
import rangers.dat
from tqdm.auto import tqdm

import utils


def show_dat(file_path):
    dat = rangers.dat.DAT.from_dat(file_path)
    _print_dat(dat)


def transl_dat_file(
    source_dat_path, target_dat_path, transl_func, stdout=False, notify_progress=False
):

    lang_dat = rangers.dat.DAT.from_dat(source_dat_path)
    lang_dat_transl = _transl_dat_obj(lang_dat, transl_func, notify_progress)

    if stdout:
        _print_dat(lang_dat_transl)
    else:
        lang_dat_transl.to_dat(target_dat_path, fmt="HDMain")


def translate_mod(folder_path, transl_func, rewrite=False, notify_progress=False):

    cfg_path = folder_path / "CFG"
    rus_path = cfg_path / "Rus" / "Lang.dat"
    eng_path = cfg_path / "Eng" / "Lang.dat"

    if eng_path.exists():
        if rewrite:
            warnings.warn(
                f"English dat file found. File will be backed up and replaced. Path: {eng_path}"
            )

            _backup_file(eng_path)
        else:
            warnings.warn(f"English dat file found. Skipping. Path: {eng_path}")
            return

    if rus_path.exists():
        transl_dat_file(
            rus_path, eng_path, transl_func, notify_progress=notify_progress
        )

    module_info_path = folder_path / "ModuleInfo.txt"

    if module_info_path.exists():
        _backup_file(module_info_path)
        _transl_module_info(module_info_path, transl_func)
    else:
        raise Exception("Module Info not found. It's not a valid mod folder")


def _transl_dat_obj(lang_dat, transl_func, notify_progress):

    lang_dict = lang_dat.to_dict()
    count = utils.count_dict_scalars(lang_dict)
    pbar = None
    if notify_progress:
        pbar = tqdm(total=count)

        def _tqdm_wrapper(x):
            pbar.update(1)
            return transl_func(x)

        transl_func = _tqdm_wrapper

    try:
        lang_dict_transl = utils.apply_on_dict_scalars(lang_dict, transl_func)
    finally:
        if pbar is not None:
            pbar.__exit__()
    return rangers.dat.DAT.from_dict(lang_dict_transl)


def _transl_module_info(module_info_path, transl_func):
    module_info = _read_module_info(module_info_path)
    location = module_info_path.parent.parent.name
    module_info_transl = _transl_module_info_file(module_info, location, transl_func)

    module_info_lines = [f"{k}={v}" for k, v in module_info_transl]
    module_info_text = "\r\n".join(module_info_lines) + "\r\n"
    with open(module_info_path, "w") as f:
        f.writelines(module_info_text)


def _transl_module_info_file(module_info, location, transl_func, rewrite=False):
    for key, value in module_info:
        if key == "Languages" and "Eng" in value:
            if rewrite:
                warnings.warn(
                    "English translation alredy present in module info. All translated text will be skipped over and retranslated"
                )
            else:
                return module_info

    module_info_transl = []
    add_eng = []
    for key, value in module_info:
        if key.endswith("Eng"):
            print("ignoring", key)
            # removing previous translation
            continue
        if key == "Languages" and "Eng" not in value:
            value = value + ",Eng"
        elif key in ["SmallDescription", "FullDescription"]:
            value_eng = transl_func(value)
            add_eng.append([key + "Eng", value_eng])
        elif key == "Section":
            add_eng.append([key + "Eng", location])

        module_info_transl.append([key, value])

    module_info_transl.extend(add_eng)
    return module_info_transl


def _read_module_info(module_info_path):

    module_info = []
    with open(module_info_path, "rb") as f:
        content_bytes = f.read()
    detected = chardet.detect(content_bytes)
    encoding = detected["encoding"]
    confidence = detected["confidence"]
    mod_name = f"{module_info_path.parent.parent.name}-{module_info_path.parent.name}"
    # print(f"{mod_name}: detected as {encoding}. with confidence {confidence}")
    content_text = content_bytes.decode(encoding)

    with io.StringIO(content_text) as reader:
        lines = reader.readlines()
        module_info = []
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            pieces = line.split("=")
            if len(pieces) == 2:
                module_info.append(pieces)
            elif len(pieces) == 1:
                module_info.append([pieces[0], ""])
            else:
                value = "=".join(pieces[1:])
                module_info.append([pieces[0], value])
    return module_info


def _print_dat(dat):
    dat_dict = dat.to_dict()
    pretty = json.dumps(dat_dict, indent=4, ensure_ascii=False)
    print(pretty)


def _backup_file(filepath):
    filepath = pathlib.Path(filepath)

    fs_timestamp = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")

    bckp_suffix = f"{fs_timestamp}.bckp"
    backup_path = f"{str(filepath)}.{bckp_suffix}"
    shutil.copy(filepath, backup_path)
