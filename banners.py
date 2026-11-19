# =====================================================================================
#  BANNERS
# =====================================================================================
#
#  Every banner in the bot is written in this file.
#  /banner shows them and /roll rolls on them. You do NOT need to know how to code to add one.
#
#  HOW TO ADD A NEW BANNER
#   1. Find the TEMPLATE block a bit further down this file.
#   2. Copy the whole template, from the  # add_banner(  line down to the  # )  line.
#   3. Paste it at the very bottom of this file.
#   4. Remove the "# " from the start of every line you pasted.
#      (In VS Code: select those lines and press Ctrl + /  to do it all at once)
#   5. Change the fields to what you want (every field is explained below).
#   6. Save this file and restart the bot.
#   7. Look at the bot's console. If anything is wrong it prints a [BANNER WARNING]
#      that says which banner has the problem and how to fix it.
#   8. Run /banner in Discord to see your banner. It can be rolled on with /roll straight away.
#      (You do NOT need /syncapp for a new banner, restarting the bot is enough.)
#
#  TO CHANGE A BANNER: edit its block, save, restart the bot.
#  TO REMOVE A BANNER: delete its whole block, save, restart the bot.
#
#  THE FIELDS
#   name         The banner's name in Discord. Every banner needs its own name.
#   description  A sentence or two about the banner.
#   image        (optional) A web link that starts with https:// (like the /char gifs use)
#                OR a picture inside the bot folder, like "graphics/banner.gif".
#   color        (optional) The color of the line down the side of the embed, like "#3f48cc".
#                Search "color picker" on Google to find the code for any color.
#   ssr_rate     The % chance of pulling an SSR on each roll.
#   sr_rate      The % chance of pulling an SR on each roll.
#   r_rate       The % chance of pulling an R on each roll.
#   sssr_rate    (optional) The % chance of pulling an SSSR on each roll.
#                The rates must add up to exactly 100.
#                Leave a rate out (or set it to 0) if the banner has none of that rarity.
#                Every character of the same rarity on a banner has the same chance.
#   contents     The characters you can pull, inside [ ] with a comma after each one.
#                Use the short names from the top of utils.py, like "r_trey" or "ssr_scottie".
#                Don't type the rarity anywhere, the bot works it out from utils.py by itself.
#   featured     (optional) Characters from contents that get a star in /banner.
#                This is only for show, it does NOT change anyone's chances.
#
#  THINGS THAT TRIP PEOPLE UP
#   - Text goes inside quotes:              name = "Summer Banner",
#   - Every field line ends with a comma:   description = "Hot new characters!",
#   - Numbers have NO quotes and NO % sign: ssr_rate = 3,
#   - Lines that start with # are notes for humans. The bot skips them.
#   - All banners use the same rolls, rolls are not per banner.
#   - Secret characters (like sssr_max) are left out of every banner until they are turned
#     on the way the README explains.
#   - Adding a new CHARACTER to utils.py does not put it on a banner by itself.
#     Add it to a banner's contents here too (the console warns you about characters that aren't on any banner).
#
# =====================================================================================

from banner_helper import add_banner   # leave this line alone


# ----- TEMPLATE (copy from the next line down to "# )", paste it at the bottom, then remove the "# ") -----
# add_banner(
#     name = "My New Banner",
#     description = "Write a sentence or two about the banner here.",
#     image = "https://put-a-link-to-your-picture-here.gif",
#     color = "#ff9900",
#     ssr_rate = 3,
#     sr_rate = 27,
#     r_rate = 70,
#     featured = ["ssr_trey"],
#     contents = [
#         "ssr_trey",
#         "sr_trey",
#         "r_trey",
#     ],
# )
# ----- END OF TEMPLATE -----


# ----- Standard banner (a picture from the graphics folder) -----
add_banner(
    name = "Standard",
    description = "The everyday banner. All of the regular R, SR and SSR characters can be pulled here.",
    image = "graphics/banner.gif",
    color = "#3f48cc",
    ssr_rate = 1,
    sr_rate = 29,
    r_rate = 70,
    contents = [
        # SSR
        "ssr_abraize",
        "ssr_trey",
        "ssr_jayden",
        # SR
        "sr_freeman",
        "sr_stephen",
        "sr_homestuck",
        "sr_abraize",
        "sr_trey",
        # R
        "r_abraize",
        "r_abraize2",
        "r_trey",
        "r_noah",
        "r_freeman",
        "r_stephen",
        "r_homestuck",
        "r_max",
        "r_jaiden",
    ],
)


# ----- Special banner (a fully filled in example: a web link picture, a color and a featured character) -----
add_banner(
    name = "Special Banner",
    description = "The special banner for special characters, limited time only!",
    image = "https://media.discordapp.net/attachments/1426812344549380136/1441591428042985492/SSR_SCOTTIE.gif?ex=69551be3&is=6953ca63&hm=9a1141a0f327f2f16ed80b996243679e62491b0fa2b985babdc1bc09d82cccaa&=&width=813&height=524",
    color = "#3f48cc",
    ssr_rate = 1,
    sr_rate = 29,
    r_rate = 70,
    featured = ["ssr_scottie"],
    contents = [
        # SSR
        "ssr_scottie",
        # SR
        "sr_freeman",
        "sr_stephen",
        "sr_homestuck",
        "sr_abraize",
        "sr_trey",
        # R
        "r_abraize",
        "r_abraize2",
        "r_trey",
        "r_noah",
        "r_freeman",
        "r_stephen",
        "r_homestuck",
        "r_max",
        "r_jaiden",
    ],
)
