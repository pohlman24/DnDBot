from discord.ext import commands
import random
import requests
import json
import os
import discord
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


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send_message(ctx.message.channel, 'Usage: `.r #d#` e.g. `.r 1d20`\nUse .help for more info.')


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


@bot.command()
async def spell(ctx, *spells):
    """Lets user look up a spell
        and out puts the spell in chat"""

    with open("spells.json") as f:
        data = json.load(f)

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
        with open("spells.json", 'w') as t:
            json.dump(data, t, indent=4)

    print("Ending Command...")


@bot.command()
async def combat(ctx, enemies):
    tracker = {
        "Nano": 0,
        "BlueMageJake": 0,
        "taypoh": 0,
        "Dr. Chad Thundercock": 0,
    }
    await ctx.send("Roll for Initiative! \nEveryone type your roll")
    await bot.wait_for('message', check=None)
    await bot.wait_for('message', check=None)
    await bot.wait_for('message', check=None)
    await bot.wait_for('message', check=None)

    print("before wait loop")
    for i in range(int(enemies)):
        print(i)
        await bot.wait_for('message', check=None)
        print('end of loop')

    messages = await ctx.channel.history(limit=4 + enemies).flatten()
    for message in messages:
        print(message)
        if message.author.name == 'Nano':
            tracker["Nano"] = int(message.content)
        if message.author.name == "BlueMageJake":
            tracker["BlueMageJake"] = int(message.content)
        if message.author.name == "taypoh":
            tracker["Taypoh"] = int(message.content)
        if message.author.name == "Dr. Chad Thundercock":
            tracker["Dr. Chad Thundercock"] = int(message.content)

        if message.author.name == "Tordalidar":
            temp = message.content.split
            tracker[temp[0]] = int(temp[1])

    sorted_order = sorted(tracker.items(), key=lambda x: x[1])
    for player in sorted_order:
        print(player[0], player[1])
        await ctx.send(str(player[0]) + ": " + str(player[1]))


# to add. a group stealth check. ask players for stealth check and then auto calc the average


bot.run(TOKEN)
