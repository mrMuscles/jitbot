import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import random
from collections import Counter
from PIL import Image
from dotenv import load_dotenv
import time
import traceback

from battle import *
from utils import *
from banner_helper import loadBanners, findBanner, pickCharacter, getRarity, shortDescription, RARITY_ORDER
from item_helper import loadItems, findItem, itemTitle, ownedItems, isUnequip, rollItemDrops, gristBonus, SHOP_IMAGE, MAX_STORE_ITEMS
import daily_helper

load_dotenv("token.env")

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "jitstuck"
COLLECTION_NAME = "inventory"

# Mongo Uses DBS called "jitstuck" and assumes a collection called "inventory"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
inventory_collection = db[COLLECTION_NAME]

# main.py - basic discord.py bot that goes online

# Put your bot token in the DISCORD_TOKEN environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

intents = discord.Intents.default()
intents.message_content = True  # enable if you want text commands (enable in dev portal if required)
intents.members = True

# Every new player gets this inventory document. on_ready, on_member_join and a player's first slash command all use it,
# so a new inventory always looks the same
def add_new_player(user):
    """Writes a new inventory for a player who doesn't have one yet, people who already have one aren't changed.
    Returns True when a new inventory was made."""
    if user.bot:  # Skip bots
        return False
    user_data = {
        "user_id": user.id,
        "username": str(user),
        "inventory": {},
        "rolls": 10,  # Starting rolls,
        "counter": 0,
        "team": []
    }
    # Use upsert to avoid duplicates
    result = inventory_collection.update_one(
        {"user_id": user.id},
        {"$setOnInsert": user_data},
        upsert=True
    )
    return result.upserted_id is not None


class PlayerTree(app_commands.CommandTree):
    """The bot's slash commands. Before any of them runs, someone using the bot for the first time gets their inventory
    (on_ready and on_member_join cover most people, this catches anyone they missed)."""

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.type is discord.InteractionType.autocomplete:
            return True  # they are still typing, it happens when the command is actually sent
        try:
            if add_new_player(interaction.user):
                print(f"New player: made an inventory for {interaction.user}")
        except PyMongoError as error:
            print(f"Couldn't make an inventory for {interaction.user}: {error}")
        return True  # the command always runs


bot = commands.Bot(command_prefix="/", intents=intents, help_command=None, tree_cls=PlayerTree)
startup_done = False  # on_ready runs again every time the bot reconnects, this makes the inBattle reset only happen on startup

@bot.event
async def on_ready():
    global startup_done
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Gacha Game"))
    print("teeesst")

    # Change inBattle to false for all users on bot startup
    # (not after a reconnect, the battles in memory are still going then and someone could start a second one)
    if not startup_done:
        inventory_collection.update_many({}, {"$set": {"inBattle": False}})
        startup_done = True

    # Add all users from all guilds to MongoDB
    for guild in bot.guilds:
        for member in guild.members:
            #print("Checking user:", member.name)
            if not member.bot:  # Skip bots
                print("User: " + member.name)
                add_new_player(member)
    print(f"Initialized users in database from {len(bot.guilds)} guild(s)")

@bot.event
async def on_member_join(member):
    # People who join after the bot started get added straight away (before they had no inventory until the bot restarted)
    add_new_player(member)


# Roll, inventory, Character, battle, challenge, team, viewteam, recycle, help

# Create all character choices for autocomplete
all_characters = rChar + srChar + ssrChar + specialChar# + secretChar
character_choices = [
    app_commands.Choice(name=characterTitles[char], value=char)
    for char in all_characters
]

# /char groups every version of a character together, like "abraize" -> r_abraize, r_abraize2, sr_abraize, ssr_abraize
# (the group is the dev name without the rarity at the start and any number at the end)
merged_groups = {"jayden": "jaiden"}  # groups shown as 1 character: ssr_jayden goes in with r_jaiden
character_groups = {}
for char in all_characters:
    group = char.split("_", 1)[1].rstrip("0123456789")
    character_groups.setdefault(merged_groups.get(group, group), []).append(char)
character_group_choices = [app_commands.Choice(name=name.capitalize(), value=name) for name in character_groups]
rarity_choices = [app_commands.Choice(name=rarity, value=rarity) for rarity in RARITY_ORDER if rarity != "SSSR"]  # secret characters can't be picked anyway

# Banners come from banners.py (the README's "Adding a new banner" part explains how to add one)
# They get checked here when the bot starts and any mistakes are printed in the console
BANNERS = loadBanners(all_characters)

# Items come from the "items" collection in MongoDB (the README's "Items" part explains how to add one)
# They get checked here when the bot starts and any mistakes are printed in the console
# If the collection is empty (a brand-new database) it gets filled with the starting items first
ITEMS = loadItems(db["items"])
STORE_ITEMS = [item for item in ITEMS if item["in_store"]]  # items with in_store = False (like Knife Noir) can't be bought

# The /daily rewards come from daily_rewards.py (the README's "Daily rewards" part explains them), mistakes are printed in the console
daily_helper.loadDailyRewards()

# Use abraizeEmbed as example for other characters
# HP attack and defense are integers
# evasion and accuracy are percentages

# each character will have an 8 length array that includes all attributes
# hp, atk, def, eva, acc, skill1, skill2, skill3
# the only exxception is that ssr characters will have an ultimate skill making it a 9 length array

def r_abraizeEmbed():
    embed = discord.Embed(title=characterTitles["r_abraize"], description="Abraize Masood", color=0x3f48cc)
    # add image from bannerGifs dict
    embed.set_image(url=bannerGifs["r_abraize_gif"])
    embed.add_field(name="HP:", value=characterAttributes["r_abraize"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_abraize"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_abraize"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_abraize"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_abraize"][4], inline=True)
    embed.add_field(name=characterAttributes["r_abraize"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_abraize"][6], value="Take a nap on the field, reducing self's evasion score to 0%. \nFor one turn, unable to attack or act. After said turn, gain a 15% atk and def buff to self for 2 turns.", inline=False)
    embed.add_field(name=characterAttributes["r_abraize"][7], value="Getting these done really lifted a weight off your chest. +5% acc boost for one turn.", inline=False)
    return embed

def r_abraize2Embed():
    embed = discord.Embed(title=characterTitles["r_abraize2"], description="Abraize Masood", color=0x3f48cc)
    embed.set_image(url=R_ABRAIZE2_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_abraize2"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_abraize2"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_abraize2"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_abraize2"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_abraize2"][4], inline=True)
    embed.add_field(name=characterAttributes["r_abraize2"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_abraize2"][6], value="Apply a +10% evasion buff to self for one turn, but cost 25 HP.", inline=False)
    embed.add_field(name=characterAttributes["r_abraize2"][7], value="Apply a 10% atk and def buff to all allies for 3 turns, cannot be used for 4 turns.", inline=False)
    return embed

def sr_abraizeEmbed():
    embed = discord.Embed(title=characterTitles["sr_abraize"], description="Abraize Masood", color=0x3f48cc)
    embed.set_image(url=SR_ABRAIZE_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sr_abraize"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sr_abraize"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sr_abraize"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sr_abraize"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sr_abraize"][4], inline=True)
    embed.add_field(name=characterAttributes["sr_abraize"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["sr_abraize"][6], value="Applies a -15% accuracy debuff to one enemy.", inline=False)
    embed.add_field(name=characterAttributes["sr_abraize"][7], value="Attempt to travel back in time without being doomed. Has an 85% chance of doing nothing. 15% chance that health is healed by 50% and all allies atk is buffed by 20% for one turn.", inline=False)
    return embed

def ssr_abraizeEmbed():
    embed = discord.Embed(title=characterTitles["ssr_abraize"], description="Abraize Masood", color=0x3f48cc)
    embed.set_image(url=SSR_ABRAIZE_GIF)
    embed.add_field(name="HP:", value=characterAttributes["ssr_abraize"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["ssr_abraize"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["ssr_abraize"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["ssr_abraize"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["ssr_abraize"][4], inline=True)
    embed.add_field(name=characterAttributes["ssr_abraize"][5], value="Accelerate yourself to punch the opponent. Guaranteed to hit. Applies one stack of 'Accelerated' state to self. Gain +10% atk for every consecutive 'Accelerated' state with a maximum of +100% atk. All 'Accelerated' stacks are removed when using another move.", inline=False)
    embed.add_field(name=characterAttributes["ssr_abraize"][6], value="Apply a +5% acc bonus, +40% atk bonus, and +15% def bonus to all allies for one turn and allows you to immediately take another turn. Cannot be used for another 5 turns.", inline=False)
    embed.add_field(name=characterAttributes["ssr_abraize"][7], value="Revert all party member's stats to the state they were in during the prior turn. Cannot be used for another 3 turns.", inline=False)
    embed.add_field(name=characterAttributes["ssr_abraize"][8], value="Your status as an anchor of time and your experience lends you well to combat. Turn back the wheels of time to make everything right again. Applies debuff nullification (cannot be debuffed) and a +50% atk bonus to all allies for 5 turns. Heals all allies to full. Cannot be used again.", inline=False)
    return embed

def r_treyEmbed():
    embed = discord.Embed(title=characterTitles["r_trey"], description="Treyvaughn Lewis", color=0x3f48cc)
    embed.set_image(url=R_TREY_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_trey"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_trey"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_trey"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_trey"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_trey"][4], inline=True)
    embed.add_field(name=characterAttributes["r_trey"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_trey"][6], value="Apply a one time +10% eva buff to self for one turn. Can be used again after 2 turns", inline=False)
    embed.add_field(name=characterAttributes["r_trey"][7], value="Throws cheesy fries at one enemy of choice, applies Burn on them for one turn. 70% chance to hit", inline=False)
    return embed

def sr_treyEmbed():
    embed = discord.Embed(title=characterTitles["sr_trey"], description="Treyvaughn Lewis", color=0x3f48cc)
    embed.set_image(url=SR_TREY_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sr_trey"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sr_trey"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sr_trey"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sr_trey"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sr_trey"][4], inline=True)
    embed.add_field(name=characterAttributes["sr_trey"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["sr_trey"][6], value="Applies a -10% acc debuff to all opponents for one turn.", inline=False)
    embed.add_field(name=characterAttributes["sr_trey"][7], value="The horrorterrors beckon. Give a +10% acc boost to all allies for 2 turns. Cannot be used again for 1 turn.", inline=False)
    return embed

def ssr_treyEmbed():
    embed = discord.Embed(title=characterTitles["ssr_trey"], description="Treyvaughn Lewis", color=0x3f48cc)
    embed.set_image(url=SSR_TREY_GIF)
    embed.add_field(name="HP:", value=characterAttributes["ssr_trey"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["ssr_trey"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["ssr_trey"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["ssr_trey"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["ssr_trey"][4], inline=True)
    embed.add_field(name=characterAttributes["ssr_trey"][5], value="Throw a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["ssr_trey"][6], value="Add a +100% eva buff and +10% acc buff to self for one turn. Performs a stabbing attack on one enemy that deals 10% max hp and true damage. Cannot be used for 2 turns.", inline=False)
    embed.add_field(name=characterAttributes["ssr_trey"][7], value="Redistribute the void into those around you. +50% eva buff to all allies for 3 turns, but draws attacks to you for one turn. Cannot be used again for 4 turns.", inline=False)
    embed.add_field(name=characterAttributes["ssr_trey"][8], value="Nothing can't be seen, right? Centering all of the void you control into one spot should be able to create a concentrated spot of nothing, a nothing so strong that no thing can escape it. Create a miniature \"void spot\" that stays on the battle for 3 turns. When on the stage, all ranged attacks automatically miss. For each ranged attack performed, the power grows by 50%. After every turn, power grows by 100%. At the end of 3 turns, deals the combined percentage of atk to all enemies in one burst. Cannot be used again.", inline=False)
    return embed

def r_noahEmbed():
    embed = discord.Embed(title=characterTitles["r_noah"], description="Noah Cave", color=0x3f48cc)
    embed.set_image(url=R_NOAH_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_noah"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_noah"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_noah"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_noah"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_noah"][4], inline=True)
    embed.add_field(name=characterAttributes["r_noah"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_noah"][6], value="Send an annoying text message to one enemy, applying a -5% acc debuff to them.", inline=False)
    embed.add_field(name=characterAttributes["r_noah"][7], value="Apply \"Interfere\" state to self permanently until exhausted. \"Interfere\" state allows a 50% chance of an incoming enemy attack to be negated one time before the state is exhausted and removed from self. Can only be used again after 2 turns.", inline=False)
    return embed

def sr_noahEmbed():
    embed = discord.Embed(title=characterTitles["sr_noah"], description="Noah Cave", color=0x3f48cc)
    embed.set_image(url=R_NOAH2_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sr_noah"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sr_noah"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sr_noah"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sr_noah"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sr_noah"][4], inline=True)
    embed.add_field(name=characterAttributes["sr_noah"][5], value="Order in the court! Bring the gavel down on one enemy.", inline=False)
    embed.add_field(name=characterAttributes["sr_noah"][6], value="Apply a -15% acc debuff to all enemies and draw all attacks to self for one turn.", inline=False)
    embed.add_field(name=characterAttributes["sr_noah"][7], value="Make all team members immune to damage for this turn. Cannot be used again for 3 turns.", inline=False)
    return embed

def sr_binktopEmbed():
    embed = discord.Embed(title=characterTitles["sr_binktop"], description="Binktop", color=0x3f48cc)
    if SR_BINKTOP_GIF:  # empty until the gif link is added in utils.py
        embed.set_image(url=SR_BINKTOP_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sr_binktop"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sr_binktop"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sr_binktop"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sr_binktop"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sr_binktop"][4], inline=True)
    embed.add_field(name=characterAttributes["sr_binktop"][5], value="Swipe two times with your trusty Virusword, with each swipe dealing 75% of your atk stat, but having a 15% chance of applying \"Code Rot\" (-10% atk for 2 turns) to the enemy!", inline=False)
    embed.add_field(name=characterAttributes["sr_binktop"][6], value="Hold up your shield and ready yourself to parry, you may also choose an ally to defend, gaining a 75% def boost for this turn. If an attack lands on Binktop during his parry, automatically activate Viruslash on whichever enemy landed the hit. Cannot be used for another 3 turns.", inline=False)
    embed.add_field(name=characterAttributes["sr_binktop"][7], value="Binktop channels his full McAfee Virus Protection Power into his sword for 2 turns. If he is hit, his focus is lost, and the power is lost. If allowed to channel for 2 turns, Binktop unleashes a devastating slash, dealing 265 damage + 7.5% max hp damage to an enemy. After this, Binktop is stunned for one turn. Cannot be used for another 6 turns.", inline=False)
    return embed

def r_homestuckEmbed():
    embed = discord.Embed(title=characterTitles["r_homestuck"], description="Homestuck", color=0x3f48cc)
    if R_HOMESTUCK_GIF:  # empty until the gif link is added in utils.py
        embed.set_image(url=R_HOMESTUCK_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_homestuck"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_homestuck"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_homestuck"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_homestuck"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_homestuck"][4], inline=True)
    embed.add_field(name=characterAttributes["r_homestuck"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_homestuck"][6], value="Draw all enemy attacks to self for one turn, and increase defense by 5 for this turn as well.", inline=False)
    embed.add_field(name=characterAttributes["r_homestuck"][7], value="Skips the enemy turn, but deals 10% of every other team member's hp. Cannot be used again for 2 turns.", inline=False)
    return embed

def r_maxEmbed():
    embed = discord.Embed(title=characterTitles["r_max"], description="Max Yakuvobich", color=0x3f48cc)
    if R_MAX_GIF:  # empty until the gif link is added in utils.py
        embed.set_image(url=R_MAX_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_max"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_max"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_max"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_max"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_max"][4], inline=True)
    embed.add_field(name=characterAttributes["r_max"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_max"][6], value="Restore 25 hp to self, but your next attack is guaranteed to miss.", inline=False)
    embed.add_field(name=characterAttributes["r_max"][7], value="Choose one ally to bestow a 25% boost to all stats for one turn. Cannot be used for 2 turns.", inline=False)
    return embed

def r_jaidenEmbed():
    embed = discord.Embed(title=characterTitles["r_jaiden"], description="Jaiden Ceballos", color=0x3f48cc)
    if R_JAIDEN_GIF:  # empty until the gif link is added in utils.py
        embed.set_image(url=R_JAIDEN_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_jaiden"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_jaiden"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_jaiden"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_jaiden"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_jaiden"][4], inline=True)
    embed.add_field(name=characterAttributes["r_jaiden"][5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_jaiden"][6], value="Throw an adjacent packaging box at an enemy (ranged attack). Depending on what is inside, deal different damages", inline=False)
    embed.add_field(name=characterAttributes["r_jaiden"][7], value="Commit a teammate and fuck to hit the damn opponent.", inline=False)
    return embed

def r_freemanEmbed():
    embed = discord.Embed(title=characterTitles["r_freeman"], description="Freeman", color=0x3f48cc)
    embed.set_image(url=R_FREEMAN_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_freeman"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_freeman"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_freeman"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_freeman"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_freeman"][4], inline=True)
    embed.add_field(name=characterAttributes["r_freeman"][5], value="Bitch slap the opponent with your weak arm.", inline=False)
    embed.add_field(name=characterAttributes["r_freeman"][6], value="Apply a 3% eva buff to all allies for 1 turn.", inline=False)
    embed.add_field(name=characterAttributes["r_freeman"][7], value="Apply a temporary +10% atk buff to self and deal damage to one opponent. The damage dealt is then subtracted from your hp.", inline=False)
    return embed

def sr_freemanEmbed():
    embed = discord.Embed(title=characterTitles["sr_freeman"], description="Freeman", color=0x3f48cc)
    embed.set_image(url=SR_FREEMAN_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sr_freeman"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sr_freeman"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sr_freeman"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sr_freeman"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sr_freeman"][4], inline=True)
    embed.add_field(name=characterAttributes["sr_freeman"][5], value="Nobody expects a good clocking from a gun.", inline=False)
    embed.add_field(name=characterAttributes["sr_freeman"][6], value="80% chance of the safety being on, dealing no damage. 20% that the safety was left off, dealing 10% of the enemy's current hp.", inline=False)
    embed.add_field(name=characterAttributes["sr_freeman"][7], value="Apply \"Nervous\" state to self. As long as self has \"Nervous\" state, apply a 25% chance that each attack made by an enemy can be interrupted (similar to R Noah). When an attack is interrupted, attempt to Shoot the attacking enemy.", inline=False)
    return embed

def r_stephenEmbed():
    embed = discord.Embed(title=characterTitles["r_stephen"], description="Stephen Goraynov", color=0x3f48cc)
    embed.set_image(url=R_STEPHEN_GIF)
    embed.add_field(name="HP:", value=characterAttributes["r_stephen"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["r_stephen"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["r_stephen"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["r_stephen"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["r_stephen"][4], inline=True)
    embed.add_field(name=characterAttributes["r_stephen"][5], value="Kick the shit out of one enemy.", inline=False)
    embed.add_field(name=characterAttributes["r_stephen"][6], value="Light your BALLER CIGARETTE, drawing everyone's attention towards you. Applies \"Baller\" status to self for 3 turns. If hit during \"Baller\" status, remove one stack.", inline=False)
    embed.add_field(name=characterAttributes["r_stephen"][7], value="Add +5% atk bonus for one turn per each \"Baller\" status self has.", inline=False)
    return embed

def sr_stephenEmbed():
    embed = discord.Embed(title=characterTitles["sr_stephen"], description="Stephen Goraynov", color=0x3f48cc)
    embed.set_image(url=SR_STEPHEN_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sr_stephen"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sr_stephen"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sr_stephen"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sr_stephen"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sr_stephen"][4], inline=True)
    embed.add_field(name=characterAttributes["sr_stephen"][5], value="Kick the shit out of an enemy.", inline=False)
    embed.add_field(name=characterAttributes["sr_stephen"][6], value="Begin \"Considering\" if it is worth it to intervene.", inline=False)
    embed.add_field(name=characterAttributes["sr_stephen"][7], value="Converts each stack of \"Considering\" into +10 damage and then attacks one enemy.", inline=False)
    return embed

def ssr_jaydenEmbed():
    embed = discord.Embed(title=characterTitles["ssr_jayden"], description="Jayden Ceballos", color=0x3f48cc)
    embed.set_image(url=SSR_JAYDEN_GIF)
    embed.add_field(name="HP:", value=characterAttributes["ssr_jayden"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["ssr_jayden"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["ssr_jayden"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["ssr_jayden"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["ssr_jayden"][4], inline=True)
    embed.add_field(name=characterAttributes["ssr_jayden"][5], value="Distort the space around you, dealing 50% of your atk as damage to all enemies.", inline=False)
    embed.add_field(name=characterAttributes["ssr_jayden"][6], value="Leverage your dreadful reputation as the Butler of Ill Repute. -30% acc for all enemies. Cannot be used for another 2 turns.", inline=False)
    embed.add_field(name=characterAttributes["ssr_jayden"][7], value="33% chance to buff all allies atk and def by 20%, 33% chance to debuff all enemies atk and def by 20%, 33% chance to deal 1 hp of damage to self.", inline=False)
    embed.add_field(name=characterAttributes["ssr_jayden"][8], value="With the power of creation on your side, it is your sworn duty to bring about its influence in this world. It is your job to decrease the space between you and your allies, and to increase the space between your allies and your enemies. Apply \"Regeneration\" status (5% hp heal every turn) for the next 7 turns, as well as apply \"Warped\" status (-25% acc penalty, -35% max hp, -25% def) to all enemies for the next 7 turns. Cannot be used again.", inline=False)
    return embed

def sr_homestuckEmbed():
    embed = discord.Embed(title=characterTitles["sr_homestuck"], description="Homestuck", color=0x3f48cc)
    embed.set_image(url=SR_HOMESTUCK_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sr_homestuck"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sr_homestuck"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sr_homestuck"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sr_homestuck"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sr_homestuck"][4], inline=True)
    embed.add_field(name=characterAttributes["sr_homestuck"][5], value="Roll a die! Deal damage in increments of 10 based on what you get!", inline=False)
    embed.add_field(name=characterAttributes["sr_homestuck"][6], value="Apply a -15% atk debuff to one random ally for one turn, provide a +15% atk buff to self for one turn.", inline=False)
    embed.add_field(name=characterAttributes["sr_homestuck"][7], value="Apply a -100% acc penalty to all enemies and a +100% acc bonus to all allies for one turn. Cannot be used again for 5 turns.", inline=False)
    return embed

def ssr_scottieEmbed():
    embed = discord.Embed(title=characterTitles["ssr_scottie"], description="Scottie Jenkins", color=0x3f48cc)
    embed.set_image(url=SSR_SCOTTIE_GIF)
    embed.add_field(name="HP:", value=characterAttributes["ssr_scottie"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["ssr_scottie"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["ssr_scottie"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["ssr_scottie"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["ssr_scottie"][4], inline=True)
    embed.add_field(name=characterAttributes["ssr_scottie"][5], value="Unique Property is that the attack is unaffected by accuracy debuffs and is guaranteed to connect, Low Damage and If used twice applies a doom mark", inline=False)
    embed.add_field(name=characterAttributes["ssr_scottie"][6], value="Debuff targets all enemiesby reducing accuracy and damage on all enemies for 3 turns. Accuracy and damage reduction scale for the amount of doom marks an enemy has. All doom marks are consumed and removed upon use", inline=False)
    embed.add_field(name=characterAttributes["ssr_scottie"][7], value="Redirects enemies to attack Scottie for 2 turns Damage reduction 30% Each successfull attack landed on Scottie inflicts 1 doom mark to the assailant (If an enemy does a single strong hit only one mark will apply, but if an enemy does a barrage; the amount of marks will follow accordingly) 1x12=1 mark 3x4=3 marks If Scottie is to die during martyrdom the doom marks that were already applied will explode dealing major damage to enemies. Cannot be used for another 2 turns.", inline=False)
    embed.add_field(name=characterAttributes["ssr_scottie"][8], value="Only usable after a minimum of 3 turns and if the total amount of doom makes on the field is 5 For 3 turns every enemy on the field will lose all sense of will and reason Causing a chance event for each turn applied 33% chance for an enemy to harm itself 33% chance for an enemy to attack on of its allies 33% chance for an enemy to lay motionless allowing all attack done to them be guaranteed to land", inline=False)
    return embed

def sssr_maxEmbed():
    embed = discord.Embed(title=characterTitles["sssr_max"], description="???", color=0x000000)
    embed.set_image(url=SSSR_MAX_GIF)
    embed.add_field(name="HP:", value=characterAttributes["sssr_max"][0], inline=True)
    embed.add_field(name="ATK:", value=characterAttributes["sssr_max"][1], inline=True)
    embed.add_field(name="DEF:", value=characterAttributes["sssr_max"][2], inline=True)
    embed.add_field(name="EVA:", value=characterAttributes["sssr_max"][3], inline=True)
    embed.add_field(name="ACC:", value=characterAttributes["sssr_max"][4], inline=True)
    embed.add_field(name=characterAttributes["sssr_max"][5], value="???", inline=False)
    embed.add_field(name=characterAttributes["sssr_max"][6], value="???", inline=False)
    embed.add_field(name=characterAttributes["sssr_max"][7], value="???", inline=False)
    embed.add_field(name=characterAttributes["sssr_max"][8], value="???", inline=False)
    embed.add_field(name="Lore:", value="An entity beyond comprehension. Its true nature is unknown.", inline=False)
    return embed


def roll_character(banner: dict) -> str:
    # The banner (from banners.py) says how likely each rarity is and which characters it has
    # Inside a rarity every character has the same chance
    return pickCharacter(banner)


# Suggestions while typing a banner name in /roll and /banner
# (reads banners.py live, so new banners show up after a restart without needing /syncapp)
async def banner_autocomplete(interaction: discord.Interaction, current: str):
    typed = current.strip().lower()
    return [
        app_commands.Choice(name=banner["name"], value=banner["name"])
        for banner in BANNERS
        if typed in banner["name"].lower()
    ][:25]


def banner_not_found_text(typed):
    if not BANNERS:
        return "There are no banners set up right now. An admin needs to check banners.py (the bot console says what is wrong)."
    typed = discord.utils.escape_mentions(discord.utils.escape_markdown(typed[:100]))
    names = ", ".join(f"**{banner['name']}**" for banner in BANNERS)
    return f"I couldn't find a banner called **{typed}**. The banners are: {names}"[:2000]


@bot.tree.command(name="roll")
@app_commands.describe(banner="Which banner to roll on (/banner shows them all)", amount="How many rolls to use (leave it empty to use all of them)")
@app_commands.autocomplete(banner=banner_autocomplete)
async def roll(interaction: discord.Interaction, banner: str, amount: int = None):
    """Pick a banner to roll on. Optionally specify amount to roll; otherwise roll all available."""
    chosen_banner = findBanner(BANNERS, banner)
    if not chosen_banner:
        await interaction.response.send_message(banner_not_found_text(banner), ephemeral=True)
        return

    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if not user_data:
        await interaction.response.send_message("No inventory data found.")
        return

    rolls_available = user_data.get("rolls", 0)
    if rolls_available <= 0:
        await interaction.response.send_message(f"You do not have any rolls left for the **{chosen_banner['name']}** banner.")
        return

    # Determine how many rolls to perform
    if amount is None or amount <= 0:
        to_roll = rolls_available
    else:
        to_roll = min(amount, rolls_available)

    # Take the rolls first, but only if the user still has them
    # (stops 2 /roll commands at the same time from spending the same rolls twice)
    taken = inventory_collection.update_one(
        {"user_id": interaction.user.id, "rolls": {"$gte": to_roll}},
        {"$inc": {"rolls": -to_roll}},
    )
    if taken.modified_count == 0:
        await interaction.response.send_message("Your rolls changed while rolling, please try again.")
        return

    rolled_characters = [roll_character(chosen_banner) for _ in range(to_roll)]
    inventory_collection.update_one(
        {"user_id": interaction.user.id},
        {"$inc": {f"inventory.{char}": cnt for char, cnt in Counter(rolled_characters).items()}},
    )

    embed = discord.Embed(title=f"{chosen_banner['name']} Rolls: x{to_roll}", color=chosen_banner["color"])
    if amount is not None and amount > rolls_available:
        embed.description = f"Requested {amount}, using {rolls_available} available."

    # Group results by rarity (highest first)
    for rarity in RARITY_ORDER:
        counts = Counter(char for char in rolled_characters if getRarity(char) == rarity)
        if counts:
            lines = [f"**{characterTitles.get(char, char)}** +{cnt}" for char, cnt in counts.items()]
            embed.add_field(name=f"{rarity} Characters:", value="\n".join(lines)[:1024], inline=False)

    # an SSSR pulled always shows its gif, otherwise the first SSR pulled does (the same gif its /char card uses)
    first_ssr = next((char for rarity in ("SSSR", "SSR") for char in rolled_characters if getRarity(char) == rarity), None)
    if first_ssr:
        embed.set_image(url=character_card(first_ssr).image.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command()
async def inventory(ctx):
    """Show Inventory"""
    # display inventory in some cool way maybe like how maki does and have buttons to flip through pages
    user_data = inventory_collection.find_one({"user_id": ctx.user.id})
    if user_data:
        rolls = user_data.get("rolls", 0)
        inventory = user_data.get("inventory", {})

      #  special_inventory = {char: count for char, count in inventory.items() if char in specialChar}
        sssr_inventory = {char: count for char, count in inventory.items() if char in secretChar}  # only shows once someone owns one
        ssr_inventory = {char: count for char, count in inventory.items() if char in ssrChar or char in specialChar}
        sr_inventory = {char: count for char, count in inventory.items() if char in srChar}
        r_inventory = {char: count for char, count in inventory.items() if char in rChar}

        embed = discord.Embed(title=f"{ctx.user.display_name}'s Inventory", color=0x3f48cc)

     #   if special_inventory:
      #      embed.add_field(name="Special Characters:", value="\n".join([f"{characterTitles[char]}: {count}" for char, count in special_inventory.items()]), inline=False)
        if sssr_inventory:
            embed.add_field(name="SSSR Characters:", value="\n".join([f"{characterTitles[char]}: {count}" for char, count in sssr_inventory.items()]), inline=False)
        if ssr_inventory:
            embed.add_field(name="SSR Characters:", value="\n".join([f"{characterTitles[char]}: {count}" for char, count in ssr_inventory.items()]), inline=False)

        if sr_inventory:
            embed.add_field(name="SR Characters:", value="\n".join([f"{characterTitles[char]}: {count}" for char, count in sr_inventory.items()]), inline=False)
        if r_inventory:
            embed.add_field(name="R Characters:", value="\n".join([f"{characterTitles[char]}: {count}" for char, count in r_inventory.items()]), inline=False)

        embed.add_field(name="Rolls:", value=str(rolls), inline=False)
        embed.add_field(name="Points Needed for Next Roll:", value=str(10 - user_data.get("counter", 0)), inline=False)

        await ctx.response.send_message(embed=embed)
    else:
        await ctx.response.send_message(f"{ctx.user.mention} No inventory data found.")

async def char_type_autocomplete(interaction: discord.Interaction, current: str):
    """The cards of the character (and rarity) already picked in /char or /recycle, so the user can pick 1 of them."""
    picked = interaction.namespace  # what the user filled in so far (character / rarity are None until they're picked)
    typed = current.strip().lower()
    return [
        app_commands.Choice(name=characterTitles[char], value=char)
        for char in character_groups.get(picked.character, all_characters)
        if (picked.rarity is None or getRarity(char) == picked.rarity) and typed in characterTitles[char].lower()
    ][:25]

# Ephemeral Message
@bot.tree.command()
@app_commands.rename(char_type="type")
@app_commands.describe(character="Which character to show", rarity="Only show this rarity (leave it empty to show every rarity)",
                       char_type="Only show this 1 card (leave it empty to show all of them)")
@app_commands.choices(character=character_group_choices, rarity=rarity_choices)
@app_commands.autocomplete(char_type=char_type_autocomplete)
async def char(interaction: discord.Interaction, character: app_commands.Choice[str], rarity: app_commands.Choice[str] = None, char_type: str = None):
    """Show Character Info"""
    # Every version of the character (only the chosen rarity if one was picked)
    char_dev_names = [char for char in character_groups[character.value] if rarity is None or getRarity(char) == rarity.value]
    if not char_dev_names:
        await interaction.response.send_message(f"**{character.name}** has no **{rarity.value}** characters!", ephemeral=True)
        return

    # Only the 1 card picked in type (the menu gives its dev name, typing the full title out works too)
    if char_type is not None:
        char_dev_names = [char for char in char_dev_names if char_type.strip().lower() in (char, characterTitles[char].lower())]
        if not char_dev_names:
            typed = discord.utils.escape_mentions(discord.utils.escape_markdown(char_type[:100]))
            rarity_text = f" **{rarity.value}**" if rarity else ""
            await interaction.response.send_message(f"**{typed}** is not one of **{character.name}'s**{rarity_text} cards! Pick one from the **type** menu.", ephemeral=True)
            return

    # Only show the ones the user owns
    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if user_data:
        inventory = user_data.get("inventory", {})
        # if sssr_max then continue even if user does not own
        char_dev_names = [char for char in char_dev_names if inventory.get(char, 0) >= 1 or char == "sssr_max"]
        if not char_dev_names:
            await interaction.response.defer()
            await interaction.followup.send(file=discord.File(otherImages["no_own_png"]))
            return
    else:
        await interaction.response.send_message("No inventory data found.")
        return

    yesMax = "sssr_max" in char_dev_names
    if yesMax:
        await interaction.response.defer()
    else:
        await interaction.response.defer(ephemeral=True)

    embeds = [character_embed(char_dev_name) for char_dev_name in char_dev_names]

    # A message can hold 10 embeds and 6000 characters in total, so a big group gets split over more messages
    messages = [[]]
    for embed in embeds:
        if len(messages[-1]) == 10 or sum(len(e) for e in messages[-1]) + len(embed) > 6000:
            messages.append([])
        messages[-1].append(embed)

    # The messages below will be hidden from other users.
    for message_embeds in messages:
        await interaction.followup.send(embeds=message_embeds, ephemeral=not yesMax)
    if yesMax:
        await asyncio.sleep(2)  # asyncio.sleep instead of time.sleep so the whole bot doesn't freeze for 2 seconds
        await interaction.delete_original_response()


def character_embed(char_dev_name):
    """The /char card of 1 character."""
    if char_dev_name == "r_abraize":
        embed = r_abraizeEmbed()
    elif char_dev_name == "r_abraize2":
        embed = r_abraize2Embed()
    elif char_dev_name == "sr_abraize":
        embed = sr_abraizeEmbed()
    elif char_dev_name == "ssr_abraize":
        embed = ssr_abraizeEmbed()
    elif char_dev_name == "r_trey":
        embed = r_treyEmbed()
    elif char_dev_name == "sr_trey":
        embed = sr_treyEmbed()
    elif char_dev_name == "ssr_trey":
        embed = ssr_treyEmbed()
    elif char_dev_name == "r_noah":
        embed = r_noahEmbed()
    elif char_dev_name == "sr_noah":
        embed = sr_noahEmbed()
    elif char_dev_name == "r_freeman":
        embed = r_freemanEmbed()
    elif char_dev_name == "sr_freeman":
        embed = sr_freemanEmbed()
    elif char_dev_name == "ssr_jayden":
        embed = ssr_jaydenEmbed()
    elif char_dev_name == "r_stephen":
        embed = r_stephenEmbed()
    elif char_dev_name == "sr_stephen":
        embed = sr_stephenEmbed()
    elif char_dev_name == "sr_homestuck":
        embed = sr_homestuckEmbed()
    elif char_dev_name == "ssr_scottie":
        embed = ssr_scottieEmbed()
    elif char_dev_name == "r_homestuck":
        embed = r_homestuckEmbed()
    elif char_dev_name == "r_max":
        embed = r_maxEmbed()
    elif char_dev_name == "r_jaiden":
        embed = r_jaidenEmbed()
    elif char_dev_name == "sr_binktop":
        embed = sr_binktopEmbed()
    elif char_dev_name == "sssr_max":
        embed = sssr_maxEmbed()
    else:
        embed = discord.Embed(title=characterTitles.get(char_dev_name, char_dev_name), description=f"Character **{char_dev_name}** does not have a card yet!", color=0x3f48cc)
    return embed


def bannerListEmbed():
    embed = discord.Embed(title="Banners", description="Use **/banner name:** to see what is inside a banner and **/roll** to roll on it.", color=0x3f48cc)
    if not BANNERS:
        embed.description = "There are no banners set up right now. An admin needs to check banners.py (the bot console says what is wrong)."
    for banner in BANNERS[:24]:
        embed.add_field(name=banner["name"], value=shortDescription(banner["description"]), inline=False)
    if len(BANNERS) > 24:
        embed.add_field(name=f"...and {len(BANNERS) - 24} more", value="Start typing in **/banner name:** to find them.", inline=False)
    return embed

def bannerEmbed(banner):
    embed = discord.Embed(title=banner["name"], description=banner["description"][:4096], color=banner["color"])
    if banner["image_url"]:
        embed.set_image(url=banner["image_url"])
    elif banner["image_file"]:
        embed.set_image(url=f"attachment://{banner['image_name']}")  # the file itself gets attached in banner_command
    # contents grouped by rarity, highest first (secret characters that are turned off were already left out when the banners loaded)
    for rarity in RARITY_ORDER:
        chars = banner["pools"][rarity]
        if not chars:
            continue
        rate = banner["rates"].get(rarity, 0)
        if rate:
            title = f"{rarity}: {rate:g}% ({rate / len(chars):.3g}% each)"
        else:
            title = f"{rarity}: 0% (can't be pulled)"
        lines = [("⭐ " if char in banner["featured"] else "") + characterTitles.get(char, char) for char in chars]
        embed.add_field(name=title, value="\n".join(lines)[:1024], inline=False)
    footer = f"Roll on this banner with /roll banner:{banner['name']}"
    if banner["featured"]:
        footer = "⭐ = featured • " + footer
    embed.set_footer(text=footer)
    return embed

@bot.tree.command(name="banner")
@app_commands.describe(name="Which banner to look at (leave it empty to list every banner)")
@app_commands.autocomplete(name=banner_autocomplete)
async def banner_command(interaction: discord.Interaction, name: str = None):
    """Show the banners and what can be pulled from them"""
    # every /banner reply is ephemeral: only the person who used the command sees it, and Discord gives it a "Dismiss message" link
    if name is None:
        await interaction.response.send_message(embed=bannerListEmbed(), ephemeral=True)
        return

    chosen_banner = findBanner(BANNERS, name)
    if not chosen_banner:
        await interaction.response.send_message(banner_not_found_text(name), ephemeral=True)
        return

    embed = bannerEmbed(chosen_banner)
    # pictures from the graphics folder have to be attached to the message, web links don't
    if chosen_banner["image_file"] and os.path.exists(chosen_banner["image_file"]):
        await interaction.response.send_message(embed=embed, file=discord.File(chosen_banner["image_file"], filename=chosen_banner["image_name"]), ephemeral=True)
    else:
        if chosen_banner["image_file"]:
            embed.set_image(url=None)  # the picture was deleted after the bot started
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================================================
# ITEMS: /item store, /item equip and /item show
# ============================================================================
# Players buy items with Grist and put 1 of them in their team's item slot, the item helps the whole team in battle
# Saved on the player: "grist" (a number), "items" (names of the items they own, 1 of each), "equipped_item" (a name or None)
# Players from before items existed don't have those fields yet, a missing field counts as 0 / nothing
# Every /item reply is ephemeral: only the person who used the command sees it

item_group = app_commands.Group(name="item", description="Buy, equip and look at items")


def itemStoreEmbed(user_data):
    owned = ownedItems(user_data)
    rolls = user_data.get("rolls", 0)
    embed = discord.Embed(title="Item Store", description=f"You have **{user_data.get('grist', 0)}** Grist and **{rolls}** roll{'' if rolls == 1 else 's'}.\nPress a button to buy something. Put items on your team with **/item equip**.", color=0x3f48cc)
    if not STORE_ITEMS:
        embed.description += "\nThere are no items for sale right now. An admin needs to check the items collection in MongoDB (the bot console says what is wrong)."
    # rolls can be bought as many times as they like (the price is rollPrice in utils.py)
    embed.add_field(name=f"🎲 Roll • {rollPrice} Grist", value="One roll to use on any banner with **/roll**. You can buy as many as you like.", inline=False)
    embed.add_field(name=f"🎲 {rollBundleAmount} Rolls • {rollBundlePrice} Grist", value=f"{rollBundleAmount} rolls at once for less Grist. You can buy as many as you like.", inline=False)
    for item in STORE_ITEMS[:MAX_STORE_ITEMS]:
        if item["name"] == user_data.get("equipped_item"):
            status = " ⭐ Equipped"
        elif item["name"] in owned:
            status = " ✅ Owned"
        else:
            status = ""
        name = f"{itemTitle(item)} • {item['price']} Grist{status}"[:256]
        value = f"{item['description']}\n**Effect:** {item['effect_text']}"[:1024]
        if len(embed) + len(name) + len(value) > 5800:  # an embed can only hold 6000 characters in total
            embed.add_field(name="...", value="Not every item fits here, but they can all still be bought with the buttons.", inline=False)
            break
        embed.add_field(name=name, value=value, inline=False)
    if os.path.exists(SHOP_IMAGE):
        embed.set_image(url="attachment://shop.png")  # the picture itself gets attached in /item store
    return embed


def itemMessage(item, heading, description):
    """The embed for 1 item, plus its picture attached when it is a file in the bot folder (ready for send_message)."""
    embed = discord.Embed(title=heading[:256], description=description[:4096], color=0x3f48cc)
    embed.add_field(name="Effect:", value=item["effect_text"][:1024], inline=False)
    message = {"embed": embed, "ephemeral": True}
    if item["image_url"]:
        embed.set_thumbnail(url=item["image_url"])
    elif item["image_file"] and os.path.exists(item["image_file"]):
        embed.set_thumbnail(url=f"attachment://{item['image_name']}")
        message["file"] = discord.File(item["image_file"], filename=item["image_name"])
    return message


class ItemStoreView(discord.ui.View):
    """A Buy a Roll button, then 1 buy button per item in the store (items the player already owns are greyed out)."""

    def __init__(self, user_data):
        super().__init__(timeout=180)
        self.store_interaction = None  # the /item store interaction, used to grey out the buttons when they time out
        self.show_buttons(user_data)

    def show_buttons(self, user_data):
        self.clear_items()
        roll_button = discord.ui.Button(label=f"🎲 Buy a Roll ({rollPrice} Grist)", style=discord.ButtonStyle.primary, row=0)
        roll_button.callback = self.buy_roll
        self.add_item(roll_button)
        bundle_button = discord.ui.Button(label=f"🎲 Buy {rollBundleAmount} Rolls ({rollBundlePrice} Grist)", style=discord.ButtonStyle.primary, row=0)
        bundle_button.callback = lambda interaction: self.buy_roll(interaction, rollBundleAmount, rollBundlePrice)
        self.add_item(bundle_button)
        owned = ownedItems(user_data)
        for index, item in enumerate(STORE_ITEMS[:MAX_STORE_ITEMS], start=2):  # start=2 because the 2 roll buttons are first
            emoji = f"{item['emoji']} " if item["emoji"] else ""
            if item["name"] in owned:
                button = discord.ui.Button(label=f"{emoji}{item['name']} (owned)"[:80], style=discord.ButtonStyle.secondary, disabled=True, row=index // 5)
            else:
                button = discord.ui.Button(label=f"{emoji}{item['name']} ({item['price']} Grist)"[:80], style=discord.ButtonStyle.success, row=index // 5)
                button.callback = self.buy_pressed(item["name"])
            self.add_item(button)

    def buy_pressed(self, item_name):
        async def callback(interaction: discord.Interaction):
            item = findItem(STORE_ITEMS, item_name)
            # take the Grist and give the item in 1 update, and only if they can afford it and don't own it yet
            # (so double clicking can't buy it twice or take the Grist below 0)
            bought = inventory_collection.update_one(
                {"user_id": interaction.user.id, "grist": {"$gte": item["price"]}, "items": {"$ne": item["name"]}},
                {"$inc": {"grist": -item["price"]}, "$push": {"items": item["name"]}},
            )
            user_data = inventory_collection.find_one({"user_id": interaction.user.id})
            if not user_data:
                await interaction.response.send_message(f"{interaction.user.mention} No inventory data found. Please contact an Admin immediately.", ephemeral=True)
                return
            if bought.modified_count == 0:
                if item["name"] in ownedItems(user_data):
                    text = f"You already own **{itemTitle(item)}**. Put it on your team with **/item equip**."
                else:
                    grist = user_data.get("grist", 0)
                    text = f"You need **{item['price'] - grist}** more Grist to buy **{itemTitle(item)}**. It costs **{item['price']}** and you have **{grist}**."
                await interaction.response.send_message(text, ephemeral=True)
                return
            # show the new Grist and grey the item out in the store, then confirm the purchase
            self.show_buttons(user_data)
            await interaction.response.edit_message(embed=itemStoreEmbed(user_data), view=self)
            await interaction.followup.send(f"You bought **{itemTitle(item)}** for **{item['price']}** Grist! You have **{user_data.get('grist', 0)}** Grist left.\nPut it on your team with **/item equip**.", ephemeral=True)
        return callback

    async def buy_roll(self, interaction: discord.Interaction, amount=1, price=rollPrice):
        # take the Grist and give the roll(s) in 1 update, and only if they can afford it (so the Grist can't go below 0)
        bought = inventory_collection.update_one(
            {"user_id": interaction.user.id, "grist": {"$gte": price}},
            {"$inc": {"grist": -price, "rolls": amount}},
        )
        what = "a roll" if amount == 1 else f"{amount} rolls"
        user_data = inventory_collection.find_one({"user_id": interaction.user.id})
        if not user_data:
            await interaction.response.send_message(f"{interaction.user.mention} No inventory data found. Please contact an Admin immediately.", ephemeral=True)
            return
        if bought.modified_count == 0:
            grist = user_data.get("grist", 0)
            await interaction.response.send_message(f"You need **{price - grist}** more Grist to buy {what}. It costs **{price}** and you have **{grist}**.", ephemeral=True)
            return
        # show the new Grist and rolls in the store, then confirm the purchase
        self.show_buttons(user_data)
        await interaction.response.edit_message(embed=itemStoreEmbed(user_data), view=self)
        rolls = user_data.get("rolls", 0)
        await interaction.followup.send(f"You bought {what} for **{price}** Grist! You have **{rolls}** roll{'' if rolls == 1 else 's'} and **{user_data.get('grist', 0)}** Grist left.\nUse it with **/roll**.", ephemeral=True)

    async def on_timeout(self):
        # grey out the buttons once the store has been open for 3 minutes
        for child in self.children:
            child.disabled = True
        if self.store_interaction:
            try:
                await self.store_interaction.edit_original_response(view=self)
            except discord.HTTPException:
                pass


@item_group.command(name="store")
async def item_store(interaction: discord.Interaction):
    """Buy items with Grist"""
    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if not user_data:
        await interaction.response.send_message(f"{interaction.user.mention} No inventory data found. Please contact an Admin immediately.", ephemeral=True)
        return
    view = ItemStoreView(user_data)
    message = {"embed": itemStoreEmbed(user_data), "view": view, "ephemeral": True}
    if os.path.exists(SHOP_IMAGE):
        message["file"] = discord.File(SHOP_IMAGE, filename="shop.png")
    await interaction.response.send_message(**message)
    view.store_interaction = interaction


# Suggestions while typing in /item equip: only the items the player owns, plus Nothing to empty the slot
async def owned_item_autocomplete(interaction: discord.Interaction, current: str):
    user_data = inventory_collection.find_one({"user_id": interaction.user.id}) or {}
    typed = current.strip().lower()
    equipped = user_data.get("equipped_item")
    choices = []
    for name in ownedItems(user_data):
        item = findItem(ITEMS, name)
        if item and typed in item["name"].lower():
            label = itemTitle(item) + (" (equipped)" if item["name"] == equipped else "")
            choices.append(app_commands.Choice(name=label[:100], value=item["name"]))
    if equipped and typed in "nothing (unequip your item)":
        choices.append(app_commands.Choice(name="Nothing (unequip your item)", value="unequip"))
    return choices[:25]


@item_group.command(name="equip")
@app_commands.describe(item="The item to put in your team's item slot (pick Nothing to empty the slot)")
@app_commands.autocomplete(item=owned_item_autocomplete)
async def item_equip(interaction: discord.Interaction, item: str):
    """Put one of your items in your team's item slot"""
    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if not user_data:
        await interaction.response.send_message(f"{interaction.user.mention} No inventory data found. Please contact an Admin immediately.", ephemeral=True)
        return
    equipped = user_data.get("equipped_item")
    old_item = findItem(ITEMS, equipped)
    old_title = itemTitle(old_item) if old_item else equipped

    # Nothing empties the item slot, the item stays with their items
    if isUnequip(item):
        if not equipped:
            await interaction.response.send_message("You don't have an item equipped.", ephemeral=True)
            return
        inventory_collection.update_one({"user_id": interaction.user.id}, {"$set": {"equipped_item": None}})
        await interaction.response.send_message(f"Took **{old_title}** off your team. It's back with your items and your item slot is empty.", ephemeral=True)
        return

    chosen = findItem(ITEMS, item)
    owned = ownedItems(user_data)
    if not chosen:
        typed = discord.utils.escape_mentions(discord.utils.escape_markdown(item[:100]))
        yours = ", ".join(f"**{itemTitle(findItem(ITEMS, name))}**" for name in owned if findItem(ITEMS, name))
        text = f"There's no item called **{typed}**. " + (f"Your items are: {yours}" if yours else "You don't own any items yet, buy one with **/item store**.")
        await interaction.response.send_message(text[:2000], ephemeral=True)
        return
    if chosen["name"] not in owned:
        if chosen["in_store"]:
            how = "Buy it with **/item store** first."
        elif chosen["drop_from"]:
            how = f"It can only be found by beating **{chosen['drop_from']}** in /battle."
        else:
            how = "It can't be bought."
        await interaction.response.send_message(f"You don't own **{itemTitle(chosen)}** yet. {how}", ephemeral=True)
        return
    if not user_data.get("team"):
        # same message as /viewteam when there is no team
        embed = discord.Embed(title="No Team Set", description="You have not set a team yet. Use the /team command to set your team of 4 characters.", color=0x3f48cc)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    if equipped == chosen["name"]:
        await interaction.response.send_message(f"**{itemTitle(chosen)}** is already equipped.", ephemeral=True)
        return

    # only equip it if they still own it
    inventory_collection.update_one({"user_id": interaction.user.id, "items": chosen["name"]}, {"$set": {"equipped_item": chosen["name"]}})
    notes = ["Your whole team gets this bonus in battle."]
    if equipped:
        notes.append(f"**{old_title}** went back to your items.")
    if user_data.get("inBattle"):
        notes.append("It starts working in your next battle.")
    await interaction.response.send_message(**itemMessage(chosen, f"Equipped {itemTitle(chosen)}", "\n".join(notes)))


@item_group.command(name="show")
async def item_show(interaction: discord.Interaction):
    """Show the item in your team's item slot"""
    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if not user_data:
        await interaction.response.send_message(f"{interaction.user.mention} No inventory data found. Please contact an Admin immediately.", ephemeral=True)
        return
    equipped = user_data.get("equipped_item")
    item = findItem(ITEMS, equipped)
    if not equipped:
        await interaction.response.send_message("You don't have an item equipped. Buy one with **/item store**, then put it on your team with **/item equip**.", ephemeral=True)
    elif not item:
        name = discord.utils.escape_mentions(discord.utils.escape_markdown(str(equipped)[:100]))
        await interaction.response.send_message(f"Your equipped item **{name}** isn't in the game anymore, so it does nothing. Pick another one with **/item equip**.", ephemeral=True)
    else:
        await interaction.response.send_message(**itemMessage(item, f"Equipped Item: {itemTitle(item)}", item["description"]))


bot.tree.add_command(item_group)


# ============================================================================
# DAILY REWARDS: /daily
# ============================================================================
# The rewards are in daily_rewards.py, daily_helper.py works out the streak and the reward
# Saved on the player: "last_daily" (when they last claimed, a UTC date), "daily_streak" (the day 1-7 they last claimed)
# and "daily_got_sr_noah" (true once /daily gave them Noah Cave, it stays true even if they recycle him)
# Players without those fields have never claimed and can claim straight away. Every /daily reply is ephemeral

def character_card(char):
    """The /char embed of a character (each one has a function above called <character>Embed, like sr_noahEmbed)."""
    make_card = globals().get(f"{char}Embed")
    return make_card() if make_card else discord.Embed(title=characterTitles.get(char, char), color=0x3f48cc)


def add_daily_fields(embed, user_data, now, streak):
    """The streak bar and what the next claim gives (and when)."""
    embed.add_field(name="Streak:", value=f"Day {streak}/{daily_helper.STREAK_DAYS}\n{daily_helper.streakBar(streak)}", inline=False)
    day, reward_text, ready_at, streak_ends = daily_helper.nextClaim(user_data, now)
    when = f"Claim it {daily_helper.discordTime(ready_at)}"
    if day > 1:
        when += f", before {daily_helper.discordTime(streak_ends, 'f')} to keep your streak"
    embed.add_field(name="Next reward:", value=f"Day {day}: {reward_text}\n{when}.", inline=False)


@bot.tree.command(name="daily")
async def daily_command(interaction: discord.Interaction):
    """Claim your daily reward (a 7 day streak)"""
    if not daily_helper.dailyRewardsReady():
        await interaction.response.send_message("Daily rewards aren't set up right now. An admin needs to check daily_rewards.py (the bot console says what is wrong).", ephemeral=True)
        return
    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if not user_data:
        await interaction.response.send_message(f"{interaction.user.mention} No inventory data found. Please contact an Admin immediately.", ephemeral=True)
        return

    now = daily_helper.utcNow()
    plan = daily_helper.planClaim(user_data, now)
    if plan["ready"]:
        # the 24 hour check, the new streak and the reward all happen in 1 update, and only if nothing changed since the
        # player was read above (so 2 /daily at the same moment can only give the reward once)
        claimed = inventory_collection.update_one(daily_helper.claimFilter(interaction.user.id, user_data, plan, now), daily_helper.claimUpdate(plan, now))
        user_data = inventory_collection.find_one({"user_id": interaction.user.id}) or user_data
        if claimed.modified_count == 0:
            plan = daily_helper.planClaim(user_data, now)  # usually another /daily got there first, so now it's too early
            if plan["ready"]:
                await interaction.response.send_message("Your daily reward changed while claiming, please try **/daily** again.", ephemeral=True)
                return

    # too early: nothing in the database changed
    if not plan["ready"]:
        embed = discord.Embed(title="⏳ Too early!", description=f"You already claimed your daily reward. Come back in **{daily_helper.timeLeft(plan['readyAt'], now)}** ({daily_helper.discordTime(plan['readyAt'])}).", color=0x3f48cc)
        add_daily_fields(embed, user_data, now, plan["streak"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    reward = plan["reward"]
    notes = []
    if plan["broken"]:
        notes.append(f"More than {daily_helper.settings['grace']:g} hours passed since your last claim, so your streak was reset to Day 1.")
    if reward["insteadOf"]:
        notes.append(f"You already own (or already got) **{characterTitles.get(reward['insteadOf'], reward['insteadOf'])}**, so you got rolls instead.")
    if reward["character"]:
        # the special announcement: the character's /char card (with its gif) as the reward message
        title = characterTitles.get(reward["character"], reward["character"])
        embed = character_card(reward["character"])
        embed.title = f"🎉 Day {plan['day']} Reward: {title}!"
        embed.description = "\n".join([f"You got {daily_helper.describeReward(reward)}!",
                                       f"**{title}** is now in your inventory. Look at them with **/char** and put them on your team with **/team**."] + notes)
    else:
        embed = discord.Embed(title=f"📅 Daily Reward: Day {plan['day']}/{daily_helper.STREAK_DAYS}", description="\n".join([f"You got {daily_helper.describeReward(reward)}!"] + notes), color=0x3f48cc)
    embed.add_field(name="Grist:", value=str(user_data.get("grist", 0)), inline=True)
    if reward["rolls"]:
        embed.add_field(name="Rolls:", value=str(user_data.get("rolls", 0)), inline=True)
    add_daily_fields(embed, user_data, now, plan["day"])
    await interaction.response.send_message(embed=embed, ephemeral=True)


class View(discord.ui.View):
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="yes_button", emoji="♻️")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="no_button", emoji="🥺")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

class PickView(discord.ui.View):
    """A menu to pick 1 character from (/recycle uses it when more than 1 of the user's characters match)."""
    def __init__(self, options):
        super().__init__()
        self.pick_menu.options = options

    @discord.ui.select(placeholder="Pick which one to recycle", custom_id="pick_menu")
    async def pick_menu(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer()

#Recycle Command
@bot.tree.command()
@app_commands.rename(char_type="type")
@app_commands.describe(character="Which character to recycle", rarity="Only this rarity (leave it empty to pick from every rarity)", amount="How many to recycle",
                       char_type="The 1 card to recycle (leave it empty to pick from a menu if more than 1 match)")
@app_commands.choices(character=character_group_choices, rarity=rarity_choices)
@app_commands.autocomplete(char_type=char_type_autocomplete)
async def recycle(ctx: discord.Interaction, character: app_commands.Choice[str], amount: int, rarity: app_commands.Choice[str] = None, char_type: str = None):
    # SSR = 100 points to counter, SR = 5 points to counter, R = 1 point to counter
    # 10 r's for 1 roll, 2 sr for 2 rolls and 1 ssr for 10 rolls
    # if counter = 10 inside mongodb per user then give 1 roll otherwise update and tell user to recycle more
    """Recycle Characters for Rolls"""
    # Example: /recycle abraize 10 R
    # then show embed saying "Would you like to recycle" [character] x [amount], "you will gain [calculated rolls] rolls" (calculated rolls may be in decimal format for example if they recycle 15 r's then it will say 1.5 rolls)

    # a 0 or negative amount used to give the user free characters instead of taking them away
    if amount < 1:
        await ctx.response.send_message("You have to recycle at least **1** character.", ephemeral=True)
        return

    # Every version of the character (only the chosen rarity if one was picked), same as /char
    char_dev_names = [char for char in character_groups[character.value] if rarity is None or getRarity(char) == rarity.value]
    if not char_dev_names:
        await ctx.response.send_message(f"**{character.name}** has no **{rarity.value}** characters!", ephemeral=True)
        return

    # Only the 1 card picked in type (the menu gives its dev name, typing the full title out works too), same as /char
    if char_type is not None:
        char_dev_names = [char for char in char_dev_names if char_type.strip().lower() in (char, characterTitles[char].lower())]
        if not char_dev_names:
            typed = discord.utils.escape_mentions(discord.utils.escape_markdown(char_type[:100]))
            rarity_text = f" **{rarity.value}**" if rarity else ""
            await ctx.response.send_message(f"**{typed}** is not one of **{character.name}'s**{rarity_text} cards! Pick one from the **type** menu.", ephemeral=True)
            return

    async def send(**message):
        """The first message answers the command, after the pick menu it replaces the menu instead."""
        if ctx.response.is_done():
            await ctx.edit_original_response(content=message.get("content"), embed=message.get("embed"), view=message.get("view"))
        else:
            await ctx.response.send_message(**message, ephemeral=True)

    user_data = inventory_collection.find_one({"user_id": ctx.user.id})
    if user_data:
        inventory = user_data.get("inventory", {})
        owned = [char for char in char_dev_names if inventory.get(char, 0) >= 1]

        # Check if user owns the character
        if not owned:
            if "sssr_max" in char_dev_names:
                embed = discord.Embed(title="You Can't Recycle What You Don't Know", color=0x000000)
                await ctx.response.send_message(embed=embed, ephemeral=True)
                await asyncio.sleep(2)
                await ctx.delete_original_response()
                return
            await ctx.response.defer(ephemeral=True)
            await ctx.followup.send(file=discord.File(otherImages["no_own_png"]), ephemeral=True)
            return

        # More than 1 match (like Abraize's 2 R's) and no type was picked, so the user picks which one from a menu
        char_dev_name = owned[0]
        if len(owned) > 1:
            options = [discord.SelectOption(label=characterTitles.get(char, char)[:100], value=char, description=f"{getRarity(char)}, you have x{inventory[char]}")
                       for char in owned[:25]]
            await ctx.response.send_message(f"Which **{character.name}** do you want to recycle **x{amount}** of?", view=PickView(options), ephemeral=True)
            menu = await ctx.original_response()

            def picked(interaction: discord.Interaction):
                return (interaction.user.id == ctx.user.id
                        and interaction.message is not None and interaction.message.id == menu.id
                        and (interaction.data or {}).get("custom_id") == "pick_menu")
            try:
                pick = await bot.wait_for("interaction", check=picked, timeout=30.0)
            except asyncio.TimeoutError:
                await send(content="Recycling timed out. Please try again.")
                return
            char_dev_name = pick.data["values"][0]

        char_title = characterTitles.get(char_dev_name, char_dev_name)
        char_count = inventory.get(char_dev_name, 0)

        if char_count >= amount:
            # Determine points based on character rarity (specialChar characters are SSR too)
            if char_dev_name in ssrChar or char_dev_name in specialChar:
                points = 100 * amount
            elif char_dev_name in srChar:
                points = 5 * amount
            elif char_dev_name in rChar:
                points = 1 * amount
            else:
                await send(content=f"Character **{char_title}** does not exist!")
                return

            # Calculate rolls to add
            # rolls to add must be integer never float
            current_points = user_data.get("counter", 0)
            total_points = current_points + points
            rolls_to_add = total_points // 10  # 10 points = 1 roll

            # embed awaiting user confirmation by button click yes or no to recycle or not
            embed = discord.Embed(title=f"Would you like to recycle {char_title} x {amount}? ", color=0x3f48cc)
            await send(embed=embed, view=View())
            prompt = await ctx.original_response()

            # if view is custom id of yes button then proceed with recycling
            # (only buttons on THIS message count, and other interactions like slash commands don't have a custom_id at all)
            def check(interaction: discord.Interaction):
                return (interaction.user.id == ctx.user.id
                        and interaction.message is not None and interaction.message.id == prompt.id
                        and (interaction.data or {}).get("custom_id") in ["yes_button", "no_button"])
            try:
                interaction = await bot.wait_for("interaction", check=check, timeout=10.0)

                if interaction.data["custom_id"] == "yes_button":
                    # Proceed with recycling
                    # Counter examples: if points = 20 then add 2 rolls and counter = 0, if points = 15 then add 1 roll and counter = 5, if points = 7 then add 0 rolls and counter = 7
                    # if points = 5 and they recycled 1 sr which is 5 points then add 1 roll and set coutner to 0
                    # Remove full tens from the counter and convert them into rolls
                    # (counter is read again because it could have changed while the buttons were up)
                    current_points = (inventory_collection.find_one({"user_id": ctx.user.id}) or {}).get("counter", 0)
                    new_total = current_points + points
                    rolls_gain = new_total // 10
                    new_counter = new_total % 10

                    # only recycle if they still have enough (stops 2 recycle prompts from recycling the same characters twice)
                    recycled = inventory_collection.update_one(
                        {"user_id": ctx.user.id, f"inventory.{char_dev_name}": {"$gte": amount}},
                        {
                            "$inc": {
                                f"inventory.{char_dev_name}": -amount,
                                "rolls": rolls_gain
                            },
                            "$set": {
                                "counter": new_counter
                            }
                        }
                    )
                    if recycled.modified_count == 0:
                        await ctx.followup.send(f"You no longer have enough **{char_title}'s** to recycle **x{amount}**.", ephemeral=True)
                        await ctx.edit_original_response(view=None)
                        return

                    # if character count goes to 0 then remove character from inventory (and from their team so they can't battle with it)
                    updated_user_data = inventory_collection.find_one({"user_id": ctx.user.id})
                    updated_inventory = updated_user_data.get("inventory", {})
                    if updated_inventory.get(char_dev_name, 0) == 0:
                        inventory_collection.update_one(
                            {"user_id": ctx.user.id},
                            {"$unset": {f"inventory.{char_dev_name}": ""}, "$pull": {"team": char_dev_name}}
                        )
                   # user_data = inventory_collection.find_one({"user_id": ctx.user.id})


                  #  if rolls_to_add == 0:
                    embed = discord.Embed(title=f"Recycled **{char_title} x{amount}**. Your total rolls is **{updated_user_data.get('rolls', 0)}** rolls.", color=0x3f48cc)
                    embed.set_image(url=otherImages["recycle_gif"])
                    await ctx.followup.send(embed=embed, ephemeral=True)
                else:  # no_button pressed
                    await ctx.followup.send("Recycling cancelled.", ephemeral=True)
            except asyncio.TimeoutError:
                await ctx.followup.send("Recycling timed out. Please try again.", ephemeral=True)
            # take the Yes / No buttons away once they've been answered or timed out
            await ctx.edit_original_response(view=None)


        else:
            await send(content=f"You do not have enough **{char_title}'s** to recycle **x{amount}**. You currently have **x{char_count}**.")
    else:
        await ctx.response.send_message(f"{ctx.user.mention} No inventory data found. Please contact an Admin immediately.", ephemeral=True)

@bot.tree.command()
async def viewteam(ctx: discord.Interaction):
    """View your Team of maximum 4 Characters"""
    user_data = inventory_collection.find_one({"user_id": ctx.user.id})
    if user_data:
        team = user_data.get("team", [])
        if team:
            embed = discord.Embed(title=f"{ctx.user.display_name}'s Team", color=0x3f48cc)
            team_titles = [characterTitles.get(char, char) for char in team]
            for i, title in enumerate(team_titles, 1):
                embed.add_field(name=f"Slot {i}", value=title, inline=False)
            # the team's item slot (/item equip)
            equipped = findItem(ITEMS, user_data.get("equipped_item"))
            embed.add_field(name="Item", value=itemTitle(equipped) if equipped else "Empty (use /item equip)", inline=False)
            await ctx.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="No Team Set", description="You have not set a team yet. Use the /team command to set your team of 4 characters.", color=0x3f48cc)
            await ctx.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Error", description=f"{ctx.user.mention} No inventory data found.", color=0xff0000)
        await ctx.response.send_message(embed=embed)

# there cannot be 2 of the same character for example /team r_abraize r_abraize r_noah r_freeman is invalid and /team r_abraize sr_abraize r_noah r_freeman is invalid
@bot.tree.command()
@app_commands.choices(
    char1=character_choices,
    char2=character_choices,
    char3=character_choices,
    char4=character_choices
)
async def team(ctx: discord.Interaction, char1: app_commands.Choice[str] = None, char2: app_commands.Choice[str] = None, char3: app_commands.Choice[str] = None, char4: app_commands.Choice[str] = None):
    """Set your Team of maximum 4 Characters"""
    team_choices = [c for c in [char1, char2, char3, char4] if c]

    if not team_choices:
        await ctx.response.send_message("Please provide at least one character to add to your team.")
        return

    # Convert choices to dev names
    team_chars = [c.value for c in team_choices]
    team_titles = [c.name for c in team_choices]

    # Check for duplicates
    if len(team_chars) != len(set(team_chars)):
        await ctx.response.send_message("You cannot have duplicate characters in your team!")
        return

    # cannot have 2 versions of the same character for example r_abraize and ssr_abraize
    base_names = set()
    for char in team_chars:
        parts = char.split('_', 1)
        base_name = parts[1] if len(parts) > 1 else char
        base_name = base_name.rstrip("0123456789")  # r_abraize2 is still Abraize
        if base_name in base_names:
            await ctx.response.send_message(f"You cannot have multiple versions of the same character in your team! **({base_name})**")
            return
        base_names.add(base_name)

    # Check if user owns the characters
    user_data = inventory_collection.find_one({"user_id": ctx.user.id})
    if user_data:
        inventory = user_data.get("inventory", {})
        for i, char in enumerate(team_chars):
            if inventory.get(char, 0) < 1:
                if char == "sssr_max":
                    embed = discord.Embed(title="Is It On Your Team?", color=0x000000)
                    await ctx.response.send_message(embed=embed)
                    await asyncio.sleep(2)
                    await ctx.delete_original_response()
                    return
                await ctx.response.defer()
                await ctx.followup.send(file=discord.File(otherImages["no_own_png"]))
                return
    else:
        # before this it said "Team Updated Successfully!" even though nothing was saved
        await ctx.response.send_message(f"{ctx.user.mention} No inventory data found. Please contact an Admin immediately.")
        return

    # Update team in database
    inventory_collection.update_one(
        {"user_id": ctx.user.id},
        {"$set": {"team": team_chars}}
    )

    # show titles of characters in team
    await ctx.response.send_message("Team Updated Successfully! Your team order is:\n" + "\n".join(team_titles))

# ============================================================================
# CHARACTER ABILITIES MAPPING
# ============================================================================
# Maps character names to their abilities (skills 1, 2, 3, and optional ultimate)
# Format: character_name: [skill1, skill2, skill3] or [skill1, skill2, skill3, ultimate]

# Battle Command - PvE
# The battle screen has 8 total slots, 4 for the player's team and 4 for the enemy team (enemy team does not have to fill all 4 slots)
# There are multiple enemy types to fight
# Currently: Ruffian, Grunt, Spearman, Agent
# There will be multiple backgrounds to choose from but currently will be randomly decided
# Using Pillow (PIL) we will create a battle screen image that shows the player's team on the right and the enemy team on the left with background

# ============================================================================
# DYNAMIC CHARACTER POSITIONING SYSTEM
# ============================================================================
#
# This system ensures characters are properly placed on the battle screen
# based on their "feet" position, preventing cutoff issues.
#
# HOW TO ADD A NEW CHARACTER:
# 1. Add the character's PNG file to the repository
# 2. Add an entry to characterImages dictionary (already done for most)
# 3. Calculate the character's feet position:
#    - Open the character image
#    - Find the width and height (e.g., using PIL: Image.open("char.png").size)
#    - Default feet position is (width/2, height) - bottom-middle of image
#    - Add entry to characterFeet dictionary below
# 4. If the character floats, add an entry to characterFloatingOffset
#    - Use negative values to move up (floating)
#    - Use positive values to move down
#
# HOW TO FINE-TUNE CHARACTER POSITIONING:
# 1. Run the battle command and examine the output
# 2. If a character's feet don't align properly:
#    - Adjust the X coordinate in characterFeet to shift left/right
#    - Adjust the Y coordinate in characterFeet to change where feet are
# 3. If a character should float or sink:
#    - Add/modify entry in characterFloatingOffset
#
# EXAMPLE:
# For a character image that is 100x200 pixels:
# - Default feet position would be (50, 200) - center bottom
# - If feet are actually 10 pixels from the left: use (10, 200)
# - If character should float 15 pixels up: add to characterFloatingOffset with value -15
# ============================================================================

# Character "feet" positions - where the character's feet/bottom-middle are located within their sprite
# Format: (x_offset_from_left, y_offset_from_top)
# By default, feet are at (width/2, height), but can be adjusted manually for fine-tuning
characterFeet = {
    "r_abraize": (53, 252),
    "r_abraize2": (57, 226),
    "sr_abraize": (70, 209),
    "ssr_abraize": (87, 235),
    "r_trey": (52, 247),
    "sr_trey": (68, 263),
    "ssr_trey": (72, 291),
    "r_noah": (39, 214),
    "sr_noah": (61, 184),
    "r_freeman": (49, 241),
    "sr_freeman": (57, 206),
    "ssr_jayden": (56, 278),
    "r_stephen": (52, 215),
    "sr_stephen": (72, 222),
    "sr_homestuck": (117, 228),
    "ssr_scottie": (55, 283),
    "r_homestuck": (66, 239),
    "r_max": (66, 220),
    "r_jaiden": (49, 257),
    "sr_binktop": (88, 175),  # the foot he stands on (the other leg is drawn further back)
}

# Special Y-axis adjustments for floating characters
# Negative values move character UP (floating effect)
# Positive values move character DOWN (sinking effect)
characterFloatingOffset = {
    "ssr_scottie": -20,  # Floating character - moves up 20 pixels
}

# Target ground positions for team slots on the battle screen
# These are the positions where character feet should be placed
# Format: (x, y) - coordinates on the background where feet touch the ground
# Note: These use 0-based indexing (slot_index 0-3 in code)
teamSlotGroundPositions = [
    (470, 450),  # Index 0 (Slot 1 in /viewteam) - Down
    (360, 380),  # Index 1 (Slot 2 in /viewteam) - Left
    (580, 360),  # Index 2 (Slot 3 in /viewteam) - Right
    (440, 340),  # Index 3 (Slot 4 in /viewteam) - Up
]

def draw_battle_screen(user_id, scene_base, team, summoned=()):
    """The battle picture: the background with the starting enemies (scene_base), then the summoned enemies that are
    still standing (Garry's Mod's Addonshields, in their summonSpots from utils.py), then the team in front.
    Saved as battle_screen_<user id>.png, the path is returned."""
    image = scene_base.copy()
    background_size = image.size

    # summoned enemies, the ones further back (higher up) first so the closer ones get drawn over them
    placed = []
    for kind, slot in summoned:
        layout = summonSpots.get(kind)
        if layout and os.path.exists(enemyImages.get(kind, "")):
            placed.append((layout["spots"][slot % len(layout["spots"])], kind, layout.get("scale", 1)))
    for spot, kind, scale in sorted(placed, key=lambda place: place[0][1]):
        summon_image = Image.open(enemyImages[kind])
        if scale != 1:
            summon_image = summon_image.resize((round(summon_image.width * scale), round(summon_image.height * scale)), Image.LANCZOS)
        image.paste(summon_image, spot, summon_image)

    # Place team characters dynamically based on their feet positions
    # Reverse order so slot 1 (index 0) is pasted last and appears on top
    for i, char_name in reversed(list(enumerate(team))):
        if char_name in characterImages:
            char_image_path = characterImages[char_name]
            if os.path.exists(char_image_path):
                char_image = Image.open(char_image_path)
                char_position = calculate_character_position(char_name, i, background_size)
                image.paste(char_image, char_position, char_image)

    # save the combined image to a new file
    # save to new file based on discord id, example: battle_screen_123456789.png
    combined_image_path = f"./graphics/battle/battle_screen_{user_id}.png"
    image.save(combined_image_path)
    return combined_image_path


def calculate_character_position(char_name, slot_index, background_size):
    """
    Calculate the paste position for a character based on their feet position.

    Args:
        char_name: Character identifier (e.g., "r_abraize")
        slot_index: Team slot index (0-3)
        background_size: Tuple of (width, height) of the background image

    Returns:
        Tuple of (x, y) coordinates where the character image should be pasted
    """
    # Get the target ground position for this slot
    target_x, target_y = teamSlotGroundPositions[slot_index]

    # Get the character's feet position within their sprite
    # If not defined, calculate default position from the image
    if char_name not in characterFeet:
        char_image_path = characterImages.get(char_name)
        if char_image_path and os.path.exists(char_image_path):
            char_img = Image.open(char_image_path)
            char_width, char_height = char_img.size
            # Default: bottom-middle of the image
            feet_x, feet_y = char_width // 2, char_height
        else:
            # Fallback if image doesn't exist
            feet_x, feet_y = 0, 0
    else:
        feet_x, feet_y = characterFeet[char_name]

    # Calculate where to paste the character so their feet align with the target
    paste_x = target_x - feet_x
    paste_y = target_y - feet_y

    # Apply floating offset if this character is a floater
    floating_offset = characterFloatingOffset.get(char_name, 0)
    paste_y += floating_offset

    # Prevent cutoff on the edges
    char_image_path = characterImages.get(char_name)
    if char_image_path and os.path.exists(char_image_path):
        char_img = Image.open(char_image_path)
        char_width, char_height = char_img.size

        # Ensure character doesn't go off the right edge
        if paste_x + char_width > background_size[0]:
            paste_x = background_size[0] - char_width

        # Ensure character doesn't go off the bottom edge
        if paste_y + char_height > background_size[1]:
            paste_y = background_size[1] - char_height

        # Ensure character doesn't go off the left edge
        if paste_x < 0:
            paste_x = 0

        # Ensure character doesn't go off the top edge
        if paste_y < 0:
            paste_y = 0

    return (int(paste_x), int(paste_y))

# ============================================================================
# BATTLE EMBED + BUTTONS
# ============================================================================
# battle.py does all of the battle logic, this part only shows it to the user:
#   - the embed shows everyone's hp, their buffs/debuffs and the battle log (updated after every turn)
#   - the buttons are the current character's abilities, target buttons (Options F / G), Skip and Retreat

BATTLE_TIMEOUT = 300  # seconds without a button press before the battle ends by itself

# reason numbers for endBattle() in battle.py
BATTLE_END_REASONS = {"retreat": 0, "defeat": 1, "victory": 2, "timeout": 3, "error": 4}

# text + embed color for every way a battle can end
BATTLE_ENDINGS = {
    "victory": ("🏆 **Victory!** Your team won the battle!", 0x2ecc71),
    "defeat": ("☠️ **Defeat...** Your whole team got knocked out.", 0xe74c3c),
    "retreat": ("🏳️ You retreated from the battle!", 0x95a5a6),
    "timeout": ("⌛ The battle ended because no buttons were pressed for 5 minutes.", 0x95a5a6),
    "error": ("⚠️ Something went wrong so the battle was ended. The error is in the bot console.", 0xe74c3c),
}


def hp_bar(hp, max_hp, length=10):
    """Text hp bar like ██████░░░░"""
    filled = round(length * hp / max_hp) if max_hp > 0 else 0
    if hp > 0:
        filled = max(1, filled)  # never looks empty while still standing
    return "█" * filled + "░" * (length - filled)


def format_battle_units(rows, hide_hp=False):
    """One line per character with their hp bar, plus a line under it for their buffs/debuffs.
    hide_hp (Noah's Larpometer) shows ??? instead of the hp bar and numbers."""
    lines = []
    for row in rows:
        if not row["alive"]:
            lines.append(f"~~{row['name']}~~ 💀")
            continue
        marker = "▶ " if row["current"] else ""
        hp = "`??????????` ???" if hide_hp else f"`{hp_bar(row['hp'], row['maxHp'])}` {row['hp']}/{row['maxHp']}"
        lines.append(f"{marker}**{row['name']}** {hp}")
        if row["effects"]:
            effects = row["effects"] if len(row["effects"]) <= 150 else row["effects"][:147] + "..."
            lines.append(f"   ↳ {effects}")
    return "\n".join(lines)[:1024] or "\u200b"


def newest_lines(lines, limit=1024):
    """Embed fields can only hold 1024 characters, so keep the newest log lines that fit."""
    kept, size = [], 0
    for line in reversed(lines):
        if len(line) > limit:
            line = line[:limit - 3] + "..."
        if size + len(line) + 1 > limit:
            break
        kept.append(line)
        size += len(line) + 1
    return "\n".join(reversed(kept)) or "\u200b"


def build_battle_embed(user_id, enemy_name, prompt=None, ending=None):
    """The battle embed: whose turn it is, hp of both teams, the battle log and the battle screen image."""
    summary = getBattleSummary(user_id)
    embed = discord.Embed(title=f"⚔️ Battle vs {enemy_name} — Round {summary['round']}", color=0x3f48cc)
    if ending:
        embed.description, embed.colour = BATTLE_ENDINGS[ending]
    else:
        embed.description = prompt or f"It's **{summary['turn']}**'s turn, pick an ability!"
    embed.add_field(name="Your Team", value=format_battle_units(summary["players"], summary["hideHP"]), inline=False)
    enemies_text = format_battle_units(summary["enemies"], summary["hideHP"])
    if summary["field"]:
        enemies_text = (enemies_text + "\n" + summary["field"])[:1024]
    embed.add_field(name="Enemies", value=enemies_text, inline=False)
    embed.add_field(name="Battle Log", value=newest_lines(summary["log"]), inline=False)
    # the image is already attached to the message, pointing at it again keeps it inside the embed after edits
    embed.set_image(url=f"attachment://battle_screen_{user_id}.png")
    embed.set_footer(text="(2t) = turns left • The battle ends after 5 minutes without a button press")
    return embed


# it seems that you need to have a "view" to allow buttons
class BattleView(discord.ui.View):
    """Buttons for one battle. They get rebuilt every turn from what battle.py says the current character can do."""

    def __init__(self, user_id: int, enemy_name: str, grist_reward: int = 0, enemy_kind: str = None):
        super().__init__(timeout=BATTLE_TIMEOUT)
        self.user_id = user_id
        self.enemy_name = enemy_name
        self.grist_reward = grist_reward  # Grist for winning (gristRewards in utils.py)
        self.enemy_kind = enemy_kind      # the /battle choice ("Jack Noir"), items with that drop_from can drop
        self.last_interaction = None  # newest interaction on this battle, used to edit the message if the battle times out
        self.layout = 0               # goes up every time the buttons change so clicks on old buttons get ignored
        self.scene = None             # (background + starting enemies, team) from /battle, for drawing the picture again
        self.drawn_summons = []       # the summoned enemies on the picture right now (Garry's Mod's Addonshields)
        self.show_ability_buttons()

    def show_ability_buttons(self):
        """Row 1: the current character's abilities (greyed out while on cooldown), row 2: Skip and Retreat."""
        self.layout += 1
        self.clear_items()
        for index, ability in enumerate(getAbilityButtons(self.user_id)):
            label = ability["name"] if ability["ready"] else f"{ability['name']} ({ability['note']})"
            button = discord.ui.Button(label=label[:80], style=discord.ButtonStyle.primary, disabled=not ability["ready"], row=0)
            button.callback = self.ability_pressed(index, self.layout)
            self.add_item(button)
        self.add_retreat_button()

    def show_target_buttons(self, ability_index, targets):
        """Options F / G: one button per possible target, plus Back, Skip and Retreat."""
        self.layout += 1
        self.clear_items()
        for unit, name in targets:
            button = discord.ui.Button(label=name[:80], style=discord.ButtonStyle.success, row=0)
            button.callback = self.target_pressed(ability_index, unit, self.layout)
            self.add_item(button)
        back = discord.ui.Button(label="Back", style=discord.ButtonStyle.secondary, row=1)
        back.callback = self.back_pressed(self.layout)
        self.add_item(back)
        self.add_retreat_button()

    def add_retreat_button(self):
        # Skip goes right before Retreat so it sits directly to its left
        skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.success, row=1)
        skip.callback = self.skip_pressed(self.layout)
        self.add_item(skip)
        retreat = discord.ui.Button(label="Retreat", style=discord.ButtonStyle.danger, row=1)
        retreat.callback = self.retreat_pressed
        self.add_item(retreat)

    async def check_press(self, interaction: discord.Interaction, layout=None):
        """Only the person battling can press the buttons, and only the newest ones."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return False
        if not battleExists(self.user_id) or (layout is not None and layout != self.layout):
            await interaction.response.send_message("Those buttons are out of date!", ephemeral=True)
            return False
        self.last_interaction = interaction
        return True

    def ability_pressed(self, ability_index, layout):
        async def callback(interaction: discord.Interaction):
            if not await self.check_press(interaction, layout):
                return
            # moves with Option F / G need a target picked first when there is more than 1 choice
            targets = getTargetChoices(self.user_id, ability_index)
            if targets:
                ability_name = getAbilityButtons(self.user_id)[ability_index]["name"]
                self.show_target_buttons(ability_index, targets)
                embed = build_battle_embed(self.user_id, self.enemy_name, prompt=f"Who should **{ability_name}** target?")
                await interaction.response.edit_message(embed=embed, view=self)
                return
            await self.take_turn(interaction, ability_index, None)
        return callback

    def target_pressed(self, ability_index, target, layout):
        async def callback(interaction: discord.Interaction):
            if not await self.check_press(interaction, layout):
                return
            await self.take_turn(interaction, ability_index, target)
        return callback

    def back_pressed(self, layout):
        async def callback(interaction: discord.Interaction):
            if not await self.check_press(interaction, layout):
                return
            self.show_ability_buttons()
            await interaction.response.edit_message(embed=build_battle_embed(self.user_id, self.enemy_name), view=self)
        return callback

    def skip_pressed(self, layout):
        async def callback(interaction: discord.Interaction):
            if not await self.check_press(interaction, layout):
                return
            # an Option Z move: only the current character's action is skipped, then the battle carries on like after any move
            await self.take_turn(interaction, "skip", None)
        return callback

    async def retreat_pressed(self, interaction: discord.Interaction):
        """Retreat button to end the battle."""
        if not await self.check_press(interaction):
            return
        await self.finish(interaction, "retreat")

    async def take_turn(self, interaction, ability_index, target):
        # battle.py does the move, then the rest of the turn order (enemy turn + end of round included)
        advanceBattle(self.user_id, ability_index, target)
        result = getBattleResult(self.user_id)
        if result:
            await self.finish(interaction, result)
            return
        self.show_ability_buttons()
        await interaction.response.edit_message(embed=build_battle_embed(self.user_id, self.enemy_name), view=self, **self.redraw_scene())

    async def finish(self, interaction, ending):
        embed = build_battle_embed(self.user_id, self.enemy_name, ending=ending)  # before battle.py throws the battle away
        scene = self.redraw_scene()
        embed.description += self.end_battle(ending)
        await interaction.response.edit_message(embed=embed, view=self, **scene)

    def redraw_scene(self):
        """When summoned enemies (Garry's Mod's Addonshields) show up or go away the battle picture gets drawn again.
        Returns the new picture for edit_message, or nothing when the picture didn't change."""
        if not self.scene or not battleExists(self.user_id):
            return {}
        summoned = getBattleSummary(self.user_id)["summoned"]
        if summoned == self.drawn_summons:
            return {}
        self.drawn_summons = summoned
        return {"attachments": [discord.File(draw_battle_screen(self.user_id, *self.scene, summoned))]}

    def end_battle(self, ending):
        """Cleans up the battle in battle.py, sets inBattle back to false and disables every button.
        A victory also gives the Grist reward, the text about it is returned for the embed."""
        # grist_bonus items (Noah's Larpometer), asked before battle.py throws the battle (and its equipped item) away
        bonus, bonus_item = gristBonus(self.user_id, self.grist_reward)
        if battleExists(self.user_id):
            endBattle(self.user_id, BATTLE_END_REASONS[ending])
        # set in mongodb battle over (and add the Grist in the same update when they won)
        update = {"$set": {"inBattle": False}}
        reward_text = ""
        if ending == "victory" and self.grist_reward:
            update["$inc"] = {"grist": self.grist_reward + bonus}
            bonus_text = f" (+{bonus} from **{itemTitle(bonus_item)}**)" if bonus else ""
            reward_text = f"\n💰 You got **{self.grist_reward + bonus}** Grist{bonus_text}! Spend it in **/item store**."
        inventory_collection.update_one(
            {"user_id": self.user_id},
            update
        )
        # items that can drop from this enemy (their drop_from), only given if they don't own it yet (1 of each item)
        if ending == "victory":
            for dropped in rollItemDrops(self.enemy_kind):
                got = inventory_collection.update_one(
                    {"user_id": self.user_id, "items": {"$ne": dropped["name"]}},
                    {"$push": {"items": dropped["name"]}}
                )
                if got.modified_count:
                    reward_text += f"\n🎁 **{self.enemy_kind}** dropped **{itemTitle(dropped)}**! Put it on your team with **/item equip**."
        for item in self.children:
            item.disabled = True
        self.stop()
        return reward_text

    async def on_timeout(self):
        if not battleExists(self.user_id):
            return
        embed = build_battle_embed(self.user_id, self.enemy_name, ending="timeout")
        self.end_battle("timeout")
        if self.last_interaction:
            try:
                await self.last_interaction.edit_original_response(embed=embed, view=self)
            except discord.HTTPException as error:
                print("Could not update the timed out battle message:", error)

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        # a bug in the battle code ends the battle instead of leaving the user stuck "in battle"
        print(f"Battle error for user {self.user_id}:")
        traceback.print_exception(type(error), error, error.__traceback__)
        embed = None
        if battleExists(self.user_id):
            try:
                embed = build_battle_embed(self.user_id, self.enemy_name, ending="error")
            except Exception:
                embed = None
        self.end_battle("error")
        try:
            if interaction.response.is_done():
                await interaction.followup.send(BATTLE_ENDINGS["error"][0], ephemeral=True)
            elif embed:
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.edit_message(content=BATTLE_ENDINGS["error"][0], view=self)
        except discord.HTTPException:
            pass


@bot.tree.command(name = "battle")
@app_commands.choices(enemies=[
    app_commands.Choice(name="Ruffian", value="Ruffian"),
    app_commands.Choice(name="Grunt", value="Grunt"),
    app_commands.Choice(name="Spearman", value="Spearman"),
    app_commands.Choice(name="Agent", value="Agent"),
    app_commands.Choice(name="Jack Noir", value="Jack Noir"),
    app_commands.Choice(name="Garry's Mod", value="Garry's Mod"),
])
async def battle(interaction: discord.Interaction,enemies:app_commands.Choice[str]):
    """Battle an Enemy"""
    # Get user's team
    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if not user_data:
        await interaction.response.send_message(f"{interaction.user.mention} No inventory data found. Please contact an Admin immediately.")
        return

    # Check if user is already in a battle
    if user_data.get("inBattle", False):
        await interaction.response.send_message("You are already in a battle! Please finish your current battle before starting a new one.", ephemeral=True)
        return

    team = user_data.get("team", [])
    if len(team) < 1:
        await interaction.response.send_message("You are not ready to fight!\nSet a team first using the /team command otherwise you will perish!")
        return

    # characters that were recycled after the team was set, or that have no battle abilities yet (like the secret character)
    # used to crash the battle or let people fight with characters they don't own anymore
    inventory = user_data.get("inventory", {})
    not_owned = [char for char in team if inventory.get(char, 0) < 1]
    cant_fight = [char for char in team if char not in characterAbilities]
    if not_owned or cant_fight:
        problems = [f"You don't own **{characterTitles.get(char, char)}** anymore." for char in not_owned]
        problems += [f"**{characterTitles.get(char, char)}** can't battle yet." for char in cant_fight if char not in not_owned]
        await interaction.response.send_message("\n".join(problems) + "\nPick a new team with the /team command first!")
        return

    # Garry's Mod has his own background (enemyBackgrounds in utils.py), every other fight is on purple2
    background_file = backgrounds[enemyBackgrounds.get(enemies.value, DEFAULT_BACKGROUND)]

    # comnbine background and sprite images ontop one another using PIL
    background_image = Image.open(background_file)

    # Place enemies first (in the background layer)
    enemy_count = 1  # Default to 1 enemy
    enemyList = []

    if enemies.name == "Grunt":
        enemy_image = Image.open(enemyImages[enemies.name])
        background_image.paste(enemy_image, enemySpots[enemies.name], enemy_image)
        enemyList.append(enemies.name)
    elif enemies.name == "Ruffian":
        # 50/50 if 2 or 1 ruffians show up
        roll = random.random()
        if roll < 0.5:
            enemy_count = 2
            ruffianB = Image.open(enemyImages["RuffianBack"])
            ruffianF = Image.open(enemyImages["RuffianFront"])
            background_image.paste(ruffianB, enemySpots["RuffianBack"], ruffianB)
            background_image.paste(ruffianF, enemySpots["RuffianFront"], ruffianF)
            for i in range(enemy_count):
                enemyList.append(f"Ruffian{i+1}")
        else:
            ruffianB = Image.open(enemyImages["RuffianBack"])
            background_image.paste(ruffianB, enemySpots["RuffianSolo"], ruffianB)
            enemyList.append("Ruffian1")
    else:
        enemy_image = Image.open(enemyImages[enemies.name])
        background_image.paste(enemy_image, enemySpots[enemies.name], enemy_image)
        enemyList.append(enemies.name)

    for a in enemyList:
        print("ENEMY IN LIST:", a)

    # the background + starting enemies is kept, so enemies summoned later (Garry's Mod's Addonshields) can be drawn in
    # between them and the team, then the team goes on top and it gets saved (draw_battle_screen)
    scene_base = background_image.copy()
    combined_image_path = draw_battle_screen(interaction.user.id, scene_base, team)

    # battle.py sets up the turn order, hp and abilities for this user's battle (plus the equipped item's bonuses)
    startBattle(interaction.user.id, team, enemyList, user_data.get("equipped_item"))
    # set inbattle in mongodb
    inventory_collection.update_one(
        {"user_id": interaction.user.id},
        {"$set": {"inBattle": True}}
    )

    enemy_title = enemies.name if len(enemyList) == 1 else f"{len(enemyList)} {enemies.name}s"
    # Grist for winning comes from gristRewards in utils.py ("Ruffian x2" when 2 ruffians showed up)
    reward_name = enemies.name if len(enemyList) == 1 else f"{enemies.name} x{len(enemyList)}"
    if reward_name not in gristRewards:
        print(f"No Grist reward for {reward_name!r} in gristRewards (utils.py), winning this battle gives 0 Grist")
    battle_view = BattleView(interaction.user.id, enemy_title, gristRewards.get(reward_name, 0), enemies.name)
    battle_view.scene = (scene_base, team)  # for drawing the picture again when enemies get summoned
    battle_embed = build_battle_embed(interaction.user.id, enemy_title)
    opening_result = getBattleResult(interaction.user.id)
    if opening_result:
        # the battle can already be over when it starts, if an item (Protein Brick) made the team skip turns until they lost
        battle_embed = build_battle_embed(interaction.user.id, enemy_title, ending=opening_result)
        battle_embed.description += battle_view.end_battle(opening_result)
    try:
        await interaction.response.send_message(file=discord.File(combined_image_path), embed=battle_embed, view=battle_view)
    except Exception:
        battle_view.end_battle("error")  # don't leave the user stuck "in battle" if the message never got sent
        raise
    battle_view.last_interaction = interaction


HELP_GIF_URL = "https://media.discordapp.net/attachments/796742546910871562/1442307872490000432/JITSTUCKMOBILEGAME.gif?ex=6926efa1&is=69259e21&hm=160f8b3552a36078f4941e02aafbb3408a95be77be4f5ffa6697ff3aacd53397&format=webp&animated=true"
@bot.tree.command(name="help")
async def help_command(ctx):
    """Show Help"""
    await ctx.response.send_message(HELP_GIF_URL)

@bot.command()
async def syncapp(ctx: commands.Context) -> None:
    """Sync app commands to Discord."""
    await ctx.bot.tree.sync()
    await ctx.send('Application commands synchronized!')



if __name__ == "__main__":
    bot.run(TOKEN)