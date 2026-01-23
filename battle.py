import random
from utils import *

# Store global variable of turn order based on discord id so that battles dont get mixed up between users at same time
turnOrder = {}
whosTurn = {}
allAbilities = {}
battleStats = {}

def startBattle(discordID, team, enemies):
  print("Battle Started with user", discordID)
  allAbilities[discordID] = getAllAbilities(discordID, team, enemies)
  turnOrder[discordID] = calculateTurnOrder(discordID, team, enemies)
  for member in team:
    print(f"Team member {member} abilities: {allAbilities[discordID]['players'][member]}")
  for enemy in enemies:
    print(f"Enemy {enemy} abilities: {allAbilities[discordID]['enemies'][enemy]}")

  print("Turn order is:", turnOrder)
  print("DiscordID turn order is", turnOrder[discordID])
  whosTurn[discordID] = turnOrder[discordID][0]

  # Get hp and defense of players and place into battleEHP
  battleStats[discordID] = getStats(discordID, team, enemies)

  print(battleStats[discordID])

  print("Battle Start Configuration Finished", discordID)
  # should return character abilities from characterattributes for first character on team
  return allAbilities[discordID]['players'][whosTurn[discordID]]

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
    return allAbilities[discordID]['players'][whosTurn[discordID]]
  else:
    print("Next turn is for", whosTurn[discordID])
  return allAbilities[discordID]['players'][whosTurn[discordID]]


def enemyTurn(discordID):
  # nothing yet
  print("Enemy turn for user", discordID)
  # do enemy logic here

  # get all enemies in this battle for discord id
  enemiesInBattle = list(battleStats[discordID]['enemies'].keys())
  print("Enemies in battle are:", enemiesInBattle)

  # get first enemy then next enemy until all have gone
  # need to jump back up here if enemy has moves remaining

  for enemy in enemiesInBattle:
    while battleStats[discordID]['enemies'][enemy]['moves'] > 0:
      damageDealt = 0
      targetsChosen = []

      # randomly select an ability from enemy abilities
      enemyAbilitiesList = allAbilities[discordID]['enemies'][enemy]
      print(f"Abilities for enemy {enemy} are:", enemyAbilitiesList)
      selectedAbility = random.choice(list(enemyAbilitiesList.keys()))  # same chance for each ability
      print(f"Enemy {enemy} selected ability:", selectedAbility)

      # do option checks
      options = enemyAbilitiesList[selectedAbility]
      print(f"Options for ability {selectedAbility} are:", options)

      if 'A' in options:
        print(f"Enemy {enemy} is using attack ability {selectedAbility}")
        damageDealt = battleStats[discordID]['enemies'][enemy]['attack']
      if 'F' in options:
        print(f"Enemy {enemy} is targeting player {random.choice(list(battleStats[discordID]['players'].keys()))} using {selectedAbility}")
      if 'Z' in options:
        print(f"Enemy {enemy} is skipping their turn using ability {selectedAbility}")


      if targetsChosen is None or len(targetsChosen) == 0:
        print(f"Enemy {enemy} did not select any targets, error in logic")
        targetsChosen = [random.choice(list(battleStats[discordID]['players'].keys()))]

      if damageDealt > 0:
        for target in targetsChosen:
          print(f"Enemy {enemy} planning to deal {damageDealt} damage to player {target} using ability {selectedAbility}")

          # accuracy check
          if random.randint(1, 100) > battleStats[discordID]['enemies'][enemy]['accuracy']:
            print(f"Enemy {enemy}'s attack missed player {target}!")
          else:
            # evasion check
            if random.randint(1, 100) <= battleStats[discordID]['players'][target]['evasion']:
              print(f"Player {target} evaded the attack from enemy {enemy}!")
            else:
              print(f"Enemy {enemy} hit player {target} for {damageDealt} damage!")
              # do
              battleStats[discordID]['players'][target]['ehp'] -= damageDealt

        # battleStats[discordID]['players'][target]['ehp'] -= damageDealt
        print(f"Player {target} now has {battleStats[discordID]['players'][target]['ehp']} ehp remaining")

      # repeat for number of moves enemy has
      enemyMoves = battleStats[discordID]['enemies'][enemy]['moves']
     # print(f"Enemy {enemy} has {enemyMoves} moves")

      if enemyMoves >= 1:
        battleStats[discordID]['enemies'][enemy]['moves'] -= 1
        print(f"Enemy {enemy} has {battleStats[discordID]['enemies'][enemy]['moves']} moves remaining")
        continue

 # print("Enemy logic happened for user", discordID)
 # each enemy gets to attack twice
  # reset back to the beginning of turn order because enemy turn is now over (temp code)

  # Note: double check that both enemies can attack before this is called when implementing logic
  # Every enemy has a certain amount of moves based on their enemyAttributes

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

def getStats(discordID, team, enemies):
  allStats = {
    "players": {},
    "enemies": {}
  }

  for player in team:
    allStats['players'][player] = {
      "ehp": characterAttributes[player.lower()][0] + int(characterAttributes[player.lower()][2] * (1.0 if player in rChar else 1.5 if player in srChar else 2.0)),
      "attack": characterAttributes[player.lower()][1],
      "evasion": characterAttributes[player.lower()][3],
      "accuracy": characterAttributes[player.lower()][4],
    }

  for enemy in enemies:
    allStats['enemies'][enemy] = {
      "ehp": enemyAttributes[enemy][0] + int(enemyAttributes[enemy][2] * 1.2),
      "attack": enemyAttributes[enemy][1],
      "evasion": enemyAttributes[enemy][4],
      "accuracy": enemyAttributes[enemy][5],
      "moves": enemyAttributes[enemy][3],
    }

  return allStats


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
