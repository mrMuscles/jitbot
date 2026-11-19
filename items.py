# =====================================================================================
#  ITEMS
# =====================================================================================
#
#  Every item in the bot is written in this file.
#  Players buy items with Grist in /item store, then put ONE of them in their team's item slot
#  with /item equip. The equipped item helps the whole team in every battle.
#  You do NOT need to know how to code to add or change an item.
#
#  HOW TO ADD A NEW ITEM
#   1. Find the TEMPLATE block a bit further down this file.
#   2. Copy the whole template, from the  # add_item(  line down to the  # )  line.
#   3. Paste it at the very bottom of this file.
#   4. Remove the "# " from the start of every line you pasted.
#      (In VS Code: select those lines and press Ctrl + /  to do it all at once)
#   5. Change the fields to what you want (every field is explained below).
#   6. Save this file and restart the bot.
#   7. Look at the bot's console. If anything is wrong it prints an [ITEM WARNING]
#      that says which item has the problem and how to fix it.
#   8. Run /item store in Discord to see your item.
#      (You do NOT need /syncapp for a new item, restarting the bot is enough.)
#
#  TO CHANGE AN ITEM: edit its block, save, restart the bot. Balancing an item only means changing its numbers.
#  TO REMOVE AN ITEM: delete its whole block, save, restart the bot.
#  DON'T RENAME AN ITEM that people already bought. Items are saved by their name,
#  so everyone who owns the old name would lose it.
#  The store shows the items in the same order as this file.
#
#  THE FIELDS
#   name         The item's name in Discord. Every item needs its own name.
#   price        How much Grist it costs. A whole number above 0.
#   description  A sentence or two about the item, shown in the store.
#   emoji        (optional) An emoji shown next to the name, like "🪙".
#   image        (optional) A web link that starts with https:// OR a picture inside the bot folder,
#                like "graphics/items/luckycoin.png". It shows in /item show and /item equip.
#   effect       What kind of thing the item does. Pick ONE from the list below, inside quotes,
#                then add the numbers that effect needs underneath it.
#
#  THE EFFECTS (and the numbers each one needs)
#   "stat_percent"    The whole team gets a % bonus for the whole battle.
#                     Numbers: any of  hp, attack, defense, evasion, accuracy
#   "stat_flat"       The whole team gets a flat bonus for the whole battle.
#                     Numbers: any of  hp, attack, defense, evasion, accuracy
#   "temp_stat_flat"  Like stat_flat, but only for the first few turns of each battle.
#                     Numbers: any of  hp, attack, defense, evasion, accuracy
#                              and  turns = how many turns it lasts
#   "crit_chance"     Every hit your team lands has a chance to be a critical hit.
#                     Numbers: chance = the % chance,  multiplier = how hard a crit hits (1.5 = 1.5x damage)
#   "periodic_heal"   Every few turns, everyone on the team heals a % of their max HP.
#                     Numbers: every = how many turns apart (5 = turns 5, 10, 15...),  percent = % of max HP healed
#  The items below use every one of these effects, so you can also copy the one that is closest to what you want.
#
#  WHAT THE STAT NUMBERS DO (they work like the buffs that abilities give)
#   hp        stat_percent: that % more max HP.     stat_flat: that much more HP.
#   attack    stat_percent: that % more damage.     stat_flat: that much more ATK.
#   defense   the team takes that % less damage. (DEF is already part of HP, so a DEF bonus lowers damage taken instead)
#   evasion   gets added to the % chance to dodge. (3% EVA with evasion = 10 becomes 13%)
#   accuracy  gets added to the % chance to hit.   (90% ACC with accuracy = 5 becomes 95%)
#   atk, eva and acc work as short names too. "def" does NOT work (Python keeps that word for itself), use defense.
#  A "turn" is one full round of a battle: your whole team goes, then the enemies go.
#  Item bonuses only last for the battle. They are never saved onto the characters.
#
#  NEED A NEW KIND OF EFFECT? Something that isn't in the list above (like "heal when you get hit")
#  needs code in item_helper.py and battle.py first. An item that uses an effect from the list
#  only ever needs this file.
#
#  THINGS THAT TRIP PEOPLE UP
#   - Text goes inside quotes:              name = "Lucky Coin",
#   - Every field line ends with a comma:   price = 30,
#   - Numbers have NO quotes and NO % sign: attack = 5,
#   - Lines that start with # are notes for humans. The bot skips them.
#
# =====================================================================================

from item_helper import add_item   # leave this line alone


# ----- TEMPLATE (copy from the next line down to "# )", paste it at the bottom, then remove the "# ") -----
# add_item(
#     name = "My New Item",
#     price = 25,
#     description = "Write a sentence or two about the item here.",
#     emoji = "🗡️",
#     image = "graphics/items/my_new_item.png",
#     effect = "stat_percent",
#     attack = 5,
#     defense = 5,
# )
# ----- END OF TEMPLATE -----


# ----- Agent Knife: +5% ATK and +10% EVA -----
add_item(
    name = "Agent Knife",
    price = 35,
    description = "A knife taken off a Dersite agent. Light, sharp and easy to dodge with.",
    emoji = "🔪",
    image = "graphics/items/agentknife.png",
    effect = "stat_percent",
    attack = 5,
    evasion = 10,
)


# ----- Dersite Enforcer Hat: the team takes 5% less damage -----
add_item(
    name = "Dersite Enforcer Hat",
    price = 50,
    description = "An enforcer's cap. Somehow it makes the whole team tougher.",
    emoji = "🧢",
    image = "graphics/items/grunthat.png",
    effect = "stat_percent",
    defense = 5,
)


# ----- Dersite Longman's Spear: +15% ACC -----
add_item(
    name = "Dersite Longman's Spear",
    price = 50,
    description = "A long Dersite spear that helps your team line up their hits.",
    emoji = "🔱",
    image = "graphics/items/spearmanspear.png",
    effect = "stat_percent",
    accuracy = 15,
)


# ----- Lucky Coin: 2% chance for a hit to do 1.5x damage -----
add_item(
    name = "Lucky Coin",
    price = 30,
    description = "Flip it before a fight. Every now and then a hit lands extra hard.",
    emoji = "🪙",
    image = "graphics/items/luckycoin.png",
    effect = "crit_chance",
    chance = 2,
    multiplier = 1.5,
)


# ----- Perfectly Generic Object: +1 to every stat for the first 3 turns -----
add_item(
    name = "Perfectly Generic Object",
    price = 5,
    description = "It's perfectly generic. It helps a little, for a little while.",
    emoji = "📦",
    image = "graphics/items/perfectlygenericobject.png",
    effect = "temp_stat_flat",
    hp = 1,
    attack = 1,
    defense = 1,
    evasion = 1,
    accuracy = 1,
    turns = 3,
)


# ----- Bag of Purina Treats: heal 5% of max HP on turns 5, 10, 15... -----
add_item(
    name = "Bag of Purina Treats",
    price = 45,
    description = "A snack break every few turns keeps the team going.",
    emoji = "🦴",
    image = "graphics/items/treats.png",
    effect = "periodic_heal",
    every = 5,
    percent = 5,
)


# ----- Dersite Knuckledusters: +5% ACC -----
add_item(
    name = "Dersite Knuckledusters",
    price = 20,   # nobody has picked a price for this one yet, change it to what you want
    description = "Brass knuckles from Derse. They steady your aim.",
    emoji = "👊",
    image = "graphics/items/dersiteknuckleduster.png",
    effect = "stat_percent",
    accuracy = 5,
)
