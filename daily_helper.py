# This file runs /daily: it loads the reward schedule from daily_rewards.py, checks it for mistakes when the bot starts,
# and works out the streak and the reward for each claim (main.py does the database update and the replies)
# To change the rewards you only need to edit daily_rewards.py, nothing in here

import difflib
import math
from datetime import datetime, timedelta, timezone

from utils import characterTitles

STREAK_DAYS = 7
REWARD_FIELDS = ["grist", "rolls", "character", "rolls_instead"]

settings = {"cooldown": 24, "grace": 48}  # hours, filled in from daily_rewards.py when the bot starts
schedule = {}                              # day (1-7) -> {"grist", "rolls", "character", "rolls_instead"}
_loaded = False                            # True once daily_rewards.py could be read


def isWholeNumber(value):
    return isinstance(value, int) and not isinstance(value, bool)

def isNumber(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def say(text):
    try:
        print(text)
    except UnicodeEncodeError:  # some consoles can't print emojis or accents
        print(text.encode("ascii", "replace").decode())

def warn(text):
    say(f"[DAILY WARNING] {text}")


# ============================================================================
# LOADING + CHECKING (runs once when the bot starts)
# ============================================================================

def loadDailyRewards():
    """Reads daily_rewards.py and checks it. Returns False (and /daily stays off) if the file can't be used at all."""
    global _loaded
    _loaded = False
    schedule.clear()
    print("Loading daily rewards from daily_rewards.py...")
    try:
        import daily_rewards as data
    except SyntaxError as error:
        warn(f"daily_rewards.py has a typing mistake on line {error.lineno}: {error.msg}")
        warn("/daily is turned off until it is fixed. Check the commas, the { } brackets, and that numbers have no quotes.")
        return False
    except Exception as error:
        warn(f"daily_rewards.py couldn't be read ({type(error).__name__}: {error}). /daily is turned off until it is fixed.")
        return False

    # the 2 time settings
    for name, key, default in (("DAILY_COOLDOWN_HOURS", "cooldown", 24), ("STREAK_GRACE_HOURS", "grace", 48)):
        value = getattr(data, name, default)
        if not isNumber(value) or value <= 0:
            warn(f"{name} has to be a number above 0, like  {name} = {default}  so {default} is used.")
            value = default
        settings[key] = value
    if settings["grace"] < settings["cooldown"]:
        warn(f"STREAK_GRACE_HOURS ({settings['grace']:g}) is shorter than DAILY_COOLDOWN_HOURS ({settings['cooldown']:g}), "
             f"so every streak would break. {settings['cooldown'] * 2:g} is used instead.")
        settings["grace"] = settings["cooldown"] * 2

    # the 7 days
    rewards = getattr(data, "DAILY_REWARDS", None)
    if not isinstance(rewards, dict):
        warn("DAILY_REWARDS is missing or isn't written like  DAILY_REWARDS = { 1: {...}, 2: {...}, ... }  "
             "so /daily is turned off until it is fixed.")
        return False
    for day in rewards:
        if day not in range(1, STREAK_DAYS + 1):
            warn(f"DAILY_REWARDS has a day {day!r}, but the days are the numbers 1 to {STREAK_DAYS} (no quotes), so it was ignored.")
    for day in range(1, STREAK_DAYS + 1):
        schedule[day] = checkDay(day, rewards.get(day))

    _loaded = True
    say("Daily rewards: " + ", ".join(f"day {day} = {describeDay(schedule[day])}" for day in schedule))
    return True


def checkDay(day, entry):
    """Checks 1 day of DAILY_REWARDS. Anything wrong gets a warning and is left out."""
    reward = {"grist": 0, "rolls": 0, "character": None, "rolls_instead": 0}
    where = f"Day {day} in DAILY_REWARDS"
    if entry is None:
        warn(f"{where} is missing, so that day gives nothing.")
        return reward
    if not isinstance(entry, dict):
        warn(f'{where} has to be written like  {day}: {{"grist": 10}},  so that day gives nothing.')
        return reward
    for field, value in entry.items():
        if field not in REWARD_FIELDS:
            guess = difflib.get_close_matches(str(field), REWARD_FIELDS, n=1)
            warn(f'{where}: "{field}" isn\'t something a day can give, so it was ignored.' + (f' Did you mean "{guess[0]}"?' if guess else ""))
        elif field == "character":
            if value in characterTitles:
                reward["character"] = value
            else:
                guess = difflib.get_close_matches(str(value), list(characterTitles), n=1)
                warn(f'{where}: "{value}" isn\'t a character in utils.py (use the short name, like "sr_noah"), so it was ignored.'
                     + (f' Did you mean "{guess[0]}"?' if guess else ""))
        elif not isWholeNumber(value) or value < 0:
            warn(f'{where}: {field} has to be a whole number of 0 or more with no quotes, like "{field}": 10, so it was ignored.')
        else:
            reward[field] = value
    if reward["rolls_instead"] and not reward["character"]:
        warn(f"{where}: rolls_instead only does something next to a character, so it was ignored.")
        reward["rolls_instead"] = 0
    if not (reward["grist"] or reward["rolls"] or reward["character"]):
        warn(f"{where} doesn't give anything.")
    return reward


def dailyRewardsReady():
    return _loaded


def dailyOnlyCharacters():
    """Characters /daily gives away. banner_helper.py keeps them off every banner, so /daily is the only way to get them."""
    try:
        import daily_rewards
        return {day.get("character") for day in daily_rewards.DAILY_REWARDS.values()
                if isinstance(day, dict) and isinstance(day.get("character"), str)}
    except Exception:
        return set()  # loadDailyRewards() prints what is wrong with the file


# ============================================================================
# A CLAIM (used by /daily in main.py)
# ============================================================================

def utcNow():
    return datetime.now(timezone.utc)


def asUTC(value):
    """MongoDB gives dates back without a timezone, they are always UTC. Anything that isn't a date counts as never claimed."""
    if not isinstance(value, datetime):
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def flagField(character):
    """The field that remembers /daily gave this player the character, like "daily_got_sr_noah" (it stays after recycling)."""
    return f"daily_got_{character}"


def streakOf(user_data):
    """The day they claimed last time (0 = never). An odd value (like one typed wrong in Compass) counts as no streak."""
    streak = user_data.get("daily_streak", 0)
    return streak if isWholeNumber(streak) and 0 <= streak <= STREAK_DAYS else 0


def nextDay(streak):
    return 1 if streak >= STREAK_DAYS or streak < 1 else streak + 1


def resolveReward(day, user_data):
    """What that day gives this player. A character they own or already got from /daily turns into rolls_instead."""
    entry = schedule.get(day) or {"grist": 0, "rolls": 0, "character": None, "rolls_instead": 0}
    reward = {"grist": entry["grist"], "rolls": entry["rolls"], "character": None, "insteadOf": None}
    character = entry["character"]
    if character:
        inventory = user_data.get("inventory") if isinstance(user_data.get("inventory"), dict) else {}
        owned = inventory.get(character, 0)
        if (isNumber(owned) and owned >= 1) or user_data.get(flagField(character)):
            reward["rolls"] += entry["rolls_instead"]
            reward["insteadOf"] = character
        else:
            reward["character"] = character
    return reward


def planClaim(user_data, now):
    """Works out what /daily right now does for this player.
    ready = False: too early, "readyAt" says when they can claim. ready = True: "day", "broken" and "reward" say what they get."""
    last = asUTC(user_data.get("last_daily"))
    streak = streakOf(user_data)
    plan = {"streak": streak}
    if last and now - last < timedelta(hours=settings["cooldown"]):
        plan.update(ready=False, readyAt=last + timedelta(hours=settings["cooldown"]))
        return plan
    # more than the grace window since the last claim breaks the streak, otherwise it's the next day (after day 7 it's day 1 again)
    broken = bool(last) and streak > 0 and now - last > timedelta(hours=settings["grace"])
    day = 1 if (last is None or broken) else nextDay(streak)
    plan.update(ready=True, day=day, broken=broken, reward=resolveReward(day, user_data))
    return plan


def claimFilter(userId, user_data, plan, now):
    """The claim only goes through if last_daily is still exactly what was read (and old enough),
    so when 2 /daily run at the same moment, only 1 of them can change the document."""
    flt = {"user_id": userId}
    raw = user_data.get("last_daily")
    if raw is None:
        flt["last_daily"] = None  # matches a missing last_daily too (never claimed)
    elif isinstance(raw, datetime):
        flt["last_daily"] = {"$eq": raw, "$lte": now - timedelta(hours=settings["cooldown"])}
    else:
        flt["last_daily"] = raw   # something that isn't a date (counts as never claimed)
    character = plan["reward"]["character"]
    if character:
        # and they still don't own the character or got it from /daily before (so nobody ends up with 2)
        flt[f"inventory.{character}"] = {"$not": {"$gte": 1}}
        flt[flagField(character)] = {"$ne": True}
    return flt


def claimUpdate(plan, now):
    """The new time + streak and the reward, all in 1 update."""
    reward = plan["reward"]
    update = {"$set": {"last_daily": now, "daily_streak": plan["day"]}}
    give = {}
    if reward["grist"]:
        give["grist"] = reward["grist"]
    if reward["rolls"]:
        give["rolls"] = reward["rolls"]
    if reward["character"]:
        give[f"inventory.{reward['character']}"] = 1
        update["$set"][flagField(reward["character"])] = True
    if give:
        update["$inc"] = give
    return update


def nextClaim(user_data, now):
    """Their next claim if they keep the streak going: (day, reward text, when they can claim it, when the streak breaks)."""
    last = asUTC(user_data.get("last_daily")) or now
    day = nextDay(streakOf(user_data))
    return (day, describeReward(resolveReward(day, user_data)),
            last + timedelta(hours=settings["cooldown"]), last + timedelta(hours=settings["grace"]))


# ============================================================================
# TEXT
# ============================================================================

def describeReward(reward):
    """Like "**20** Grist" or "**[S'all Good, Man] Noah Cave**"."""
    parts = []
    if reward["grist"]:
        parts.append(f"**{reward['grist']}** Grist")
    if reward["rolls"]:
        parts.append(f"**{reward['rolls']}** roll" + ("" if reward["rolls"] == 1 else "s"))
    if reward["character"]:
        parts.append(f"**{characterTitles.get(reward['character'], reward['character'])}**")
    return " and ".join(parts) or "nothing"


def describeDay(entry):
    """For the console when the bot starts, like "10 Grist" or "[S'all Good, Man] Noah Cave (or 10 rolls)"."""
    parts = []
    if entry["grist"]:
        parts.append(f"{entry['grist']} Grist")
    if entry["rolls"]:
        parts.append(f"{entry['rolls']} rolls")
    if entry["character"]:
        parts.append(f"{characterTitles.get(entry['character'], entry['character'])} (or {entry['rolls_instead']} rolls)")
    return " + ".join(parts) or "nothing"


def streakBar(day):
    return "🟩" * day + "⬜" * (STREAK_DAYS - day)


def timeLeft(until, now):
    """Like "5h 12m" (rounded up, so it never says 0m)."""
    minutes = max(1, math.ceil((until - now).total_seconds() / 60))
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def discordTime(moment, style="R"):
    """Discord shows <t:...:R> as "in 5 hours" in every player's own timezone."""
    return f"<t:{int(moment.timestamp())}:{style}>"
