import app
import pytest
import rangers.dat


def test_translate_mod(tmp_path):

    mod_folder = tmp_path / "ModSection" / "TestMod"
    mod_folder.mkdir(parents=True, exist_ok=True)
    _add_mod_files(mod_folder)

    def apply_fn(x):
        return x.upper()

    app.translate_mod(mod_folder, apply_fn)

    # assert modsection = TestMod
    # assert cfg/eng exists
    mod_info_bckp = (mod_folder).glob("ModuleInfo*.bckp")
    assert 1 == len(list(mod_info_bckp)), "Module info should have backup"

    eng_lang_dat = mod_folder / "CFG" / "Eng" / "Lang.dat"
    assert eng_lang_dat.exists(), "eng lang dat should exist"

    mod_info_path = mod_folder / "ModuleInfo.txt"
    module_info = app._read_module_info(mod_info_path)
    sectionengs = [v for k, v in module_info if k == "SectionEng"]
    assert 1 == len(sectionengs), "Expected exactly one SectionEng"
    section_eng_val = sectionengs[0]
    assert section_eng_val == "ModSection"


def _get_module_info_text(
    name="TestMod",
    section="TestSection",
    small_description="Small Description",
    full_description_list=["line1", "line2"],
):

    full_desc_lines = [f"FullDescription={fl}" for fl in full_description_list]
    full_desc_par = "\r\n".join(full_desc_lines)
    return f"""Name={name}
Author=t1,t2
Conflict=
Dependence=
Priority=2
Section={section}
Languages=Rus
SmallDescription={small_description}
{full_desc_par}
"""


def _get_test_rus_lang_dict():
    return {"Scripts": {"a": "b"}, "Items": {"x": ["a", "b", "c"]}}


def _add_mod_files(mod_root):

    module_info_text = _get_module_info_text()
    module_info_path = mod_root / "ModuleInfo.txt"
    module_info_path.write_text(module_info_text, encoding="utf-8")

    cfg = mod_root / "CFG"
    rus = cfg / "Rus"
    rus.mkdir(parents=True)
    rus_lang_dat_path = rus / "Lang.dat"

    lang_dict = _get_test_rus_lang_dict()
    lang_dat = rangers.dat.DAT.from_dict(lang_dict)
    lang_dat.to_dat(rus_lang_dat_path, fmt="HDMain")
