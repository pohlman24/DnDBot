from discord.ext import commands
import discord
bot = commands.Bot(command_prefix="!")


class Character(commands.cog):

    def __init__(self,bot,name="Derkin", hp=10, ac=13, speed=30, initiative=2):
        # will need a spell-list as a dict or list
        # need inventory
        # maybe have stats as an object
        self.bot = bot
        self.name = name
        self.hp = hp
        self.ac = ac
        self.speed = speed
        self.initiative = initiative
        self.spell_list = {}
        self.stats = {}
        self.inventory = []
        self.owner = ""

    def set_character(self, ctx):
        print("Enter character's name")
        await ctx.send("Enter character's name")
        # name = input()
        print("Enter character's max health")
        # hp = input()
        print("Enter character's armor class")
        # ac = input()
        print("Enter character's speed")
        # speed = input()
        print("Enter character's initiative modifier")
        # initiative = input()
        # self.owner = bot.

    def get_character(self):
        print(f"Name: {self.name}")
        print(f"Health: {self.hp}")
        print(f"Armor class: {self.ac}")
        print(f"Speed: {self.speed}")
        print(f"Initiative modifier: {self.initiative}")

    def update_name(self):
        print("\nEnter new name")
        self.name = input()

    def update_health(self):
        print("\nEnter new health")
        self.hp = input()

    def update_armor_class(self):
        print("\nEnter new armor class")
        self.ac = input()

    def update_speed(self):
        print("\nEnter new speed")
        self.speed = input()

    def update_initiative(self):
        print("\nEnter new initiative modifier")
        self.initiative = input()


def setup(bot):
    bot.add_cog(Character(bot))

