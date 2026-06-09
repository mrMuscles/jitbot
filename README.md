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
 - If you want to enable sssr_max then go to line 77 of main.py and uncomment the + secretChar
 - Finally any changes you do to the bots code you must stop and restart the bot for them to truly apply