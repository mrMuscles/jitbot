# This file will store any big things to share between Main or Battle that isn't logic but just data

'''
Technically every character that exists HERE must actually exist below
abraizeChar = ["r_abraize", "r_abraize2", "sr_abraize", "ssr_abraize"]
treyChar = ["r_trey", "ssr_trey"]
noahChar = ["r_noah", "sr_noah"]
freemanChar = ["r_freeman", "sr_freeman"]
stephenChar = ["r_stephen", "sr_stephen"]
jaydenChar = ["ssr_jayden", "r_jaiden"]
homestuckChar = ["r_homestuck", "sr_homestuck"]
scottieChar = ["ssr_scottie"]
maxChar = ["r_max", "sssr_max"]
binktopChar = ["sr_binktop"]
'''

# Characters that exists here are every character in the game but in each section
rChar = ["r_abraize", "r_abraize2", "r_trey", "r_noah", "r_freeman", "r_stephen", "r_homestuck", "r_max", "r_jaiden"]
srChar = ["sr_freeman", "sr_stephen", "sr_homestuck", "sr_abraize", "sr_trey", "sr_noah", "sr_binktop"]
ssrChar = ["ssr_abraize", "ssr_trey", "ssr_jayden"]
specialChar = ["ssr_scottie"]
secretChar = ["sssr_max"]

# Character Titles for displaying to user
characterTitles = {
    "r_abraize": "[Rolling in Success] Abraize Masood",
    "r_abraize2": "[Productivity Time] Abraize Masood",
    "sr_abraize": "[Time on my Side] Abraize Masood",
    "ssr_abraize": "[Rewind] Abraize Masood",
    "r_trey": "[Irish Golden Standard] Treyvaughn Lewis",
    "sr_trey": "[Heavy Sleeper] Treyvaughn Lewis",
    "ssr_trey": "[Seeker of Silence] Treyvaughn Lewis",
    "r_noah": "[pillagingPirate] Noah Cave",
    "sr_noah": "[S'all Good, Man] Noah Cave",
    "r_freeman": "[Who I am to Me] Freeman",
    "sr_freeman": "[Freedom in Jeopardy] Freeman",
    "r_stephen": "[You Marlowe?] Stephen Goraynov",
    "sr_stephen": "[Master of Intervention] Stephen Goraynov",
    "ssr_jayden": "[Sworn Protectorate of Creation] Jayden Ceballos",
    "sr_homestuck": "[Thief in God's Clothing] Homestuck",
    "r_homestuck": "[Tour of a Lifetime] Homestuck",
    "r_max": "[I can make a-] Max Yakuvobich",
    "r_jaiden": "[Picked up, Packed up] Jaiden Ceballos",
    "ssr_scottie": "[Overwhelming Dread] Scottie Jenkins",
    "sr_binktop": "[Saviour of the Digital Realm] Binktop",
    "sssr_max": "[???] ???"
}

backgrounds = {
    "purple1": "./graphics/battle/purple1.png",
    "purple2": "./graphics/battle/purple2.png",
    "garrysmod": "./graphics/battle/garrysmodbackground.png"
}
# /battle uses purple2, unless the enemy has its own background here
DEFAULT_BACKGROUND = "purple2"
enemyBackgrounds = {
    "Garry's Mod": "garrysmod",
}

characterImages ={
    "r_abraize": "./graphics/battle/r_abraize.png",
    "r_abraize2": "./graphics/battle/r_abraize2.png",
    "sr_abraize": "./graphics/battle/sr_abraize.png",
    "ssr_abraize": "./graphics/battle/ssr_abraize.png",
    "r_trey": "./graphics/battle/r_trey.png",
    "sr_trey": "./graphics/battle/sr_trey.png",
    "ssr_trey": "./graphics/battle/ssr_trey.png",
    "r_noah": "./graphics/battle/r_noah.png",
    "sr_noah": "./graphics/battle/sr_noah.png",   # cut out of r_noah2.png (that file has 4 characters in it)
    "r_freeman": "./graphics/battle/r_freeman.png",
    "sr_freeman": "./graphics/battle/sr_freeman.png",
    "ssr_jayden": "./graphics/battle/ssr_jayden.png",
    "r_stephen": "./graphics/battle/r_stephen.png",
    "sr_stephen": "./graphics/battle/sr_stephen.png",
    "sr_homestuck": "./graphics/battle/sr_homestuck.png",
    "ssr_scottie": "./graphics/battle/ssr_scottie.png",
    "r_homestuck": "./graphics/battle/r_homestuck.png",
    "r_max": "./graphics/battle/r_max.png",
    "r_jaiden": "./graphics/battle/r_jaiden.png",
    "sr_binktop": "./graphics/battle/sr_binktop.png"
}
enemyImages = {
    "RuffianBack": "./graphics/battle/ruffianBack.png",   # file names match the capital letters of the real files
    "RuffianFront": "./graphics/battle/ruffianFront.png", # (Windows doesn't care, but Linux / Mac servers can't find them otherwise)
    "Grunt": "./graphics/battle/grunt.png",
    "Spearman": "./graphics/battle/spearman.png",
    "Agent": "./graphics/battle/agent.png",
    "Jack Noir": "./graphics/battle/jackNoir.png",
    "Garry's Mod": "./graphics/battle/gmod.png",
    "Addonshield": "./graphics/battle/addonshield.png"
}

# Character Banner GIFs
bannerGifs = {
    "r_abraize_gif": "https://media.discordapp.net/attachments/1426812344549380136/1442262933018251467/R_ABRAIZE.gif?ex=692a1187&is=6928c007&hm=ea36ca7f4742ec74ad4786385624dbbbf1c69ba9c809bf2499c5b23b85f39b38&=&width=813&height=524",
}

otherImages = {
    "recycle_gif": "https://media.discordapp.net/attachments/796742546910871562/1455728132240703593/recycled_B.gif?ex=69873838&is=6985e6b8&hm=6b929831bdc757d1cdd10794bbb60f8c7d946ab84f13f5e5f58d011f93e7f99b&=&width=813&height=524",
    "no_own_png": "./graphics/broke.png"
}

NO_OWN_PNG = "./graphics/broke.png"

R_ABRAIZE2_GIF = "https://media.discordapp.net/attachments/796742546910871562/1444044329583640748/R_ABRAIZE_PROD.gif?ex=692b4695&is=6929f515&hm=1ecc69064ddd0b38a7b3e9be1d13e2541c99e9e7c0948619b3d486e3ac440f06&=&width=678&height=438"
SR_ABRAIZE_GIF = "https://media.discordapp.net/attachments/907662210619289600/1441575065413091500/SR_ABRAIZ.gif?ex=69414626&is=693ff4a6&hm=c51aa1cf7872069ee96e7365b27d288de2e9cb3d9780375137cebaf6d7196d89&=&width=813&height=524"
SSR_ABRAIZE_GIF = "https://media.discordapp.net/attachments/796742546910871562/1453592615822950450/SSR_ABRAIZE.gif?ex=6955435e&is=6953f1de&hm=ef8fb3a6bcb7f6fccec9f36850b8b8d3954a9bfc118843171d03fdf9af369e68&=&width=678&height=438"
R_TREY_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1442262950055251978/R_TREY.gif?ex=692aba4b&is=692968cb&hm=6467f2663cac2d80ffd3f61f9de3436133557568e4b00cec63ee4cbdb1d6da40&=&width=813&height=524"
SR_TREY_GIF = "https://media.discordapp.net/attachments/907662210619289600/1442648569579307180/SR_TREY.gif?ex=6941396e&is=693fe7ee&hm=d12a52705f4952d3860d273dcce43f3598f971d5d581209f61fd46108823194d&=&width=813&height=524"
SSR_TREY_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1438298186409185393/SSR_TREY.gif?ex=692ace51&is=69297cd1&hm=705ffe6482d8c46a88742a82e6565c28ff53cbba9ea15eebe990dfacde708469&=&width=813&height=524"
R_NOAH_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1438298195829719193/R_NOAH.gif?ex=692ace54&is=69297cd4&hm=a4ab137787708b382bd26b0659a39b768dece0b7d0eb03898b4fe4b180428133&=&width=601&height=438"
R_NOAH2_GIF = "https://cdn.discordapp.com/attachments/907662210619289600/1572809217637621830/SR_NOAH_3.gif?ex=6affb83a&is=6afe66ba&hm=cd228f4e33d18f6ec0f959a5bb3a79fc35dcbe6c22fddb36663aed0f72f05298&"
R_FREEMAN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1442262942660952268/R_FREEMAN.gif?ex=692aba49&is=692968c9&hm=3f1edc05a01b0c793ab7ddfe3519054630c1523e68b5c29ec5d4be6624d0e1c0&=&width=813&height=524"
SR_FREEMAN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1438298206193586187/SR_FREEMAN.gif?ex=692ace56&is=69297cd6&hm=6e42e1d45a353ffc60916f54593933273fea88e2d69d400c91f8c6899172174e&=&width=678&height=438"
R_STEPHEN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1443821437378105444/R_STEPHEN.gif?ex=692b1fbf&is=6929ce3f&hm=97986106339c3febd0bb243c25c13f870c331eb2376c2b3bcefc053fac64e26b&=&width=813&height=524"
SR_STEPHEN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1443821457846046741/SR_STEPHEN.gif?ex=692b1fc4&is=6929ce44&hm=fbccf7579c4c5189be6d18689bc65a7e62b064bdd075647ddc64428721d53b3e&=&width=813&height=524"
SSR_JAYDEN_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1441662516672331836/SSR_JAYDEN.gif?ex=692a8558&is=692933d8&hm=c5f5376d3603ce635598548977465872e7a3662802986c6f742c1f590eadd7a4&=&width=813&height=524"
SR_HOMESTUCK_GIF = "https://media.discordapp.net/attachments/907662210619289600/1441689825911505026/SR_HOMESTUCK.gif?ex=6941b107&is=69405f87&hm=181544c05734a721ea53bbe630dcb4b25ed7b95327661a807b97bdba81cc7506&=&width=813&height=524"
SSR_SCOTTIE_GIF = "https://media.discordapp.net/attachments/1426812344549380136/1441591428042985492/SSR_SCOTTIE.gif?ex=69551be3&is=6953ca63&hm=9a1141a0f327f2f16ed80b996243679e62491b0fa2b985babdc1bc09d82cccaa&=&width=813&height=524"
SSSR_MAX_GIF = "https://media.discordapp.net/attachments/1442548563879133357/1460374051834040505/000.png?ex=6966aed2&is=69655d52&hm=2daa8e27abbb1eae7996c33f6b705308567264b3bbaa4bfaa9c889ca95c4e244&=&format=webp&quality=lossless&width=1240&height=698"
R_HOMESTUCK_GIF = "https://media.discordapp.net/attachments/907662210619289600/1572833434982817802/R_HOMESTUCK.gif?ex=6affcec8&is=6afe7d48&hm=ca625cfb04880771fd058c6b5d9ff076c2781b5c117970f0a9152d4ade002888"
R_MAX_GIF = "https://media.discordapp.net/attachments/907662210619289600/1572833434357727273/R_MAX2.gif?ex=6affcec8&is=6afe7d48&hm=e52418210d467478e525be4e53f2c69e93381a93178ec72f27427d9ffb7f2005"
R_JAIDEN_GIF = "https://media.discordapp.net/attachments/907662210619289600/1572833434643202190/R_JAIDEN.gif?ex=6affcec8&is=6afe7d48&hm=2734c1b5863d9073f6402b039175ba1e8a9f77356c484ef07962dffd7b6f7933"
SR_BINKTOP_GIF = "https://cdn.discordapp.com/attachments/907662210619289600/1573813352096989287/SR_BINKTOP.gif?ex=6b035f67&is=6b020de7&hm=4a67c5ce7dd236e655fecd00395fac6965e21b6c082a1a8f7a71d4029e412791&"



enemySpots = {
    "Grunt": (0, 0),
    "RuffianBack": (-25, 130),
    "RuffianFront": (0, 260),
    "RuffianSolo": (0, 150),
    "Spearman": (15, 145),
    "Agent": (20, 150),
    "Jack Noir": (0, 150),
    "Garry's Mod": (0, 37)
}

# Enemies that get summoned during a battle (Garry's Mod's Addonshields) are drawn onto the battle screen when they show up:
# the 1st one goes in the 1st spot, the 2nd in the 2nd... (more than there are spots start again from the 1st)
# "scale" shrinks the picture (0.6 = 60% of its size)
summonSpots = {
    "Addonshield": {"scale": 0.6, "spots": [(150, 232), (30, 236), (190, 160), (75, 150)]},
}

# Enemies that summon more enemies during the battle: every "everyDamage" damage they take, 1 "summon" shows up
# (the summon needs its own enemyAttributes and enemyAbilities line, and it vanishes if the enemy that summoned it is defeated)
enemySummons = {
    "Garry's Mod": {"summon": "Addonshield", "everyDamage": 161},
}

# Enemy Attributes and Character Attributes (5 basic stats, how many moves they get, plus abilities name)
# HP, Attack, Defense, Moves, Evasion, Accuracy, Abilities
enemyAttributes = {
    "Ruffian1": [125, 5, 5, 2, 0, 80, "Punch"],
    "Ruffian2": [125, 5, 5, 2, 0, 80, "Punch"],
    "Grunt": [400, 25, 45, 2, 0, 65, "Punch", "Slam, Deal 15 Damage to all party members"],
    "Spearman": [175, 5, 5, 2, 0, 80, "Punch", "Swipe, Deal 20 damage to all party members", "Stab, Apply 15%% attack damage bonus to self for this turn and deal damage"],
    "Agent": [175, 15, 5, 2, 0, 80, "Punch", "Sneak, Add 15%% evasion to self for next 4 turns, then use Punch"],
    "Jack Noir": [1000, 30, 10, 3, 5, 90, "Stab", "Shiv, Deal damage and apply bleed to player (-3% hp per turn) for one turn, this can stack", "Slash, Deal only 5 damage to all party members, but apply bleed to all party members for one turn.", "Extra Passive: Attack lowest health party member each turn"],
    "Garry's Mod": [650, 70, 65, 2, 0, 85, "Hit, Deal 50% of atk to a targeted enemy", "Addon-Smash!, Rear up for 1 turn then come crashing down on a targeted enemy for full atk", "Passive: Every 161 damage taken, summon an Addonshield in front of himself"],
    "Addonshield": [100, 0, 15, 1, 0, 0, "Draw Attack, The player team's attacks on Garry's Mod hit the Addonshield instead"]
}

# Grist the player gets for WINNING a /battle (losing, retreating or timing out gives nothing)
# The names are the /battle choices. "Ruffian" is when 1 ruffian shows up, "Ruffian x2" is when 2 show up
# A new enemy needs a line here too, otherwise beating it gives 0 Grist
gristRewards = {
    "Ruffian": 5,
    "Ruffian x2": 7,
    "Spearman": 7,
    "Agent": 9,
    "Grunt": 15,
    "Jack Noir": 35,
    "Garry's Mod": 50,
}

# How much Grist 1 roll costs in /item store (a whole number above 0)
rollPrice = 15
# The 10 rolls deal in /item store: how many rolls it gives and how much Grist it costs (whole numbers above 0)
rollBundleAmount = 10
rollBundlePrice = 135
# Only Get the 5 stats from here (abilities are defined in characterAbilities)
# HP, Attack, Defense, Evasion, Accuracy, Abilities
characterAttributes = {
    "r_abraize": [120, 10, 10, 3, 90, "Punch", "Sleep", "Missing Assignments"],
    "r_abraize2": [120, 10, 10, 3, 90, "Punch", "Eat Note", "Productivity Time"],
    "sr_abraize":  [220, 15, 20, 3, 90, "Punch", "Slow", "Attempt"],
    "ssr_abraize": [400, 35, 35, 3, 90, "Accelerated Punch", "Fast Forward", "Rewind", "Universal Stabilizer"],
    "r_trey": [150, 12, 8, 3, 90, "Punch", "Irish Goodbye", "Cheesy Fries"],
    "sr_trey": [250, 15, 20, 3, 75, "Punch", "Drowsy", "Whispers from Beyond"],
    "ssr_trey": [425, 30, 25, 30, 90, "Punch", "Cloak and Dagger", "Shroud", "Reality Sink"],
    "r_noah": [125, 10, 8, 3, 90, "Punch", "Fiddle", "Bo"],
    "sr_noah": [180, 15, 8, 3, 92, "Gavel Strike", "Mock", "Defense Lawyer"],
    "r_freeman": [100, 8, 8, 10, 90, "Slap", "Ponder", "SMASH!"],
    "sr_freeman": [180, 8, 8, 10, 90, "Pistol Whip", "Shoot", "Hide"],
    "r_stephen": [130, 9, 8, 3, 90, "Dropkick", "Light up", "Lock the fuck in"],
    "sr_stephen": [180, 9, 8, 3, 90, "Dropkick", "Consider Intervening", "HIYAAAHHH!"],
    "ssr_jayden": [400, 30, 30, 5, 90, "Distort", "Butler of Swatabi", "Indecision", "Genesis"],
    "sr_homestuck": [180, 18, 15, 5, 90, "Impractical Assailants", "Plunder", "Thief"],
    "ssr_scottie": [320, 40, 40, 5, 90, "Fated Strike", "Existential Dread", "Martyrdom", "Nihilism"],
    "r_homestuck": [140, 11, 7, 5, 90, "Punch", "Spotlight Shift", "Rules for thee"],
    "r_max": [165, 10, 13, 2, 90, "Punch", "Brick Eating", "Tour Alliance"],
    "r_jaiden": [120, 9, 10, 3, 90, "Punch", "Pick Up", "Commitment and Fuck"],
    "sr_binktop": [270, 20, 25, 0, 90, "Viruslash", "McAfee 265+ Antivirus Shield", "Premium Subscription Malware Annihilating Slash"],
    "sssr_max": ["?", "??", "???", "???", "???", "???", "???", "???", "???", "?????"]
}


# HP, Attack, Defense are all Flat Numbers
# Evasion and Accuracy are percentages

# Character titles do not matter in Battle.py as main.py will convert the names to the correct format when needed

# ============================================================================
# HOW AN ABILITY IS WRITTEN
# ============================================================================
# "Ability Name": [option letters..., {numbers}]
#   - the letters say WHAT the move does (Options below)
#   - the dict at the end is optional and says HOW MUCH / HOW LONG
#   - example: "Productivity Time": ['C', 'D', 'H', {"buff": {"BB": 10, "CC": 10}, "turns": 3, "cooldown": 4}]
#       = AOE at Teammates (C) + Buff (D) + Cooldown (H)
#       = +10% attack and +10% defense for the whole team for 3 turns, then it can't be used for 4 turns
#
# A "turn" is one full round: every player goes, then every enemy goes
# Anything an enemy does during its turn starts counting on the next round,
# so an enemy's "for 4 turns" covers the players' next 4 turns
# ============================================================================

# Option A = Damage using Attack Stat (Should be extra parameter in function when calling damaging moves to add damage)
#            Hits 1 enemy (all of them with Option B) and rolls accuracy vs evasion
#            numbers: "power" = % of attack used (default 100), "damage" = flat damage instead of the attack stat,
#                     "percentMaxHP" / "percentCurrentHP" = damage is a % of the target's hp, "trueDamage" = ignores defense buffs,
#                     "sureHit" = can't miss or be evaded, "recoil" = % of the damage dealt that the user takes too,
#                     "hits" = how many times each target gets hit (each hit rolls to hit on its own, SR Binktop's Viruslash),
#                     "hitDebuff": {"name", "chance", "debuff", "turns"} = every hit that lands has a chance to debuff the target (Code Rot)
# Option B = Area of Effect at Enemies
# Option C = Area of Effect at Teammates
# Option D = Buff: the whole team with Option C, one picked teammate with Option G, otherwise yourself
#            numbers: "buff": {stat: %}, "turns", "heal" = % of max hp healed, "debuffImmune" = can't be debuffed while it lasts,
#                     "damageImmune" = can't take any damage while it lasts (hits, Burn, Bleed), paying your own hp still works,
#                     "sureHitsNextTurn": "status name" = every attack they make on their next turn hits (R Jaiden's Commitment)
# Option E = Debuff: every enemy with Option B, one picked enemy with Option F (or the enemy hit by Option A),
#            with no target letter it lands on yourself (or a random teammate with Option O "randomAlly")
#            numbers: "debuff": {stat: %}, "turns"
#            (a buff never goes to the enemies and B / F always aim the debuff at them,
#             that is how Thief can debuff all enemies AND buff the whole team in 1 move)
# Option F = Specific Target on opposing team (the player picks with buttons when there is more than 1, enemies pick on their own)
# Option G = Specific Target on own team (the player picks with buttons when there is more than 1)
# Option H = Cooldown before you can use the same move again, numbers: "cooldown" = how many turns
# Option I = Stacks of same kind on targets which works with 1 or multiple targets
#            numbers: "stacks": {"name", "add", "max", "turns", "perStack": {stat: % for each stack}, "resetOnOtherMove", "loseStackWhenHit"}
#                     "consumeStacks": {"name", "bonusPerStack"} = uses up all the stacks for extra % damage
#                                      {"name", "flatPerStack"}  = uses up all the stacks for extra flat damage (+10 = 10 more damage per stack)
#                     "buffPerStack": {"name", "stats"} = the buff is multiplied by how many stacks you have
# Option J = Rewind (SSR Abraize): the team's hp, buffs and debuffs go back to how they were at the start of the previous turn
# Option K = Sleep (R Abraize): skip your next turn then wake up with a buff, numbers: "sleepTurns", "wakeBuff": {stat: %}, "wakeTurns"
# Option L = Taunt: the other side's single target attacks have to go at you, numbers: "taunt" = how many turns
#            (an enemy taunting, like Addonshield's Draw Attack, makes the party's attacks on its teammates hit it instead)
# Option M = Lingering effect that does something every turn, numbers: "lingering": {...}
#            "Burn" / "Bleed" = lose "percent" of max hp every turn (lands on the other side like Option E, "stackable" lets it stack)
#            "Regeneration" with "heal": True = heal "percent" of max hp every turn (lands on your side like Option D)
#            "Void Spot" (SSR Trey) = sits on the field, ranged attacks miss and power it up, it grows every turn and then bursts
# Option N = Interrupt: "interrupt": {"name", "chance", "guardsAllies", "counter"} = a status with a chance to cancel an enemy
#            attack, it is used up once it works (R Noah's Interfere protects Noah, SR Freeman's Nervous protects the whole team)
# Option O = Luck: "chance" = % the move works at all, "outcomes" = list of moves and 1 gets picked at random,
#            "weights" = how likely each outcome is (same order as outcomes, leave it out for equal chances),
#            "outcomeText" (inside an outcome) = what the battle log says when that outcome is picked,
#            an F next to the outcomes lets the player pick the enemy first (R Jaiden's Pick Up),
#            "randomAlly" = the debuff lands on a random teammate, "dice": [sides, damage for each number rolled]
# Option P = Doom Marks (SSR Scottie): "doom" = "fatedStrike" / "dread" / "martyrdom" / "nihilism"
# Option Q = Jack Noir Special Passive (Attack lowest health target each turn)
# Option R = Future Boss Special Reserved
# OPtion S = Future Boss Special Reserved
# Option T = Future Boss Special Reserved
# Option U = Future Boss Special Reserved
# Option V = Future Boss Special Reserved
# OPtion W = Future Boss Special Reserved
# Option X = reserved
# Option Y = reserved
# Option Z = Skip Move (For Dev, the Skip button in /battle uses it too), "skipText" = what the battle log says

# Other numbers any move can have
#   "turns" = how long buffs/debuffs last (default 1, 0 = only for the rest of the current turn)
#   "once" = can only be used once per battle (ultimates)
#   "extraTurn" = the user goes again straight away
#   "selfDamage" = flat hp the user pays, "selfHeal" = % of max hp the user heals, "selfHealHP" = flat hp the user heals
#   "allyCost" = every other teammate pays that % of their max hp (it can't knock them out)
#   "skipEnemyTurn" = the enemies skip their next turn (R Homestuck's Rules for thee)
#   "missNextAttack": "status name" = the user's next attack misses no matter what (R Max's Brick Eating)
#   "accuracy" = replaces the user's accuracy for this move (and makes a move without Option A roll to hit too)
#   "ranged" = it is a ranged attack (these miss while a Void Spot is on the field)
#   "buffName" / "debuffName" = name shown in the embed for the buff/debuff (like "Warped")
#   "failText" = what the battle log says when an Option O "chance" move doesn't work
#   "parry": {"buff", "counter"} = buff + Parry on yourself for "turns", every attack that lands on you gets the "counter" move back,
#            with Option G the picked teammate is defended (single target attacks on them hit you instead) (SR Binktop's Antivirus Shield)
#   "windUp": "status name" = enemies only: using the move just winds up (shown as that status) and ends the enemy's turn,
#            the move really happens at the start of its next turn, "windUpText" / "releaseText" = the battle log (Garry's Mod's Addon-Smash!)
#   "channel": {"skipTurns", "damage", "percentMaxHP", "stunTurns"} = Channeling: your next "skipTurns" turns are skipped and getting hit
#            cancels it (you can act again), if it runs out you hit the Option F enemy for damage + % of its max hp, then you're Stunned
#            (SR Binktop's Annihilating Slash)

# Options D and E are Basic buffs meaning they only change the 5 main stats of HP, Attack, Defense, Evasion, and Accuracy
# These are the stat codes used inside "buff" / "debuff":
#   AA = HP       -> changes max hp by that % (current hp can't go above the new max)
#   BB = Attack   -> +10 = deals 10% more damage
#   CC = Defense  -> +10 = takes 10% less damage (base defense is already inside ehp, so defense buffs change damage taken instead)
#   DD = Accuracy -> added straight onto the percentage (90% accuracy with DD +10 = 100%)
#   EE = Evasion  -> added straight onto the percentage
statNames = {"AA": "HP", "BB": "ATK", "CC": "DEF", "DD": "ACC", "EE": "EVA"}

# The Skip button in /battle: an Option Z move, so the current character does nothing and the next one goes
skipMove = ['Z', {"skipText": "and stood idle, boggling vacantly at the enemy"}]

# Abilities Moveset + Options for abilities (what every move does is written in the /char embeds in main.py)
characterAbilities = {
  "r_abraize": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    # Evasion drops to 0% and you skip your next turn, then wake up with +15% atk and def for 2 turns
    "Sleep": ['E', 'K', {"debuff": {"EE": 100}, "turns": 2, "sleepTurns": 1, "wakeBuff": {"BB": 15, "CC": 15}, "wakeTurns": 2}],
    "Missing Assignments": ['D', {"buff": {"DD": 5}, "turns": 1}]   # +5% accuracy to self for 1 turn
  },
  "r_abraize2": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Eat Note": ['D', {"buff": {"EE": 10}, "turns": 1, "selfDamage": 25}],  # +10% evasion to self for 1 turn, costs 25 hp
    # +10% atk and def for the whole team for 3 turns, 4 turn cooldown
    "Productivity Time": ['C', 'D', 'H', {"buff": {"BB": 10, "CC": 10}, "turns": 3, "cooldown": 4}]
  },
  "sr_abraize": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Slow": ['E', 'F', {"debuff": {"DD": 15}, "turns": 2}],         # -15% accuracy to 1 enemy for 2 turns
    # 15% chance to work: heals self for 50% and gives the whole team +20% atk for 1 turn
    "Attempt": ['C', 'D', 'O', {"chance": 15, "selfHeal": 50, "buff": {"BB": 20}, "turns": 1,
                                "failText": "but nothing happened... (it only works 15% of the time)"}]
  },
  "ssr_abraize": {
    # Can't miss, +1 Accelerated stack (+10% atk each, max 10 = +100%), all stacks are lost when using any other move
    "Accelerated Punch": ['A', 'F', 'I', {"sureHit": True, "stacks": {"name": "Accelerated", "add": 1, "max": 10,
                                                                      "perStack": {"BB": 10}, "resetOnOtherMove": True}}],
    # +5% acc, +40% atk, +15% def for the team for 1 turn and you go again straight away, 5 turn cooldown
    "Fast Forward": ['C', 'D', 'H', {"buff": {"DD": 5, "BB": 40, "CC": 15}, "turns": 1, "extraTurn": True, "cooldown": 5}],
    "Rewind": ['H', 'J', {"cooldown": 3}],                          # Team goes back to how it was last turn, 3 turn cooldown
    # Ultimate: the team can't be debuffed, +50% atk for 5 turns and everyone is healed to full, once per battle
    "Universal Stabilizer": ['C', 'D', {"buff": {"BB": 50}, "turns": 5, "debuffImmune": True, "heal": 100, "once": True}]
  },
  "r_trey": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Irish Goodbye": ['D', 'H', {"buff": {"EE": 10}, "turns": 1, "cooldown": 2}],  # +10% evasion to self for 1 turn, 2 turn cooldown
    # 70% chance to hit 1 enemy with Burn (loses 5% of their max hp at the end of the turn)
    "Cheesy Fries": ['F', 'M', {"accuracy": 70, "ranged": True, "lingering": {"name": "Burn", "percent": 5, "turns": 1}}]
  },
  "sr_trey": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Drowsy": ['B', 'E', {"debuff": {"DD": 10}, "turns": 1}],       # -10% accuracy to all enemies for 1 turn
    "Whispers from Beyond": ['C', 'D', 'H', {"buff": {"DD": 10}, "turns": 2, "cooldown": 1}]  # +10% accuracy for the team for 2 turns, 1 turn cooldown
  },
  "ssr_trey": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    # +100% eva and +10% acc to self for 1 turn, then stab 1 enemy for 10% of their max hp as true damage, 2 turn cooldown
    "Cloak and Dagger": ['A', 'D', 'F', 'H', {"buff": {"EE": 100, "DD": 10}, "turns": 1, "percentMaxHP": 10,
                                              "trueDamage": True, "cooldown": 2}],
    # +50% evasion for the team for 3 turns, but enemies have to attack you for 1 turn, 4 turn cooldown
    "Shroud": ['C', 'D', 'H', 'L', {"buff": {"EE": 50}, "turns": 3, "taunt": 1, "cooldown": 4}],
    # Ultimate: Void Spot for 3 turns, ranged attacks miss (+50% power each), +100% power every turn, then it bursts on all enemies
    "Reality Sink": ['M', {"lingering": {"name": "Void Spot", "turns": 3, "growPerTurn": 100, "growPerRanged": 50}, "once": True}]
  },
  "r_noah": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Fiddle": ['E', 'F', {"debuff": {"DD": 5}, "turns": 2}],        # -5% accuracy to 1 enemy for 2 turns
    "Bo": ['H', 'N', {"interrupt": {"name": "Interfere", "chance": 50}, "cooldown": 2}]  # 50% to cancel the next hit on self, 2 turn cooldown
  },
  "sr_noah": {
    "Gavel Strike": ['A', 'F'],                                     # Flat Damage using Attack Stat
    # -15% accuracy to all enemies and enemies have to attack you, both for 1 turn
    "Mock": ['B', 'E', 'L', {"debuff": {"DD": 15}, "turns": 1, "taunt": 1}],
    # the whole team can't take any damage for the rest of this turn, 3 turn cooldown
    "Defense Lawyer": ['C', 'D', 'H', {"damageImmune": True, "turns": 0, "cooldown": 3}]
  },
  "r_freeman": {
    "Slap": ['A', 'F'],                                             # Flat Damage using Attack Stat
    "Ponder": ['C', 'D', {"buff": {"EE": 3}, "turns": 1}],          # +3% evasion for the team for 1 turn
    "SMASH!": ['A', 'D', 'F', {"buff": {"BB": 10}, "turns": 1, "recoil": 100}]  # +10% atk to self then attack, take the same damage back
  },
  "sr_freeman": {
    "Pistol Whip": ['A', 'F'],                                      # Flat Damage using Attack Stat
    # 20% chance the safety is off and it deals 10% of the enemy's current hp
    "Shoot": ['A', 'F', 'O', {"chance": 20, "percentCurrentHP": 10, "sureHit": True, "ranged": True,
                              "failText": "but the safety was on!"}],
    # Nervous: 25% chance to interrupt any enemy attack on the team and Shoot the attacker back (used up once it works)
    "Hide": ['N', {"interrupt": {"name": "Nervous", "chance": 25, "guardsAllies": True, "counter": "Shoot"}}]
  },
  "r_stephen": {
    "Dropkick": ['A', 'F'],                                         # Flat Damage using Attack Stat
    # +1 Baller stack for 3 turns and enemies have to attack you for 3 turns, every hit you take removes a stack
    "Light up": ['I', 'L', {"stacks": {"name": "Baller", "add": 1, "turns": 3, "loseStackWhenHit": True}, "taunt": 3}],
    "Lock the fuck in": ['D', 'I', {"buffPerStack": {"name": "Baller", "stats": {"BB": 5}}, "turns": 1}]  # +5% atk per Baller stack for 1 turn
  },
  "sr_stephen": {
    "Dropkick": ['A', 'F'],                                         # Flat Damage using Attack Stat
    "Consider Intervening": ['I', {"stacks": {"name": "Considering", "add": 1, "turns": 3}}],  # +1 Considering stack (lasts 3 turns)
    "HIYAAAHHH!": ['A', 'F', 'I', {"consumeStacks": {"name": "Considering", "flatPerStack": 15}}]  # +15 damage per stack, uses them up
  },
  "ssr_jayden": {
    "Distort": ['A', 'B', {"power": 50}],                           # 50% of atk as damage to all enemies (less damage since it hits all of them)
    "Butler of Swatabi": ['B', 'E', 'H', {"debuff": {"DD": 30}, "turns": 2, "cooldown": 2}],  # -30% accuracy to all enemies for 2 turns, 2 turn cooldown
    # 1/3: +20% atk and def for the team, 1/3: -20% atk and def to all enemies, 1/3: lose 1 hp
    "Indecision": ['O', {"outcomes": [
      ['C', 'D', {"buff": {"BB": 20, "CC": 20}, "turns": 2}],
      ['B', 'E', {"debuff": {"BB": 20, "CC": 20}, "turns": 2}],
      [{"selfDamage": 1}]
    ]}],
    # Ultimate: Regeneration (5% hp every turn) for the team and Warped (-25% acc, -35% max hp, -25% def) on all enemies for 5 turns
    "Genesis": ['B', 'C', 'E', 'M', {"lingering": {"name": "Regeneration", "percent": 5, "turns": 7, "heal": True},
                                     "debuff": {"DD": 25, "AA": 35, "CC": 25}, "debuffName": "Warped", "turns": 5, "once": True}]
  },
  "sr_homestuck": {
    "Impractical Assailants": ['A', 'F', 'O', {"dice": [6, 10]}],  # Roll a die, 10 damage for every number rolled
    # +15% atk to self and -15% atk to a random teammate for 1 turn
    "Plunder": ['D', 'E', 'O', {"buff": {"BB": 15}, "debuff": {"BB": 15}, "randomAlly": True, "turns": 1}],
    # -100% accuracy to all enemies and +100% accuracy for the team for 1 turn, 5 turn cooldown
    "Thief": ['B', 'C', 'D', 'E', 'H', {"buff": {"DD": 100}, "debuff": {"DD": 100}, "turns": 1, "cooldown": 5}]
  },
  "ssr_scottie": {
    # Low damage (50% atk) that can't miss, every 2nd hit on the same enemy gives it a Doom Mark
    "Fated Strike": ['A', 'F', 'P', {"power": 50, "sureHit": True, "doom": "fatedStrike"}],
    # All enemies: -(15% + 7.5% per Doom Mark) atk and -(20% + 5% per Doom Mark) acc for 3 turns, uses up the marks
    "Existential Dread": ['B', 'E', 'P', {"doom": "dread", "debuff": {"BB": 15, "DD": 20}, "perMark": {"BB": 7.5, "DD": 5}, "turns": 3}],
    # Enemies have to attack you and you take 30% less damage for 2 turns, every hit you take gives the attacker a Doom Mark
    # If you get knocked out during it, every Doom Mark explodes for 150% of your atk, 2 turn cooldown
    "Martyrdom": ['D', 'H', 'L', 'P', {"buff": {"CC": 30}, "turns": 2, "taunt": 2, "doom": "martyrdom", "explodePower": 150, "cooldown": 2}],
    # Ultimate: from turn 4 with 5+ Doom Marks out, for 3 turns every enemy hurts itself, hits an ally or lies still each turn
    "Nihilism": ['B', 'P', {"doom": "nihilism", "requiresRound": 4, "requiresMarks": 5, "turns": 3, "once": True}]
  },
  "r_homestuck": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    # enemies have to attack you for 1 turn and you take 5% less damage this turn (+5 DEF)
    "Spotlight Shift": ['D', 'L', {"buff": {"CC": 5}, "turns": 0, "taunt": 1}],
    # the enemies skip their next turn, but every other teammate loses 10% of their max hp (it can't knock them out), 2 turn cooldown
    "Rules for thee": ['H', {"skipEnemyTurn": True, "allyCost": 10, "cooldown": 2}]
  },
  "r_max": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    # heal 25 hp, but the next attack misses no matter what
    "Brick Eating": [{"selfHealHP": 25, "missNextAttack": "Full of Brick"}],
    # pick a teammate: +25% to every stat for 1 turn, 2 turn cooldown
    "Tour Alliance": ['D', 'G', 'H', {"buff": {"AA": 25, "BB": 25, "CC": 25, "DD": 25, "EE": 25}, "turns": 1, "cooldown": 2}]
  },
  "r_jaiden": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    # throw a box at the enemy you pick (ranged), what's inside decides the damage, "weights" = the % chance of each box
    "Pick Up": ['F', 'O', {"weights": [15, 15, 30, 20, 19, 1], "outcomes": [
      ['A', 'F', {"damage": 1, "ranged": True, "outcomeText": "the box had a teddy bear"}],
      ['A', 'F', {"damage": 15, "ranged": True, "outcomeText": "the box had a lovely vase"}],
      ['A', 'F', {"damage": 10, "ranged": True, "outcomeText": "the box had school supplies"}],
      ['A', 'F', {"damage": 15, "ranged": True, "outcomeText": "the box had a precious game console"}],
      ['A', 'F', {"damage": 2, "ranged": True, "outcomeText": "the box had rolled up posters"}],
      ['A', 'F', {"damage": 50, "ranged": True, "outcomeText": "the box had a live beartrap"}]
    ]}],
    # pick a teammate: every attack they make on their next turn is guaranteed to hit
    "Commitment and Fuck": ['D', 'G', {"sureHitsNextTurn": "Committed"}]
  },
  "sr_binktop": {
    # 2 swipes at 1 enemy, 75% atk each, every swipe that lands has a 15% chance of Code Rot (-10% atk for 2 turns)
    "Viruslash": ['A', 'F', {"power": 75, "hits": 2, "hitDebuff": {"name": "Code Rot", "chance": 15, "debuff": {"BB": 10}, "turns": 2}}],
    # +75% def and Parry for this turn (every attack that lands on him gets a Viruslash back), 3 turn cooldown
    # pick a teammate to defend (their single target attacks hit him instead), picking himself defends nobody
    "McAfee 265+ Antivirus Shield": ['G', 'H', {"parry": {"buff": {"CC": 75}, "counter": "Viruslash"}, "turns": 0, "cooldown": 3}],
    # pick an enemy, Channeling skips his next 2 turns (getting hit cancels it and he can act again), then 265 + 7.5% of the
    # enemy's max hp as damage and he is Stunned for 1 turn, 6 turn cooldown
    "Premium Subscription Malware Annihilating Slash": ['F', 'H', {"channel": {"skipTurns": 2, "damage": 265, "percentMaxHP": 7.5, "stunTurns": 1},
                                                                   "cooldown": 6}]
  }
}

enemyAbilities = {
  "Ruffian1": {
    "Punch": ['A', 'F']                                             # Flat Damage using Attack Stat
  },
  "Ruffian2": {
    "Punch": ['A', 'F']                                             # Flat Damage using Attack Stat
  },
  "Grunt": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Slam": ['A', 'B', {"damage": 20}]                              # 20 damage to all party members
  },
  "Spearman": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Swipe": ['A', 'B', {"damage": 20}],                            # 20 damage to all party members
    "Stab": ['A', 'D', 'F', {"buff": {"BB": 15}, "turns": 0}]       # +15% atk for the rest of this turn, then attack
  },
  "Agent": {
    "Punch": ['A', 'F'],                                            # Flat Damage using Attack Stat
    "Sneak": ['A', 'D', 'F', {"buff": {"EE": 15}, "turns": 4}]      # +15% evasion for the next 4 turns, then Punch
  },
  "Jack Noir": {
    "Stab": ['A', 'F', 'Q'],                                        # Hits the party member with the lowest hp
    # Hits the lowest hp party member and makes them Bleed (3% of max hp next turn), Bleed stacks
    "Shiv": ['A', 'F', 'I', 'M', 'Q', {"lingering": {"name": "Bleed", "percent": 3, "turns": 1, "stackable": True}}],
    # Only 5 damage, but to all party members and they all Bleed
    "Slash": ['A', 'B', 'M', {"damage": 5, "lingering": {"name": "Bleed", "percent": 3, "turns": 1, "stackable": True}}]
  },
  "Garry's Mod": {
    "Hit": ['A', 'F', {"power": 50}],                               # 50% of atk to 1 party member
    # rears up (that ends his turn), then at the start of his next turn comes crashing down for 100% of atk on 1 party member
    "Addon-Smash!": ['A', 'F', {"windUp": "Rearing Up", "windUpText": "rears up", "releaseText": "comes crashing down"}]
  },
  "Addonshield": {
    # Taunt for enemies: the party's single target attacks on Garry's Mod hit the Addonshield instead
    "Draw Attack": ['L', {"taunt": 1}]
  }
}
