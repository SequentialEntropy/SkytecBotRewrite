import discord
from discord.ext import commands
import os
import asyncio

try:
    from SetEnviron import environ
    environ()
except FileNotFoundError:
    print("SetEnviron file not found. Make sure a .env file is present or environment variables are set instead.")

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

        @self.bot.command()
        async def ping(ctx):
            await self.bot.say("Pong! Hello, " + ctx.message.author.mention)
            return

if __name__ == "__main__":

    try:
        main_bot = MainBot(os.environ["TOKEN"])
    except KeyError:
        print("Environment Variables not found. Unable to assign token.")