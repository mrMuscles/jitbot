# This file loads the items from the "items" collection in MongoDB, checks them for mistakes when the bot starts,
# and does what each kind of item effect does in battle (battle.py calls the functions at the bottom)
# To add or change an item you only need MongoDB Compass (the README's "Items" part explains how), nothing in here
# A brand-new KIND of effect needs code in here (EFFECTS, effectText and the battle part) and maybe a hook in battle.py

import math
import os
import random

from pymongo.errors import PyMongoError

from banner_helper import closestMatch, BOT_FOLDER, IMAGE_TYPES, MAX_IMAGE_BYTES
from utils import enemyAttributes


def isNumber(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def isWholeNumber(value):
    # 35 and 35.0 both count (Compass sometimes saves whole numbers as Double)
    return isNumber(value) and float(value).is_integer()

def typeHint(value):
    # numbers typed in Compass with quotes around them get saved as text, which is an easy mistake to make
    return " It is saved as text (String), change its type to Int32 or Double in Compass." if isinstance(value, str) else ""


# The fields an item document in MongoDB can have
REQUIRED_FIELDS = ["name", "description", "effect"]
OPTIONAL_FIELDS = ["price",                         # needed for every item that is in the store
                   "emoji", "image",
                   "in_store",                      # false = it can't be bought (like Knife Noir)
                   "drop_from", "drop_chance",      # a /battle enemy that can drop it when you win, and the % chance
                   "skip_chance", "skip_text",      # a downside any item can have (Protein Brick)
                   "skip_turns",                    # a downside: the team skips its first few turns (Huawei Laptop)
                   "hide_hp"]                       # a downside: nobody's HP can be seen during battles (Noah's Larpometer)

# The /battle enemies an item can drop from ("Ruffian1" and "Ruffian2" are both "Ruffian")
ENEMY_NAMES = sorted({enemy.rstrip("0123456789") for enemy in enemyAttributes})

# The stats an item can change, the short names (like atk or def) work too
STAT_FIELDS = {"hp": "hp", "attack": "attack", "atk": "attack", "defense": "defense", "defence": "defense", "def": "defense",
               "evasion": "evasion", "eva": "evasion", "accuracy": "accuracy", "acc": "accuracy"}
STAT_ORDER = ["hp", "attack", "defense", "evasion", "accuracy"]

# The other numbers effects use: (what it has to be, the check, an example)
NUMBER_RULES = {
    "turns": ("a whole number above 0", lambda value: isWholeNumber(value) and value >= 1, '"turns": 3'),
    "chance": ("a number above 0 and up to 100", lambda value: isNumber(value) and 0 < value <= 100, '"chance": 2'),
    "multiplier": ("a number above 0", lambda value: isNumber(value) and value > 0, '"multiplier": 1.5'),
    "every": ("a whole number above 0", lambda value: isWholeNumber(value) and value >= 1, '"every": 5'),
    "percent": ("a number above 0", lambda value: isNumber(value) and value > 0, '"percent": 5'),
}
WHOLE_NUMBERS = ["turns", "every"]

# Every kind of effect the bot knows: does it use the stat numbers, and which other numbers it needs
EFFECTS = {
    "stat_percent": {"stats": True, "numbers": []},
    "stat_flat": {"stats": True, "numbers": []},
    "temp_stat_flat": {"stats": True, "numbers": ["turns"]},
    "crit_chance": {"stats": False, "numbers": ["chance", "multiplier"]},
    "periodic_heal": {"stats": False, "numbers": ["every", "percent"]},
    "basic_attack_bleed": {"stats": False, "numbers": ["percent", "turns"]},
    "grist_bonus": {"stats": False, "numbers": ["percent"]},                # more Grist for winning (Noah's Larpometer)
    "skip_enemy_turns": {"stats": False, "numbers": ["turns"]},             # the enemies skip their first turns (Samsung Camera)
    "delayed_stat_percent": {"stats": True, "numbers": ["turns"]},          # like stat_percent, but only after the first turns (Huawei Laptop)
}
STAT_EFFECTS = [effect for effect, rules in EFFECTS.items() if rules["stats"]]
PERCENT_EFFECTS = ["stat_percent", "delayed_stat_percent"]  # their hp and attack numbers are a %, not a flat amount

ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS + list(STAT_FIELDS) + list(NUMBER_RULES)

# /item equip uses these words to empty the item slot, so no item can be called one of them
UNEQUIP_WORDS = ["unequip", "nothing", "none", "empty"]

SHOP_IMAGE = os.path.join(BOT_FOLDER, "graphics", "shop.png")  # the picture in /item store
MAX_STORE_ITEMS = 23  # Discord allows 25 buttons on 1 message, and 2 of them are the Buy a Roll and Buy 10 Rolls buttons

_items = []  # the items that passed the checks (main.py and battle.py both use this list)


# ============================================================================
# STARTING ITEMS
# ============================================================================
# Only used when the MongoDB items collection is completely empty (like on a brand-new database):
# the bot copies these into it once. After that the items in MongoDB are the real ones and editing this list does nothing.
STARTING_ITEMS = [
    {"name": "Agent Knife", "price": 35,
     "description": "The Dersite solo agent's trusty knife. Light, sharp, and easy to dodge with.",
     "emoji": "🔪", "image": "graphics/items/agentknife.png",
     "effect": "stat_percent", "attack": 5, "evasion": 10},
    {"name": "Dersite Enforcer Hat", "price": 50,
     "description": "Large cap of the Dersite Grunt. Gives off a menacing aura.",
     "emoji": "🧢", "image": "graphics/items/grunthat.png",
     "effect": "stat_percent", "defense": 5},
    {"name": "Dersite Longman's Spear", "price": 50,
     "description": "A long Dersite spear that helps your team line up their hits.",
     "emoji": "🔱", "image": "graphics/items/spearmanspear.png",
     "effect": "stat_percent", "accuracy": 15},
    {"name": "Lucky Coin", "price": 30,
     "description": "How did you get your hands on this?",
     "emoji": "🪙", "image": "graphics/items/luckycoin.png",
     "effect": "crit_chance", "chance": 2, "multiplier": 1.5},
    {"name": "Perfectly Generic Object", "price": 5,
     "description": "It's perfectly generic.",
     "emoji": "📦", "image": "graphics/items/perfectlygenericobject.png",
     "effect": "temp_stat_flat", "hp": 1, "attack": 1, "defense": 1, "evasion": 1, "accuracy": 1, "turns": 3},
    {"name": "Bag of Purina Treats", "price": 45,
     "description": "Dog treats to brighten your day and make you yip with joy.",
     "emoji": "🦴", "image": "graphics/items/treats.png",
     "effect": "periodic_heal", "every": 5, "percent": 5},
    {"name": "Dersite Knuckledusters", "price": 20,
     "description": "Crack skulls with these Dersite Enforcer's knuckledusters!.",
     "emoji": "👊", "image": "graphics/items/dersiteknuckleduster.png",
     "effect": "stat_percent", "accuracy": 5},
    {"name": "Protein Brick", "price": 75,
     "description": "Its structure, while prismatic, is completely unknowable.",
     "emoji": "🧱", "image": "graphics/items/proteinbrick.png",
     "effect": "stat_percent", "attack": 50, "skip_chance": 50,
     "skip_text": "It was sour, everyone nurses their horrified stomachs this turn."},
    {"name": "Knife Noir", "in_store": False, "drop_from": "Jack Noir", "drop_chance": 10,
     "description": "Jack Noir's own knife, taken from him after a hard fight. Afflict bleed via stabbing during every basic attack.",
     "emoji": "🗡️", "image": "graphics/items/knifenoir.png",
     "effect": "basic_attack_bleed", "percent": 3, "turns": 1},
    {"name": "Noah's Larpometer", "price": 65,
     "description": "Noah's very own Larp Meter. It's so busy measuring everyone's performativeness that nobody can read their HP anymore.",
     "emoji": "📟", "image": "graphics/items/noahslarpometer.png",
     "effect": "grist_bonus", "percent": 10, "hide_hp": True},
    {"name": "Samsung Camera", "price": 40,
     "description": "A point-and-shoot camera. The flash catches the enemies off guard before the fight even starts.",
     "emoji": "📷", "image": "graphics/items/camera.png",
     "effect": "skip_enemy_turns", "turns": 1},
    {"name": "Huawei Laptop", "price": 90,
     "description": "A Huawei laptop with Garry's Mod open. It takes forever to boot, but once it's running your team is unstoppable.",
     "emoji": "💻", "image": "graphics/items/huaweilaptop.png",
     "effect": "delayed_stat_percent", "attack": 25, "defense": 25, "accuracy": 25, "turns": 3,
     "skip_turns": 3, "skip_text": "The Huawei Laptop is still booting up, so your team waits and skips its turn."},
]


def say(text):
    try:
        print(text)
    except UnicodeEncodeError:  # some consoles can't print emojis or accents
        print(text.encode("ascii", "replace").decode())

def warn(text):
    say(f"[ITEM WARNING] {text}")


# ============================================================================
# LOADING + CHECKING (runs once when the bot starts)
# ============================================================================

def loadItems(collection):
    """Reads every item from the MongoDB items collection, checks them and returns the ones that work.
    A completely empty collection (a brand-new database) gets the STARTING_ITEMS first."""
    _items.clear()
    print("Loading items from MongoDB (the items collection)...")
    try:
        if collection.count_documents({}) == 0:
            collection.insert_many([dict(item) for item in STARTING_ITEMS])
            say(f"The items collection was empty, so the {len(STARTING_ITEMS)} starting items were added to it.")
        typedItems = list(collection.find().sort("_id", 1))  # oldest first, so new items go at the end of the store
    except PyMongoError as error:
        warn(f"Couldn't read the items from MongoDB, so /item store will be empty until the bot is restarted "
             f"with MongoDB running. ({error})")
        return _items

    for typed in typedItems:
        item = checkItem(typed)
        if item:
            _items.append(item)

    if _items:
        say(f"Loaded {len(_items)} item(s): " + ", ".join(item["name"] for item in _items))
        forSale = [item for item in _items if item["in_store"]]
        if len(forSale) > MAX_STORE_ITEMS:
            warn(f"There are {len(forSale)} items in the store, but /item store can only show {MAX_STORE_ITEMS} buttons. "
                 f"Only the {MAX_STORE_ITEMS} that were added first can be bought.")
    else:
        warn("No items were loaded, so /item store will be empty until the items collection in MongoDB is fixed.")
    return _items


def checkItem(typed):
    """Checks 1 item document. Prints a warning for every problem and returns None if the item can't be used."""
    itemId = typed.pop("_id", "?")
    name = typed.get("name")
    if isinstance(name, str) and name.strip():
        where = f'Item "{name.strip()}"'
    else:
        where = f"The item with _id {itemId} in the items collection"

    def skip(reason):
        warn(f"{where} was NOT loaded because {reason}")
        return None

    # fields that don't exist (usually a typo like "pirce")
    for field in typed:
        if field not in ALL_FIELDS:
            warn(f'{where}: "{field}" is not an item field, so it was ignored.{closestMatch(field, ALL_FIELDS)}')

    missing = [field for field in REQUIRED_FIELDS if field not in typed]
    if missing:
        return skip("it is missing " + " and ".join(f'"{field}"' for field in missing) + ".")

    # name, price, description
    if not isinstance(name, str) or not name.strip():
        return skip('the name has to be text, like "name": "Lucky Coin"')
    name = name.strip()
    if len(name) > 80:
        return skip("the name is longer than 80 letters, which is too long for a Discord button.")
    if name.lower() in UNEQUIP_WORDS:
        return skip(f'"{name}" is the word /item equip uses to empty the item slot. Give the item another name.')
    if findItem(_items, name):
        return skip("another item already has this name. Every item needs its own name.")
    inStore = typed.get("in_store", True)
    if not isinstance(inStore, bool):
        return skip('in_store has to be true or false (the Boolean type in Compass), like "in_store": false')
    price = typed.get("price")
    if inStore and price is None:
        return skip('it is missing "price". Items in the store need a price (add "in_store": false if it shouldn\'t be sold).')
    if inStore and (not isWholeNumber(price) or price < 1):
        return skip('the price has to be a whole number above 0, like "price": 30.' + typeHint(price))
    if not inStore and price is not None:
        warn(f"{where}: it isn't in the store (in_store is false), so its price is never used.")
    description = typed["description"]
    if not isinstance(description, str) or not description.strip():
        return skip('the description has to be text, like "description": "A shiny coin."')

    # which kind of effect
    effect = typed["effect"]
    if not isinstance(effect, str) or effect.strip().lower() not in EFFECTS:
        known = ", ".join(f'"{kind}"' for kind in EFFECTS)
        return skip(f'"{effect}" is not an effect the bot knows. The effects are: {known}.{closestMatch(effect, list(EFFECTS))} '
                    "A brand-new kind of effect needs code first (the README explains).")
    effect = effect.strip().lower()
    rules = EFFECTS[effect]

    # real fields that this kind of effect doesn't use (like chance on a stat_percent item)
    used = REQUIRED_FIELDS + OPTIONAL_FIELDS + rules["numbers"] + (list(STAT_FIELDS) if rules["stats"] else [])
    for field in typed:
        if field in ALL_FIELDS and field not in used:
            warn(f'{where}: the "{effect}" effect doesn\'t use "{field}", so it was ignored.')

    item = {"name": name, "price": int(price) if inStore else 0, "in_store": inStore, "description": description.strip(),
            "effect": effect, "stats": {}, "drop_from": None, "drop_chance": 0}

    # the stat numbers (stat effects only)
    if rules["stats"]:
        for field, value in typed.items():
            stat = STAT_FIELDS.get(field)
            if stat is None:
                continue
            if stat in item["stats"]:
                warn(f'{where}: {stat} is in this item twice, only the first one counts.')
            elif not isNumber(value) or value < 0:
                warn(f'{where}: {field} has to be a number of 0 or more, like "{field}": 5, so it was ignored.' + typeHint(value))
            elif value:
                item["stats"][stat] = value
        if not item["stats"]:
            return skip(f'the "{effect}" effect needs at least one stat number above 0, like "attack": 5')

    # the other numbers this kind of effect needs
    for field in rules["numbers"]:
        meaning, isOk, example = NUMBER_RULES[field]
        if field not in typed:
            return skip(f'the "{effect}" effect needs {field}, like {example}')
        if not isOk(typed[field]):
            return skip(f"{field} has to be {meaning}, like {example}." + typeHint(typed[field]))
        item[field] = int(typed[field]) if field in WHOLE_NUMBERS else typed[field]

    # dropping from an enemy when you win the battle (Knife Noir)
    dropFrom, dropChance = typed.get("drop_from"), typed.get("drop_chance")
    if dropFrom is not None or dropChance is not None:
        enemy = next((name for name in ENEMY_NAMES if isinstance(dropFrom, str) and name.lower() == dropFrom.strip().lower()), None)
        if enemy is None:
            enemies = ", ".join(f'"{name}"' for name in ENEMY_NAMES)
            warn(f"{where}: drop_from has to be one of the /battle enemies ({enemies}), so it doesn't drop from anything."
                 + closestMatch(dropFrom, [name.lower() for name in ENEMY_NAMES]))
        elif not isNumber(dropChance) or not 0 < dropChance <= 100:
            warn(f'{where}: drop_chance has to be a number above 0 and up to 100, like "drop_chance": 10, '
                 "so it doesn't drop from anything." + typeHint(dropChance))
        else:
            item["drop_from"], item["drop_chance"] = enemy, dropChance
    if not inStore and not item["drop_from"]:
        warn(f"{where}: it isn't in the store and doesn't drop from any enemy, so players can only get it if an admin gives it to them.")

    # the downside: a chance every turn that the whole team skips its turn (Protein Brick)
    skipChance = typed.get("skip_chance", 0)
    if not isNumber(skipChance) or not 0 <= skipChance < 100:
        return skip('skip_chance has to be a number of 0 or more and below 100, like "skip_chance": 50.' + typeHint(skipChance))
    item["skip_chance"] = skipChance
    # the downside: the whole team skips its first few turns of every battle (Huawei Laptop)
    skipTurns = typed.get("skip_turns", 0)
    if not isWholeNumber(skipTurns) or skipTurns < 0:
        return skip('skip_turns has to be a whole number of 0 or more, like "skip_turns": 3.' + typeHint(skipTurns))
    item["skip_turns"] = int(skipTurns)
    # the downside: nobody's HP can be seen during battles (Noah's Larpometer)
    hideHP = typed.get("hide_hp", False)
    if not isinstance(hideHP, bool):
        return skip('hide_hp has to be true or false (the Boolean type in Compass), like "hide_hp": true')
    item["hide_hp"] = hideHP
    skipText = typed.get("skip_text")
    if skipText is not None and not skipChance and not skipTurns:
        warn(f"{where}: skip_text only does something when the item has a skip_chance or skip_turns, so it was ignored.")
    elif skipText is not None and (not isinstance(skipText, str) or not skipText.strip()):
        warn(f'{where}: skip_text has to be text, like "skip_text": "Your team trips over.", so the normal text is used.')
        skipText = None
    item["skip_text"] = skipText.strip() if skipText else f"Your team fumbled the {name} and skips its turn!"

    emoji = typed.get("emoji") or ""
    if not isinstance(emoji, str):
        warn(f'{where}: emoji has to be text, like "emoji": "🪙", so it was left out.')
        emoji = ""
    item["emoji"] = emoji.strip()[:20]
    item["image_url"], item["image_file"], item["image_name"] = checkImage(typed.get("image"), where)
    item["effect_text"] = effectText(item)
    return item


def checkImage(image, where):
    """Returns (web link, file path, attachment name). Only 1 of the first 2 is filled in, or neither if there is no usable picture."""
    if image is None or image == "":
        return None, None, None
    if not isinstance(image, str):
        warn(f"{where}: image has to be text, so the item has no picture.")
        return None, None, None
    image = image.strip()
    if image.lower().startswith(("http://", "https://")):
        return image, None, None
    fullPath = image if os.path.isabs(image) else os.path.join(BOT_FOLDER, image)
    extension = os.path.splitext(image)[1].lower()
    if not os.path.isfile(fullPath):
        warn(f'{where}: the image file "{image}" doesn\'t exist, so the item has no picture. '
             'Check the spelling, and that the file is inside the bot folder (like "graphics/items/my_item.png").')
    elif extension not in IMAGE_TYPES:
        warn(f'{where}: "{image}" isn\'t a picture Discord can show (use .png, .jpg, .gif or .webp), so the item has no picture.')
    elif os.path.getsize(fullPath) > MAX_IMAGE_BYTES:
        warn(f'{where}: "{image}" is bigger than 10 MB, which is too big for Discord, so the item has no picture.')
    else:
        return None, fullPath, "item_image" + extension
    return None, None, None


# ============================================================================
# TEXT (what an item does, in plain English)
# ============================================================================

def effectText(item):
    """Shown in /item store, /item show, /item equip and the battle log."""
    text = mainEffectText(item)
    downsides = []
    if item.get("skip_turns"):
        turns = item["skip_turns"]
        downsides.append("your whole team skips its first turn of each battle" if turns == 1
                         else f"your whole team skips its first {turns} turns of each battle")
    if item.get("skip_chance"):
        downsides.append(f"every turn there's a {item['skip_chance']:g}% chance your whole team skips its turn")
    if item.get("hide_hp"):
        downsides.append("nobody's HP can be seen during battles")
    if downsides:
        text += ", but " + joinWords(downsides)
    return text


def statWords(item):
    """The stat bonuses of a stat effect item, like "+25% ATK, 25% less damage taken and +25% ACC"."""
    percent = item["effect"] in PERCENT_EFFECTS
    parts = []
    for stat in STAT_ORDER:
        amount = item["stats"].get(stat)
        if not amount:
            continue
        if stat == "hp":
            parts.append(f"+{amount:g}% max HP" if percent else f"+{amount:g} HP")
        elif stat == "attack":
            parts.append(f"+{amount:g}% ATK" if percent else f"+{amount:g} ATK")
        elif stat == "defense":
            parts.append(f"{amount:g}% less damage taken")
        elif stat == "evasion":
            parts.append(f"+{amount:g}% EVA")
        else:
            parts.append(f"+{amount:g}% ACC")
    return joinWords(parts)


def mainEffectText(item):
    effect = item["effect"]
    if effect in STAT_EFFECTS:
        text = statWords(item) + " for every team member"
        if effect == "temp_stat_flat":
            turns = item["turns"]
            text += " during the first turn of each battle" if turns == 1 else f" during the first {turns} turns of each battle"
        if effect == "delayed_stat_percent":
            text += f" from turn {item['turns'] + 1} of each battle on"
        return text
    if effect == "grist_bonus":
        return f"+{item['percent']:g}% Grist for every battle your team wins (rounded up)"
    if effect == "skip_enemy_turns":
        turns = item["turns"]
        return "The enemy team skips its first turn of each battle" if turns == 1 else f"The enemy team skips its first {turns} turns of each battle"
    if effect == "crit_chance":
        return f"Every hit your team lands has a {item['chance']:g}% chance to be a critical hit for {item['multiplier']:g}x damage"
    if effect == "periodic_heal":
        every = item["every"]
        when = "Every turn" if every == 1 else f"Every {ordinal(every)} turn (turns {every}, {every * 2}, {every * 3}...)"
        return f"{when}, each team member heals {item['percent']:g}% of their max HP"
    if effect == "basic_attack_bleed":
        when = "at the end of the turn" if item["turns"] == 1 else f"at the end of each turn for {item['turns']} turns"
        return (f"Every hit from your team's basic attacks (each character's first move, like Punch or Dropkick) "
                f"gives the enemy a stack of Bleed, which takes {item['percent']:g}% of its max HP {when}")
    return effect


def joinWords(parts):
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def ordinal(number):
    suffix = "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


# ============================================================================
# USED BY main.py
# ============================================================================

def findItem(items, typedName):
    """The item with this name (capital letters and spaces at the ends don't matter), or None."""
    wanted = typedName.strip().lower() if isinstance(typedName, str) else ""
    for item in items:
        if item["name"].lower() == wanted:
            return item
    return None


def itemTitle(item):
    return f"{item['emoji']} {item['name']}" if item["emoji"] else item["name"]


def ownedItems(user_data):
    """Names of the items a player owns (players from before items existed don't have the field yet)."""
    owned = (user_data or {}).get("items", [])
    return owned if isinstance(owned, list) else []


def isUnequip(typed):
    return isinstance(typed, str) and typed.strip().lower() in UNEQUIP_WORDS


def rollItemDrops(enemyName):
    """The items that dropped after beating this /battle enemy (every item with drop_from rolls its own drop_chance)."""
    return [item for item in _items if item["drop_from"] == enemyName and random.uniform(0, 100) < item["drop_chance"]]


# ============================================================================
# BATTLE (battle.py calls these, items only ever help the player's team, never the enemies)
# ============================================================================
# Order: base stats -> flat bonuses -> % bonuses. They get worked into the battle copy of the stats when the battle starts
# Nothing in here touches the database, the boosted stats only live as long as the battle does

def _battle():
    import battle  # battle.py imports this file too, so battle.py is only imported here once a battle is running
    return battle


def icon(item):
    return item["emoji"] or "🎒"


def addStats(stats, item):
    """Adds the item's stat numbers to 1 team member's battle stats. Returns exactly what was added, so it can be taken off again.
    defense goes into "itemDefense", which damageTakenMultiplier() in battle.py counts like a defense buff (5 = 5% less damage)."""
    percent = item["effect"] in PERCENT_EFFECTS
    added = {}
    for stat, amount in item["stats"].items():
        if stat == "hp":
            extra = int(stats["maxEhp"] * amount / 100) if percent else int(round(amount))
            stats["maxEhp"] += extra
            stats["ehp"] += extra
            added["maxEhp"] = extra
        else:
            key = {"attack": "attack", "defense": "itemDefense", "evasion": "evasion", "accuracy": "accuracy"}[stat]
            # % attack makes the attack number bigger, the others are already %s so they get added straight on (like buffs)
            extra = stats[key] * amount / 100 if (percent and stat == "attack") else amount
            stats[key] = stats.get(key, 0) + extra
            added[key] = extra
    return added


def battleStart(discordID, itemName):
    """startBattle() calls this right before round 1. Remembers the equipped item and adds its stat bonuses to the team."""
    b = _battle()
    item = findItem(_items, itemName)
    if itemName and not item:
        print(f"Equipped item {itemName!r} of user {discordID} isn't in the MongoDB items collection anymore, so it does nothing")
    if not item:
        return
    state = {"data": item, "temporary": {}}  # temporary = what temp_stat_flat added to each team member
    b.battleInfo[discordID]['item'] = state
    if item["effect"] in STAT_EFFECTS and item["effect"] != "delayed_stat_percent":  # delayed ones start in roundStart
        for unit, stats in b.battleStats[discordID]['players'].items():
            added = addStats(stats, item)
            if item["effect"] == "temp_stat_flat":
                state["temporary"][unit] = added
    b.addLog(discordID, f"{icon(item)} **{item['name']}**: {item['effect_text']}")


def roundStart(discordID):
    """startRound() calls this after the round number goes up. Temporary bonuses wear off and heals happen here."""
    b = _battle()
    info = b.battleInfo[discordID]
    state = info.get('item')
    if not state:
        return
    item = state["data"]
    roundNumber = info['round']

    # temp_stat_flat: the bonus is there for the first "turns" rounds, then exactly what was added gets taken off again
    if item["effect"] == "temp_stat_flat" and state["temporary"] and roundNumber > item["turns"]:
        for unit, added in state["temporary"].items():
            stats = b.battleStats[discordID]['players'][unit]
            for key, extra in added.items():
                stats[key] -= extra
            b.clampHP(discordID, 'players', unit)  # hp can't stay above the lower max hp
        state["temporary"] = {}
        b.addLog(discordID, f"⌛ The **{item['name']}** bonus wore off.")

    # delayed_stat_percent (Huawei Laptop): the bonus starts on turn "turns" + 1 and lasts the rest of the battle
    if item["effect"] == "delayed_stat_percent" and roundNumber == item["turns"] + 1:
        for unit in b.aliveUnits(discordID, 'players'):
            addStats(b.battleStats[discordID]['players'][unit], item)
        b.addLog(discordID, f"{icon(item)} **{item['name']}** kicks in: {statWords(item)} for every team member for the rest of the battle!")

    # periodic_heal: every few rounds each team member that is still standing heals a % of their max hp
    if item["effect"] == "periodic_heal" and roundNumber % item["every"] == 0:
        healed = []
        for unit in b.aliveUnits(discordID, 'players'):
            amount = max(1, round(b.maxHP(discordID, 'players', unit) * item["percent"] / 100))
            gained = b.healUnit(discordID, 'players', unit, amount)
            if gained:
                healed.append(f"**{b.displayName(discordID, 'players', unit)}** +{gained}")
        text = "healed " + ", ".join(healed) if healed else "the team is already at full HP"
        b.addLog(discordID, f"{icon(item)} **{item['name']}**: {text}")


def teamSkipsTurn(discordID):
    """startBattle() and nextTurn() call this when the team's part of a round is about to start.
    Items with a skip_chance (Protein Brick) can make the whole team skip it. Returns True when they skip, after logging it."""
    b = _battle()
    info = b.battleInfo[discordID]
    state = info.get('item')
    if not state or info['result']:
        return False
    item = state["data"]
    # skip_turns (Huawei Laptop): the first few turns of every battle are always skipped
    if info['round'] <= item["skip_turns"]:
        b.addLog(discordID, f"{icon(item)} {item['skip_text']} ({info['round']}/{item['skip_turns']})")
        return True
    if not item["skip_chance"] or random.uniform(0, 100) >= item["skip_chance"]:
        return False
    b.addLog(discordID, f"{icon(item)} {item['skip_text']}")
    return True


def enemiesSkipTurn(discordID):
    """enemyTurn() calls this before the enemies move. skip_enemy_turns items (Samsung Camera) make them skip their
    first few turns of the battle. Returns True when they skip, after logging it."""
    b = _battle()
    info = b.battleInfo[discordID]
    state = info.get('item')
    if not state or state["data"]["effect"] != "skip_enemy_turns" or info['round'] > state["data"]["turns"]:
        return False
    item = state["data"]
    b.addLog(discordID, f"{icon(item)} **{item['name']}**: the enemies' turn was skipped!")
    return True


def hidesHP(discordID):
    """getBattleSummary() asks this: hide_hp items (Noah's Larpometer) hide everyone's HP in the battle embed."""
    state = _battle().battleInfo[discordID].get('item')
    return bool(state and state["data"]["hide_hp"])


def gristBonus(discordID, reward):
    """The BattleView asks this when a battle is won, before the battle is cleaned up.
    grist_bonus items (Noah's Larpometer) give that % more Grist, rounded up. Returns (extra Grist, the item) or (0, None)."""
    b = _battle()
    state = b.battleInfo[discordID].get('item') if b.battleExists(discordID) else None
    if not reward or not state or state["data"]["effect"] != "grist_bonus":
        return 0, None
    return math.ceil(reward * state["data"]["percent"] / 100), state["data"]


def hitLanded(discordID, side, actor, abilityName, foeSide, target):
    """hostileMove() calls this after a hit has landed and done its damage. Returns text for the battle log ("" = nothing happened).
    basic_attack_bleed items (Knife Noir): a hit from a character's basic attack (their first move) gives the target a stack of Bleed."""
    if side != 'players':
        return ""
    b = _battle()
    state = b.battleInfo[discordID].get('item')
    if not state or state["data"]["effect"] != "basic_attack_bleed":
        return ""
    if abilityName != next(iter(b.allAbilities[discordID][side][actor])):
        return ""  # only the first move of each character counts as its basic attack
    if not b.isAlive(discordID, foeSide, target) or b.isDebuffImmune(discordID, foeSide, target):
        return ""
    item = state["data"]
    # the same kind of Bleed as Jack Noir's (endRound() in battle.py does the damage), every hit adds another stack
    b.addLingering(discordID, foeSide, target, {"name": "Bleed", "percent": item["percent"], "turns": item["turns"], "stackable": True})
    return f"{icon(item)} **{b.displayName(discordID, foeSide, target)}** is bleeding"


def criticalHit(discordID, side, damage):
    """hostileMove() calls this once an attack has landed. crit_chance items can turn it into a critical hit.
    Returns (damage, extra text for the battle log)."""
    if side != 'players':
        return damage, ""
    state = _battle().battleInfo[discordID].get('item')
    if not state or state["data"]["effect"] != "crit_chance":
        return damage, ""
    item = state["data"]
    if random.uniform(0, 100) >= item["chance"]:
        return damage, ""
    return max(1, round(damage * item["multiplier"])), " 💥 **Critical hit!**"
