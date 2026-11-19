# Jit Bot

**The ultimate Discord Jitstuck GACHA GAME experience!**

## Installation Requirements:
 - "**Visual Studio Code**": I suggest you get this because you can add your github account directly to the IDE and you can talk to the github copilot AI directly inside of the codespace and it'll automatically read the code (so you don't have to copy and paste into chatgpt or something else)
 - Python 3.14.0 or something similar works
 - Mongodb --> Currently it points to localhost
 - Make sure you get MongoDB compass as itll be easier to use (its the GUI version)

 That should be it however if there are any errors let me know

## How to Setup:

### Install the Zip
 - Click the green button that says code and install the zip of the repository
 - Unzip the repository into a location of your choosing
 - Create a new file called "token.env" it will be used later

### Setup Discord Bot
 - Watch any tutorial on youtube on how to setup a discord bot and going through Discord interface and adding to private server
 - **Note:** When you get the discord bot token add the token to the new file you made called "token.env" --> inside this file add the discord bot token like so:
 - DISCORD_TOKEN=[PLACE TOKEN HERE!]

### Setup MongoDB
 - Open MongoDB (Compass) and create a new database with the name of "jitstuck" and inside make a collection called: "inventory" --> on new users found it will auto generate everything required (hopefully)
 - The "items" collection gets made and filled with the starting items by itself the first time the bot starts

### Time to Run!:
 - You should be able to run the main.py file and it will be all good to go!
 - If python is not in your PATH you will have to force it when running main.py
 - Try this first: python3 main.py
 - If not then do something like:

  & C:/Users/Youruser/AppData/Local/Python/pythoncore-3.14-64/python.exe c:/Users/YourUser/jitbotlocation/main.py

## A Few Final Notes:
 - You can always run /syncapp which will reset everything and fix any weird synchronization issues. Dont forget to reload Discord [CTRL + R] after running this command as the client needs a refresh too!
 - /embedtest is a nightmare command that shows literally most maximum possible functions of discord embeds and will be removed soon and if i dont remove it you can remove it yourself
 - All gifs pertaining to /char have to be taken from a web link so sadly can't be stored locally (it is possible but discord doesn't like it so unless an issue is ran into then they will stay like that) --> this means you can't view them without running the bot and running the command
 - Battle.py is where all the battle logic SHOULD go --> Main.py asks stuff of battle.py to do and it does all LOGIC
 - Utils.py is a beautiful simple python file that stores pure data and can be referenced from Battle.py or main.py
 - calculate_feet.py should be moved into its own folder called "tools" as its never run by the program and you would only run it yourself with specific parameters when adding a new character to figure out spacing
 - I suggest moving the final 3 pngs and gifs into folders to keep it clean and fixing the code when it points to them
 - If you want to enable sssr_max then go to main.py, find the line that starts with all_characters = (near the top, search for it with CTRL + F) and uncomment the + secretChar
 - Finally any changes you do to the bots code you must stop and restart the bot for them to truly apply

## Adding a new banner
Banners are what /roll rolls on and what /banner shows. They all live in one file called **banners.py**, and you don't need to know how to code to add one.

1. Stop the bot.
2. Open **banners.py**. The top of the file explains every field.
3. Find the block marked **TEMPLATE**. Copy everything from the `# add_banner(` line down to the `# )` line.
4. Paste it at the very bottom of the file.
5. Remove the `# ` from the start of every line you pasted. In VS Code you can select the lines and press **Ctrl + /** to do it all at once.
6. Fill it in:
   - **name**: what the banner is called in Discord. Every banner needs its own name.
   - **description**: a sentence or two about the banner.
   - **image** (optional): a web link starting with https://, or a picture inside the bot folder like `graphics/banner.gif`.
   - **color** (optional): a color code like `"#3f48cc"`.
   - **ssr_rate, sr_rate, r_rate** (and sssr_rate if you need it): the % chance of each rarity. They must add up to exactly 100.
   - **contents**: the characters that can be pulled, using the short names from the top of utils.py like `"r_trey"`. You don't type the rarity, the bot gets it from utils.py.
   - **featured** (optional): characters that get a star in /banner. It's only for show and doesn't change the chances.
7. Save the file and start the bot again.
8. Read the console. If something is wrong you'll see a **[BANNER WARNING]** line that names the banner and says what to fix, for example a misspelled character name or rates that don't add up to 100. The bot keeps running, it just leaves out what it can't use.
9. In Discord run **/banner** to check it, and **/roll** to roll on it.

Good to know:
 - Changing or adding banners only needs a **restart**. You only need **/syncapp** when a command itself changes, like the first time you run this version of the bot (because /banner is new and /roll changed). After a /syncapp remember to reload Discord with CTRL + R.
 - To change a banner edit its block. To remove a banner delete its block. Then restart.
 - All banners share the same rolls.
 - Adding a new character to utils.py doesn't put it on any banner by itself. Add it to a banner's contents too. The console warns you about any character that isn't on a banner.
 - Secret characters like sssr_max are left out of every banner until you turn them on (see A Few Final Notes above).

## Items
Players buy items with **Grist** in **/item store**, put one in their team's item slot with **/item equip**, and check it with **/item show**. The equipped item helps the whole team in every battle. Every /item reply is only visible to the player who used the command.

| Item | Price | What it does |
|---|---|---|
| Agent Knife | 35 | +5% ATK and +10% EVA for every team member |
| Dersite Enforcer Hat | 50 | Every team member takes 5% less damage |
| Dersite Longman's Spear | 50 | +15% ACC for every team member |
| Lucky Coin | 30 | Every hit your team lands has a 2% chance to be a critical hit for 1.5x damage |
| Perfectly Generic Object | 5 | +1 HP, +1 ATK, 1% less damage taken, +1% EVA and +1% ACC for every team member, only during the first 3 turns of each battle |
| Bag of Purina Treats | 45 | On turns 5, 10, 15 and so on, each team member heals 5% of their max HP |
| Dersite Knuckledusters | 20 | +5% ACC for every team member |
| Protein Brick | 75 | +50% ATK for every team member, but every turn there's a 50% chance the whole team hits themselves in the head with it and skips its turn |
| Knife Noir | Not sold | Every hit from a character's basic attack (their first move, like Punch or Dropkick) gives the enemy a stack of Bleed: 3% of its max HP at the end of the turn. Has a 10% chance to drop when you beat Jack Noir |

How items work:
 - A player can own one of each item. Equipping doesn't use the item up, and swapping puts the old item back with their other items.
 - The item is locked in when a battle starts. Swapping items during a battle only counts from the next battle.
 - EVA and ACC bonuses are added onto the % chance, the same way ability buffs work. A "turn" is one full round of a battle.
 - Item bonuses only exist during battles. They are never saved onto the characters.

### Grist
Players earn Grist by **winning** a /battle. Losing, retreating or letting the battle time out gives nothing.

| Enemy | Grist for winning |
|---|---|
| Ruffian (1 shows up) | 5 |
| Ruffians (2 show up) | 7 |
| Spearman | 7 |
| Agent | 9 |
| Grunt | 15 |
| Jack Noir | 35 |

Players can spend Grist on items, or on rolls with the **Buy a Roll** button in /item store. A roll costs 15 Grist and they can buy as many as they like. To change the price, edit **rollPrice** in utils.py and restart the bot.

To change the battle amounts, edit **gristRewards** in utils.py (search for it with CTRL + F) and restart the bot. A new enemy needs a line there too, otherwise beating it gives 0 Grist and the console says so.

To give someone Grist by hand (for testing or as a reward), use MongoDB Compass:
1. Open the **jitstuck** database, then the **inventory** collection.
2. Type `{ "username": "theirname" }` in the filter box and press **Find**.
3. Hover over their document and click the pencil (**Edit Document**).
4. If they have no **grist** field yet, click the **+** next to the last field and add one called `grist`. Set its type to **Int32**, not String, then type the amount.
5. Click **Update**. It works straight away, without restarting the bot.

### Where items are saved
Everything about items is in MongoDB, in the **jitstuck** database:
 - The **items** collection has one document for every item: its name, price, description, picture and what it does.
 - Each player's document in the **inventory** collection has their **grist**, the **items** they own and their **equipped_item**.

The first time the bot starts with an empty **items** collection, it fills it with the starting items from the table above. After that you add and change items in MongoDB Compass, and you never need to touch the code. If you ever delete every item, the bot puts the starting items back on the next start.

### Adding a new item
1. Open MongoDB Compass, then the **jitstuck** database, then the **items** collection.
2. Click **ADD DATA**, then **Insert document**.
3. Delete what's in the box and paste this template:
   ```json
   {
     "name": "My New Item",
     "price": 25,
     "description": "Write a sentence or two about the item here.",
     "emoji": "🗡️",
     "image": "graphics/items/my_new_item.png",
     "effect": "stat_percent",
     "attack": 5,
     "defense": 5
   }
   ```
4. Change the values to what you want. The fields are explained below. Keep the quotes around text, and leave numbers without quotes.
5. Click **Insert**.
6. Restart the bot and read the console. If something is wrong you'll see an **[ITEM WARNING]** line that names the item and says what to fix, for example a price saved as text or a misspelled effect. The bot keeps running, it just leaves out what it can't use.
7. In Discord run **/item store** to check it. New items go at the end of the store.

To **change** an item, hover over its document in Compass, click the pencil, change the value, click **Update** and restart the bot. To **remove** one, click the bin icon on its document and restart.

**The fields:**
 - **name**: what the item is called in Discord. Every item needs its own name.
 - **price**: how much Grist it costs, a whole number above 0. Not needed when in_store is false.
 - **description**: a sentence or two shown in the store.
 - **emoji** (optional): an emoji shown next to the name.
 - **image** (optional): a web link starting with https://, or a picture inside the bot folder like `graphics/items/luckycoin.png`.
 - **effect**: what kind of thing it does, plus the numbers that effect needs:

| effect | What it does | Numbers it needs |
|---|---|---|
| `stat_percent` | The whole team gets a % bonus for the whole battle | any of `hp`, `attack`, `defense`, `evasion`, `accuracy` |
| `stat_flat` | The whole team gets a flat bonus for the whole battle | any of `hp`, `attack`, `defense`, `evasion`, `accuracy` |
| `temp_stat_flat` | Like stat_flat, but only for the first few turns of each battle | the stats, plus `turns` |
| `crit_chance` | Every hit the team lands has a chance to be a critical hit | `chance` (the %), `multiplier` (1.5 = 1.5x damage) |
| `periodic_heal` | Every few turns, everyone on the team heals a % of their max HP | `every` (5 = turns 5, 10, 15...), `percent` |
| `basic_attack_bleed` | Every hit from a basic attack (each character's first move) gives the enemy a stack of Bleed | `percent` (of the enemy's max HP), `turns` |

 - What the stat numbers do: `hp` and `attack` are a % with stat_percent and a flat amount with stat_flat. `defense` always means the team takes that % less damage. `evasion` and `accuracy` are added onto the % chance to dodge or hit. The short names `atk`, `def`, `eva` and `acc` work too.
 - **in_store**, **drop_from** and **drop_chance** (optional): for an item that can't be bought and drops from an enemy instead, like Knife Noir. Use `"in_store": false`, the /battle enemy like `"drop_from": "Jack Noir"` and the % chance like `"drop_chance": 10`.
 - **skip_chance** and **skip_text** (optional): a downside like the Protein Brick has. skip_chance is the % chance every turn that the whole team skips its turn, and skip_text is what the battle log says when it happens.

Good to know:
 - Adding or changing items needs a **restart** of the bot. You need **/syncapp** once, the first time you run this version of the bot, because /item is a new command. After a /syncapp remember to reload Discord with CTRL + R.
 - Numbers have to be saved as numbers. If Compass shows a number in quotes, its type is String: click the type next to the value and change it to **Int32** (or **Double** for numbers like 1.5).
 - Don't rename an item that people already own. Players' items are saved by name, so they would lose it.
 - A brand-new kind of effect (something none of the effects above can do) needs code in item_helper.py and battle.py first.
 - The store can show up to 24 items, because Discord allows 25 buttons and one of them is Buy a Roll.

## Daily rewards
Players can use **/daily** once every 24 hours. Every claim moves them one day along a 7 day streak, and after day 7 it starts again at day 1. If more than 48 hours pass between two claims, the streak breaks and they go back to day 1. Every /daily reply is only visible to the player who used it.

| Day | Reward |
|---|---|
| 1, 2, 3 | 10 Grist each |
| 4, 5, 6 | 20 Grist each |
| 7 | **[S'all Good, Man] Noah Cave**, or 10 rolls if they already own him or already got him from /daily before |

Noah Cave can't be pulled from any banner, so /daily is the only way to get him, and every player can only get him from /daily once (even if they recycle him).

### Changing the rewards
1. Open **daily_rewards.py**. The top of the file explains everything a day can give.
2. Change the numbers, for example `4: {"grist": 25},`. Numbers have no quotes.
3. To change the waiting times, change **DAILY_COOLDOWN_HOURS** (24) or **STREAK_GRACE_HOURS** (48).
4. Save the file, restart the bot and read the console. Mistakes show up as a **[DAILY WARNING]** line that says what to fix.

Good to know:
 - Changing the rewards only needs a **restart**. You need **/syncapp** once, the first time you run this version of the bot, because /daily is a new command. After a /syncapp remember to reload Discord with CTRL + R.
 - Each player's document in MongoDB gets **last_daily** (when they last claimed, in UTC), **daily_streak** (the day they last claimed, 1 to 7) and **daily_got_sr_noah** (true once /daily gave them Noah Cave). Players without these fields have never claimed and can claim straight away.
 - A character used as a /daily reward is kept off every banner automatically. The console warns if banners.py lists it.