import discord
from discord.ext import commands
import os
import asyncio

try:
    from SetEnviron import environ
    environ()
    import Webserver
    Webserver.server()
except FileNotFoundError:
    print("SetEnviron file not found. Make sure a .env file is present or environment variables are set instead.")


sizes = ["small", "medium", "large"]
staffrole = 653410679424024586


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
            await self.bot.change_presence(activity=discord.Activity(name='Skytec City', type=discord.ActivityType.watching))

        @self.bot.command()
        async def ping(ctx):
            await ctx.channel.send("Pong! Hello, " + ctx.message.author.mention)
            return

        @self.bot.command()
        @commands.has_any_role(staffrole)
        async def status(ctx, statustype, message):
            if statustype == "playing":
                await self.bot.change_presence(activity=discord.Activity(name=message, type=discord.ActivityType.playing))
            elif statustype == "watching":
                await self.bot.change_presence(activity=discord.Activity(name=message, type=discord.ActivityType.watching))
            elif statustype == "listening":
                await self.bot.change_presence(activity=discord.Activity(name=message, type=discord.ActivityType.listening))
            elif statustype == "streaming":
                await self.bot.change_presence(activity=discord.Activity(name=message, type=discord.ActivityType.streaming))
            elif statustype == "custom":
                await self.bot.change_presence(activity=discord.Activity(name=message, type=discord.ActivityType.custom))
            else:
                await ctx.channel.send("Invalid Status Type: " + statustype + ", Please choose from Playing/Watching/Listening/Streaming/Custom.")
                return
            await ctx.channel.send("Status changed to type: " + statustype + ", message: " + message + ".")

if __name__ == "__main__":

    try:
        main_bot = MainBot(os.environ["TOKEN"])
    except KeyError:
        print("Environment Variables not found. Unable to assign token.")