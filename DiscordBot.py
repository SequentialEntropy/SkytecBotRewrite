import discord
from discord.ext import commands
import os
import asyncio

try:
    from SetEnviron import environ
    environ()
except FileNotFoundError:
    pass

sizes = ["small", "medium", "large"]

class MainBot:

    def __init__(self, token):
        self.bot = commands.Bot(command_prefix=("-"))
        self.token = token
        self.define_commands()
        self.bot.run(self.token)

    def define_commands(self):

        @self.bot.event
        async def on_ready():
            await self.bot.change_presence(game=discord.Game(name="Skytec City", type=3))

        @self.bot.command(pass_context=True)
        async def ping(ctx):
            await self.bot.say("Pong! Hello, " + ctx.message.author.mention)
            return

        @self.bot.command(pass_context=True)
        async def apply(ctx, sellitems, size):
            if size in sizes:
                await self.bot.say(ctx.message.author.mention + " You applied for a " + size + " size plot and you are planning to sell " + sellitems + ".")
            else:
                await self.bot.say(ctx.message.author.mention + " Plot size " + size + " is invalid. Please choose from " + ", ".join(sizes) + ".")

if __name__ == "__main__":

    try:
        main_bot = MainBot(os.environ["TOKEN"])
    except KeyError:
        print("Environment Variables not found. Unable to assign token.")