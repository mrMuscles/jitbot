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
    "rTrey": [250, 12, 8, "3%", "90%", "Punch", "Irish Goodbye", "Cheesy Fries"],
    "rNoah": [180, 10, 8, "3%", "90%", "Punch", "Fiddle", "Bo"],
    "rFreeman": [180, 8, 8, "10%", "90%", "Slap", "Ponder", "SMASH!"]
}
# HP, Attack, Defense are all Flat Numbers
# Evasion and Accuracy are percentages

'''
  "Name of Character" = {
    "Name of Ability": ['A', 'C'],
    "Ability 2": ['B', 'C'],
    "Ability 3": ['A']
  }
  "Character 2" = {
    "Ability 1": ['D', 'C'],
    "Ability 2": ['A', 'B', 'E'],
    "Ability 3": ['C']
   }

  '''
# Option A = Damage using Attack Stat
# Option B = Damage based off number such as B20 = 20 Damage, if no number then error out
# Option B = Area of Effect for Enemies
# Option C = Area of Effect for Teammates
# Option D = Buff (However if Option B then it should AOE Buff Enemies and if Option C then AOE Buff Teammates)
# Option E = Debuff (However if Option B then it should AOE Debuff Enemies and if Option C then AOE Debuff Teammates)
# Options D and E are Basic buffs meaning they only change the 5 main stats of HP, Attack, Defense, Evasion, and Accuracy