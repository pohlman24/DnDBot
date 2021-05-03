from discord.ext import commands
import random
import requests
import json
import os
import operator
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print('--------')


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


def read_file(file):
    with open(file, "r") as f:
        data = json.load(f)
    f.close()
    return data


def write_file(data):
    with open("players.json", 'w') as t:
        json.dump(data, t, indent=4)
    t.close()


async def delete_messages(ctx, user_author):
    messages = await ctx.channel.history(limit=100).flatten()

    for msg in messages:
        if msg.author == bot.user:
            if msg.content.startswith("Rolling"):
                print("deleting 'Rolling'")
                await msg.delete()
            if msg.content.startswith("  "):
                print("deleting '  '")
                await msg.delete()
            if msg.content.startswith("@"+str(user_author)):
                print("deleting '@user'")
                msg.delete()

        if msg.author == user_author:
            if msg.content.startswith('!r'):
                await msg.delete()


@bot.command(pass_context=True)
async def r(ctx, roll: str):
    """Rolls a dice using #d# format.
    e.g .r 3d6"""

    result_total = 0
    result_string = ''
    try:
        try: 
            num_dice = roll.split('d')[0]
            dice_val = roll.split('d')[1]
        except Exception as e:
            print(e)
            await ctx.send("Format has to be in #d# %s." % ctx.message.author.name)
            return

        if int(num_dice) > 500:
            await ctx.send("I cant roll that many dice %s." % ctx.message.author.name)
            return

        await delete_messages(ctx.message, ctx.message.author)  # ctx.message.author
        
        await ctx.send("Rolling %s d%s for %s" % (num_dice, dice_val, ctx.message.author.name))
        rolls, limit = map(int, roll.split('d'))

        for roll in range(rolls):
            number = random.randint(1, limit)
            result_total = result_total + number
            
            if result_string == '':
                result_string += str(number)
            else:
                result_string += ', ' + str(number)
        
        if num_dice == '1':
            await ctx.send(ctx.message.author.mention + "  :game_die:\n**Result:** " + result_string)
        else:
            await ctx.send(ctx.message.author.mention + "  :game_die:\n**Result:** " + result_string)

    except Exception as e:
        print(e)
        return

# add check to see if spell is real
# add check to see if spell it ritual, if so it needs to be added to the name
@bot.command()
async def spell(ctx, *spells):
    """Lets user look up a spell
        and out puts the spell in chat"""
    data = read_file("spells.json")

    called_spell = " ".join(spells).lower()
    called_spell = called_spell.replace(" ", "-")

    temp = (data["Spells"])
    if any(d.get("name") == called_spell for d in temp):
        # checks if spell name is in json file
        spell_index = next((index for (index, d) in enumerate(temp) if d["name"] == called_spell), None)
        # finds the index of spell
        temp_list = []
        new_list = ""

        for line in temp[spell_index].values():
            if line == "Level:" or line == "Casting time:" or line == "Range:" or line == "Components:" \
                    or line == "Duration:":
                temp_list.append(line + " ")
            elif line == "At higher level":
                temp_list.append("-"+line + "\n")
            else:
                temp_list.append(line + "\n")
            new_list = "".join(temp_list)
        await ctx.send("```diff" + "\n" + new_list + "```")
    else:
        await ctx.send("Loading spell...")
        i = 0
        url = 'https://www.dnd-spells.com/spell/' + called_spell
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        my_dict = {}
        temp_list = []
        for string in soup.find('div', class_='col-md-12').stripped_strings:
            if string == 'Remove the adds':
                continue
            if string == 'A':
                break
            i = i + 1
            if i == 1:
                temp_list.append(string + "\n")
                my_dict["name"] = called_spell
            elif string == "Level:" or string == "Casting time:" or string == "Range:" or \
                    string == "Components:" or string == "Duration:":
                temp_list.append(string + " ")
                my_dict[i] = string
            elif string == "At higher level":
                temp_list.append("-"+string + "\n")
            else:
                temp_list.append(string + "\n")
                my_dict[i] = string

        new_list = "".join(temp_list)
        await ctx.send("```diff" + "\n" + new_list + "```")
        temp.append(my_dict)
        write_file(data)

# need to account for if people roll the same number
# need to move tracker to json file so that you can use future commands to it
# Ex. update player names
@bot.command()
async def combat(ctx, npc):
    """Keeps track of Initiative order. Use the command followed by number of NPCs
    """
    data = read_file("players.json")
# check if any players enter the same number
# if they did then ask for their dex mods
# compare dex mods and announce who goes first
# update JSON file
# if they are the same then ask to reroll
# compare rerolls an announce who goes first
# update JSON file.
    await ctx.send("Roll for Initiative! \nEveryone type your roll")
    for i in range(len(data["players"])):
        await bot.wait_for('message', check=None)

    messages = await ctx.channel.history(limit=len(data["players"])).flatten()
    for message in messages:
        for player in data["combat"]:
            if message.author.name == player:
                data["combat"][player] = int(message.content)
                write_file(data)

    if int(npc) != 0:
        await ctx.send("DM, enter any NPC names followed by their rolls\nExample: 'Wolf 16'")
        for i in range(int(npc)):
            await bot.wait_for('message', check=None)
        messages = await ctx.channel.history(limit=int(npc)).flatten()
        for message in messages:
            print(message)
            if message.author.name != data["DM"]:
                continue
            else:
                temp = message.content.split()
                data["combat"][temp[0]] = int(temp[1])

    # plan on making this its own function when I expand more on combat
    data = read_file("players.json")
    sorted_order = sorted(data["combat"].items(), key=operator.itemgetter(1), reverse=True)
    temp_string = ""
    for player in sorted_order:
        temp_string += f"{str(player[0])}: {str(player[1])}\n"
    await ctx.send(f"```{temp_string}```")


@bot.command()
async def endcombat(ctx):
    """Ends the current combat session"""
    data = read_file("players.json")
    to_delete = set(data["combat"].keys()).difference(data["players"])
    for combatant in to_delete:
        del data["combat"][combatant]

    write_file(data)


@bot.command()
async def setdm(ctx, player_name):
    """Sets the DM player using the command followed by DM player name"""
    data = read_file("players.json")
    data["DM"] = player_name
    write_file(data)


@bot.command()
async def getdm(ctx):
    """Sets the DM player using the command followed by DM player name"""
    data = read_file("players.json")
    await ctx.send(data["DM"])


@bot.command()
async def getplayers(ctx):
    """Displays list of current party"""
    data = read_file("players.json")

    temp_string = ""
    for player in data["players"]:
        temp_string += f"{player} \n"
    await ctx.send(f"```{temp_string}```")


@bot.command()
async def addplayer(ctx, *player_name):
    """Add a player to the party.
    Use command followed by new player name"""
    data = read_file("players.json")

    player_name = " ".join(player_name).title()
    if player_name not in data["players"]:
        data["players"].append(str(player_name.title()))
        write_file(data)

        await ctx.send(f"New player list")
        await getplayers(ctx)
    else:
        await ctx.send("That player is already in the party.")
        await getplayers(ctx)

@bot.command()
async def removeplayer(ctx, player_name):
    """Removes a player from the party.
    Use command followed by new player name"""
    data = read_file("players.json")
    player_name = player_name.title()
    try:
        data["players"].remove(player_name)
        write_file(data)

        await ctx.send("New Player List")
        await getplayers(ctx)
    except:
        await ctx.send("That player is not in the party.\nCurrent party list")
        await getplayers(ctx)


@bot.command()
async def removeallplayers(ctx):
    data = read_file("players.json")
    data["players"].clear()
    write_file(data)

bot.run(TOKEN)
