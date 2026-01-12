import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient
import random
from collections import Counter
from PIL import Image
from dotenv import load_dotenv
import time

from battle import *

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

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Gacha Game"))
    print("teeesst")

    # Change inBattle to false for all users on bot startup
    inventory_collection.update_many({}, {"$set": {"inBattle": False}})

    # Add all users from all guilds to MongoDB
    for guild in bot.guilds:
        for member in guild.members:
            #print("Checking user:", member.name)
            if not member.bot:  # Skip bots
                print("User: " + member.name)
                user_data = {
                    "user_id": member.id,
                    "username": str(member),
                    "inventory": {},
                    "rolls": 10,  # Starting rolls,
                    "counter": 0,
                    "team": []
                }
                # Use upsert to avoid duplicates
                inventory_collection.update_one(
                    {"user_id": member.id},
                    {"$setOnInsert": user_data},
                    upsert=True
                )
    print(f"Initialized users in database from {len(bot.guilds)} guild(s)")


# Roll, inventory, Character, battle, challenge, team, viewteam, recycle, help
'''
abraizeChar = ["r_abraize", "r_abraize2", "sr_abraize", "ssr_abraize"]
treyChar = ["r_trey", "ssr_trey"]
noahChar = ["r_noah"]
freemanChar = ["r_freeman", "sr_freeman"]
stephenChar = ["r_stephen", "sr_stephen"]
jaydenChar = ["ssr_jayden"]
homestuckChar = ["sr_homestuck"]
scottieChar = ["ssr_scottie"]
'''

rChar = ["r_abraize", "r_abraize2", "r_trey", "r_noah", "r_freeman", "r_stephen"]
srChar = ["sr_freeman", "sr_stephen", "sr_homestuck", "sr_abraize", "sr_trey"]
ssrChar = ["ssr_abraize", "ssr_trey", "ssr_jayden"]
specialChar = ["ssr_scottie"]
secretChar = ["sssr_max"]

#characters = [rChar, srChar, ssrChar]

characterTitles = {
    "r_abraize": "[Rolling in Success] Abraize Masood",
    "r_abraize2": "[Productivity Time] Abraize Masood",
    "sr_abraize": "[Time on my Side] Abraize Masood",
    "ssr_abraize": "[Rewind] Abraize Masood",
    "r_trey": "[Irish Golden Standard] Treyvaughn Lewis",
    "sr_trey": "[Heavy Sleeper] Treyvaughn Lewis",
    "ssr_trey": "[Seeker of Silence] Treyvaughn Lewis",
    "r_noah": "[pillagingPirate] Noah Cave",
    "r_freeman": "[Who I am to Me] Freeman",
    "sr_freeman": "[Freedom in Jeopardy] Freeman",
    "r_stephen": "[You Marlowe?] Stephen Goraynov",
    "sr_stephen": "[Master of Intervention] Stephen Goraynov",
    "ssr_jayden": "[Sworn Protectorate of Creation] Jayden Ceballos",
    "sr_homestuck": "[Thief in God's Clothing] Homestuck",
    "ssr_scottie": "[Eternal Guardian] Scottie Jenkins",
    "sssr_max": "[???] ???"
}

# Create all character choices for autocomplete
all_characters = rChar + srChar + ssrChar + specialChar# + secretChar
character_choices = [
    app_commands.Choice(name=characterTitles[char], value=char)
    for char in all_characters
]

R_ABRAIZE_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1442262933018251467/R_ABRAIZE.gif?ex=692a1187&is=6928c007&hm=ea36ca7f4742ec74ad4786385624dbbbf1c69ba9c809bf2499c5b23b85f39b38&=&width=813&height=524"
R_ABRAIZE2_GIF = "https://media.discordapp.net/attachments/796742546910871562/1444044329583640748/R_ABRAIZE_PROD.gif?ex=692b4695&is=6929f515&hm=1ecc69064ddd0b38a7b3e9be1d13e2541c99e9e7c0948619b3d486e3ac440f06&=&width=678&height=438"
SR_ABRAIZE_GIF = "https://media.discordapp.net/attachments/907662210619289600/1441575065413091500/SR_ABRAIZ.gif?ex=69414626&is=693ff4a6&hm=c51aa1cf7872069ee96e7365b27d288de2e9cb3d9780375137cebaf6d7196d89&=&width=813&height=524"
SSR_ABRAIZE_GIF = "https://media.discordapp.net/attachments/796742546910871562/1453592615822950450/SSR_ABRAIZE.gif?ex=6955435e&is=6953f1de&hm=ef8fb3a6bcb7f6fccec9f36850b8b8d3954a9bfc118843171d03fdf9af369e68&=&width=678&height=438"
R_TREY_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1442262950055251978/R_TREY.gif?ex=692aba4b&is=692968cb&hm=6467f2663cac2d80ffd3f61f9de3436133557568e4b00cec63ee4cbdb1d6da40&=&width=813&height=524"
SR_TREY_GIF = "https://media.discordapp.net/attachments/907662210619289600/1442648569579307180/SR_TREY.gif?ex=6941396e&is=693fe7ee&hm=d12a52705f4952d3860d273dcce43f3598f971d5d581209f61fd46108823194d&=&width=813&height=524"
SSR_TREY_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1438298186409185393/SSR_TREY.gif?ex=692ace51&is=69297cd1&hm=705ffe6482d8c46a88742a82e6565c28ff53cbba9ea15eebe990dfacde708469&=&width=813&height=524"
R_NOAH_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1438298195829719193/R_NOAH.gif?ex=692ace54&is=69297cd4&hm=a4ab137787708b382bd26b0659a39b768dece0b7d0eb03898b4fe4b180428133&=&width=601&height=438"
R_FREEMAN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1442262942660952268/R_FREEMAN.gif?ex=692aba49&is=692968c9&hm=3f1edc05a01b0c793ab7ddfe3519054630c1523e68b5c29ec5d4be6624d0e1c0&=&width=813&height=524"
SR_FREEMAN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1438298206193586187/SR_FREEMAN.gif?ex=692ace56&is=69297cd6&hm=6e42e1d45a353ffc60916f54593933273fea88e2d69d400c91f8c6899172174e&=&width=678&height=438"
R_STEPHEN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1443821437378105444/R_STEPHEN.gif?ex=692b1fbf&is=6929ce3f&hm=97986106339c3febd0bb243c25c13f870c331eb2376c2b3bcefc053fac64e26b&=&width=813&height=524"
SR_STEPHEN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1443821457846046741/SR_STEPHEN.gif?ex=692b1fc4&is=6929ce44&hm=fbccf7579c4c5189be6d18689bc65a7e62b064bdd075647ddc64428721d53b3e&=&width=813&height=524"
SSR_JAYDEN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1441662516672331836/SSR_JAYDEN.gif?ex=692a8558&is=692933d8&hm=c5f5376d3603ce635598548977465872e7a3662802986c6f742c1f590eadd7a4&=&width=813&height=524"
SR_HOMESTUCK_GIF = "https://media.discordapp.net/attachments/907662210619289600/1441689825911505026/SR_HOMESTUCK.gif?ex=6941b107&is=69405f87&hm=181544c05734a721ea53bbe630dcb4b25ed7b95327661a807b97bdba81cc7506&=&width=813&height=524"
SSR_SCOTTIE_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1441591428042985492/SSR_SCOTTIE.gif?ex=69551be3&is=6953ca63&hm=9a1141a0f327f2f16ed80b996243679e62491b0fa2b985babdc1bc09d82cccaa&=&width=813&height=524"
SSSR_MAX_GIF = "???"
RECYCLE_GIF = "https://media.discordapp.net/attachments/796742546910871562/1455728132240703593/recycled_B.gif?ex=6955c7f8&is=69547678&hm=a047b1b23feab6ea79f4c79303bd9ee6bfba8ba9b800813754e05b9615529585&=&width=678&height=438"

# Use abraizeEmbed as example for other characters
# HP attack and defense are integers
# evasion and accuracy are percentages

# each character will have an 8 length array that includes all attributes
# hp, atk, def, eva, acc, skill1, skill2, skill3
# the only exxception is that ssr characters will have an ultimate skill making it a 9 length array

r_abraizeAttributes = [200, 10, 10, "3%", "90%", "Punch", "Sleep", "Missing Assignments"]
def r_abraizeEmbed():
    embed = discord.Embed(title=f"[Rolling in Success]", description="Abraize Masood", color=0x3f48cc)
    embed.set_image(url=R_ABRAIZE_GIF)
    embed.add_field(name="HP:", value=r_abraizeAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=r_abraizeAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=r_abraizeAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=r_abraizeAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=r_abraizeAttributes[4], inline=True)
    embed.add_field(name=r_abraizeAttributes[5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=r_abraizeAttributes[6], value="Take a nap on the field, reducing self’s evasion score to 0%. \nFor one turn, unable to attack or act. After said turn, gain a 15% atk and def buff to self for 2 turns.", inline=False)
    embed.add_field(name=r_abraizeAttributes[7], value="Getting these done really lifted a weight off your chest. +5% acc boost for one turn.", inline=False)
    return embed

r_abraize2Attributes = [200, 10, 10, "3%", "90%", "Punch", "Eat Note", "Productivity Time"]
def r_abraize2Embed():
    embed = discord.Embed(title=f"[Productivity Time]", description="Abraize Masood", color=0x3f48cc)
    embed.set_image(url=R_ABRAIZE2_GIF)
    embed.add_field(name="HP:", value=r_abraize2Attributes[0], inline=True)
    embed.add_field(name="ATK:", value=r_abraize2Attributes[1], inline=True)
    embed.add_field(name="DEF:", value=r_abraize2Attributes[2], inline=True)
    embed.add_field(name="EVA:", value=r_abraize2Attributes[3], inline=True)
    embed.add_field(name="ACC:", value=r_abraize2Attributes[4], inline=True)
    embed.add_field(name=r_abraize2Attributes[5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=r_abraize2Attributes[6], value="Apply a +10% evasion buff to self for one turn, but cost 25 HP.", inline=False)
    embed.add_field(name=r_abraize2Attributes[7], value="Apply a 10% atk and def buff to all allies for 3 turns, cannot be used for 4 turns.", inline=False)
    return embed

sr_abraizeAttributes = [200, 15, 20, "3%", "90%", "Punch", "Slow", "Attempt"]
def sr_abraizeEmbed():
    embed = discord.Embed(title=f"[Time on my Side]", description="Abraize Masood", color=0x3f48cc)
    embed.set_image(url=SR_ABRAIZE_GIF)
    embed.add_field(name="HP:", value=sr_abraizeAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=sr_abraizeAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=sr_abraizeAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=sr_abraizeAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=sr_abraizeAttributes[4], inline=True)
    embed.add_field(name=sr_abraizeAttributes[5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=sr_abraizeAttributes[6], value="Applies a -15% accuracy debuff to one enemy.", inline=False)
    embed.add_field(name=sr_abraizeAttributes[7], value="Attempt to travel back in time without being doomed. Has an 85% chance of doing nothing. 15% chance that health is healed by 50% and all allies atk is buffed by 20% for one turn.", inline=False)
    return embed

ssr_abraizeAttributes = [600, 35, 35, "3%", "90%", "Accelerated Punch", "Fast Forward", "Rewind", "Universal Stabilizer"]
def ssr_abraizeEmbed():
    embed = discord.Embed(title="[Rewind]", description="Abraize Masood", color=0x3f48cc)
    embed.set_image(url=SSR_ABRAIZE_GIF)
    embed.add_field(name="HP:", value=ssr_abraizeAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=ssr_abraizeAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=ssr_abraizeAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=ssr_abraizeAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=ssr_abraizeAttributes[4], inline=True)
    embed.add_field(name=ssr_abraizeAttributes[5], value="Accelerate yourself to punch the opponent. Guaranteed to hit. Applies one stack of “Accelerated” state to self. Gain +10% atk for every consecutive “Accelerated” state with a maximum of +100% atk. All “Accelerated” stacks are removed when using another move.", inline=False)
    embed.add_field(name=ssr_abraizeAttributes[6], value="Apply a +5% acc bonus, +40% atk bonus, and +15% def bonus to all allies for one turn and allows you to immediately take another turn. Cannot be used for another 5 turns.", inline=False)
    embed.add_field(name=ssr_abraizeAttributes[7], value="Revert all party member's stats to the state they were in during the prior turn. Cannot be used for another 2 turns.", inline=False)
    embed.add_field(name=ssr_abraizeAttributes[8], value="Your status as an anchor of time and your experience lends you well to combat. Turn back the wheels of time to make everything right again. Applies debuff nullification (cannot be debuffed) and a +50% atk bonus to all allies for 5 turns. Heals all allies to full. Cannot be used again.", inline=False)
    return embed

r_treyAttributes = [250, 12, 8, "3%", "90%", "Punch", "Irish Goodbye", "Cheesy Fries"]
def r_treyEmbed():
    embed = discord.Embed(title=f"[Irish Golden Standard]", description="Treyvaughn Lewis", color=0x3f48cc)
    embed.set_image(url=R_TREY_GIF)
    embed.add_field(name="HP:", value=r_treyAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=r_treyAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=r_treyAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=r_treyAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=r_treyAttributes[4], inline=True)
    embed.add_field(name=r_treyAttributes[5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=r_treyAttributes[6], value="Apply a one time +10% eva buff to self for one turn. Can be used again after 2 turns", inline=False)
    embed.add_field(name=r_treyAttributes[7], value="Throws cheesy fries at one enemy of choice, applies Burn on them for one turn. 70% chance to hit", inline=False)
    return embed

sr_treyAttributes = [300, 15, 20, "3%", "75%", "Punch", "Drowsy", "Whispers from Beyond"]
def sr_treyEmbed():
    embed = discord.Embed(title=f"[Heavy Sleeper]", description="Treyvaughn Lewis", color=0x3f48cc)
    embed.set_image(url=SR_TREY_GIF)
    embed.add_field(name="HP:", value=sr_treyAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=sr_treyAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=sr_treyAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=sr_treyAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=sr_treyAttributes[4], inline=True)
    embed.add_field(name=sr_treyAttributes[5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=sr_treyAttributes[6], value="Applies a -10% acc debuff to all opponents for one turn.", inline=False)
    embed.add_field(name=sr_treyAttributes[7], value="The horrorterrors beckon. Give a +10% acc boost to all allies", inline=False)
    return embed

ssr_treyAttributes = [750, 30, 25, "30%", "90%", "Punch", "Cloak and Dagger", "Shroud", "Reality Sink"]
def ssr_treyEmbed():
    embed = discord.Embed(title=f"[Seeker of Silence]", description="Treyvaughn Lewis", color=0x3f48cc)
    embed.set_image(url=SSR_TREY_GIF)
    embed.add_field(name="HP:", value=ssr_treyAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=ssr_treyAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=ssr_treyAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=ssr_treyAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=ssr_treyAttributes[4], inline=True)
    embed.add_field(name=ssr_treyAttributes[5], value="Throw a mean right hook at the enemy.", inline=False)
    embed.add_field(name=ssr_treyAttributes[6], value="Add a +100% eva buff and +10% acc buff to self for one turn. Performs a stabbing attack on one enemy that deals 10% max hp and true damage. Cannot be used for 2 turns.", inline=False)
    embed.add_field(name=ssr_treyAttributes[7], value="Redistribute the void into those around you. +50% eva buff to all allies for 3 turns, but draws attacks to you for one turn. Cannot be used again for 4 turns.", inline=False)
    embed.add_field(name=ssr_treyAttributes[8], value="Nothing can't be seen, right? Centering all of the void you control into one spot should be able to create a concentrated spot of nothing, a nothing so strong that no thing can escape it. Create a miniature \"void spot\" that stays on the battle for 3 turns. When on the stage, all ranged attacks automatically miss. For each ranged attack performed, the power grows by 50%. After every turn, power grows by 100%. At the end of 3 turns, deals the combined percentage of atk to all enemies in one burst. Cannot be used again.", inline=False)
    return embed

r_noahAttributes = [180, 10, 8, "3%", "90%", "Punch", "Fiddle", "Bo"]
def r_noahEmbed():
    embed = discord.Embed(title=f"[pillagingPirate]", description="Noah Cave", color=0x3f48cc)
    embed.set_image(url=R_NOAH_GIF)
    embed.add_field(name="HP:", value=r_noahAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=r_noahAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=r_noahAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=r_noahAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=r_noahAttributes[4], inline=True)
    embed.add_field(name=r_noahAttributes[5], value="Throws a mean right hook at the enemy.", inline=False)
    embed.add_field(name=r_noahAttributes[6], value="Send an annoying text message to one enemy, applying a -5% acc debuff to them.", inline=False)
    embed.add_field(name=r_noahAttributes[7], value="Apply \"Interfere\" state to self permanently until exhausted. \"Interfere\" state allows a 50% chance of an incoming enemy attack to be negated one time before the state is exhausted and removed from self. Can only be used again after 2 turns.", inline=False)
    return embed

r_freemanAttributes = [180, 8, 8, "10%", "90%", "Slap", "Ponder", "SMASH!"]
def r_freemanEmbed():
    embed = discord.Embed(title=f"[Who I am to Me]", description="Freeman", color=0x3f48cc)
    embed.set_image(url=R_FREEMAN_GIF)
    embed.add_field(name="HP:", value=r_freemanAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=r_freemanAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=r_freemanAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=r_freemanAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=r_freemanAttributes[4], inline=True)
    embed.add_field(name=r_freemanAttributes[5], value="Bitch slap the opponent with your weak arm.", inline=False)
    embed.add_field(name=r_freemanAttributes[6], value="Apply a 3% eva buff to all allies for 1 turn.", inline=False)
    embed.add_field(name=r_freemanAttributes[7], value="Apply a temporary +10% atk buff to self and deal damage to one opponent. The damage dealt is then subtracted from your hp.", inline=False)
    return embed

sr_freemanAttributes = [180, 8, 8, "10%", "90%", "Pistol Whip", "Shoot", "Hide"]
def sr_freemanEmbed():
    embed = discord.Embed(title=f"[Freedom in Jeopardy]", description="Freeman", color=0x3f48cc)
    embed.set_image(url=SR_FREEMAN_GIF)
    embed.add_field(name="HP:", value=sr_freemanAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=sr_freemanAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=sr_freemanAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=sr_freemanAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=sr_freemanAttributes[4], inline=True)
    embed.add_field(name=sr_freemanAttributes[5], value="Nobody expects a good clocking from a gun.", inline=False)
    embed.add_field(name=sr_freemanAttributes[6], value="80% chance of the safety being on, dealing no damage. 20% that the safety was left off, dealing 10% of the enemy's current hp.", inline=False)
    embed.add_field(name=sr_freemanAttributes[7], value="Apply \"Nervous\" state to self. As long as self has \"Nervous\" state, apply a 25% chance that each attack made by an enemy can be interrupted (similar to R Noah). When an attack is interrupted, trigger Ability 2 on the attacking enemy.", inline=False)
    return embed

r_stephenAttributes = [180, 9, 8, "3%", "90%", "Dropkick", "Light up", "Lock the fuck in"]
def r_stephenEmbed():
    embed = discord.Embed(title=f"[You Marlowe?]", description="Stephen Goraynov", color=0x3f48cc)
    embed.set_image(url=R_STEPHEN_GIF)
    embed.add_field(name="HP:", value=r_stephenAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=r_stephenAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=r_stephenAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=r_stephenAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=r_stephenAttributes[4], inline=True)
    embed.add_field(name=r_stephenAttributes[5], value="Kick the shit out of one enemy.", inline=False)
    embed.add_field(name=r_stephenAttributes[6], value="Light your BALLER CIGARETTE, drawing everyone's attention towards you. Applies \"Baller\" status to self for 3 turns. If hit during \"Baller\" status, remove one stack.", inline=False)
    embed.add_field(name=r_stephenAttributes[7], value="Add +5% atk bonus for one turn per each \"Baller\" status self has.", inline=False)
    return embed

sr_stephenAttributes = [180, 9, 8, "3%", "90%", "Dropkick", "Consider Intervening", "HIYAAAHHH!"]
def sr_stephenEmbed():
    embed = discord.Embed(title=f"[Master of Intervention]", description="Stephen Goraynov", color=0x3f48cc)
    embed.set_image(url=SR_STEPHEN_GIF)
    embed.add_field(name="HP:", value=sr_stephenAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=sr_stephenAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=sr_stephenAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=sr_stephenAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=sr_stephenAttributes[4], inline=True)
    embed.add_field(name=sr_stephenAttributes[5], value="Kick the shit out of an enemy.", inline=False)
    embed.add_field(name=sr_stephenAttributes[6], value="Applies 1 stack of \"Considering\" state to self for 3 turns.", inline=False)
    embed.add_field(name=sr_stephenAttributes[7], value="Converts each stack of \"Considering\" into a 10% damage buff and then attacks one enemy.", inline=False)
    return embed

ssr_jaydenAttributes = [600, 30, 30, "5%", "90%", "Punch", "Butler of Swatabi", "Indecision", "Genesis"]
def ssr_jaydenEmbed():
    embed = discord.Embed(title=f"[Sworn Protectorate of Creation]", description="Jayden Ceballos", color=0x3f48cc)
    embed.set_image(url=SSR_JAYDEN_GIF)
    embed.add_field(name="HP:", value=ssr_jaydenAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=ssr_jaydenAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=ssr_jaydenAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=ssr_jaydenAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=ssr_jaydenAttributes[4], inline=True)
    embed.add_field(name=ssr_jaydenAttributes[5], value="Throw a mean right hook at the enemy.", inline=False)
    embed.add_field(name=ssr_jaydenAttributes[6], value="Leverage your dreadful reputation as the Butler of Ill Repute. -30% acc for all enemies.", inline=False)
    embed.add_field(name=ssr_jaydenAttributes[7], value="33% chance to buff all allies atk and def by 20%, 33% chance to debuff all enemies atk and def by 20%, 33% chance to deal 1 hp of damage to self.", inline=False)
    embed.add_field(name=ssr_jaydenAttributes[8], value="With the power of creation on your side, it is your sworn duty to bring about its influence in this world. It is your job to decrease the space between you and your allies, and to increase the space between your allies and your enemies. Apply \"Regeneration\" status (5% hp heal every turn) for the next 7 turns, as well as apply \"Warped\" status (-25% acc penalty, -35% max hp, -25% def) to all enemies for the next 7 turns. Cannot be used again.", inline=False)
    return embed

sr_homestuckAttributes = [180, 18, 15, "5%", "90%", "Impractical Assailants", "Plunder", "Thief"]
def sr_homestuckEmbed():
    embed = discord.Embed(title=f"[Thief in God's Clothing]", description="Homestuck", color=0x3f48cc)
    embed.set_image(url=SR_HOMESTUCK_GIF)
    embed.add_field(name="HP:", value=sr_homestuckAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=sr_homestuckAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=sr_homestuckAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=sr_homestuckAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=sr_homestuckAttributes[4], inline=True)
    embed.add_field(name=sr_homestuckAttributes[5], value="Roll a die! Deal damage in increments of 10 based on what you get!", inline=False)
    embed.add_field(name=sr_homestuckAttributes[6], value="Apply a -15% atk debuff to one random ally for one turn, provide a +15% atk buff to self for one turn.", inline=False)
    embed.add_field(name=sr_homestuckAttributes[7], value="Apply a -100% acc penalty to all enemies and a +100% acc bonus to all allies for one turn. Cannot be used again for 5 turns.", inline=False)
    return embed

ssr_scottieAttributes = [700, 40, 40, "5%", "90%", "Shield Bash", "Guardian's Shield", "Fortify", "Eternal Watch"]
def ssr_scottieEmbed():
    embed = discord.Embed(title=f"[Eternal Guardian]", description="Scottie Jenkins", color=0x3f48cc)
    embed.set_image(url=SSR_SCOTTIE_GIF)
    embed.add_field(name="HP:", value=ssr_scottieAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=ssr_scottieAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=ssr_scottieAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=ssr_scottieAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=ssr_scottieAttributes[4], inline=True)
    embed.add_field(name=ssr_scottieAttributes[5], value="Bash an enemy with your shield, dealing damage and a 20% chance to stun them for one turn.", inline=False)
    embed.add_field(name=ssr_scottieAttributes[6], value="Create a shield that absorbs damage equal to 20% of your max HP for all allies for 3 turns. Cannot be used again for 4 turns.", inline=False)
    embed.add_field(name=ssr_scottieAttributes[7], value="Fortify all allies, granting a +30% def buff for 3 turns. Cannot be used again for 4 turns.", inline=False)
    embed.add_field(name=ssr_scottieAttributes[8], value="Assume the role of the eternal guardian. Grant all allies a +50% def buff and damage immunity for 2 turns. Heals all allies to full HP. Cannot be used again.", inline=False)
    return embed

sssr_maxAttributes = ["?", "??", "???", "????", "?????", "?", "?", "?", "?"]
def sssr_maxEmbed():
    embed = discord.Embed(title=f"[???]", description="???", color=0x000000)
  #  embed.set_image(url=SSSR_MAX_GIF)
    embed.add_field(name="HP:", value=sssr_maxAttributes[0], inline=True)
    embed.add_field(name="ATK:", value=sssr_maxAttributes[1], inline=True)
    embed.add_field(name="DEF:", value=sssr_maxAttributes[2], inline=True)
    embed.add_field(name="EVA:", value=sssr_maxAttributes[3], inline=True)
    embed.add_field(name="ACC:", value=sssr_maxAttributes[4], inline=True)
    embed.add_field(name=sssr_maxAttributes[5], value="???", inline=False)
    embed.add_field(name=sssr_maxAttributes[6], value="???", inline=False)
    embed.add_field(name=sssr_maxAttributes[7], value="???", inline=False)
    embed.add_field(name=sssr_maxAttributes[8], value="???", inline=False)
    embed.add_field(name="Lore:", value="An entity beyond comprehension. Its true nature is unknown.", inline=False)
    return embed


def roll_character(banner: str) -> str:
    # Define character pools by rarity
  #  r_chars = ["r_abraize", "r_abraize2", "r_trey", "r_noah", "r_freeman", "r_stephen"]
   # sr_chars = ["sr_freeman", "sr_stephen"]
    #ssr_chars = ["ssr_abraize", "ssr_trey", "ssr_jayden"]

    # Roll for rarity (60% R, 29% SR, 11% SSR total)
    # Note: SSR pool has 3 chars, so each gets ~3.67% for 11% total
    # Adjusted to 1% per SSR = 3% total, with 60% R and 37% SR
    rarity_roll = random.random() * 100
    if banner == "standard":
        if rarity_roll < 1:
            # 1% chance for SSR
            return random.choice(ssrChar)
        elif rarity_roll < 30:
            # 29% chance for SR (1% to 30%)
            return random.choice(srChar)
        else:
            # 70% chance for R (30% to 100%)
            return random.choice(rChar)

    if banner == "special":
        if rarity_roll < 1:
            return random.choice(specialChar)
        elif rarity_roll < 30:
            return random.choice(srChar)
        else:
            return random.choice(rChar)

    return "Error"  # Example character


@bot.tree.command(name="roll")
@app_commands.choices(banner = [
    app_commands.Choice(name="standard", value="standard"),
    app_commands.Choice(name="special", value="special"),
])
async def roll(interaction: discord.Interaction, banner: app_commands.Choice[str], amount: int = None):
    """Pick a banner of: Standard or Special. Optionally specify amount to roll; otherwise roll all available."""

    if banner.name == "standard":
        user_data = inventory_collection.find_one({"user_id": interaction.user.id})
        if not user_data:
            await interaction.response.send_message("No inventory data found.")
            return

        rolls_available = user_data.get("rolls", 0)
        if rolls_available <= 0:
            await interaction.response.send_message("You do not have any rolls left for the **Standard** banner.")
            return

        # Determine how many rolls to perform
        if amount is None or amount <= 0:
            to_roll = rolls_available
        else:
            to_roll = min(amount, rolls_available)

        rolled_characters = []
        embed = discord.Embed(title=f"Standard Rolls: x{to_roll}", color=0x3f48cc)
        if amount is not None and amount > rolls_available:
            embed.description = f"Requested {amount}, using {rolls_available} available."

        for _ in range(to_roll):
            rolled_character = roll_character("standard")
            rolled_characters.append(rolled_character)
            inventory_collection.update_one(
                {"user_id": interaction.user.id},
                {"$inc": {f"inventory.{rolled_character}": 1}},
            )

        # Decrement only the number of rolls used
        inventory_collection.update_one(
            {"user_id": interaction.user.id},
            {"$inc": {"rolls": -to_roll}},
        )

        # Group results by rarity
        ssr_rolled = [char for char in rolled_characters if char in ssrChar]
        sr_rolled = [char for char in rolled_characters if char in srChar]
        r_rolled = [char for char in rolled_characters if char in rChar]

        def format_group(chars):
            if not chars:
                return None
            counts = Counter(chars)
            lines = []
            for char, cnt in counts.items():
                title = characterTitles.get(char, char)
                lines.append(f"**{title}** +{cnt}")
            return "\n".join(lines)

        ssr_text = format_group(ssr_rolled)
        sr_text = format_group(sr_rolled)
        r_text = format_group(r_rolled)

        if ssr_text:
            embed.add_field(name="SSR Characters:", value=ssr_text, inline=False)
        if sr_text:
            embed.add_field(name="SR Characters:", value=sr_text, inline=False)
        if r_text:
            embed.add_field(name="R Characters:", value=r_text, inline=False)

        await interaction.response.send_message(embed=embed)

    elif banner.name == "special":
        # Special banner logic
        user_data = inventory_collection.find_one({"user_id": interaction.user.id})
        if not user_data:
            await interaction.response.send_message("No inventory data found.")
            return
        rolls_available = user_data.get("rolls", 0)
        if rolls_available <= 0:
            await interaction.response.send_message("You do not have any rolls left for the **Special** banner.")
            return
        # swtich SSR with specialChar
        if amount is None or amount <= 0:
            to_roll = rolls_available
        else:
            to_roll = min(amount, rolls_available)
        rolled_characters = []
        embed = discord.Embed(title=f"Special Rolls: x{to_roll}", color=0x3f48cc)
        if amount is not None and amount > rolls_available:
            embed.description = f"Requested {amount}, using {rolls_available} available."
        for _ in range(to_roll):
            rolled_character = roll_character("special")
            rolled_characters.append(rolled_character)
            inventory_collection.update_one(
                {"user_id": interaction.user.id},
                {"$inc": {f"inventory.{rolled_character}": 1}},
            )
        # Decrement only the number of rolls used
        inventory_collection.update_one(
            {"user_id": interaction.user.id},
            {"$inc": {"rolls": -to_roll}},
        )
        # Group results by rarity
        special_rolled = [char for char in rolled_characters if char in specialChar]
        sr_rolled = [char for char in rolled_characters if char in srChar]
        r_rolled = [char for char in rolled_characters if char in rChar]
        def format_group(chars):
            if not chars:
                return None
            counts = Counter(chars)
            lines = []
            for char, cnt in counts.items():
                title = characterTitles.get(char, char)
                lines.append(f"**{title}** +{cnt}")
            return "\n".join(lines)
        special_text = format_group(special_rolled)
        sr_text = format_group(sr_rolled)
        r_text = format_group(r_rolled)
        if special_text:
            embed.add_field(name="Special Characters:", value=special_text, inline=False)
        if sr_text:
            embed.add_field(name="SR Characters:", value=sr_text, inline=False)
        if r_text:
            embed.add_field(name="R Characters:", value=r_text, inline=False)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Please select a Banner to roll from!")

@bot.tree.command()
async def inventory(ctx):
    """Show Inventory"""
    # display inventory in some cool way maybe like how maki does and have buttons to flip through pages
    user_data = inventory_collection.find_one({"user_id": ctx.user.id})
    if user_data:
        rolls = user_data.get("rolls", 0)
        inventory = user_data.get("inventory", {})

      #  special_inventory = {char: count for char, count in inventory.items() if char in specialChar}
        ssr_inventory = {char: count for char, count in inventory.items() if char in ssrChar or char in specialChar}
        sr_inventory = {char: count for char, count in inventory.items() if char in srChar}
        r_inventory = {char: count for char, count in inventory.items() if char in rChar}

        embed = discord.Embed(title=f"{ctx.user.display_name}'s Inventory", color=0x3f48cc)

     #   if special_inventory:
      #      embed.add_field(name="Special Characters:", value="\n".join([f"{characterTitles[char]}: {count}" for char, count in special_inventory.items()]), inline=False)
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

# Ephemeral Message
@bot.tree.command()
@app_commands.choices(character_name=character_choices)
async def char(interaction: discord.Interaction, character_name: app_commands.Choice[str]):
    """Show Character Info"""

    # Get the character dev name from the choice value
    char_dev_name = character_name.value

    # Check if user owns the character
    user_data = inventory_collection.find_one({"user_id": interaction.user.id})
    if user_data:
        inventory = user_data.get("inventory", {})
        if inventory.get(char_dev_name, 0) < 1:
            # if sssr_max then continue even if user does not own
            if char_dev_name == "sssr_max":
                pass
            else:
                NO_OWN_PNG = "./broke.png"
                await interaction.followup.send(file=discord.File(NO_OWN_PNG))
                return
    else:
        await interaction.followup.send("No inventory data found.")
        return

    if char_dev_name == "sssr_max":
        await interaction.response.defer()
    else:
        await interaction.response.defer(ephemeral=True)

    # The message below will be hidden from other users.
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
    elif char_dev_name == "sssr_max":
        embed = sssr_maxEmbed()
        yesMax = True
    else:
        await interaction.followup.send(f"Character **{char_dev_name}** does not exist!")
        return

    await interaction.followup.send(embed=embed)
    if yesMax:
        time.sleep(2)
        await interaction.delete_original_response()


class View(discord.ui.View):
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="yes_button", emoji="♻️")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="no_button", emoji="🥺")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

#Recycle Command
@bot.tree.command()
@app_commands.choices(character_name=character_choices)
async def recycle(ctx: discord.Interaction, character_name: app_commands.Choice[str], amount: int):
    # SSR = 100 points to counter, SR = 5 points to counter, R = 1 point to counter
    # 10 r's for 1 roll, 2 sr for 2 rolls and 1 ssr for 10 rolls
    # if counter = 10 inside mongodb per user then give 1 roll otherwise update and tell user to recycle more
    """Recycle Characters for Rolls"""
    # Example: /recycle r_abraize 10
    # then show embed saying "Would you like to recycle" [character_name] x [amount], "you will gain [calculated rolls] rolls" (calculated rolls may be in decimal format for example if they recycle 15 r's then it will say 1.5 rolls)

    # Get the character dev name from the choice value
    char_dev_name = character_name.value
    char_title = character_name.name

    user_data = inventory_collection.find_one({"user_id": ctx.user.id})
    if user_data:
        inventory = user_data.get("inventory", {})
        char_count = inventory.get(char_dev_name, 0)

        # Check if user owns the character
        if char_count < 1:
            if char_dev_name == "sssr_max":
                embed = discord.Embed(title="You Can't Recycle What You Don't Know", color=0x000000)
                await ctx.response.send_message(embed=embed)
                time.sleep(2)
                await ctx.delete_original_response()
                return
            NO_OWN_PNG = "./broke.png"
            await ctx.response.send_message(file=discord.File(NO_OWN_PNG))
            return

        if char_count >= amount:
            # Determine points based on character rarity
            if char_dev_name in ssrChar:
                points = 100 * amount
            elif char_dev_name in srChar:
                points = 5 * amount
            elif char_dev_name in rChar:
                points = 1 * amount
            else:
                await ctx.response.send_message(f"Character **{char_title}** does not exist!")
                return

            # Calculate rolls to add
            # rolls to add must be integer never float
            current_points = user_data.get("counter", 0)
            total_points = current_points + points
            rolls_to_add = total_points // 10  # 10 points = 1 roll

            # embed awaiting user confirmation by button click yes or no to recycle or not
            embed = discord.Embed(title=f"Would you like to recycle {char_title} x {amount}? ", color=0x3f48cc)
            await ctx.response.send_message(embed=embed, view=View())

            # if view is custom id of yes button then proceed with recycling
            def check(interaction: discord.Interaction):
                return interaction.user.id == ctx.user.id and interaction.data["custom_id"] in ["yes_button", "no_button"]
            try:
                interaction = await bot.wait_for("interaction", check=check, timeout=10.0)

                if interaction.data["custom_id"] == "yes_button":
                    # Proceed with recycling
                    # Counter examples: if points = 20 then add 2 rolls and counter = 0, if points = 15 then add 1 roll and counter = 5, if points = 7 then add 0 rolls and counter = 7
                    # if points = 5 and they recycled 1 sr which is 5 points then add 1 roll and set coutner to 0
                    # Remove full tens from the counter and convert them into rolls
                    new_total = current_points + points
                    rolls_gain = new_total // 10
                    new_counter = new_total % 10

                    inventory_collection.update_one(
                        {"user_id": ctx.user.id},
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

                    # if character count goes to 0 then remove character from inventory
                    updated_user_data = inventory_collection.find_one({"user_id": ctx.user.id})
                    updated_inventory = updated_user_data.get("inventory", {})
                    if updated_inventory.get(char_dev_name, 0) == 0:
                        inventory_collection.update_one(
                            {"user_id": ctx.user.id},
                            {"$unset": {f"inventory.{char_dev_name}": ""}}
                        )
                   # user_data = inventory_collection.find_one({"user_id": ctx.user.id})


                  #  if rolls_to_add == 0:
                    embed = discord.Embed(title=f"Recycled **{char_title} x{amount}**. Your total rolls is **{rolls_gain + user_data.get('rolls', 0)}** rolls.", color=0x3f48cc)
                    embed.set_image(url=RECYCLE_GIF)
                    await ctx.followup.send(embed=embed)
                else:  # no_button pressed
                    await ctx.followup.send("Recycling cancelled.")
            except asyncio.TimeoutError:
                await ctx.followup.send("Recycling timed out. Please try again.")


        else:
            await ctx.response.send_message(f"You do not have enough **{char_title}'s** to recycle **x{amount}**. You currently have **x{char_count}**.")
    else:
        await ctx.response.send_message(f"{ctx.user.mention} No inventory data found. Please contact an Admin immediately.")

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
                    time.sleep(2)
                    await ctx.delete_original_response()
                    return
                NO_OWN_PNG = "./broke.png"
                await ctx.response.send_message(file=discord.File(NO_OWN_PNG))
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
backgrounds = {
    "purple": "./purple.png"
}
characterImages ={
    "r_abraize": "./r_abraize.png",
    "r_abraize2": "./r_abraize2.png",
    "sr_abraize": "./sr_abraize.png",
    "ssr_abraize": "./ssr_abraize.png",
    "r_trey": "./r_trey.png",
    "sr_trey": "./sr_trey.png",
    "ssr_trey": "./ssr_trey.png",
    "r_noah": "./r_noah.png",
    "r_freeman": "./r_freeman.png",
    "sr_freeman": "./sr_freeman.png",
    "ssr_jayden": "./ssr_jayden.png",
    "r_stephen": "./r_stephen.png",
    "sr_stephen": "./sr_stephen.png",
    "sr_homestuck": "./sr_homestuck.png",
    "ssr_scottie": "./ssr_scottie.png"
}
enemyImages = {
    "RuffianBack": "./ruffianBack.png",
    "RuffianFront": "./ruffianFront.png",
    "Grunt": "./grunt.png",
    "Spearman": "./spearman.png",
    "Agent": "./agent.png",
    "Jack Noir": "./jackNoir.png"
}
enemySpots = {
    "Grunt": (0, 0),
    "RuffianBack": (-25, 130),
    "RuffianFront": (0, 260),
    "RuffianSolo": (0, 150),
    "Spearman": (15, 145),
    "Agent": (20, 150),
    "Jack Noir": (0, 150)
}

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
    "r_freeman": (49, 241),
    "sr_freeman": (57, 206),
    "ssr_jayden": (56, 278),
    "r_stephen": (52, 215),
    "sr_stephen": (72, 222),
    "sr_homestuck": (117, 228),
    "ssr_scottie": (55, 283),
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

'''
# ============================================================================
# BATTLE STATE AND COMBAT CALCULATIONS
# ============================================================================

def parse_percentage_stat(value) -> float:
    """Parse a percentage stat (e.g., '90%' or 0.90) to a float."""
    if isinstance(value, str):
        return float(value.rstrip('%')) / 100
    return float(value)

def get_character_rarity_multiplier(char_name: str) -> float:
    """Get the rarity multiplier for a character (R=1, SR=1.5, SSR=2)."""
    if char_name in ssrChar or char_name in specialChar:
        return 2.0
    elif char_name in srChar:
        return 1.5
    elif char_name in rChar:
        return 1.0
    return 1.0

def get_character_attributes(char_name: str) -> dict:
    """Get base attributes for a character."""
    # Map character names to their attribute arrays
    char_attr_map = {
        "r_abraize": r_abraizeAttributes,
        "r_abraize2": r_abraize2Attributes,
        "sr_abraize": sr_abraizeAttributes,
        "ssr_abraize": ssr_abraizeAttributes,
        "r_trey": r_treyAttributes,
        "sr_trey": sr_treyAttributes,
        "ssr_trey": ssr_treyAttributes,
        "r_noah": r_noahAttributes,
        "r_freeman": r_freemanAttributes,
        "sr_freeman": sr_freemanAttributes,
        "ssr_jayden": ssr_jaydenAttributes,
        "r_stephen": r_stephenAttributes,
        "sr_stephen": sr_stephenAttributes,
        "sr_homestuck": sr_homestuckAttributes,
        "ssr_scottie": ssr_scottieAttributes,
    }

    attrs = char_attr_map.get(char_name, [200, 10, 10, "3%", "90%"])
    return {
        "hp": attrs[0],
        "atk": attrs[1],
        "def": attrs[2],
        "eva": parse_percentage_stat(attrs[3]),
        "acc": parse_percentage_stat(attrs[4]),
    }

def calculate_ehp(hp: int, defense: int, rarity_multiplier: float) -> int:
    """Calculate Effective Health Points (EHP = HP + DEF * Rarity)."""
    return hp + int(defense * rarity_multiplier)

def calculate_displayed_hp(current_ehp: int, total_ehp: int, total_hp: int) -> int:
    """Calculate displayed HP from current EHP."""
    if total_ehp <= 0:
        return 0
    ratio = current_ehp / total_ehp
    displayed_hp = ratio * total_hp
    return max(0, int(displayed_hp + 0.5))  # Round up

def apply_damage_to_ehp(current_ehp: int, damage: int) -> int:
    """Apply damage to EHP and return new EHP."""
    return max(0, current_ehp - damage)

def roll_accuracy(accuracy: float) -> bool:
    """Roll for accuracy. Returns True if attack hits."""
    return random.random() < accuracy

def roll_evasion(evasion: float) -> bool:
    """Roll for evasion. Returns True if attack is dodged."""
    return random.random() < evasion

# ============================================================================
# BATTLE VIEW - Interactive Battle System with Turn Mechanics
# ============================================================================

class BattleView(discord.ui.View):
    """
    Interactive battle view with dynamic ability buttons and turn system.

    Features:
    - Dynamic ability buttons that change based on current character
    - Turn system: players take turns, then enemy turn with 10-second delay
    - Retreat button to end battle
    - Full combat calculations with HP, DEF, ATK, EVA, ACC
    - Buff/debuff tracking system
    """

    def __init__(self, team: list, enemy_name: str, user_id: int, enemy_count: int = 1):
        super().__init__(timeout=300)  # 5 minute timeout
        self.team = team
        self.enemy_name = enemy_name
        self.user_id = user_id
        self.current_character_index = 0
        self.is_enemy_turn = False
        self.battle_ended = False
        self.battle_log = []  # Store battle actions for embed updates
        self.enemy_count = enemy_count  # Number of enemies (1 or 2 for Ruffian)

        # Initialize player states
        self.player_states = {}
        for char_name in team:
            attrs = get_character_attributes(char_name)
            rarity_mult = get_character_rarity_multiplier(char_name)
            total_ehp = calculate_ehp(attrs["hp"], attrs["def"], rarity_mult)

            self.player_states[char_name] = {
                "base_hp": attrs["hp"],
                "base_atk": attrs["atk"],
                "base_def": attrs["def"],
                "base_eva": attrs["eva"],
                "base_acc": attrs["acc"],
                "current_ehp": total_ehp,
                "total_ehp": total_ehp,
                "rarity_mult": rarity_mult,
                "is_alive": True,
                "buffs": {},  # {buff_name: {value: float, duration: int}}
                "debuffs": {},  # {debuff_name: {value: float, duration: int}}
            }

        # Initialize enemy states
        self.enemy_states = []
        enemy_attrs = enemyAttributes.get(enemy_name, [175, 5, 5, "0%", "80%", "Punch"])  # Default with at least one ability
        for i in range(enemy_count):
            enemy_hp = enemy_attrs[0]
            enemy_id = f"{enemy_name}_{i}"
            # Safely get abilities (everything after index 4)
            enemy_abilities = enemy_attrs[5:] if len(enemy_attrs) > 5 else ["Punch"]
            self.enemy_states.append({
                "id": enemy_id,
                "name": enemy_name,
                "base_hp": enemy_hp,
                "base_atk": enemy_attrs[1],
                "base_def": enemy_attrs[2],
                "base_eva": parse_percentage_stat(enemy_attrs[3]),
                "base_acc": parse_percentage_stat(enemy_attrs[4]),
                "current_hp": enemy_hp,
                "total_hp": enemy_hp,
                "is_alive": True,
                "buffs": {},
                "debuffs": {},
                "abilities": enemy_abilities,
            })

        # Update buttons for the first character
        self.update_ability_buttons()

    def get_current_character(self):
        """Get the currently active character."""
        # Skip dead characters
        while self.current_character_index < len(self.team):
            char = self.team[self.current_character_index]
            if self.player_states[char]["is_alive"]:
                return char
            self.current_character_index += 1
        return None

    def get_alive_players(self):
        """Get list of alive players."""
        return [char for char in self.team if self.player_states[char]["is_alive"]]

    def get_alive_enemies(self):
        """Get list of alive enemies."""
        return [enemy for enemy in self.enemy_states if enemy["is_alive"]]

    def create_hp_display(self):
        """Create HP display text for all characters."""
        hp_lines = []

        # Player HP
        hp_lines.append("**Players:**")
        for char_name in self.team:
            state = self.player_states[char_name]
            if state["is_alive"]:
                displayed_hp = calculate_displayed_hp(
                    state["current_ehp"],
                    state["total_ehp"],
                    state["base_hp"]
                )
                char_title = characterTitles.get(char_name, char_name)
                hp_lines.append(f"{char_title}: {displayed_hp}/{state['base_hp']} HP")
            else:
                char_title = characterTitles.get(char_name, char_name)
                hp_lines.append(f"{char_title}: ☠️ DEAD")

        # Enemy HP
        hp_lines.append("\n**Enemies:**")
        for enemy in self.enemy_states:
            if enemy["is_alive"]:
                enemy_name = enemy["name"] if self.enemy_count == 1 else f"{enemy['name']} {enemy['id'].split('_')[1]}"
                hp_lines.append(f"{enemy_name}: {enemy['current_hp']}/{enemy['total_hp']} HP")
            else:
                enemy_name = enemy["name"] if self.enemy_count == 1 else f"{enemy['name']} {enemy['id'].split('_')[1]}"
                hp_lines.append(f"{enemy_name}: ☠️ DEAD")

        return "\n".join(hp_lines)

    def create_battle_embed(self):
        """Create or update the battle embed with current state."""
        current_char = self.get_current_character()

        # Build description with current turn info and battle log
        if self.battle_ended:
            description = f"Battle against **{self.enemy_name}** has ended.\n\n"
        elif self.is_enemy_turn:
            description = f"**{self.enemy_name}**'s turn!\n\n"
        elif current_char:
            char_title = characterTitles.get(current_char, current_char)
            description = f"It's **{char_title}**'s turn!\n\n"
        else:
            description = f"Battle against **{self.enemy_name}**\n\n"

        # Add recent battle log (last 5 entries)
        if self.battle_log:
            description += "**Battle Log:**\n"
            for log_entry in self.battle_log[-5:]:
                description += f"• {log_entry}\n"

        embed = discord.Embed(
            title="Battle Screen",
            description=description,
            color=0x3f48cc
        )
        embed.set_image(url="attachment://battle_screen.png")

        # Add HP display as a field
        hp_display = self.create_hp_display()
        embed.add_field(name="HP Status", value=hp_display, inline=False)

        return embed

    def update_ability_buttons(self):
        """Update ability buttons based on current character."""
        # Remove existing ability buttons (keep only retreat button)
        for item in self.children[:]:
            if hasattr(item, 'custom_id') and item.custom_id and item.custom_id.startswith('ability_'):
                self.remove_item(item)

        if self.battle_ended:
            return

        current_char = self.get_current_character()
        if not current_char:
            return

        # Get abilities for current character
        abilities = characterAbilities.get(current_char, [])

        # Create buttons for each ability
        for i, ability_name in enumerate(abilities):
            button = discord.ui.Button(
                label=ability_name,
                style=discord.ButtonStyle.primary,
                custom_id=f"ability_{i}",
                row=i // 5  # Discord allows max 5 buttons per row
            )
            button.callback = self.create_ability_callback(i, ability_name)
            self.add_item(button)

    def create_ability_callback(self, ability_index: int, ability_name: str):
        """Create a callback function for an ability button."""
        async def callback(interaction: discord.Interaction):
            # Check if the user is the battle owner
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This is not your battle!", ephemeral=True)
                return

            if self.is_enemy_turn:
                await interaction.response.send_message("It's the enemy's turn!", ephemeral=True)
                return

            if self.battle_ended:
                await interaction.response.send_message("The battle has ended!", ephemeral=True)
                return

            # Get current character
            current_char = self.get_current_character()
            char_title = characterTitles.get(current_char, current_char)

            # Add to battle log
            self.battle_log.append(f"{char_title} used {ability_name}!")

            # Move to next character (skip dead ones)
            self.current_character_index += 1

            # Skip dead characters
            while self.current_character_index < len(self.team):
                next_char = self.team[self.current_character_index]
                if self.player_states[next_char]["is_alive"]:
                    break
                self.current_character_index += 1

            # Check if all alive players have gone
            if self.current_character_index >= len(self.team):
                # Switch to enemy turn
                self.is_enemy_turn = True
                self.battle_log.append(f"All players have acted. {self.enemy_name}'s turn!")
                # Hide Players ability buttons until their turn
                for item in self.children:
                    if hasattr(item, 'custom_id') and item.custom_id and item.custom_id.startswith('ability_'):
                        item.disabled = True
                # Update embed with new state
                new_embed = self.create_battle_embed()
                await interaction.response.edit_message(embed=new_embed, view=self)

                await self.execute_enemy_turn(interaction)
            else:
                # Update buttons for next character
                self.update_ability_buttons()

                # Update embed with new state
                new_embed = self.create_battle_embed()
                await interaction.response.edit_message(embed=new_embed, view=self)

        return callback

    async def execute_enemy_turn(self, interaction: discord.Interaction):
        """Execute the enemy turn with a 10-second delay."""
        # Wait 10 seconds for enemy turn
        await asyncio.sleep(1)

        # If retreated then cancel this action
        if self.battle_ended:
            return

        # Process each alive enemy's turn
        alive_enemies = self.get_alive_enemies()
        for enemy in alive_enemies:
            if self.battle_ended:
                break

            # Choose random ability (exclude passive descriptions)
            # Safely filter only string abilities that don't start with "Extra Passive"
            abilities = [a for a in enemy["abilities"] if isinstance(a, str) and not a.startswith("Extra Passive")]
            if not abilities:
                continue
            chosen_ability = random.choice(abilities)
            # Parse ability to check if it's AOE or single target
            is_aoe = "all party" in chosen_ability.lower() or "all allies" in chosen_ability.lower()

            # Get target(s)
            alive_players = self.get_alive_players()
            if not alive_players:
                break

            if is_aoe:
                targets = alive_players
            else:
                targets = [random.choice(alive_players)]

            # Execute attack on each target
            for target_char in targets:
                # Get enemy's effective stats (with buffs/debuffs)
                enemy_acc = enemy["base_acc"]
                enemy_atk = enemy["base_atk"]

                # Apply buffs/debuffs to accuracy and attack
                for buff_name, buff_data in enemy["buffs"].items():
                    if "acc" in buff_name.lower():
                        enemy_acc += buff_data["value"]
                    elif "atk" in buff_name.lower():
                        enemy_atk = int(enemy_atk * (1 + buff_data["value"]))

                for debuff_name, debuff_data in enemy["debuffs"].items():
                    if "acc" in debuff_name.lower():
                        enemy_acc -= debuff_data["value"]
                    elif "atk" in debuff_name.lower():
                        enemy_atk = int(enemy_atk * (1 - debuff_data["value"]))

                # Roll for accuracy
                if not roll_accuracy(enemy_acc):
                    enemy_name = enemy["name"] if self.enemy_count == 1 else f"{enemy['name']} {enemy['id'].split('_')[1]}"
                    char_title = characterTitles.get(target_char, target_char)
                    self.battle_log.append(f"{enemy_name}'s attack missed {char_title}!")
                    continue

                # Roll for evasion
                target_state = self.player_states[target_char]
                target_eva = target_state["base_eva"]

                # Apply buffs/debuffs to evasion
                for buff_name, buff_data in target_state["buffs"].items():
                    if "eva" in buff_name.lower():
                        target_eva += buff_data["value"]

                for debuff_name, debuff_data in target_state["debuffs"].items():
                    if "eva" in debuff_name.lower():
                        target_eva -= debuff_data["value"]

                if roll_evasion(target_eva):
                    enemy_name = enemy["name"] if self.enemy_count == 1 else f"{enemy['name']} {enemy['id'].split('_')[1]}"
                    char_title = characterTitles.get(target_char, target_char)
                    self.battle_log.append(f"{char_title} dodged {enemy_name}'s attack!")
                    continue

                # Apply damage
                damage = enemy_atk
                target_state["current_ehp"] = apply_damage_to_ehp(target_state["current_ehp"], damage)

                # Calculate displayed HP
                displayed_hp = calculate_displayed_hp(
                    target_state["current_ehp"],
                    target_state["total_ehp"],
                    target_state["base_hp"]
                )

                enemy_name = enemy["name"] if self.enemy_count == 1 else f"{enemy['name']} {enemy['id'].split('_')[1]}"
                char_title = characterTitles.get(target_char, target_char)
                self.battle_log.append(f"{enemy_name} hit {char_title} for {damage} damage! ({displayed_hp} HP remaining)")

                # Check if player died
                if target_state["current_ehp"] <= 0:
                    target_state["is_alive"] = False
                    self.battle_log.append(f"💀 {char_title} has fallen in battle!")

                    # Regenerate battle screen without dead player and update message
                    await self.regenerate_battle_screen(interaction)

        # Decrement buff/debuff durations and remove expired ones
        self.update_buff_debuff_durations()

        # Check if all players are dead
        if not self.get_alive_players():
            self.battle_ended = True
            self.battle_log.append(f"💀 All players have fallen! {self.enemy_name} wins!")

            # Disable all buttons
            for item in self.children:
                item.disabled = True

            # Update embed with loss message
            new_embed = self.create_battle_embed()
            try:
                await interaction.message.edit(embed=new_embed, view=self)
            except (discord.HTTPException, discord.NotFound):
                pass

            # Set user as no longer in battle
            inventory_collection.update_one(
                {"user_id": self.user_id},
                {"$set": {"inBattle": False}}
            )

            self.stop()
            return

        # Enemy turn complete, switch back to player turn
        self.is_enemy_turn = False
        self.current_character_index = 0

        # Skip to first alive character
        while self.current_character_index < len(self.team):
            char = self.team[self.current_character_index]
            if self.player_states[char]["is_alive"]:
                break
            self.current_character_index += 1

        # Update buttons for first alive character
        self.update_ability_buttons()

        # Update embed with new state
        new_embed = self.create_battle_embed()
        try:
            await interaction.message.edit(embed=new_embed, view=self)
        except (discord.HTTPException, discord.NotFound):
            pass  # In case message can't be edited or was deleted

    def update_buff_debuff_durations(self):
        """Decrement buff/debuff durations and remove expired ones."""
        # Update player buffs/debuffs
        for char_name in self.team:
            state = self.player_states[char_name]

            # Update buffs
            expired_buffs = []
            for buff_name, buff_data in state["buffs"].items():
                buff_data["duration"] -= 1
                if buff_data["duration"] <= 0:
                    expired_buffs.append(buff_name)
            for buff_name in expired_buffs:
                del state["buffs"][buff_name]

            # Update debuffs
            expired_debuffs = []
            for debuff_name, debuff_data in state["debuffs"].items():
                debuff_data["duration"] -= 1
                if debuff_data["duration"] <= 0:
                    expired_debuffs.append(debuff_name)
            for debuff_name in expired_debuffs:
                del state["debuffs"][debuff_name]

        # Update enemy buffs/debuffs
        for enemy in self.enemy_states:
            # Update buffs
            expired_buffs = []
            for buff_name, buff_data in enemy["buffs"].items():
                buff_data["duration"] -= 1
                if buff_data["duration"] <= 0:
                    expired_buffs.append(buff_name)
            for buff_name in expired_buffs:
                del enemy["buffs"][buff_name]

            # Update debuffs
            expired_debuffs = []
            for debuff_name, debuff_data in enemy["debuffs"].items():
                debuff_data["duration"] -= 1
                if debuff_data["duration"] <= 0:
                    expired_debuffs.append(debuff_name)
            for debuff_name in expired_debuffs:
                del enemy["debuffs"][debuff_name]

    async def regenerate_battle_screen(self, interaction: discord.Interaction):
        """Regenerate battle screen image with current alive characters and update Discord message."""
        # Get alive players
        alive_players = self.get_alive_players()
        alive_enemies = self.get_alive_enemies()

        # Get a random background
        background_name, background_file = random.choice(list(backgrounds.items()))
        background_image = Image.open(background_file)
        background_size = background_image.size

        # Place enemies (only alive ones)
        if self.enemy_name == "Ruffian":
            if len(alive_enemies) == 2:
                ruffianB = Image.open(enemyImages["RuffianBack"])
                ruffianF = Image.open(enemyImages["RuffianFront"])
                background_image.paste(ruffianB, enemySpots["RuffianBack"], ruffianB)
                background_image.paste(ruffianF, enemySpots["RuffianFront"], ruffianF)
            elif len(alive_enemies) == 1:
                ruffianB = Image.open(enemyImages["RuffianBack"])
                background_image.paste(ruffianB, enemySpots["RuffianSolo"], ruffianB)
        elif alive_enemies:
            enemy_image = Image.open(enemyImages[self.enemy_name])
            background_image.paste(enemy_image, enemySpots[self.enemy_name], enemy_image)

        # Place team characters (only alive ones)
        # We need to maintain original slot positions
        for i, char_name in reversed(list(enumerate(self.team))):
            if self.player_states[char_name]["is_alive"]:
                if char_name in characterImages:
                    char_image_path = characterImages[char_name]
                    if os.path.exists(char_image_path):
                        char_image = Image.open(char_image_path)
                        char_position = calculate_character_position(char_name, i, background_size)
                        background_image.paste(char_image, char_position, char_image)

        # Save the combined image
        combined_image_path = "./battle_screen.png"
        background_image.save(combined_image_path)

        # Update the Discord message with the new image
        new_embed = self.create_battle_embed()
        try:
            await interaction.message.edit(
                embed=new_embed,
                attachments=[discord.File(combined_image_path)],
                view=self
            )
        except (discord.HTTPException, discord.NotFound):
            pass  # In case message can't be edited or was deleted

    # Temporary Skip Player Turn Button
    @discord.ui.button(label="Skip All Players", style=discord.ButtonStyle.secondary, custom_id="skip_turn_button", row=4)
    async def skip_turn_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to skip All players' turn."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return
        if self.is_enemy_turn:
            await interaction.response.send_message("It's the enemy's turn!", ephemeral=True)
            return
        if self.battle_ended:
            await interaction.response.send_message("The battle has ended!", ephemeral=True)
            return
        # Acknowledge the interaction quickly to satisfy Discord's 3 second limit
        await interaction.response.defer()

        # Move to enemy turn directly
        self.current_character_index = len(self.team)  # Skip all players
        self.is_enemy_turn = True
        self.battle_log.append(f"All players have acted. {self.enemy_name}'s turn!")

        # Disable ability buttons until enemy turn completes
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id and item.custom_id.startswith('ability_'):
                item.disabled = True

        # Update the message embed/view to reflect the state change
        try:
            new_embed = self.create_battle_embed()
            await interaction.message.edit(embed=new_embed, view=self)
        except (discord.HTTPException, discord.NotFound):
            pass

        # Execute the enemy turn (this will include the 10s delay)
        await self.execute_enemy_turn(interaction)


    @discord.ui.button(label="Retreat", style=discord.ButtonStyle.danger, custom_id="retreat_button", row=4)
    async def retreat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retreat button to end the battle."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return

        if self.battle_ended:
            await interaction.response.send_message("The battle has already ended!", ephemeral=True)
            return

        # End the battle
        self.battle_ended = True

        # Add retreat to battle log
        self.battle_log.append(f"You retreated from the battle against {self.enemy_name}!")

        # Disable all buttons
        for item in self.children:
            item.disabled = True

        # Update embed with retreat message
        new_embed = self.create_battle_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)

        # Set user as no longer in battle
        inventory_collection.update_one(
            {"user_id": self.user_id},
            {"$set": {"inBattle": False}}
        )

        # Stop the view
        self.stop()

    async def on_timeout(self):
        """Called when the view times out after 5 minutes of inactivity."""
        # Set user as no longer in battle
        inventory_collection.update_one(
            {"user_id": self.user_id},
            {"$set": {"inBattle": False}}
        )

        # Stop the view
        self.stop()

        # Call parent's on_timeout if it exists
        await super().on_timeout()
'''
@bot.tree.command(name = "battle")
@app_commands.choices(enemies=[
    app_commands.Choice(name="Ruffian", value="Ruffian"),
    app_commands.Choice(name="Grunt", value="Grunt"),
    app_commands.Choice(name="Spearman", value="Spearman"),
    app_commands.Choice(name="Agent", value="Agent"),
    app_commands.Choice(name="Jack Noir", value="Jack Noir"),
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

    # get a random background from the backgrounds hashmap
    background_name, background_file = random.choice(list(backgrounds.items()))

    # comnbine background and r_abraize images ontop one another using PIL
    background_image = Image.open(background_file)
    background_size = background_image.size

    # Place enemies first (in the background layer)
    enemy_count = 1  # Default to 1 enemy
    if enemies.name == "Grunt":
        enemy_image = Image.open(enemyImages[enemies.name])
        background_image.paste(enemy_image, enemySpots[enemies.name], enemy_image)
    elif enemies.name == "Ruffian":
        # 50/50 if 2 or 1 ruffians show up
        roll = random.random()
        if roll < 0.5:
            enemy_count = 2
            ruffianB = Image.open(enemyImages["RuffianBack"])
            ruffianF = Image.open(enemyImages["RuffianFront"])
            background_image.paste(ruffianB, enemySpots["RuffianBack"], ruffianB)
            background_image.paste(ruffianF, enemySpots["RuffianFront"], ruffianF)
        else:
            ruffianB = Image.open(enemyImages["RuffianBack"])
            background_image.paste(ruffianB, enemySpots["RuffianSolo"], ruffianB)
    elif enemies.name == "Spearman":
        enemy_image = Image.open(enemyImages[enemies.name])
        background_image.paste(enemy_image, enemySpots[enemies.name], enemy_image)
    elif enemies.name == "Agent":
        enemy_image = Image.open(enemyImages[enemies.name])
        background_image.paste(enemy_image, enemySpots[enemies.name], enemy_image)
    elif enemies.name == "Jack Noir":
        enemy_image = Image.open(enemyImages[enemies.name])
        background_image.paste(enemy_image, enemySpots[enemies.name], enemy_image)

    enemyList = []
    for _ in range(enemy_count):
        enemyList.append(enemies.name)

    # Place team characters dynamically based on their feet positions
    # Reverse order so slot 1 (index 0) is pasted last and appears on top
    for i, char_name in reversed(list(enumerate(team))):
        if char_name in characterImages:
            char_image_path = characterImages[char_name]
            if os.path.exists(char_image_path):
                char_image = Image.open(char_image_path)
                char_position = calculate_character_position(char_name, i, background_size)
                background_image.paste(char_image, char_position, char_image)

    # save the combined image to a new file
    combined_image_path = "./battle_screen.png"
    background_image.save(combined_image_path)

    embed = discord.Embed(
        title="Battle Screen",
        description=f"Battle against **{enemies.name}** is starting!",
        color=0x3f48cc
    )
    embed.set_image(url="attachment://battle_screen.png")

    battleStart = startBattle(interaction.user.id, team, enemyList)
    # set inbattle in mongodb
    inventory_collection.update_one(
        {"user_id": interaction.user.id},
        {"$set": {"inBattle": True}}
    )

    # it seems that you need to have a "view" to allow buttons
    class battleView(discord.ui.View):
        def __init__(self, user_id: int):
            super().__init__()
            self.user_id = user_id
            self.build_ability_buttons(battleStart)

        def build_ability_buttons(self, abilities):
            # Remove old ability buttons (keep Retreat)
            self.clear_items()
            self.add_item(self.retreat_button)

            for i, ability_name in enumerate(abilities):
                button = discord.ui.Button(
                    label=ability_name,
                    style=discord.ButtonStyle.primary,
                    row=i // 5
                )

                async def ability_callback(interaction: discord.Interaction, ability_index=i, ability_name=ability_name):
                    if interaction.user.id != self.user_id:
                        await interaction.response.send_message("This is not your battle!", ephemeral=True)
                        return
                    await interaction.response.defer()
                    nextCharacter = advanceBattle(interaction.user.id, ability_index)

                   # self.build_ability_buttons(nextCharacter)
                   # await interaction.edit_original_response(view=self)

                button.callback = ability_callback
                self.add_item(button)



        @discord.ui.button(label="Retreat", style=discord.ButtonStyle.danger, custom_id="retreat_button", row=1)
        async def retreat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            """Retreat button to end the battle."""
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This is not your battle!", ephemeral=True)
                return

            # End the battle
            endBattle(interaction.user.id, 0)
            # set in mongodb battle over
            inventory_collection.update_one(
                {"user_id": interaction.user.id},
                {"$set": {"inBattle": False}}
            )

            # Disable all buttons
            for item in self.children:
                item.disabled = True

            await interaction.response.edit_message(view=self)
            await interaction.followup.send("You have retreated from the battle like a baby")

    battle_view = battleView(interaction.user.id)
    await interaction.response.send_message(file=discord.File(combined_image_path), embed=embed, view=battle_view)


'''
    # Create battle view with interactive buttons
    #battle_view = BattleView(team=team, enemy_name=enemies.name, user_id=interaction.user.id, enemy_count=enemy_count)

    # Create initial battle embed
    #embed = battle_view.create_battle_embed()
    embed = discord.Embed(
        title="Battle Screen",
        description=f"Battle against **{enemies.name}** is starting!",
        color=0x3f48cc
    )
    embed.set_image(url="attachment://battle_screen.png")

    # Set user as in battle
    inventory_collection.update_one(
        {"user_id": interaction.user.id},
        {"$set": {"inBattle": True}}
    )

    # send the combined image as a discord message with interactive buttons
    try:
        await interaction.response.send_message(
            file=discord.File(combined_image_path),
            embed=embed,
           # view=battle_view
        )
    except (discord.HTTPException, discord.DiscordException) as e:
        # If sending fails, reset the battle state
        inventory_collection.update_one(
            {"user_id": interaction.user.id},
            {"$set": {"inBattle": False}}
        )
        raise'''


HELP_GIF_URL = "https://media.discordapp.net/attachments/796742546910871562/1442307872490000432/JITSTUCKMOBILEGAME.gif?ex=6926efa1&is=69259e21&hm=160f8b3552a36078f4941e02aafbb3408a95be77be4f5ffa6697ff3aacd53397&format=webp&animated=true"
@bot.tree.command(name="help")
async def help_command(ctx):
    """Show Help"""
    await ctx.response.send_message(HELP_GIF_URL)

@bot.command()
@commands.is_owner()  # Prevent other people from using the command
async def syncapp(ctx: commands.Context) -> None:
    """Sync app commands to Discord."""
    await ctx.bot.tree.sync()
    await ctx.send('Application commands synchronized!')



if __name__ == "__main__":
    bot.run(TOKEN)