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
            print("Bot is ready.")
            await self.bot.change_presence(activity=discord.Activity(name='Shadow Debug Noob', type=discord.ActivityType.watching))

        @self.bot.command()
        async def ping(ctx):
            await ctx.channel.send("Pong! Hello, " + ctx.message.author.mention)
            return

if __name__ == "__main__":

    try:
        main_bot = MainBot(os.environ["TOKEN"])
    except KeyError:
        print("Environment Variables not found. Unable to assign token.")