import copy
import random
from utils import *
import item_helper  # the equipped item (items are in MongoDB), item_helper.py does what it does in battle

# Store global variable of turn order based on discord id so that battles dont get mixed up between users at same time
turnOrder = {}
whosTurn = {}
allAbilities = {}
battleStats = {}
battleEffects = {}  # global buffs and debuffs array for each battle (AA-EE stats) + every other status (stacks, taunts, burns...)
battleLog = {}      # what happened in the battle, shown to the user in the battle embed
battleInfo = {}     # round number, cooldowns, used ultimates, rewind snapshots, void spot, display names and the result

LOG_LIMIT = 40      # only remember the newest lines of each battle log (main.py shows as many as fit in the embed)

# Every effect inside battleEffects[discordID] is a dict like:
#   {"side": "players", "unit": "r_abraize", "name": "Productivity Time", "kind": "buff",
#    "stats": {"BB": 10, "CC": 10}, "turns": 3, "fresh": False}
# kind = "buff" / "debuff" (Options D and E, AA-EE stats), "status" (stacks, taunts, sleep...), "dot" (Burn, Bleed, Regeneration)
# turns = turns left (None = until it gets used up), fresh = made during the enemy turn so it starts counting next round


# ============================================================================
# START / ADVANCE / END (the functions main.py calls)
# ============================================================================

def startBattle(discordID, team, enemies, item=None):
  print("Battle Started with user", discordID)
  allAbilities[discordID] = getAllAbilities(discordID, team, enemies)
  turnOrder[discordID] = calculateTurnOrder(discordID, team, enemies)
  # Get hp and defense of players and place into battleEHP
  battleStats[discordID] = getStats(discordID, team, enemies)
  battleEffects[discordID] = []
  battleLog[discordID] = []
  battleInfo[discordID] = {
    "round": 0,
    "phase": "players",       # "players" -> "enemies" -> "roundEnd"
    "names": getDisplayNames(team, enemies),
    "cooldowns": {},          # (side, unit, ability): first round it can be used again (Option H)
    "usedOnce": set(),        # (side, unit, ability) of "once" moves that were already used (ultimates)
    "snapshots": [],          # hp + effects at the start of the last 2 rounds (Option J Rewind)
    "voidSpot": None,         # SSR Trey's Reality Sink (Option M)
    "skipEnemyTurn": False,   # R Homestuck's Rules for thee: the next enemy turn gets skipped
    "pending": [],            # log lines waiting for the current move's line to be written first (defeats, explosions)
    "result": None,           # "victory" or "defeat" once the battle is decided
    "item": None,             # the equipped item (item_helper.battleStart fills this in)
  }
  print("Turn order is:", turnOrder[discordID])

  enemyNames = " & ".join(displayName(discordID, 'enemies', enemy) for enemy in enemies)
  addLog(discordID, f"⚔️ The battle against **{enemyNames}** begins!")
  item_helper.battleStart(discordID, item)  # the equipped item's bonuses for the team
  startRound(discordID)
  whosTurn[discordID] = turnOrder[discordID][0]
  if item_helper.teamSkipsTurn(discordID):
    # the item (Protein Brick) made the team skip round 1: going on from the last team member runs the enemy turn first
    whosTurn[discordID] = turnOrder[discordID][turnOrder[discordID].index("0") - 1]
    nextTurn(discordID)

  print("Battle Start Configuration Finished", discordID)
  # should return character abilities from characterattributes for first character on team
  return allAbilities[discordID]['players'][whosTurn[discordID]]

def advanceBattle(discordID, abilityUsed, target=None):
  # once everything with configuration is finished then startBattle will end and return with first character on team abilities
  # then if any button is pressed from main.py that isnt retreat it should call advanceBattle
  # abilityUsed = which ability button (0 = Ab1 up to 2, 3 = ult), target = unit picked for Option F / G (None = picked automatically)
  # it does all the calculations and updates all the stored data for that battle (hp, buffs/debuffs, cooldowns)
  # then it returns the abilities for the next character in the turn order (None once the battle is over)
  if not battleExists(discordID) or battleInfo[discordID]['result']:
    return None

  actor = whosTurn[discordID]
  abilities = allAbilities[discordID]['players'][actor]
  abilityNames = list(abilities.keys())
  if abilityUsed is None or not 0 <= abilityUsed < len(abilityNames):
    print("Invalid ability", abilityUsed, "for", actor)
    return abilities
  abilityName = abilityNames[abilityUsed]
  ready, reason = abilityStatus(discordID, 'players', actor, abilityName)
  if not ready:
    print(f"{actor} can't use {abilityName} right now ({reason})")
    return abilities

  print(f"Round {battleInfo[discordID]['round']}: {actor} used {abilityName}" + (f" on {target}" if target else ""))
  extraTurn = optionChecks(discordID, 'players', actor, abilityName, abilities[abilityName], target)

  if checkBattleOver(discordID):
    return None
  if extraTurn and isAlive(discordID, 'players', actor):
    addLog(discordID, f"⏩ **{displayName(discordID, 'players', actor)}** gets to go again!")
  else:
    nextTurn(discordID)
  if battleInfo[discordID]['result']:
    return None
  return allAbilities[discordID]['players'][whosTurn[discordID]]

def endBattle(discordID, reason):
  # 0 == reason is retreat
  # 1 == reason is all characters defeated
  # 2 == reason is victory
  # 3 == reason is the battle timed out (nobody pressed a button)
  # 4 == reason is something broke
  if 0 == reason:
    print("User", discordID, "has retreated from battle")
  elif 1 == reason:
    print("User", discordID, "has been defeated in battle")
  elif 2 == reason:
    print("User", discordID, "has won the battle")
  elif 3 == reason:
    print("User", discordID, "battle timed out")
  else:
    print("Error with battle: ", discordID)
  print("Battle ended with user, now cleanup for ", discordID)
  # discard battle and cleanup
  for battleData in (turnOrder, whosTurn, allAbilities, battleStats, battleEffects, battleLog, battleInfo):
    battleData.pop(discordID, None)


# ============================================================================
# TURN ORDER / ROUNDS
# ============================================================================

def nextTurn(discordID):
  # Moves whosTurn to the next player that can act. Reaching "0" in the turn order runs the enemy turn
  # (which also ends the round), then it carries on from the top of the team
  order = turnOrder[discordID]
  index = order.index(whosTurn[discordID]) + 1
  for _ in range(1000):  # safety net so a logic bug can't freeze the bot
    if battleInfo[discordID]['result']:
      return
    if index == 0 and item_helper.teamSkipsTurn(discordID):
      index = order.index("0")  # the item (Protein Brick) made the whole team skip this round, so the enemies go
    if index >= len(order) or order[index] == "0":
      print("Enemy turn, no abilities to return")
      enemyTurn(discordID)
      index = 0
      continue
    unit = order[index]
    index += 1
    if not isAlive(discordID, 'players', unit):
      continue
    if skipsTurn(discordID, 'players', unit):
      addLog(discordID, f"💤 **{displayName(discordID, 'players', unit)}** is fast asleep and skips their turn.")
      continue
    whosTurn[discordID] = unit
    print("Next turn is for", unit)
    return
  raise RuntimeError(f"Turn order got stuck for battle {discordID}")

def enemyTurn(discordID):
  # Every enemy uses all of its moves (enemyAttributes "Moves"), then the round ends and the next one starts
  print("Enemy turn for user", discordID)
  info = battleInfo[discordID]
  info['phase'] = 'enemies'

  # R Homestuck's Rules for thee: the enemies don't get to do anything this turn
  skipped = info['skipEnemyTurn']
  info['skipEnemyTurn'] = False
  if skipped:
    addLog(discordID, "⛔ The enemies' turn was skipped!")

  # get first enemy then next enemy until all have gone (nobody when the turn was skipped)
  for enemy in ([] if skipped else list(battleStats[discordID]['enemies'].keys())):
    if info['result']:
      break
    if not isAlive(discordID, 'enemies', enemy):
      continue
    # Motionless (from Nihilism) only lasts until the enemy's own next turn
    removeStatus(discordID, 'enemies', enemy, "Motionless")
    if findEffect(discordID, 'enemies', enemy, "Nihilism", 'status'):
      nihilismTurn(discordID, enemy)
      checkBattleOver(discordID)
      continue
    if skipsTurn(discordID, 'enemies', enemy):
      addLog(discordID, f"💤 **{displayName(discordID, 'enemies', enemy)}** can't move this turn.")
      continue

    # repeat for number of moves enemy has
    for move in range(battleStats[discordID]['enemies'][enemy]['moves']):
      if info['result'] or not isAlive(discordID, 'enemies', enemy):
        break
      enemyAbilitiesList = allAbilities[discordID]['enemies'][enemy]
      usable = [name for name in enemyAbilitiesList if abilityStatus(discordID, 'enemies', enemy, name)[0]]
      if not usable:
        break
      selectedAbility = random.choice(usable)  # same chance for each ability
      print(f"Enemy {enemy} selected ability:", selectedAbility)
      optionChecks(discordID, 'enemies', enemy, selectedAbility, enemyAbilitiesList[selectedAbility])
      checkBattleOver(discordID)

  if not info['result']:
    endRound(discordID)
    checkBattleOver(discordID)
  if not info['result']:
    startRound(discordID)

def nihilismTurn(discordID, enemy):
  # SSR Scottie's Nihilism (Option P) takes over the enemy's whole turn:
  # 1/3 it hurts itself, 1/3 it attacks one of its allies, 1/3 it lies motionless (every attack on it lands)
  name = displayName(discordID, 'enemies', enemy)
  allies = [other for other in aliveUnits(discordID, 'enemies') if other != enemy]
  event = random.randint(1, 3)
  if event == 2 and not allies:
    event = 1  # nobody else to hit so it hurts itself
  if event == 3:
    addStatus(discordID, 'enemies', enemy, "Motionless", turns=1, addStacks=0, sureHitAgainst=True)
    addLog(discordID, f"🌀 **{name}** is lost in Nihilism and lies motionless... every attack on it will land!")
    return
  victim = enemy if event == 1 else random.choice(allies)
  total = 0
  for move in range(battleStats[discordID]['enemies'][enemy]['moves']):
    if not isAlive(discordID, 'enemies', victim):
      break
    damage, note = computeDamage(discordID, 'enemies', enemy, 'enemies', victim, {})
    total += dealDamage(discordID, 'enemies', victim, damage)
  if victim == enemy:
    addLog(discordID, f"🌀 **{name}** is lost in Nihilism and hurts itself for {total} damage!")
  else:
    addLog(discordID, f"🌀 **{name}** is lost in Nihilism and attacks its ally **{displayName(discordID, 'enemies', victim)}** for {total} damage!")

def startRound(discordID):
  info = battleInfo[discordID]
  info['round'] += 1
  info['phase'] = 'players'
  takeSnapshot(discordID)
  addLog(discordID, f"**— Round {info['round']} —**")
  item_helper.roundStart(discordID)  # items that do something at the start of a round (heals, bonuses wearing off)

def endRound(discordID):
  # End of a full round: lingering effects tick (Option M), the Void Spot grows, then every timer counts down by 1
  info = battleInfo[discordID]
  info['phase'] = 'roundEnd'

  # Option M: Burn / Bleed / Regeneration (stacks of the same one are added together into 1 log line)
  groups = {}
  for effect in battleEffects[discordID]:
    if effect['kind'] == 'dot' and not effect['fresh']:
      groups.setdefault((effect['side'], effect['unit'], effect['name']), []).append(effect)
  for (side, unit, name), effects in groups.items():
    if not isAlive(discordID, side, unit):
      continue
    amount = sum(max(1, round(maxHP(discordID, side, unit) * effect['percent'] / 100)) for effect in effects)
    who = displayName(discordID, side, unit)
    stacks = f" x{len(effects)}" if len(effects) > 1 else ""
    if effects[0]['heal']:
      healed = healUnit(discordID, side, unit, amount)
      addLog(discordID, f"💚 **{who}** heals {healed} HP from {name}")
    elif isDamageImmune(discordID, side, unit):
      addLog(discordID, f"🛡️ **{who}** is protected from {name}{stacks}")  # SR Noah's Defense Lawyer
    else:
      dealt = dealDamage(discordID, side, unit, amount)
      icon = "🔥" if name == "Burn" else "🩸"
      addLog(discordID, f"{icon} **{who}** takes {dealt} damage from {name}{stacks}")
  if checkBattleOver(discordID):
    return

  tickVoidSpot(discordID)
  if checkBattleOver(discordID):
    return

  # count down every timer, effects made during the enemy turn ("fresh") start counting from now on
  expired = []
  for effect in list(battleEffects[discordID]):
    if effect.get('turns') is None:
      continue
    if effect.get('fresh'):
      effect['fresh'] = False
      continue
    effect['turns'] -= 1
    if effect['turns'] <= 0:
      removeEffect(discordID, effect)
      expired.append(effect)
  for effect in expired:
    # Option K: when Sleep wears off the wake up buff kicks in
    wake = effect.get('onExpire')
    if wake and isAlive(discordID, effect['side'], effect['unit']):
      applyStatChange(discordID, effect['side'], effect['unit'], wake['name'], wake['stats'], wake['turns'], 'buff')
      addLog(discordID, f"☀️ **{displayName(discordID, effect['side'], effect['unit'])}** woke up: {formatStats(wake['stats'])}{turnsText(wake['turns'])}")
  clampAllHP(discordID)

def tickVoidSpot(discordID):
  # SSR Trey's Reality Sink (Option M): +100% power every turn, after 3 turns it bursts on every enemy
  info = battleInfo[discordID]
  spot = info['voidSpot']
  if not spot:
    return
  spot['power'] += spot['growPerTurn']
  spot['turns'] -= 1
  if spot['turns'] > 0:
    return
  info['voidSpot'] = None
  ownerSide, owner = spot['owner']
  foeSide = otherSide(ownerSide)
  attack = attackStat(discordID, ownerSide, owner) if isAlive(discordID, ownerSide, owner) else battleStats[discordID][ownerSide][owner]['attack']
  blasts = []
  for foe in aliveUnits(discordID, foeSide):
    damage = max(1, round(attack * spot['power'] / 100 * damageTakenMultiplier(discordID, foeSide, foe)))
    blasts.append((foe, dealDamage(discordID, foeSide, foe, damage)))
  hits = ", ".join(f"**{displayName(discordID, foeSide, foe)}** for {damage}" for foe, damage in blasts)
  addLog(discordID, f"🌀 The Void Spot bursts at {spot['power']}% power and hits {hits}!")

def checkBattleOver(discordID):
  # Returns "victory" / "defeat" once one side is out of units, otherwise None
  info = battleInfo[discordID]
  if info['result']:
    return info['result']
  if not aliveUnits(discordID, 'enemies'):
    info['result'] = 'victory'
  elif not aliveUnits(discordID, 'players'):
    info['result'] = 'defeat'
  else:
    return None
  flushLog(discordID)
  addLog(discordID, "🏆 **Victory!**" if info['result'] == 'victory' else "☠️ **Your team was defeated...**")
  print("Battle over for", discordID, "->", info['result'])
  return info['result']


# ============================================================================
# ABILITIES (players and enemies both go through here)
# ============================================================================

def splitOptions(options):
  # ['C', 'D', {"buff": ...}] -> (['C', 'D'], {"buff": ...}), the dict at the end holds the numbers
  if options and isinstance(options[-1], dict):
    return list(options[:-1]), options[-1]
  return list(options), {}

def optionChecks(discordID, side, actor, abilityName, options, chosenTarget=None):
  # would love to move all options to this function somehow in the future -> done, every move for players AND enemies runs here
  # Uses the option letters + numbers from utils.py, writes the move to the battle log
  # Returns True when the user gets another turn straight away (Fast Forward)
  letters, params = splitOptions(options)
  info = battleInfo[discordID]
  move = {"side": side, "actor": actor, "ability": abilityName, "parts": [], "lucky": 'O' in letters}

  # Option I: stacks like "Accelerated" disappear as soon as the user does a different move
  clearStacksOnOtherMove(discordID, side, actor, params)
  # R Jaiden's Commitment: a Committed unit can't miss during this turn, then it runs out (taken off further down)
  committed = [effect for effect in getEffects(discordID, side, actor) if effect.get('sureHits')]

  extraTurn = False
  if 'O' in letters and 'chance' in params and random.randint(1, 100) > params['chance']:
    # Option O: luck based move that didn't work this time
    move['parts'].append(params.get('failText', "but nothing happened..."))
  elif 'O' in letters and params.get('outcomes'):
    # Option O: pick 1 of the outcomes at random and do that instead ("weights" = how likely each one is, otherwise all equal)
    outcomeLetters, outcomeParams = splitOptions(random.choices(params['outcomes'], weights=params.get('weights'))[0])
    if outcomeParams.get('outcomeText'):
      move['parts'].append(outcomeParams['outcomeText'])
    extraTurn = resolveMove(discordID, move, outcomeLetters, outcomeParams, chosenTarget)
  else:
    extraTurn = resolveMove(discordID, move, letters, params, chosenTarget)

  # Option H: cooldown, "once": ultimates only work 1 time per battle
  key = (side, actor, abilityName)
  if 'H' in letters:
    info['cooldowns'][key] = info['round'] + params.get('cooldown', 1) + 1
  if params.get('once'):
    info['usedOnce'].add(key)
  for effect in committed:
    removeEffect(discordID, effect)

  writeMoveLog(discordID, move)
  return extraTurn

def resolveMove(discordID, move, letters, params, chosenTarget):
  # Does what the letters say, in this order: costs, buffs (D), self debuffs (E), statuses (I K L N P), Rewind (J),
  # lingering effects on your side (M) and then everything aimed at the other side (A B E F M P)
  side, actor = move['side'], move['actor']
  parts = move['parts']
  info = battleInfo[discordID]
  turns = params.get('turns', 1)

  # Option Z: skip move (for dev)
  if 'Z' in letters:
    parts.append("but nothing happened (this move isn't finished yet)")
    return False

  # costs / gains for the user
  if params.get('selfDamage'):
    parts.append(f"paid {payHP(discordID, side, actor, params['selfDamage'])} HP")
  if params.get('selfHeal'):
    parts.append(f"healed {healUnit(discordID, side, actor, maxHP(discordID, side, actor) * params['selfHeal'] / 100)} HP")
  if params.get('selfHealHP'):
    parts.append(f"healed {healUnit(discordID, side, actor, params['selfHealHP'])} HP")
  if params.get('missNextAttack'):
    # R Max's Brick Eating: the next attack misses no matter what (hostileMove uses it up)
    addStatus(discordID, side, actor, params['missNextAttack'], addStacks=0, sureMiss=True)
    parts.append("the next attack will miss")
  if params.get('skipEnemyTurn'):
    # R Homestuck's Rules for thee (enemyTurn does the skipping)
    info['skipEnemyTurn'] = True
    parts.append("the enemies lose their next turn")
  if params.get('allyCost'):
    # every other teammate pays a % of their max hp (like the other hp costs, it can't knock anyone out)
    paid = [f"**{displayName(discordID, side, unit)}** lost {payHP(discordID, side, unit, maxHP(discordID, side, unit) * params['allyCost'] / 100)} HP"
            for unit in aliveUnits(discordID, side) if unit != actor]
    if paid:
      parts.append(", ".join(paid))

  # Option D: buffs for your own side (whole team with C, picked teammate with G, otherwise yourself)
  if 'D' in letters:
    targets = friendlyTargets(discordID, side, actor, letters, chosenTarget)
    who = groupName(discordID, side, targets, actor)
    stats = dict(params.get('buff', {}))
    if 'I' in letters and 'buffPerStack' in params:
      # Option I: the buff is multiplied by how many stacks you have (Lock the fuck in + Baller)
      perStack = params['buffPerStack']
      count = stackCount(discordID, side, actor, perStack['name'])
      for code, amount in perStack['stats'].items():
        stats[code] = stats.get(code, 0) + amount * count
      if count == 0:
        parts.append(f"no {perStack['name']} stacks to use")
    stats = {code: amount for code, amount in stats.items() if amount}
    if stats:
      for target in targets:
        applyStatChange(discordID, side, target, move['ability'], stats, turns, 'buff', params.get('buffName'))
      parts.append(f"{formatStats(stats)}{'' if who == 'self' else ' for ' + who}{turnsText(turns)}")
    if params.get('heal'):
      healed = sum(healUnit(discordID, side, target, maxHP(discordID, side, target) * params['heal'] / 100) for target in targets)
      parts.append(f"healed {healed} HP" if who == 'self' else f"healed {who} for {healed} HP")
    if params.get('debuffImmune'):
      for target in targets:
        cleanse(discordID, side, target)
        addStatus(discordID, side, target, "Stabilized", turns=turns, addStacks=0, debuffImmune=True)
      parts.append(f"{'self' if who == 'self' else who} can't be debuffed{turnsText(turns)}")
    if params.get('damageImmune'):
      # SR Noah's Defense Lawyer: no damage at all while it lasts
      for target in targets:
        addStatus(discordID, side, target, "Lawyered Up", turns=turns, addStacks=0, damageImmune=True)
      parts.append(f"{'self' if who == 'self' else who} can't take damage{turnsText(turns)}")
    if params.get('sureHitsNextTurn'):
      # R Jaiden's Commitment: every attack they make on their next turn hits (optionChecks takes it off after that turn)
      for target in targets:
        addStatus(discordID, side, target, params['sureHitsNextTurn'], addStacks=0, sureHits=True)
      parts.append(f"{'self' if who == 'self' else who} can't miss next turn")

  # Option E with no enemy target letter: the debuff lands on yourself (Sleep) or a random teammate (Option O, Plunder)
  hostile = 'A' in letters or 'B' in letters or 'F' in letters
  if 'E' in letters and not hostile:
    if 'O' in letters and params.get('randomAlly'):
      teammates = [unit for unit in aliveUnits(discordID, side) if unit != actor]
      victims = [random.choice(teammates)] if teammates else []
    else:
      victims = [actor]
    stats = {code: -amount for code, amount in params.get('debuff', {}).items()}
    landed = [victim for victim in victims if applyStatChange(discordID, side, victim, move['ability'], stats, turns, 'debuff', params.get('debuffName'))]
    if landed:
      who = groupName(discordID, side, landed, actor)
      parts.append(f"{formatStats(stats)}{'' if who == 'self' else ' on ' + who}{turnsText(turns)}")

  # Option K: Sleep, skip your next turn then wake up with a buff (wake up happens in endRound)
  if 'K' in letters:
    wake = {"name": move['ability'], "stats": params.get('wakeBuff', {}), "turns": params.get('wakeTurns', 1)}
    addStatus(discordID, side, actor, "Asleep", turns=params.get('sleepTurns', 1) + 1, addStacks=0, skipTurn=True, onExpire=wake)
    parts.append(f"fell asleep 💤 (skips next turn, then wakes up with {formatStats(wake['stats'])})")

  # Option L: Taunt, enemies' single target attacks have to go at you
  if 'L' in letters:
    tauntTurns = params.get('taunt', 1)
    addStatus(discordID, side, actor, "Taunt", turns=tauntTurns, addStacks=0, taunt=True)
    parts.append(f"is drawing all attacks{turnsText(tauntTurns)}")

  # Option I: gain stacks (Accelerated, Baller, Considering)
  if 'I' in letters and 'stacks' in params:
    stack = params['stacks']
    status = addStatus(discordID, side, actor, stack['name'], turns=stack.get('turns'), addStacks=stack.get('add', 1),
                       maxStacks=stack.get('max'), stackLabel=True, perStack=stack.get('perStack'),
                       resetOnOtherMove=stack.get('resetOnOtherMove'), loseStackWhenHit=stack.get('loseStackWhenHit'))
    parts.append(f"{stack['name']} x{status['stacks']}")

  # Option N: Interrupt status (Interfere / Nervous)
  if 'N' in letters and 'interrupt' in params:
    guard = params['interrupt']
    chance = guard.get('chance', 50)
    addStatus(discordID, side, actor, guard['name'], turns=guard.get('turns'), addStacks=0, interruptChance=chance,
              guardsAllies=guard.get('guardsAllies'), counter=guard.get('counter'))
    protects = "the team" if guard.get('guardsAllies') else "self"
    parts.append(f"{guard['name']} is up ({chance}% to stop the next attack on {protects})")

  # Option P: Martyrdom, every hit taken gives the attacker a Doom Mark and they explode if you get knocked out
  if 'P' in letters and params.get('doom') == 'martyrdom':
    perMark = round(battleStats[discordID][side][actor]['attack'] * params.get('explodePower', 150) / 100)
    addStatus(discordID, side, actor, "Martyrdom", turns=turns, addStacks=0, doomOnHit=True, explodePerMark=perMark)
    parts.append("every hit taken gives the attacker a Doom Mark")

  # Option J: Rewind
  if 'J' in letters:
    parts.append(rewindTeam(discordID, side, actor))

  # Option M on your own side (Regeneration) or on the field (Void Spot)
  lingering = params.get('lingering') if 'M' in letters else None
  if lingering and lingering['name'] == "Void Spot":
    info['voidSpot'] = {"owner": (side, actor), "turns": lingering.get('turns', 3), "power": 0,
                        "growPerTurn": lingering.get('growPerTurn', 100), "growPerRanged": lingering.get('growPerRanged', 50)}
    parts.append(f"a Void Spot opened 🌀 (ranged attacks miss, it bursts in {lingering.get('turns', 3)} turns)")
  elif lingering and lingering.get('heal'):
    targets = friendlyTargets(discordID, side, actor, letters, chosenTarget)
    for target in targets:
      addLingering(discordID, side, target, lingering)
    parts.append(f"{lingering['name']} for {groupName(discordID, side, targets, actor)}{turnsText(lingering.get('turns', 1))}")

  # everything aimed at the other side
  if hostile:
    hostileMove(discordID, move, letters, params, chosenTarget)

  return bool(params.get('extraTurn'))

def hostileMove(discordID, move, letters, params, chosenTarget):
  # Options A (damage), E (debuffs), M (Burn / Bleed) and P (Doom Marks) on 1 enemy (F) or all of them (B)
  side, actor = move['side'], move['actor']
  foeSide = otherSide(side)
  parts = move['parts']
  info = battleInfo[discordID]
  turns = params.get('turns', 1)

  # SR Freeman's Nervous (Option N) can stop the whole attack before it happens
  if 'A' in letters and tryNervousInterrupt(discordID, move):
    return

  targets = hostileTargets(discordID, side, actor, letters, chosenTarget)
  if not targets:
    parts.append("but there was nobody to hit")
    return

  # R Max's Brick Eating: the first attack after it misses no matter what
  full = next((effect for effect in getEffects(discordID, side, actor) if effect.get('sureMiss')), None) if 'A' in letters else None
  if full:
    removeEffect(discordID, full)
    parts.append(f"missed {groupName(discordID, foeSide, targets)} ({full['name']} 🧱)")
    return

  # Option I: HIYAAAHHH! turns its stacks into extra damage (this is the "extra parameter" for Option A)
  bonus, flatBonus = 0, 0
  if 'I' in letters and 'consumeStacks' in params:
    consume = params['consumeStacks']
    count = stackCount(discordID, side, actor, consume['name'])
    removeStatus(discordID, side, actor, consume['name'])
    if 'flatPerStack' in consume:
      flatBonus = count * consume['flatPerStack']  # flat damage for each stack
      gained = f"+{flatBonus:g} damage"
    else:
      bonus = count * consume.get('bonusPerStack', 10)  # % damage for each stack
      gained = f"+{bonus:g}% damage"
    parts.append(f"cashed in {count} {consume['name']} for {gained}" if count else f"no {consume['name']} stacks to cash in")

  rollsToHit = 'A' in letters or 'accuracy' in params
  lingering = params.get('lingering') if 'M' in letters else None
  if lingering and (lingering.get('heal') or lingering['name'] == "Void Spot"):
    lingering = None  # those were already handled on your own side
  baseDebuff = {code: -amount for code, amount in params.get('debuff', {}).items()}
  debuffed, lingered, lostWill = [], [], []
  totalDealt = 0

  for target in targets:
    if not isAlive(discordID, side, actor):
      break  # the attacker went down mid move (Doom Marks exploding, counter attacks)
    if not isAlive(discordID, foeSide, target):
      continue
    targetName = f"**{displayName(discordID, foeSide, target)}**"

    # SSR Trey's Void Spot swallows every ranged attack and grows stronger
    if params.get('ranged') and info['voidSpot']:
      info['voidSpot']['power'] += info['voidSpot']['growPerRanged']
      parts.append(f"the Void Spot swallowed the attack on {targetName} (+{info['voidSpot']['growPerRanged']}% power)")
      continue

    if rollsToHit:
      attackCheck = accEvaCheck(discordID, side, actor, target, params)
      if attackCheck == 1:
        parts.append(f"missed {targetName}")
        continue
      if attackCheck == 2:
        parts.append(f"{targetName} evaded")
        continue

    if 'A' in letters:
      # SR Noah's Defense Lawyer: a target that can't take damage ignores the whole hit
      if isDamageImmune(discordID, foeSide, target):
        parts.append(f"{targetName} is protected and takes no damage")
        continue
      # R Noah's Interfere (Option N) can cancel a hit aimed at them
      if tryInterfere(discordID, foeSide, target, parts):
        continue
      # SSR Scottie's Martyrdom (Option P): hitting a martyr gives the attacker a Doom Mark
      # (added before the damage so it still counts if this hit knocks Scottie out)
      markedAttacker = False
      if any(effect.get('doomOnHit') for effect in getEffects(discordID, foeSide, target)):
        addStatus(discordID, side, actor, "Doom Mark", addStacks=1, stackLabel=True)
        markedAttacker = True
      damage, note = computeDamage(discordID, side, actor, foeSide, target, params, bonus, flatBonus)
      damage, crit = item_helper.criticalHit(discordID, side, damage)  # crit_chance items (Lucky Coin)
      totalDealt += dealDamage(discordID, foeSide, target, damage)
      parts.append(f"{note}hit {targetName} for {damage}{crit}")
      if markedAttacker:
        parts.append(f"**{displayName(discordID, side, actor)}** got a Doom Mark")
      afterHit(discordID, foeSide, target, letters, params, parts)
      itemText = item_helper.hitLanded(discordID, side, actor, move['ability'], foeSide, target)  # on-hit items (Knife Noir)
      if itemText:
        parts.append(itemText)

    if not isAlive(discordID, foeSide, target):
      continue

    if 'E' in letters:
      stats = dict(baseDebuff)
      if 'P' in letters and params.get('doom') == 'dread':
        # Existential Dread is stronger for every Doom Mark the enemy has, then the marks get used up
        marks = stackCount(discordID, foeSide, target, "Doom Mark")
        for code, amount in params.get('perMark', {}).items():
          stats[code] = stats.get(code, 0) - amount * marks
        removeStatus(discordID, foeSide, target, "Doom Mark")
        if applyStatChange(discordID, foeSide, target, move['ability'], stats, turns, 'debuff', params.get('debuffName')):
          parts.append(f"{formatStats(stats)} on {targetName}{turnsText(turns)}")
        else:
          parts.append(f"{targetName} can't be debuffed")
      elif applyStatChange(discordID, foeSide, target, move['ability'], stats, turns, 'debuff', params.get('debuffName')):
        debuffed.append(target)
      else:
        parts.append(f"{targetName} can't be debuffed")

    if lingering:
      if isDebuffImmune(discordID, foeSide, target):
        parts.append(f"{targetName} is immune to {lingering['name']}")
      else:
        addLingering(discordID, foeSide, target, lingering)
        lingered.append(target)

    if 'P' in letters and params.get('doom') == 'nihilism':
      addStatus(discordID, foeSide, target, "Nihilism", turns=turns, addStacks=0)
      lostWill.append(target)

  if debuffed:
    label = f"{params['debuffName']} " if params.get('debuffName') else ""
    parts.append(f"{label}{formatStats(baseDebuff)} on {groupName(discordID, foeSide, debuffed)}{turnsText(turns)}")
  if lingered:
    parts.append(f"{lingering['name']} on {groupName(discordID, foeSide, lingered)}{turnsText(lingering.get('turns', 1))}")
  if lostWill:
    parts.append(f"{groupName(discordID, foeSide, lostWill)} lost all will to fight{turnsText(turns)}")

  # SMASH!: the damage dealt comes out of the user's hp too
  if params.get('recoil') and totalDealt:
    parts.append(f"took {payHP(discordID, side, actor, totalDealt * params['recoil'] / 100)} recoil damage")

def afterHit(discordID, targetSide, target, letters, params, parts):
  # Things that happen once a hit lands
  if not isAlive(discordID, targetSide, target):
    return
  targetName = f"**{displayName(discordID, targetSide, target)}**"
  # R Stephen's Baller stacks (Option I) go down by 1 every time he gets hit
  for effect in getEffects(discordID, targetSide, target):
    if effect.get('loseStackWhenHit'):
      effect['stacks'] -= 1
      if effect['stacks'] <= 0:
        removeEffect(discordID, effect)
        parts.append(f"{targetName} lost their last {effect['name']} stack")
      else:
        parts.append(f"{targetName} lost a {effect['name']} stack")
  # SSR Scottie's Fated Strike (Option P): every 2nd hit on the same enemy gives it a Doom Mark
  if 'P' in letters and params.get('doom') == 'fatedStrike':
    fated = addStatus(discordID, targetSide, target, "Fated", addStacks=1, stackLabel=True)
    if fated['stacks'] >= 2:
      removeEffect(discordID, fated)
      mark = addStatus(discordID, targetSide, target, "Doom Mark", addStacks=1, stackLabel=True)
      parts.append(f"Doom Mark on {targetName} (x{mark['stacks']})")

def accEvaCheck(discordID, side, attacker, target, params=None):
  # returns 1 of 3 things, 0 = Hit, 1 = Miss, 2 = Evade
  params = params or {}
  targetSide = otherSide(side)
  # "sureHit" moves, Motionless targets (Nihilism) and Committed attackers (R Jaiden's Commitment) always hit
  if (params.get('sureHit') or any(effect.get('sureHitAgainst') for effect in getEffects(discordID, targetSide, target))
      or any(effect.get('sureHits') for effect in getEffects(discordID, side, attacker))):
    return 0
  # accuracy check ("accuracy" in the move replaces the user's accuracy, like Cheesy Fries 70%)
  accuracy = params.get('accuracy', battleStats[discordID][side][attacker]['accuracy']) + statModifier(discordID, side, attacker, 'DD')
  if random.randint(1, 100) > accuracy:
    return 1
  # evasion check
  if random.randint(1, 100) <= evasionStat(discordID, targetSide, target):
    return 2
  return 0

def computeDamage(discordID, attackerSide, attacker, targetSide, target, params, bonus=0, flatBonus=0):
  # Option A: attack stat (or flat / % hp / dice) -> attack buffs (BB) + bonus % -> + flatBonus -> target's defense buffs (CC)
  # Returns (damage, text for the log like "rolled a 4 ")
  note = ""
  scales = True  # % hp damage doesn't get stronger with attack buffs
  if 'percentMaxHP' in params:
    base = maxHP(discordID, targetSide, target) * params['percentMaxHP'] / 100
    scales = False
  elif 'percentCurrentHP' in params:
    base = battleStats[discordID][targetSide][target]['ehp'] * params['percentCurrentHP'] / 100
    scales = False
  elif 'dice' in params:
    sides, perPip = params['dice']
    pips = random.randint(1, sides)
    base = pips * perPip
    note = f"rolled a {pips} and "
  elif 'damage' in params:
    base = params['damage']
  else:
    base = battleStats[discordID][attackerSide][attacker]['attack'] * params.get('power', 100) / 100
  if scales:
    base *= max(0, 1 + (statModifier(discordID, attackerSide, attacker, 'BB') + bonus) / 100)
  base += flatBonus  # flat extra damage (HIYAAAHHH! stacks), attack buffs don't change it but the target's defense does
  if not params.get('trueDamage'):
    base *= damageTakenMultiplier(discordID, targetSide, target)
  return max(1, round(base)), note

def hostileTargets(discordID, side, actor, letters, chosenTarget):
  # B = every enemy, otherwise the picked target (F), or one gets picked for you
  foeSide = otherSide(side)
  foes = aliveUnits(discordID, foeSide)
  if not foes:
    return []
  if 'B' in letters:
    return foes
  if chosenTarget in foes:
    return [chosenTarget]
  if side == 'enemies':
    # enemy AI: taunts (Option L) pull attacks first, then Jack Noir's passive (Option Q), otherwise random
    taunting = [unit for unit in foes if isTaunting(discordID, foeSide, unit)]
    if taunting:
      return [random.choice(taunting)]
    if 'Q' in letters:
      return [min(foes, key=lambda unit: battleStats[discordID][foeSide][unit]['ehp'])]
  return [random.choice(foes)]

def friendlyTargets(discordID, side, actor, letters, chosenTarget):
  # C = whole team, G = picked teammate, otherwise yourself
  allies = aliveUnits(discordID, side)
  if 'C' in letters:
    return allies
  if 'G' in letters:
    if chosenTarget in allies:
      return [chosenTarget]
    if side == 'enemies' and allies:
      return [random.choice(allies)]
  return [actor] if isAlive(discordID, side, actor) else []

def tryNervousInterrupt(discordID, move):
  # SR Freeman's Nervous (Option N): any attack on the team can get interrupted, then Freeman fires his counter (Shoot) back
  side, actor = move['side'], move['actor']
  foeSide = otherSide(side)
  for guardian in aliveUnits(discordID, foeSide):
    for status in getEffects(discordID, foeSide, guardian):
      if not status.get('guardsAllies') or random.randint(1, 100) > status.get('interruptChance', 0):
        continue
      removeEffect(discordID, status)
      move['parts'].append(f"but **{displayName(discordID, foeSide, guardian)}**'s {status['name']} interrupted it! 😰")
      writeMoveLog(discordID, move)
      counter = status.get('counter')
      guardianAbilities = allAbilities[discordID][foeSide][guardian]
      if counter in guardianAbilities and isAlive(discordID, side, actor):
        optionChecks(discordID, foeSide, guardian, counter, guardianAbilities[counter], actor)
      return True
  return False

def tryInterfere(discordID, side, unit, parts):
  # R Noah's Interfere (Option N): chance to cancel a hit aimed at the unit, used up once it works
  for status in getEffects(discordID, side, unit):
    if 'interruptChance' in status and not status.get('guardsAllies'):
      if random.randint(1, 100) <= status['interruptChance']:
        removeEffect(discordID, status)
        parts.append(f"**{displayName(discordID, side, unit)}**'s {status['name']} cancelled the hit!")
        return True
  return False

def clearStacksOnOtherMove(discordID, side, actor, params):
  # Option I: stacks like "Accelerated" are lost as soon as the unit uses a different move
  keep = params.get('stacks', {}).get('name')
  for effect in getEffects(discordID, side, actor):
    if effect.get('resetOnOtherMove') and effect['name'] != keep:
      removeEffect(discordID, effect)

def takeSnapshot(discordID):
  # saved at the start of every round for Rewind
  info = battleInfo[discordID]
  snapshot = {
    "hp": {side: {unit: stats['ehp'] for unit, stats in battleStats[discordID][side].items()} for side in ('players', 'enemies')},
    "effects": copy.deepcopy(battleEffects[discordID]),
  }
  info['snapshots'] = (info['snapshots'] + [snapshot])[-2:]

def rewindTeam(discordID, side, actor):
  # Option J (SSR Abraize Rewind): the team's hp, buffs and debuffs go back to the start of the previous turn
  # (knocked out teammates come back if they were still standing back then)
  snapshots = battleInfo[discordID]['snapshots']
  if not snapshots:
    return "but there was nothing to rewind"
  snapshot = snapshots[0]
  for unit, hp in snapshot['hp'][side].items():
    battleStats[discordID][side][unit]['ehp'] = hp
  oldEffects = [copy.deepcopy(effect) for effect in snapshot['effects'] if effect['side'] == side]
  battleEffects[discordID] = [effect for effect in battleEffects[discordID] if effect['side'] != side] + oldEffects
  clearStacksOnOtherMove(discordID, side, actor, {})
  clampAllHP(discordID)
  if len(snapshots) == 1:
    return "rewound the team to the start of the battle ⏪"
  return "rewound the team to the start of last turn ⏪"


# ============================================================================
# BUFFS / DEBUFFS / STATUSES (everything inside battleEffects)
# ============================================================================

def durationFor(discordID, turns):
  # A turn is a full round. Effects made during the enemy turn start counting next round, otherwise
  # an enemy's "for one turn" would run out before the players ever saw it. 0 = only the rest of this round
  if turns is None:
    return None, False
  if turns <= 0:
    return 1, False
  return turns, battleInfo[discordID]['phase'] == 'enemies'

def getEffects(discordID, side, unit):
  return [effect for effect in battleEffects[discordID] if effect['side'] == side and effect['unit'] == unit]

def findEffect(discordID, side, unit, name, kind=None):
  for effect in battleEffects[discordID]:
    if effect['side'] == side and effect['unit'] == unit and effect['name'] == name and (kind is None or effect['kind'] == kind):
      return effect
  return None

def removeEffect(discordID, effect):
  battleEffects[discordID] = [other for other in battleEffects[discordID] if other is not effect]

def removeStatus(discordID, side, unit, name):
  for effect in getEffects(discordID, side, unit):
    if effect['kind'] == 'status' and effect['name'] == name:
      removeEffect(discordID, effect)

def addStatus(discordID, side, unit, name, turns=None, addStacks=1, maxStacks=None, **props):
  # Named statuses ("Accelerated", "Baller", "Doom Mark", "Asleep", "Taunt"...)
  # Adding one that is already there puts the stacks on top and refreshes how long it lasts
  status = findEffect(discordID, side, unit, name, 'status')
  if status is None:
    status = {"side": side, "unit": unit, "name": name, "kind": "status", "stacks": 0, "turns": None, "fresh": False}
    battleEffects[discordID].append(status)
  status['stacks'] += addStacks
  if maxStacks:
    status['stacks'] = min(status['stacks'], maxStacks)
  if turns is not None:
    status['turns'], status['fresh'] = durationFor(discordID, turns)
  for key, value in props.items():
    if value is not None:
      status[key] = value
  return status

def applyStatChange(discordID, side, unit, source, stats, turns, kind, label=None):
  # Options D / E with the AA-EE stats. Using the same move on the same unit again refreshes it instead of stacking forever
  # Returns False when a debuff got blocked (Universal Stabilizer)
  if kind == 'debuff' and isDebuffImmune(discordID, side, unit):
    return False
  for effect in getEffects(discordID, side, unit):
    if effect['kind'] == kind and effect['name'] == source:
      removeEffect(discordID, effect)
  duration, fresh = durationFor(discordID, turns)
  battleEffects[discordID].append({"side": side, "unit": unit, "name": source, "kind": kind, "stats": dict(stats),
                                   "turns": duration, "fresh": fresh, "label": label})
  clampHP(discordID, side, unit)
  return True

def addLingering(discordID, side, unit, lingering):
  # Option M: Burn / Bleed / Regeneration. Stackable ones get another copy with its own timer, others refresh
  if not lingering.get('stackable'):
    for effect in getEffects(discordID, side, unit):
      if effect['kind'] == 'dot' and effect['name'] == lingering['name']:
        removeEffect(discordID, effect)
  duration, fresh = durationFor(discordID, lingering.get('turns', 1))
  battleEffects[discordID].append({"side": side, "unit": unit, "name": lingering['name'], "kind": "dot",
                                   "percent": lingering.get('percent', 5), "heal": bool(lingering.get('heal')),
                                   "turns": duration, "fresh": fresh})

def cleanse(discordID, side, unit):
  # removes debuffs and Burn / Bleed (Universal Stabilizer)
  for effect in getEffects(discordID, side, unit):
    if effect['kind'] == 'debuff' or (effect['kind'] == 'dot' and not effect['heal']):
      removeEffect(discordID, effect)

def stackCount(discordID, side, unit, name):
  status = findEffect(discordID, side, unit, name, 'status')
  return status['stacks'] if status else 0

def totalStacks(discordID, side, name):
  return sum(stackCount(discordID, side, unit, name) for unit in aliveUnits(discordID, side))

def isTaunting(discordID, side, unit):
  return any(effect.get('taunt') for effect in getEffects(discordID, side, unit))

def skipsTurn(discordID, side, unit):
  return any(effect.get('skipTurn') for effect in getEffects(discordID, side, unit))

def isDebuffImmune(discordID, side, unit):
  return any(effect.get('debuffImmune') for effect in getEffects(discordID, side, unit))

def isDamageImmune(discordID, side, unit):
  return any(effect.get('damageImmune') for effect in getEffects(discordID, side, unit))


# ============================================================================
# STATS / HP
# ============================================================================

def statModifier(discordID, side, unit, code):
  # total % change to 1 stat (AA-EE) from every buff, debuff and stack on the unit
  total = 0
  for effect in getEffects(discordID, side, unit):
    total += effect.get('stats', {}).get(code, 0)
    total += effect.get('perStack', {}).get(code, 0) * effect.get('stacks', 0)
  return total

def maxHP(discordID, side, unit):
  # AA buffs / debuffs change max hp by a %
  base = battleStats[discordID][side][unit]['maxEhp']
  return max(1, int(base * (1 + statModifier(discordID, side, unit, 'AA') / 100)))

def attackStat(discordID, side, unit):
  return battleStats[discordID][side][unit]['attack'] * max(0, 1 + statModifier(discordID, side, unit, 'BB') / 100)

def evasionStat(discordID, side, unit):
  return battleStats[discordID][side][unit]['evasion'] + statModifier(discordID, side, unit, 'EE')

def damageTakenMultiplier(discordID, side, unit):
  # CC +30 = take 30% less damage, CC -25 = take 25% more
  # an equipped item's defense bonus counts the same way
  defense = statModifier(discordID, side, unit, 'CC') + battleStats[discordID][side][unit].get('itemDefense', 0)
  return max(0, 1 - defense / 100)

def isAlive(discordID, side, unit):
  return battleStats[discordID][side][unit]['ehp'] > 0

def aliveUnits(discordID, side):
  return [unit for unit, stats in battleStats[discordID][side].items() if stats['ehp'] > 0]

def otherSide(side):
  return 'enemies' if side == 'players' else 'players'

def dealDamage(discordID, side, unit, amount):
  # takes hp away and returns the damage done, 0 hp = defeated
  stats = battleStats[discordID][side][unit]
  if stats['ehp'] <= 0 or isDamageImmune(discordID, side, unit):
    return 0
  amount = max(0, int(round(amount)))
  stats['ehp'] = max(0, stats['ehp'] - amount)
  if stats['ehp'] == 0:
    handleDefeat(discordID, side, unit)
  return amount

def payHP(discordID, side, unit, amount):
  # hp the user pays for their own move (Eat Note, SMASH! recoil, Indecision), this never knocks them out
  stats = battleStats[discordID][side][unit]
  lost = max(0, min(int(round(amount)), stats['ehp'] - 1))
  stats['ehp'] -= lost
  return lost

def healUnit(discordID, side, unit, amount):
  # heals up to max hp (knocked out units can't be healed), returns how much was healed
  stats = battleStats[discordID][side][unit]
  if stats['ehp'] <= 0:
    return 0
  before = stats['ehp']
  stats['ehp'] = min(maxHP(discordID, side, unit), stats['ehp'] + max(0, int(round(amount))))
  return max(0, stats['ehp'] - before)

def handleDefeat(discordID, side, unit):
  queueLog(discordID, f"💀 **{displayName(discordID, side, unit)}** was defeated!")
  martyr = next((effect for effect in getEffects(discordID, side, unit) if effect.get('explodePerMark')), None)
  # everything on a defeated unit goes away
  battleEffects[discordID] = [effect for effect in battleEffects[discordID] if not (effect['side'] == side and effect['unit'] == unit)]
  # SSR Scottie's Martyrdom (Option P): getting knocked out while it is up makes every Doom Mark explode
  if martyr:
    explodeDoomMarks(discordID, side, unit, martyr['explodePerMark'])

def explodeDoomMarks(discordID, side, unit, perMark):
  foeSide = otherSide(side)
  blasts = []
  for foe in aliveUnits(discordID, foeSide):
    marks = stackCount(discordID, foeSide, foe, "Doom Mark")
    if marks:
      removeStatus(discordID, foeSide, foe, "Doom Mark")
      blasts.append((foe, marks * perMark))
  if not blasts:
    return
  hits = ", ".join(f"**{displayName(discordID, foeSide, foe)}** for {damage}" for foe, damage in blasts)
  queueLog(discordID, f"💥 **{displayName(discordID, side, unit)}**'s Doom Marks explode and hit {hits}!")
  for foe, damage in blasts:
    dealDamage(discordID, foeSide, foe, damage)

def clampHP(discordID, side, unit):
  stats = battleStats[discordID][side][unit]
  stats['ehp'] = min(stats['ehp'], maxHP(discordID, side, unit))

def clampAllHP(discordID):
  for side in ('players', 'enemies'):
    for unit in battleStats[discordID][side]:
      clampHP(discordID, side, unit)


# ============================================================================
# INFO FOR MAIN.PY (embed + buttons)
# ============================================================================

def battleExists(discordID):
  return discordID in battleInfo

def getBattleResult(discordID):
  # None while the battle is still going, otherwise "victory" / "defeat"
  return battleInfo[discordID]['result'] if battleExists(discordID) else None

def abilityStatus(discordID, side, unit, abilityName):
  # (can it be used right now?, short reason shown on the button like "2t" or "used")
  info = battleInfo[discordID]
  key = (side, unit, abilityName)
  if key in info['usedOnce']:
    return False, "used"
  readyRound = info['cooldowns'].get(key, 0)
  if readyRound > info['round']:
    return False, f"{readyRound - info['round']}t"
  letters, params = splitOptions(allAbilities[discordID][side][unit][abilityName])
  if 'P' in letters and params.get('doom') == 'nihilism':
    if info['round'] < params.get('requiresRound', 0):
      return False, f"turn {params['requiresRound']}+"
    marks = totalStacks(discordID, otherSide(side), "Doom Mark")
    if marks < params.get('requiresMarks', 0):
      return False, f"{marks}/{params['requiresMarks']} marks"
  return True, ""

def getAbilityButtons(discordID):
  # The current character's abilities in button order: [{"name", "ready", "note"}]
  actor = whosTurn[discordID]
  buttons = []
  for abilityName in allAbilities[discordID]['players'][actor]:
    ready, note = abilityStatus(discordID, 'players', actor, abilityName)
    buttons.append({"name": abilityName, "ready": ready, "note": note})
  return buttons

def getTargetChoices(discordID, abilityIndex):
  # Options F / G: when the move needs a picked target and there is more than 1 choice,
  # returns [(unit, display name)] so main.py can show target buttons, otherwise None
  actor = whosTurn[discordID]
  abilities = allAbilities[discordID]['players'][actor]
  abilityNames = list(abilities.keys())
  if not 0 <= abilityIndex < len(abilityNames):
    return None
  letters, params = splitOptions(abilities[abilityNames[abilityIndex]])
  if 'O' in letters and params.get('outcomes') and 'F' not in letters:
    return None  # random outcome, nothing to pick (an F next to the outcomes means the enemy gets picked first, like Pick Up)
  if ('F' in letters or 'A' in letters) and 'B' not in letters:
    side = 'enemies'
  elif 'G' in letters and 'C' not in letters:
    side = 'players'
  else:
    return None
  choices = [(unit, displayName(discordID, side, unit)) for unit in aliveUnits(discordID, side)]
  return choices if len(choices) > 1 else None

def getBattleSummary(discordID):
  # Everything main.py needs to draw the battle embed
  info = battleInfo[discordID]

  def unitRows(side):
    rows = []
    for unit, stats in battleStats[discordID][side].items():
      rows.append({
        "name": displayName(discordID, side, unit),
        "hp": stats['ehp'],
        "maxHp": maxHP(discordID, side, unit),
        "alive": stats['ehp'] > 0,
        "effects": describeEffects(discordID, side, unit),
        "current": side == 'players' and unit == whosTurn.get(discordID) and not info['result'],
      })
    return rows

  spot = info['voidSpot']
  return {
    "round": info['round'],
    "turn": displayName(discordID, 'players', whosTurn[discordID]),
    "result": info['result'],
    "players": unitRows('players'),
    "enemies": unitRows('enemies'),
    "field": f"🌀 Void Spot: {spot['power']}% power, bursts in {spot['turns']}t" if spot else None,
    "log": list(battleLog[discordID]),
  }

def describeEffects(discordID, side, unit):
  # Short text of everything on a unit, like "ATK+10% DEF+10% (3t), Taunt (1t), Bleed x2 (1t)"
  parts = []
  lingering = {}
  for effect in getEffects(discordID, side, unit):
    turns = f" ({effect['turns']}t)" if effect.get('turns') else ""
    if effect['kind'] in ('buff', 'debuff'):
      label = f"{effect['label']} " if effect.get('label') else ""
      parts.append(f"{label}{formatStats(effect['stats'])}{turns}")
    elif effect['kind'] == 'dot':
      count, shownTurns = lingering.get(effect['name'], (0, turns))
      lingering[effect['name']] = (count + 1, shownTurns)
    else:
      stacks = f" x{effect['stacks']}" if effect.get('stackLabel') else ""
      parts.append(f"{effect['name']}{stacks}{turns}")
  for name, (count, turns) in lingering.items():
    parts.append(f"{name}{f' x{count}' if count > 1 else ''}{turns}")
  return ", ".join(parts)

def displayName(discordID, side, unit):
  return battleInfo[discordID]['names'][side].get(unit, unit)


# ============================================================================
# BATTLE LOG (shown in the embed)
# ============================================================================

def addLog(discordID, text):
  # add a line to the battle log, then any lines that were waiting for it (like "X was defeated!")
  if discordID not in battleLog:
    return
  battleLog[discordID].append(text)
  flushLog(discordID)

def queueLog(discordID, text):
  battleInfo[discordID]['pending'].append(text)

def flushLog(discordID):
  pending = battleInfo[discordID]['pending']
  battleLog[discordID].extend(pending)
  pending.clear()
  del battleLog[discordID][:-LOG_LIMIT]

def writeMoveLog(discordID, move):
  # 1 line per move: "🔹 **R Abraize** used **Punch**: hit **Ruffian 1** for 10"
  if move.get('logged'):
    return
  move['logged'] = True
  icon = "🔹" if move['side'] == 'players' else "🔸"
  dice = " 🎲" if move.get('lucky') else ""
  line = f"{icon} **{displayName(discordID, move['side'], move['actor'])}** used **{move['ability']}**{dice}"
  if move['parts']:
    line += ": " + ", ".join(move['parts'])
  addLog(discordID, line)

def formatStats(stats):
  # {"BB": 10, "DD": -15} -> "ATK+10% ACC-15%"
  return " ".join(f"{statNames.get(code, code)}{amount:+g}%" for code, amount in stats.items() if amount)

def turnsText(turns):
  return " (this turn)" if turns == 0 else f" ({turns}t)"

def groupName(discordID, side, units, actor=None):
  # "self" / "the team" / "all enemies" / list of names, for the log
  if not units:
    return "nobody"
  if units == [actor]:
    return "self"
  everyone = aliveUnits(discordID, side)
  if len(units) > 1 and set(units) == set(everyone):
    return "the team" if side == 'players' else "all enemies"
  return ", ".join(f"**{displayName(discordID, side, unit)}**" for unit in units)


# ============================================================================
# BATTLE SETUP
# ============================================================================

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
  #        "r_abraize": {"Punch": ['A', 'F'], "Sleep": [...], "Missing Assignments": [...]},
  #        ...
  #    },
  #    "enemies": {
  #        "Ruffian1": {"Punch": ['A', 'F']},
  #        ...
  #    }
  #  }

def getStats(discordID, team, enemies):
  allStats = {
    "players": {},
    "enemies": {}
  }

  for player in team:
    ehp = characterAttributes[player.lower()][0] + int(characterAttributes[player.lower()][2] * (1.0 if player in rChar else 1.5 if player in srChar else 2.0))
    allStats['players'][player] = {
      "ehp": ehp,
      "maxEhp": ehp,
      "attack": characterAttributes[player.lower()][1],
      "evasion": characterAttributes[player.lower()][3],
      "accuracy": characterAttributes[player.lower()][4],
    }

  for enemy in enemies:
    ehp = enemyAttributes[enemy][0] + int(enemyAttributes[enemy][2] * 1.2)
    allStats['enemies'][enemy] = {
      "ehp": ehp,
      "maxEhp": ehp,
      "attack": enemyAttributes[enemy][1],
      "evasion": enemyAttributes[enemy][4],
      "accuracy": enemyAttributes[enemy][5],
      "moves": enemyAttributes[enemy][3]
    }

  return allStats

def getDisplayNames(team, enemies):
  # short names for the embed: "r_abraize" -> "R Abraize", "Ruffian1" -> "Ruffian 1" (or just "Ruffian" when it is alone)
  names = {"players": {}, "enemies": {}}
  for member in team:
    rarity, _, base = member.partition('_')
    names['players'][member] = f"{rarity.upper()} {base.capitalize()}" if base else member
  for enemy in enemies:
    base = enemy.rstrip("0123456789")
    sameKind = [other for other in enemies if other.rstrip("0123456789") == base]
    if base != enemy and len(sameKind) > 1:
      names['enemies'][enemy] = f"{base} {enemy[len(base):]}"
    else:
      names['enemies'][enemy] = base or enemy
  return names

def calculateTurnOrder(discordID, team, enemies):
  print("Calculating turn order for battle of user", discordID)
  # from team array/dictionary in that order then it should be enemies in that order (mostly doesnt matter as
  # there is only one enemy and the only double battle is a ruffian so priority between them doesnt matter)
  switch = ["0"]                    # used to indicate that it is the enemies turn (to remove buttons)
  order = team + switch + enemies
  return order
