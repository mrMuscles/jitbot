# This file loads the banners written in banners.py, checks them for mistakes when the bot starts
# and does the rolling for /roll
# To add or change a banner you only need to edit banners.py, nothing in here

import difflib
import inspect
import os
import random
import textwrap
import traceback

from utils import rChar, srChar, ssrChar, specialChar, secretChar, characterTitles
from daily_helper import dailyOnlyCharacters  # characters /daily gives away (daily_rewards.py) can't be on a banner

# Highest rarity first, /banner and /roll show them in this order
RARITY_ORDER = ["SSSR", "SSR", "SR", "R"]

# Which list in utils.py each rarity comes from (specialChar counts as SSR, it is only on a different banner)
RARITY_LISTS = {"SSSR": secretChar, "SSR": ssrChar + specialChar, "SR": srChar, "R": rChar}
CHARACTER_RARITY = {char: rarity for rarity, chars in RARITY_LISTS.items() for char in chars}

# The fields a banner block in banners.py can have
REQUIRED_FIELDS = ["name", "description", "contents"]
RATE_FIELDS = {"sssr_rate": "SSSR", "ssr_rate": "SSR", "sr_rate": "SR", "r_rate": "R"}
OPTIONAL_FIELDS = ["image", "color", "featured"]
ALL_FIELDS = REQUIRED_FIELDS + list(RATE_FIELDS) + OPTIONAL_FIELDS

DEFAULT_COLOR = 0x3f48cc                  # same blue as the other embeds
MAX_IMAGE_BYTES = 10 * 1024 * 1024        # biggest file a bot can upload to Discord
IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".gif", ".webp")
BOT_FOLDER = os.path.dirname(os.path.abspath(__file__))

_typedBanners = []  # every add_banner() block from banners.py, exactly as it was typed


def add_banner(**fields):
    """banners.py calls this once for every banner block. The block gets checked later in loadBanners()."""
    fields["_line"] = inspect.currentframe().f_back.f_lineno
    _typedBanners.append(fields)


def warn(text):
    text = f"[BANNER WARNING] {text}"
    try:
        print(text)
    except UnicodeEncodeError:  # some consoles can't print emojis or accents
        print(text.encode("ascii", "replace").decode())


# ============================================================================
# LOADING + CHECKING (runs once when the bot starts)
# ============================================================================

def loadBanners(shownCharacters):
    """Runs banners.py, checks every banner and returns the ones that work.
    shownCharacters = all_characters from main.py, secret characters only get used if they are turned on in there."""
    _typedBanners.clear()
    print("Loading banners from banners.py...")
    try:
        import banners  # noqa: F401  (running banners.py calls add_banner() for every block)
    except SyntaxError as error:
        warn(f"banners.py has a typing mistake on line {error.lineno}: {error.msg}")
        warn("No banners were loaded, so /roll and /banner won't work until it is fixed. "
             "Check that every field line ends with a comma and every piece of text has quotes on both sides.")
        return []
    except Exception as error:
        warn(f"banners.py stopped on line {lineInBannersFile(error)}: {explainError(error)}")
        warn("Only the banners above that line were loaded.")

    checked = []
    for typed in _typedBanners:
        banner = checkBanner(dict(typed), shownCharacters, checked)
        if banner:
            checked.append(banner)

    if checked:
        warnUnpulledCharacters(checked)
        print(f"Loaded {len(checked)} banner(s): " + ", ".join(banner["name"] for banner in checked))
    else:
        warn("No banners were loaded, so /roll and /banner won't work until banners.py is fixed.")
    return checked


def checkBanner(typed, shownCharacters, goodSoFar):
    """Checks 1 banner block. Prints a warning for every problem and returns None if the banner can't be used."""
    line = typed.pop("_line", "?")
    name = typed.get("name")
    if isinstance(name, str) and name.strip():
        where = f'Banner "{name.strip()}" (banners.py line {line})'
    else:
        where = f"The banner on banners.py line {line}"

    def skip(reason):
        warn(f"{where} was NOT loaded because {reason}")
        return None

    # fields that don't exist (usually a typo like "imgae")
    for field in typed:
        if field not in ALL_FIELDS:
            warn(f'{where}: "{field}" is not a banner field, so it was ignored.{closestMatch(field, ALL_FIELDS)}')

    missing = [field for field in REQUIRED_FIELDS if field not in typed]
    if missing:
        return skip("it is missing " + " and ".join(f'"{field}"' for field in missing) + ".")

    # name + description
    if not isinstance(name, str) or not name.strip():
        return skip('the name has to be text inside quotes, like name = "My Banner",')
    name = name.strip()
    if len(name) > 100:
        return skip("the name is longer than 100 letters, which is the most Discord allows.")
    if any(other["name"].lower() == name.lower() for other in goodSoFar):
        return skip("another banner above it already has this name. Every banner needs its own name.")
    description = typed["description"]
    if not isinstance(description, str) or not description.strip():
        return skip('the description has to be text inside quotes, like description = "A cool banner.",')

    # rates (how likely each rarity is)
    rates = {}
    for field, rarity in RATE_FIELDS.items():
        value = typed.get(field, 0)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            return skip(f"{field} has to be a number of 0 or more, with no quotes or % sign, like {field} = 5,")
        if value:
            rates[rarity] = value
    total = sum(rates.values())
    if abs(total - 100) > 0.001:
        return skip(f"the rates add up to {total:g}%, but they have to add up to exactly 100%.")

    # contents (who can be pulled), the rarity of each one comes from utils.py
    contents = typed["contents"]
    if isinstance(contents, str):
        contents = [contents]  # 1 name typed without the [ ]
    if not isinstance(contents, (list, tuple)):
        return skip('contents has to be a list of character names inside [ ], like contents = ["r_trey", "sr_trey"],')
    pools = {rarity: [] for rarity in RARITY_ORDER}
    inBanner = []
    dailyOnly = dailyOnlyCharacters()
    for typedName in contents:
        character = findCharacter(typedName)
        if character is None:
            warn(f"{where}: {characterProblem(typedName)}")
            continue
        if character in inBanner:
            warn(f'{where}: "{character}" is in contents more than once, it only counts once.')
            continue
        if character in dailyOnly:
            warn(f'{where}: "{character}" is a /daily reward (daily_rewards.py), so it can\'t be pulled from a banner and was left out.')
            continue
        if character in secretChar and character not in shownCharacters:
            warn(f'{where}: "{character}" is a secret character that is turned off, so it was left out. '
                 "(The README says how to turn it on.)")
            continue
        inBanner.append(character)
        pools[CHARACTER_RARITY[character]].append(character)

    rateField = {rarity: field for field, rarity in RATE_FIELDS.items()}
    for rarity in RARITY_ORDER:
        if rates.get(rarity) and not pools[rarity]:
            return skip(f"it gives {rarity} a {rates[rarity]:g}% chance, but none of its contents are {rarity} characters. "
                        f"Add some {rarity} characters to contents, or set {rateField[rarity]} = 0 and fix the other rates.")
        if pools[rarity] and not rates.get(rarity):
            warn(f"{where}: it has {rarity} characters but {rateField[rarity]} is 0 (or missing), so they can never be pulled.")

    # featured (only for show, marked with a star in /banner)
    featuredTyped = typed.get("featured", [])
    if isinstance(featuredTyped, str):
        featuredTyped = [featuredTyped]
    if not isinstance(featuredTyped, (list, tuple)):
        warn(f'{where}: featured has to be a list inside [ ], like featured = ["ssr_trey"], so it was ignored.')
        featuredTyped = []
    featured = []
    for typedName in featuredTyped:
        character = findCharacter(typedName)
        if character not in inBanner:
            warn(f'{where}: featured character "{typedName}" is not in this banner\'s contents, so it was not marked as featured.')
        elif character not in featured:
            featured.append(character)

    imageUrl, imageFile, imageName = checkImage(typed.get("image"), where)

    return {
        "name": name,
        "description": description.strip(),
        "rates": rates,            # {"SSR": 1, "SR": 29, "R": 70}, only rarities above 0%
        "pools": pools,            # {"SSSR": [], "SSR": [...], "SR": [...], "R": [...]}
        "featured": featured,
        "color": checkColor(typed.get("color"), where),
        "image_url": imageUrl,     # web link, goes straight into the embed
        "image_file": imageFile,   # file on this computer, gets attached to the message
        "image_name": imageName,   # name the attached file gets in Discord
    }


def checkImage(image, where):
    """Returns (web link, file path, attachment name). Only 1 of the first 2 is filled in, or neither if there is no usable image."""
    if image is None or image == "":
        return None, None, None
    if not isinstance(image, str):
        warn(f'{where}: image has to be text inside quotes, so the banner has no picture.')
        return None, None, None
    image = image.strip()
    if image.lower().startswith(("http://", "https://")):
        return image, None, None
    fullPath = image if os.path.isabs(image) else os.path.join(BOT_FOLDER, image)
    extension = os.path.splitext(image)[1].lower()
    if not os.path.isfile(fullPath):
        warn(f'{where}: the image file "{image}" doesn\'t exist, so the banner has no picture. '
             'Check the spelling, and that the file is inside the bot folder (like "graphics/my_banner.gif").')
    elif extension not in IMAGE_TYPES:
        warn(f'{where}: "{image}" isn\'t a picture Discord can show (use .png, .jpg, .gif or .webp), so the banner has no picture.')
    elif os.path.getsize(fullPath) > MAX_IMAGE_BYTES:
        warn(f'{where}: "{image}" is bigger than 10 MB, which is too big for Discord, so the banner has no picture.')
    else:
        return None, fullPath, "banner_image" + extension
    return None, None, None


def checkColor(color, where):
    """Turns "#3f48cc" (or 0x3f48cc) into the number Discord wants. Anything else gets the normal blue."""
    if color is None or color == "":
        return DEFAULT_COLOR
    if isinstance(color, int) and not isinstance(color, bool) and 0 <= color <= 0xFFFFFF:
        return color
    if isinstance(color, str):
        text = color.strip().lstrip("#")
        if len(text) == 6:
            try:
                return int(text, 16)
            except ValueError:
                pass
    warn(f'{where}: color "{color}" isn\'t a color code like "#3f48cc", so the normal blue was used.')
    return DEFAULT_COLOR


def warnUnpulledCharacters(banners):
    """Characters that aren't on any banner can't be pulled at all (secret characters and /daily rewards are left out on purpose)."""
    pullable = set()
    for banner in banners:
        for rarity in banner["rates"]:
            pullable.update(banner["pools"][rarity])
    dailyOnly = dailyOnlyCharacters()
    unpulled = [character for character in rChar + srChar + ssrChar + specialChar if character not in pullable and character not in dailyOnly]
    if unpulled:
        warn("These characters are not on any banner, so nobody can pull them right now: "
             + ", ".join(f'"{character}"' for character in unpulled)
             + ". If they should be pullable, add them to a banner's contents in banners.py.")


# ============================================================================
# SMALL HELPERS
# ============================================================================

def findCharacter(typedName):
    """The utils.py name of a character typed in banners.py (capital letters don't matter, the full title works too)."""
    if not isinstance(typedName, str):
        return None
    wanted = typedName.strip().lower()
    for character in CHARACTER_RARITY:
        if character.lower() == wanted or characterTitles.get(character, "").lower() == wanted:
            return character
    return None


def characterProblem(typedName):
    """Plain English reason why a name in contents didn't match a character."""
    if not isinstance(typedName, str):
        return f"{typedName!r} in contents isn't text inside quotes, so it was left out."
    text = f'"{typedName}" is not a character in utils.py, so it was left out.'
    # 2 names stuck together like "r_treyr_noah" means a comma is missing between them
    for first in CHARACTER_RARITY:
        rest = typedName[len(first):]
        if typedName.startswith(first) and rest in CHARACTER_RARITY:
            return text + f' It looks like a comma is missing between "{first}" and "{rest}".'
    return text + closestMatch(typedName, list(CHARACTER_RARITY))


def closestMatch(typed, options):
    guess = difflib.get_close_matches(str(typed).lower(), options, n=1)
    return f' Did you mean "{guess[0]}"?' if guess else ""


def lineInBannersFile(error):
    for frame in reversed(traceback.extract_tb(error.__traceback__)):
        if os.path.basename(frame.filename) == "banners.py":
            return frame.lineno
    return "?"


def explainError(error):
    if isinstance(error, NameError) and getattr(error, "name", None):
        return (f'Python doesn\'t know the word {error.name}. '
                f'If it is meant to be text, put quotes around it like "{error.name}".')
    if isinstance(error, TypeError):
        return ("every field has to be written like  name = \"value\",  and each field can only be used once per banner. "
                f"(Python said: {error})")
    return f"{type(error).__name__}: {error}"


# ============================================================================
# USED BY main.py
# ============================================================================

def findBanner(banners, typedName):
    """The banner with this name (capital letters and spaces at the ends don't matter), or None."""
    wanted = (typedName or "").strip().lower()
    for banner in banners:
        if banner["name"].lower() == wanted:
            return banner
    return None


def pickCharacter(banner):
    """1 roll: pick a rarity using the banner's rates, then a random character of that rarity (all equal chance)."""
    rarities = list(banner["rates"])
    rarity = random.choices(rarities, weights=[banner["rates"][r] for r in rarities])[0]
    return random.choice(banner["pools"][rarity])


def getRarity(character):
    """"SSSR" / "SSR" / "SR" / "R" from the lists in utils.py, or None if the character doesn't exist."""
    return CHARACTER_RARITY.get(character)


def shortDescription(text, length=100):
    return textwrap.shorten(text, width=length, placeholder="...")
