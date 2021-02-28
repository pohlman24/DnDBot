import discord
from discord.ext import commands
import random
import string
import re
import requests
from bs4 import BeautifulSoup

bot = commands.Bot(command_prefix="!")
# Todo make a !help command to print all the available commands 
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
        await bot.send_message(ctx.message.channel, 'Usage: `.r #d#` e.g. `.r 1d20`\nUse .help for more info.')


async def delete_messages(ctx, user_author):
    messages = await ctx.channel.history(limit=100).flatten()

    for msg in messages:
        if msg.author == bot.user:
            if msg.content.startswith("Rolling"):
                print("deleting 'Rolling'")
                await msg.delete()
            if  msg.content.startswith("  "):
                print("deleting '  '")
                await msg.delete()
            if msg.content.startswith("@"+str(user_author)):
                print("deleting '@user'")
                msg.delete()

        if msg.author == user_author:
            if msg.content.startswith('!r'):
                await msg.delete()

@bot.command(pass_context=True)
async def r(ctx, roll : str):
    """Rolls a dice using #d# format.
    e.g .r 3d6"""

    resultTotal = 0
    resultString = ''
    try:
        try: 
            numDice = roll.split('d')[0]
            diceVal = roll.split('d')[1]
        except Exception as e:
            print(e)
            await ctx.send("Format has to be in #d# %s." % ctx.message.author.name)
            return

        if int(numDice) > 500:
            await ctx.send("I cant roll that many dice %s." % ctx.message.author.name)
            return

        await delete_messages(ctx.message, ctx.message.author) #, ctx.message.author
        
        await ctx.send("Rolling %s d%s for %s" % (numDice, diceVal, ctx.message.author.name))
        rolls, limit = map(int, roll.split('d'))

        for r in range(rolls):
            number = random.randint(1, limit)
            resultTotal = resultTotal + number
            
            if resultString == '':
                resultString += str(number)
            else:
                resultString += ', ' + str(number)
        
        if numDice == '1':
            await ctx.send(ctx.message.author.mention + "  :game_die:\n**Result:** " + resultString)
        else:
            await ctx.send(ctx.message.author.mention + "  :game_die:\n**Result:** " + resultString + "\n**Total:** " + str(resultTotal))

    except Exception as e:
        print(e)
        return

@bot.command()
async def spell(ctx, *spells):
    """Lets user look up a spell
        and out puts the spell in chat"""
    # cure wounds is 16 lines long # highest is 19 so far
    # if the spell is from a addition book it will say so after the spell name "A spell from  Xanathar's Guide To Everything"
    
    print("Starting Program...")
    print(f"before manipulation {spells}")
    spell = (" ".join(spells)).lower()
    spell = spell.replace(" ", "-")
    print(f"after manipulation {spells}")

    url = 'https://www.dnd-spells.com/spell/' + spell
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    i = 0
    for string in soup.find('div', class_='col-md-12').stripped_strings: # i can fix it using the len() and basing it off of that
        if string == 'Remove the adds':
            continue
        if string == 'A':
            break
        i = i+1
        if i == 1: 
            await ctx.send(f"**{string}**") # Bolds the spell name
        elif i == 2:
            await ctx.send(f"*{string}*") # Italics the spell school
        elif i == 13:
            await ctx.send(f"*{string}*")
        elif i == 14:
            await ctx.send(f"*{string}*")
        elif i == 15:
            await ctx.send(f"**{string}**")            
        elif string == 'Level:':
            await ctx.send(f"**{string}** ")
        elif string == 'Casting time:':
            await ctx.send(f"**{string}** ")
        elif string == 'Range:':
            await ctx.send(f"**{string}** ")
        elif string == 'Components:':
            await ctx.send(f"**{string}** ")
        elif string == 'Duration:':
            await ctx.send(f"**{string}** ")
        else:
            await ctx.send(f"{string} \n")
    print("Ending Program...")


@bot.command()
async def combat(ctx, enemies):
    tracker = {
        "Nano": 0,
        "BlueMageJake": 0,
        "taypoh": 0,
        "Dr. Chad Thundercock": 0,
    }
    await ctx.send("Roll for Initative! \nEveryone type your roll")
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
        print(player[0],player[1])
        await ctx.send(str(player[0]) + ": " + str(player[1]))


# to add. a group stealth check. ask players for stealth check and then auto calc the average


bot.run('Nzk3ODg5MzM3OTIwNDU0Njc2.X_tCWg.iTR0MJFfIGa6_K-l02G6NOF_6bI')
