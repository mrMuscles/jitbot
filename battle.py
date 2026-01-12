# English only
enemyAttributes = {
    "Ruffian": [175, 5, 5, "0%", "80%", "Punch"],
    # 25 damage, 65% acc
    "Grunt": [400, 250, 45, "0%", "100%", "Punch", "Slam, Deal 15 Damage to all party members"],
    "Spearman": [175, 5, 5, "0%", "80%", "Punch", "Swipe, Deal 20 damage to all party members", "Stab, Apply 15%% attack damage bonus to self for this turn and deal damage"],
    "Agent": [175, 5, 5, "0%", "80%", "Punch", "Sneak, Add 15%% evasion to self for next 4 turns, then use Punch"],
    "Jack Noir": [1000, 30, 10, "5%", "90%", "Stab", "Shiv, Deal damage and apply bleed to player (-3% hp per turn) for one turn, this can stack", "Slash, Deal only 5 damage to all party members, but apply bleed to all party members for one turn.", "Extra Passive: Attack lowest health party member each turn"]
}
# English Only
characterAttributes = {
    "rAbraize": [200, 10, 10, "3%", "90%", "Punch", "Sleep", "Missing Assignments"],
    "rNoah": [180, 10, 8, "3%", "90%", "Punch", "Fiddle", "Bo"],
    "rTrey": [250, 12, 8, "3%", "90%", "Punch", "Irish Goodbye", "Cheesy Fries"],
    "rFreeman": [180, 8, 8, "10%", "90%", "Slap", "Ponder", "SMASH!"]
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

characterAbilities = {
  "r_abraize": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Sleep": ['Z'],                         # Skip Turn (temp)
    "Missing Assignments": ['D', 'G']       # Buff self with +5% evasion for 1 turn
  },
  "r_noah": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Fiddle": ['E', 'F'],                   # -5% debuff to all stats to 1 enemy
    "Bo": ['Z']                             # Skip turn (temp)
  },
  "r_trey": {
    "Punch": ['A'],                         # Flat Damage using Attack Stat
    "Irish Goodbye": ['Z'],                 # Skip turn (temp)
    "Cheesy Fries": ['Z']                   # Skip turn (temp)
  },
  "r_freeman": {
    "Slap": ['A'],                         # Flat Damage using Attack Stat
    "Ponder": ['C', 'D'],                  # +3% evasion buff to all teammates
    "SMASH!": ['Z']                        # Skip turn (temp)
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

def startBattle(discordID, team, enemies):
  print("Battle Started with user", discordID)
  getAllAbilities(discordID, team, enemies)
  turnOrder = calculateTurnOrder(discordID, team, enemies)
  print("Turn order is:", turnOrder)

  print("battle process finished for user", discordID)

def getAllAbilities(discordID, team, enemies):
  print("Getting abilities for players and enemies in battle of user", discordID)

  # return dictionary like this for when called by startBattle
  # allAbilities:
  #  {
  #    "players": {
  #        "rAbraize": ["Punch", "Sleep", "Missing Assignments"],
  #        ...
  #    },
  #    "enemies": {
  #        "Ruffian": ["Punch"],
  #        ...
  #    }
  #  }

def calculateTurnOrder(discordID, team, enemies):
  print("Calculating turn order for battle of user", discordID)
  # from team array/dictionary in that order then it should be enemies in that order (mostly doesnt matter as
  # there is only one enemy and the only double battle is a ruffian so priority between them doesnt matter)
  switch = ["0"]                    # used to indicate that it is the enemies turn (to remove buttons)
  order = team + switch + enemies
  return order


def endBattle(discordID, reason):
  # 0 == reason is retreat
  # 1 == reason is all characters defeated
  # 2 == reason is victory
  if 0 == reason:
    print("User", discordID, "has retreated from battle")
  elif 1 == reason:
    print("User", discordID, "has been defeated in battle")
  elif 2 == reason:
    print("User", discordID, "has won the battle")
  else:
    print("Error with battle: ", discordID)
  print("Battle ended with user, now cleanup for ", discordID)
  # discard battle and cleanup
