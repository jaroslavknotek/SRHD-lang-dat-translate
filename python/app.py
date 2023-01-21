import warnings
import io
from datetime import datetime
import json
import language
import pathlib
from tqdm.auto import tqdm
import rangers.dat
import argparse
import shutil
import chardet
import traceback
import multiprocessing as mp

class TranslatorOptimizer():
    def __init__(self):
        self.cache = {}

    def __call__(self, input_text):
        translit = language.translit(input_text)
        if translit == input_text:
            # there is nothing russian to translate
            return input_text

        elif input_text in self.cache:
            return self.cache[input_text]
        
        else:
            translated = language.translate(input_text)
            self.cache[input_text] = translated
            return translated

def _get_transl_func(args):
    if args.translate:
        return TranslatorOptimizer()
    else:
        return language.translit

def _add_transl_argument(parser):

    parser.add_argument(
        '--translate',
        help = "Uses translation instead of translition. Requires DeepL account",
        action='store_true')

def _get_args():
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(help='Subcommands')

    parser_show = subparsers.add_parser("show")
    parser_show.set_defaults(func=command_show)
    parser_show.add_argument('file')
   
    parser_transl = subparsers.add_parser("transl_dat")
    _add_transl_argument(parser_transl)
    parser_transl.add_argument('file')
    parser_transl.add_argument(
        '--stdout',
        help='Prints result to stdout, not to a file',
        action='store_true')

    parser_transl.set_defaults(func=command_transl_dat)
    
    parser_transl_mod = subparsers.add_parser("transl_mod")
    _add_transl_argument(parser_transl_mod)
    parser_transl_mod.add_argument('folder')
    parser_transl_mod.set_defaults(func=command_transl_mod)

    parser_transl_all_mods = subparsers.add_parser("transl_all_mods")

    _add_transl_argument(parser_transl_all_mods)
    parser_transl_all_mods.add_argument('folder')
    parser_transl_all_mods.set_defaults(func=command_transl_all_mods)
    return parser.parse_args()

def command_show(args):
    file_path = pathlib.Path( args.file)
    
    dat = rangers.dat.DAT.from_dat(file_path)
    _print_dat(dat)

def _print_dat(dat):
    dat_dict = dat.to_dict()
    pretty = json.dumps(dat_dict,indent=4,ensure_ascii=False)
    print(pretty)



def _transl_dat_dict(lang_dict,transl_func,pbar):

    items = list(lang_dict.items())
    for k,v in items:
        if isinstance(v , dict):
            _transl_dat_dict(v,transl_func,pbar)
        elif isinstance(v, list):
            # BUG: if the item in v is dict then it won't get translated
            try:
                v_transl = [transl_func(item) for item in v]
            except:
                warnings.warn("Can't translate list or dict in a list")
                v_transl = v

            lang_dict[k] = v_transl
            if pbar is not None:
                pbar.update(1)
        elif v is not None:
            v_transl = transl_func(v)
            lang_dict[k] = v_transl
            if pbar is not None:
                pbar.update(1)


def _count_dict(d):
    return sum([_count_dict(v) if isinstance(v, dict) else 1 for v in d.values()])

def _transl_dat(
    source_dat_path,
    target_dat_path, 
    transl_func,
    stdout = False,
    notify_progress = False):

    lang_dat = rangers.dat.DAT.from_dat(source_dat_path)
    lang_dict = lang_dat.to_dict()
    count = _count_dict(lang_dict)
    if notify_progress:
        with tqdm(total = count) as pbar:
            _transl_dat_dict(lang_dict,transl_func,pbar)
    else:
            _transl_dat_dict(lang_dict,transl_func,None)
    dat_obj = rangers.dat.DAT.from_dict(lang_dict)
    # save as a file
    if stdout:
        _print_dat(dat_obj)    
    else:
        dat_obj.to_dat(target_dat_path,fmt='HDMain')



def command_transl_dat(args):    
    transl_func = _get_transl_func(args)
    dat_file_path= pathlib.Path(args.file)
    dat_file_path_out = pathlib.Path(str(dat_file_path)+".transl")
    _transl_dat(
        dat_file_path,
        dat_file_path_out,
        transl_func,
        stdout = args.stdout,
        notify_progress=True)

    

def backup_file(filepath):
    filepath = pathlib.Path(filepath)
    
    fs_timestamp = datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')

    bckp_suffix = f"{fs_timestamp}.bckp"
    backup_path = f"{str(filepath)}.{bckp_suffix}"
    shutil.copy(filepath,backup_path)

def _process_one_mod(params):
    mod_folder, transl_func = params
    mod_name = f"{mod_folder.parent.name}/{mod_folder.name}"
    # print("Processing: ", mod_name)
    try:
        _translate_mod(mod_folder,transl_func)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"ERROR while processing {mod_name}:",e, tb)

def command_transl_all_mods(args):
    folder_path = pathlib.Path(args.folder)
    
    folders = [x for x in folder_path.glob("*/*") if x.is_dir()]
    params = [(x,_get_transl_func(args)) for x in folders] 
    total = len(params)
    with mp.Pool() as pool:
        list(tqdm(pool.imap(_process_one_mod, params),total=total))
        

def _translate_mod(
    folder_path,
    transl_func,
    rewrite=False, 
    notify_progress = False):

    cfg_path = folder_path/"CFG"
    rus_path = cfg_path/"Rus"/"Lang.dat"
    eng_path = cfg_path/"Eng"/"Lang.dat"

    if eng_path.exists():
        if rewrite:
            warnings.warn(
                f"English dat file found. File will be backed up and replaced. Path: {eng_path}"
            )

            backup_file(eng_path)
        else:
            warnings.warn(
                f"English dat file found. Skipping. Path: {eng_path}"
            )
            return

    if rus_path.exists():
        _transl_dat(
            rus_path,
            eng_path,
            transl_func,
            notify_progress = notify_progress)

    module_info_path = folder_path/"ModuleInfo.txt"

    if module_info_path.exists():
        backup_file(module_info_path)
        transl_module_info(module_info_path,transl_func)
    else:
        raise Exception("ModuleInfo.txt not found. It's not a valid mod folder")


def command_transl_mod(args):
    transl_func = _get_transl_func(args)
    folder_path = pathlib.Path(args.folder)
    
    _translate_mod(folder_path,transl_func,notify_progress=True)


def _read_module_info(module_info_path):

    module_info = []
    with open(module_info_path, 'rb') as f:
        content_bytes = f.read()
    detected = chardet.detect(content_bytes)
    encoding = detected['encoding']
    confidence = detected['confidence']
    mod_name = f"{module_info_path.parent.parent.name}-{module_info_path.parent.name}"
    print(f"{mod_name}: detected as {encoding}. with confidence {confidence}") 
    content_text = content_bytes.decode(encoding)

    with io.StringIO(content_text) as reader:
        lines = reader.readlines()
        module_info = []
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            pieces = line.split('=')
            if len(pieces) == 2:
                module_info.append(pieces)
            elif len(pieces) == 1:
                module_info.append([pieces[0],""])
            else:
                value = '='.join(pieces[1:])
                module_info.append([pieces[0], value])
    return module_info

def _transl_module_info(module_info,location,transl_func,rewrite = False):
    for key,value in module_info:
        if key == "Languages" and "Eng" in value:
            if rewrite:
                warnings.warn("English translation alredy present in module info. All translated text will be skipped over and retranslated")
            else:
                return module_info
    
    module_info_transl = []
    add_eng = []
    for key,value in module_info:
        if key.endswith('Eng'):
            print("ignoring", key)
            #removing previous translation
            continue
        if key == "Languages" and "Eng" not in value:
            value = value+",Eng"
        elif key in ['SmallDescription','FullDescription']:
            value_eng = transl_func(value)
            add_eng.append([key+"Eng", value_eng])
        elif key == 'Section':
            add_eng.append([key+"Eng",location])
        
        module_info_transl.append([key,value])

    module_info_transl.extend(add_eng)
    return module_info_transl

def transl_module_info(module_info_path,transl_func):
    module_info = _read_module_info(module_info_path)
    location = module_info_path.parent.parent.name
    module_info_transl = _transl_module_info(module_info,location,transl_func)

    module_info_lines = [f'{k}={v}' for k,v in module_info_transl]
    module_info_text = '\r\n'.join(module_info_lines) + "\r\n"
    with open(module_info_path,'w') as f: 
        f.writelines(module_info_text)


if __name__ == "__main__":
    args = _get_args()
    args.func(args)
                        
