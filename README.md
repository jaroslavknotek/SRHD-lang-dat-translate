Space Rangers HD: War Apart - Translate/transliterate mods from RUS to ENG
---

This CLI application transliterates/translates mods of Space Rangers.

**NOTE:** 
Translation: Космические рейнджеры -> Space Rangers

Transliteration: Космические рейнджеры -> Kosmicheskiye reyndzhery. It's fast and free way how to understand at least something (if you know any slavic language). 

**WARNING**: Translation uses [Deepl API](https://www.deepl.com/pro-api). To use it, you need an account. Also, if you want translate all currently available mods, then consider getting a PRO since there is more than 1 mil characters (Free has a limit of .5 mil).

# Requirements

- Deepl account, set the following environment properties
```
DEEPL_URI="https://api.deepl.com/v2/translate"
DEEPL_API_KEY=57XXXXX-76d0-5c1c-YYYY-CCCCCC
```
NOTE: `DEEPL_URI` is different for free accounts.
- Python 3.10

# Running

Clone repository and locate yourself in the root. Then run:

```
python -m virtualenv .venv
. ./.venv/bin/activate

pip install -r requirements.txt
cd python
```

Run help to see if it works `python cli.py --help`. You should see
```
usage: cli.py [-h] {show,transl_dat,transl_mod,transl_all_mods} ...

Translates or transliterates Lang.dat files of Spacer Rangers 2/HD game. 
Default behavior is transliteration as it doesn't require access to DeepL.com 
api. If you want to translate. Read README.md to find out what needs to be 
done.

positional arguments:
  {show,transl_dat,transl_mod,transl_all_mods}
                        Available
    show                Reads Lang.dat and prints it as json to stdout
    transl_mod          Translates ModuleInfo.txt and CFG/Rus/Lang.Dat in a mod folder
    transl_all_mods     Translates all mods in Space Ranger/Mods folder

options:
  -h, --help            show this help message and exit
```

## Example

**Show** content of one mod. Assuming Space Rangers is installed at `<SpaceRangers>`
```
python cli.py show <SpaceRangers>/Mods/Evolution/EvoRepairBox/CFG/Rus/Lang.dat 
```
It will print out the content as json. The following example result is just a sample for brewity.
```
{
...
    "UselessItems":{
    ...
        "BrokenWeapon_18": {
            "Cost": "Small",
            "Name": "Испорченный Лирекрон",
            "Owner": "None",
            "Size": "15",
            "Text": [
                "Больше не способен поражает цель ракетами с электромагнитной боеголовкой.",
                "<color=254,0,0>(ремонту не подлежит)<color>"
            ]
        }
    }
}
```

**Translate DAT file** using

```
python cli.py transl_dat --translate <SpaceRangers>/Mods/Evolution/EvoRepairBox/CFG/Rus/Lang.dat 
```

It will create a translated file `<SpaceRangers>/Mods/Evolution/EvoRepairBox/CFG/Rus/Lang.dat.transl`. If you want to use it. Don't forget to rename it.

**NOTE**: Notice the `--translate` parameter. Without it it will perform transliteration.

**Transliterate ONE mod** using

```
python cli.py transl_all_mods <SpaceRangers>/Mods/Evolution/EvoRepairBox
```

This will create `CFG/Eng/Lang.Dat` file with translation/transliteration and it will update `ModuleInfo.txt`.

**NOTE**: It doesn't have `--translate` parameter so the result will be transliterated **NOT Translated**

**Translate all mods**:
```
python cli.py transl_all_mods --translate <SpaceRangers>/Mods
```

Does the same as `transl_all_mods` but for all mods in Mods directory.


# Thanks To

Thanks belongs to:
- [KIaxon] (https://github.com/KIaxons) - for support
- [Ranger Tools](https://github.com/denballakh/ranger-tools) contributors. The library was used to read DAT file.
- [Cyrtranslit](https://github.com/opendatakosovo/cyrillic-transliteration) library
- [Community (discord)](https://discord.com/channels/674954439748222996/906697157346742323)

# Caveats

- Translation isn't perfect. Lang.Dat files contains text and some code. On the top of that, the text itself contains markup (e.g. `<color ...>XXX<color>`). The translator can handle this in most of the cases so I didn't event attempted to parse that.

- Some file can't be translated. The following files can't be read by the application:
  - Tweaks/KlaxonsStationsBG
  - ShusRangers/ShuSmugglers
  - ShusRangers/ShuDomiksBoss
  - Evolution/EvoBalance

# Mods that worked

The following mods were processed with this application (In total, it was 1,300,861 characters)
```
Evolution-EvoArmada
Evolution-EvoBG
Evolution-EvoFairTrade
Evolution-EvoFemRangers
Evolution-EvoGkvan
Evolution-EvoJamming
Evolution-EvoMabokit
Evolution-EvoMC
Evolution-EvoMM
Evolution-EvoMMUnique
Evolution-EvoMusic
Evolution-EvoOldBeacon
Evolution-EvoSB
Evolution-EvoTrancNPC
Expansion-ExpAcryn
Expansion-ExpArtsPlus
Expansion-ExpAutoSearch
Expansion-ExpCaravan
Expansion-ExpCB
Expansion-ExpGuns
Expansion-ExpHullsBases
Expansion-ExpProgramsNPC
Expansion-ExpRC
Expansion-ExpRepair
Expansion-ExpTraitors
OtherMods-Assistant
OtherMods-SR1ABMaps
OtherMods-SR1BG
OtherMods-SR1DoubleStar
OtherMods-SR1Epidemy
OtherMods-SR1Equipment
OtherMods-SR1Gaals&Pirates
OtherMods-SR1GovernmentQuests
OtherMods-SR1Malocs&Traders
OtherMods-SR1PelengZond
OtherMods-SR1RedSkull
OtherMods-SR1TextQuests
PlanetaryBattles-PBFirstPerson
PlanetaryBattles-PBHelpFromAbove
PlanetaryBattles-PBHomingMissiles
PlanetaryBattles-PBMyDesigns
PlanetaryBattles-PBNewColorBlack
PlanetaryBattles-PBNewColorBlue
PlanetaryBattles-PBNewColorCyan
PlanetaryBattles-PBNewColorDomBlue
PlanetaryBattles-PBNewColorDomGreen
PlanetaryBattles-PBNewColorDomRed
PlanetaryBattles-PBNewColorMix
PlanetaryBattles-PBNewColorPink
PlanetaryBattles-PBNewColorSov
PlanetaryBattles-PBNewColorViolet
PlanetaryBattles-PBNewColorWhite
PlanetaryBattles-PBNewSky
PlanetaryBattles-PBRobotsAutoBoom
PlanetaryBattles-PBSR2Balance
PlanetaryBattles-PBUniqueTemplates
Revolution-RevABMaps
Revolution-RevAcryn
Revolution-RevCaravan
Revolution-RevColonization
Revolution-RevDiplomat
Revolution-RevDominatorSpy
Revolution-RevElection
Revolution-RevJediQuest
Revolution-RevRangersArts
Revolution-RevScientist
Revolution-RevTerrorist
Revolution-RevTextQuests
Revolution-RevWarriorsAttack
Revolution-RevWarriorsVsPirates
ShusRangers-ShuBounty
ShusRangers-ShuDomiks
ShusRangers-ShuDomiksKamikaze
ShusRangers-ShuDomiksPlus
ShusRangers-ShuDomiksWin
ShusRangers-ShuEmitter
ShusRangers-ShuHomeland
ShusRangers-ShuHulls
ShusRangers-ShuKlissan
ShusRangers-ShuMercs
ShusRangers-ShuMiniBoss
ShusRangers-ShuMusic
ShusRangers-ShuNukes
ShusRangers-ShuPirates
ShusRangers-ShuQuest
ShusRangers-ShuRangersAcryns
ShusRangers-ShuRebellion
ShusRangers-ShuRG
ShusRangers-ShuSas
ShusRangers-ShuWarriors
Tweaks-BlockDShipQ
Tweaks-BlockDSystemQ
Tweaks-BlockKillShipQ
Tweaks-BlockMailQ
Tweaks-BlockSOTE
Tweaks-BlockTextQ
Tweaks-CheatTitleOff
Tweaks-DevKit
Tweaks-EndlessGame
Tweaks-GalamapBGChange
Tweaks-KlaxonsBG
Tweaks-KlaxonsCoalitionBG
Tweaks-LeoDomikShipsUpdate15
Tweaks-LeoDomikShipsUpdate30
Tweaks-OuterMusic
Tweaks-SR2ArcadeBG
Tweaks-SR2Balance
Tweaks-SR2GameOverBG
Tweaks-SR2IntroBG
Tweaks-SR2IntroMovie
Tweaks-SR2LoadingScreen
Tweaks-SR2MusicList
Tweaks-SR2RebootBalance
Tweaks-SR2Reboot
Tweaks-UtilityFunctionsPack
```
