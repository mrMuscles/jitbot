# =====================================================================================
#  DAILY REWARDS (/daily)
# =====================================================================================
#
#  Players can claim /daily once every DAILY_COOLDOWN_HOURS (24 hours).
#  Every claim moves them 1 day along a 7 day streak, and the reward depends on the day they are on.
#  After day 7 the streak starts again at day 1.
#  If more than STREAK_GRACE_HOURS (48 hours) pass between two claims, the streak is broken and goes back to day 1.
#
#  HOW TO CHANGE THE REWARDS
#   1. Change the numbers below. Numbers have NO quotes and NO % sign.
#   2. Save this file and restart the bot.
#   3. Look at the bot's console. If anything is wrong it prints a [DAILY WARNING] that says how to fix it.
#
#  WHAT A DAY CAN GIVE (use any of these inside a day's { })
#   "grist"          Grist to spend in /item store.
#   "rolls"          Rolls to use with /roll.
#   "character"      A character, using the short name from utils.py, like "sr_noah".
#                    /daily only ever gives a player that character ONCE. Players who already own it,
#                    or already got it from /daily before (even if they recycled it), get "rolls_instead" instead.
#                    That way nobody ends up with 2 of them.
#                    A character given by /daily can't be pulled from any banner: the bot leaves it out by itself.
#   "rolls_instead"  How many rolls to give when the player can't get the character (see above).
#
#  EXAMPLE: to make day 3 give 15 Grist and 1 roll, change its line to
#      3: {"grist": 15, "rolls": 1},
#
# =====================================================================================

DAILY_COOLDOWN_HOURS = 24   # how long players have to wait between claims
STREAK_GRACE_HOURS = 48     # waiting longer than this between 2 claims breaks the streak (back to day 1)

DAILY_REWARDS = {
    1: {"grist": 10},
    2: {"grist": 10},
    3: {"grist": 10},
    4: {"grist": 20},
    5: {"grist": 20},
    6: {"grist": 20},
    7: {"character": "sr_noah", "rolls_instead": 10},   # [S'all Good, Man] Noah Cave, or 10 rolls
}
