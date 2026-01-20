from utils import *

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

# Store global variable of turn order based on discord id so that battles dont get mixed up between users at same time
turnOrder = {}
whosTurn = {}
teamAbilities = {}
battleEhp = {}

def startBattle(discordID, team, enemies):
  print("Battle Started with user", discordID)
  teamAbilities[discordID] = getAllAbilities(discordID, team, enemies)
  turnOrder[discordID] = calculateTurnOrder(discordID, team, enemies)
  for member in team:
    print(f"Team member {member} abilities: {teamAbilities[discordID]['players'][member]}")
  for enemy in enemies:
    print(f"Enemy {enemy} abilities: {teamAbilities[discordID]['enemies'][enemy]}")

  print("Turn order is:", turnOrder)
  print("DiscordID turn order is", turnOrder[discordID])
  whosTurn[discordID] = turnOrder[discordID][0]

  print("Battle Start Configuration Finished", discordID)
  # should return character abilities from characterattributes for first character on team
  return teamAbilities[discordID]['players'][whosTurn[discordID]]

def advanceBattle(discordID, abilityUsed):
  # once everything with configuration is finished then startBattle will end and return with first character on team abilities
  # then if any button is pressed from main.py that isnt retreat it should call advanceBattle
  # it will advance the battle for the discordID and for the abiliyUsed (0 = Ab1 up to 2 and leave for 3 to be possible for ult)
  # then it will do all the calculations and it will update all the stored data for that battle (hp) (in future buff/debuff)
  print("Ability used was:", abilityUsed)
  print("Current turn is:", whosTurn[discordID])
  # do math here
  # then it will return the abilities for the next character in the turn order
 # whosTurn[discordID] = turnOrder[discordID][+1]
  # get abilties for next character
  if abilityUsed is not None:
    currentIndex = turnOrder[discordID].index(whosTurn[discordID])
    whosTurn[discordID] = turnOrder[discordID][currentIndex + 1]
  if whosTurn[discordID] == "0":
    print("Enemy turn, no abilities to return")
    # skip over and go to enemy logic
    enemyTurn(discordID)
    # after enemy turn is done it will return the next player character abilities
    return teamAbilities[discordID]['players'][whosTurn[discordID]]
  else:
    print("Next turn is for", whosTurn[discordID])
  return teamAbilities[discordID]['players'][whosTurn[discordID]]


def enemyTurn(discordID):
  # nothing yet
  print("Enemy turn for user", discordID)
  # do enemy logic here
 # print("Enemy logic happened for user", discordID)
 # each enemy gets to attack twice
  # reset back to the beginning of turn order because enemy turn is now over (temp code)

  # Note: double check that both enemies can attack before this is called when implementing logic

  whosTurn[discordID] = turnOrder[discordID][0]
  print("Next turn is for", whosTurn[discordID])
  #advanceBattle(discordID, None)



def getAllAbilities(discordID, team, enemies):
  print("Getting abilities for players and enemies in battle of user", discordID)
  allAbilities = {
    "players": {team[i]: characterAbilities[team[i].lower()] for i in range(len(team))},
    "enemies": {enemies[i]: enemyAbilities[enemies[i]] for i in range(len(enemies))}
  }
  return allAbilities
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
