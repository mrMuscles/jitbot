# This file will store any big things to share between Main or Battle that isn't logic but just data

'''
Technically every character that exists HERE must actually exist below
abraizeChar = ["r_abraize", "r_abraize2", "sr_abraize", "ssr_abraize"]
treyChar = ["r_trey", "ssr_trey"]
noahChar = ["r_noah"]
freemanChar = ["r_freeman", "sr_freeman"]
stephenChar = ["r_stephen", "sr_stephen"]
jaydenChar = ["ssr_jayden"]
homestuckChar = ["sr_homestuck"]
scottieChar = ["ssr_scottie"]
maxChar = ["sssr_max"]
'''
# Characters that exists here are every character in the game but in each section
rChar = ["r_abraize", "r_abraize2", "r_trey", "r_noah", "r_freeman", "r_stephen"]
srChar = ["sr_freeman", "sr_stephen", "sr_homestuck", "sr_abraize", "sr_trey"]
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
    "r_freeman": "[Who I am to Me] Freeman",
    "sr_freeman": "[Freedom in Jeopardy] Freeman",
    "r_stephen": "[You Marlowe?] Stephen Goraynov",
    "sr_stephen": "[Master of Intervention] Stephen Goraynov",
    "ssr_jayden": "[Sworn Protectorate of Creation] Jayden Ceballos",
    "sr_homestuck": "[Thief in God's Clothing] Homestuck",
    "ssr_scottie": "[Overwhelming Dread] Scottie Jenkins",
    "sssr_max": "[???] ???"
}

# Enemy Attributes and Character Attributes (5 basic stts plus abilities name)
enemyAttributes = {
    "Ruffian": [175, 5, 5, "0%", "80%", "Punch"],
    "Grunt": [400, 25, 45, "0%", "65%", "Punch", "Slam, Deal 15 Damage to all party members"],
    "Spearman": [175, 5, 5, "0%", "80%", "Punch", "Swipe, Deal 20 damage to all party members", "Stab, Apply 15%% attack damage bonus to self for this turn and deal damage"],
    "Agent": [175, 5, 5, "0%", "80%", "Punch", "Sneak, Add 15%% evasion to self for next 4 turns, then use Punch"],
    "Jack Noir": [1000, 30, 10, "5%", "90%", "Stab", "Shiv, Deal damage and apply bleed to player (-3% hp per turn) for one turn, this can stack", "Slash, Deal only 5 damage to all party members, but apply bleed to all party members for one turn.", "Extra Passive: Attack lowest health party member each turn"]
}
# Only Get the 5 stats from here (abilities are defined in characterAbilities)
# HP, Attack, Defense, Evasion, Accuracy, Abilities
characterAttributes = {
    "r_abraize": [200, 10, 10, "3%", "90%", "Punch", "Sleep", "Missing Assignments"],
    "r_abraize2": [200, 10, 10, "3%", "90%", "Punch", "Eat Note", "Productivity Time"],
    "sr_abraize":  [200, 15, 20, "3%", "90%", "Punch", "Slow", "Attempt"],
    "ssr_abraize": [600, 35, 35, "3%", "90%", "Accelerated Punch", "Fast Forward", "Rewind", "Universal Stabilizer"],
    "r_trey": [250, 12, 8, "3%", "90%", "Punch", "Irish Goodbye", "Cheesy Fries"],
    "sr_trey": [300, 15, 20, "3%", "75%", "Punch", "Drowsy", "Whispers from Beyond"],
    "ssr_trey": [750, 30, 25, "30%", "90%", "Punch", "Cloak and Dagger", "Shroud", "Reality Sink"],
    "r_noah": [180, 10, 8, "3%", "90%", "Punch", "Fiddle", "Bo"],
    "r_freeman": [180, 8, 8, "10%", "90%", "Slap", "Ponder", "SMASH!"],
    "sr_freeman": [180, 8, 8, "10%", "90%", "Pistol Whip", "Shoot", "Hide"],
    "r_stephen": [180, 9, 8, "3%", "90%", "Dropkick", "Light up", "Lock the fuck in"],
    "sr_stephen": [180, 9, 8, "3%", "90%", "Dropkick", "Consider Intervening", "HIYAAAHHH!"],
    "ssr_jayden": [600, 30, 30, "5%", "90%", "Punch", "Butler of Swatabi", "Indecision", "Genesis"],
    "sr_homestuck": [180, 18, 15, "5%", "90%", "Impractical Assailants", "Plunder", "Thief"],
    "ssr_scottie": [700, 40, 40, "5%", "90%", "Shield Bash", "Guardian's Shield", "Fortify", "Eternal Watch"],
    "sssr_max": ["?", "??", "???", "???", "???", "???", "???", "???", "???", "?????"]
}


# HP, Attack, Defense are all Flat Numbers
# Evasion and Accuracy are percentages

# Character titles do not matter in Battle.py as main.py will convert the names to the correct format when needed

# Option A = Damage using Attack Stat (Should be extra parameter in function when calling damaging moves to add damage)
# Option B = Area of Effect at Enemies
# Option C = Area of Effect at Teammates
# Option D = Buff (However if Option B then it should AOE Buff Enemies and if Option C then AOE Buff Teammates)
# Option E = Debuff (However if Option B then it should AOE Debuff Enemies and if Option C then AOE Debuff Teammates)
# Option F = Specific Target on opposing team
# Option G = Specific Target on own team
# Option Z = Skip (For Dev)

# Options D and E are Basic buffs meaning they only change the 5 main stats of HP, Attack, Defense, Evasion, and Accuracy

# Abilities Moveset + Options for abilities
characterAbilities = {
  "r_abraize": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Sleep": ['Z'],                         # Skip Turn (temp)
    "Missing Assignments": ['D', 'G']       # Buff self with +5% evasion for 1 turn
  },
  "r_abraize2": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Eat Note": ['Z'],                 # Skip turn (temp)
    "Productivity Time": ['Z']              # Skip turn (temp)
  },
  "sr_abraize": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Slow": ['Z'],                          # Skip turn (temp)
    "Attempt": ['Z']                        # Skip turn (temp)
  },
  "ssr_abraize": {
    "Accelerated Punch": ['A'],             # Flat Damage using Attack Stat
    "Fast Forward": ['Z'],                  # Skip turn (temp)
    "Rewind": ['Z'],                        # Skip turn (temp)
    "Universal Stabilizer": ['Z']          # Skip turn (temp)
  },
    "r_trey": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Irish Goodbye": ['Z'],                 # Skip turn (temp)
    "Cheesy Fries": ['Z']                   # Skip turn (temp)
  },
  "sr_trey": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Drowsy": ['Z'],                        # Skip turn (temp)
    "Whispers from Beyond": ['Z']           # Skip turn (temp)
  },
  "ssr_trey": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Cloak and Dagger": ['Z'],              # Skip turn (temp)
    "Shroud": ['Z'],                        # Skip turn (temp)
    "Reality Sink": ['Z']                   # Skip turn (temp)
  },
  "r_noah": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Fiddle": ['E', 'F'],                   # -5% debuff to all stats to 1 enemy
    "Bo": ['Z']                             # Skip turn (temp)
  },
  "r_freeman": {
    "Slap": ['A'],                         # Flat Damage using Attack Stat
    "Ponder": ['C', 'D'],                  # +3% evasion buff to all teammates
    "SMASH!": ['Z']                        # Skip turn (temp)
  },
  "sr_freeman": {
    "Pistol Whip": ['A'],                  # Flat Damage using Attack Stat
    "Shoot": ['Z'],                        # Skip turn (temp)
    "Hide": ['Z']                          # Skip turn (temp)
  },
  "r_stephen": {
    "Dropkick": ['A'],                     # Flat Damage using Attack Stat
    "Light up": ['Z'],                     # Skip turn (temp)
    "Lock the fuck in": ['Z']              # Skip turn (temp)
  },
  "sr_stephen": {
    "Dropkick": ['A'],                     # Flat Damage using Attack Stat
    "Consider Intervening": ['Z'],         # Skip turn (temp)
    "HIYAAAHHH!": ['Z']                    # Skip turn (temp)
  },
  "ssr_jayden": {
    "Punch": ['A'],                        # Flat Damage using Attack Stat
    "Butler of Swatabi": ['Z'],            # Skip turn (temp)
    "Indecision": ['Z'],                   # Skip turn (temp)
    "Genesis": ['Z']
  },
  "sr_homestuck": {
    "Impractical Assailants": ['A'],       # Flat Damage using Attack Stat
    "Plunder": ['Z'],                      # Skip turn (temp)
    "Thief": ['Z']                         # Skip turn (temp)
  },
  "ssr_scottie": {
    "Ultimate Strike": ['A'],              # Flat Damage using Attack Stat
    "Shadow Dance": ['Z'],                 # Skip turn (temp)
    "Phantom Grip": ['Z']                  # Skip turn (temp)
  }
}

enemyAbilities = {
  "Ruffian": {
    "Punch": ['A']                         # Flat Damage using Attack Stat
  },
  "Grunt": {
    "Punch": ['A'],                        # Flat Damage using Attack Stat
    "Slam": ['A', 'B']                     # Damage to all enemies
  }
}

# GIFs for Everything
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
SSSR_MAX_GIF = "https://media.discordapp.net/attachments/1442548563879133357/1460374051834040505/000.png?ex=6966aed2&is=69655d52&hm=2daa8e27abbb1eae7996c33f6b705308567264b3bbaa4bfaa9c889ca95c4e244&=&format=webp&quality=lossless&width=1240&height=698"
RECYCLE_GIF = "https://media.discordapp.net/attachments/796742546910871562/1455728132240703593/recycled_B.gif?ex=6955c7f8&is=69547678&hm=a047b1b23feab6ea79f4c79303bd9ee6bfba8ba9b800813754e05b9615529585&=&width=678&height=438"
