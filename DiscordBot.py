import discord
from discord.ext import commands
import os
import asyncio

try:
    from SetEnviron import environ
    environ()
except FileNotFoundError:
    print("SetEnviron file not found. Make sure a .env file is present or environment variables are set instead.")

try:
    import Webserver
    Webserver.server()
except FileNotFoundError:
    print("Webserver file not found. Make sure a .env file is present or environment variables are set instead.")

sizes = ["small", "medium", "large"]
staffrole = 653410679424024586

botcommands = {
    "-ping": "Sends a message back to the author | Usage: -ping",
    "-status": "Changes the status of the Skytec City bot [Requires Staff Role] | Usage: -status <playing/watching/listening/streaming/custom> <message>",
    "-kill": "Shuts down the Skytec City bot for maintenance [Requires Staff Role] | Usage: -kill",
    "-help": "Sends a list of all Skytec City commands | Usage: -help"
}

class MainBot:

    def __init__(self, token):
        self.bot = commands.Bot(command_prefix=("-"))
        self.bot.remove_command("help")
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
            embedelement = discord.Embed(
                name="Ping Command",
                description="Sends a message back to the author",
                color=discord.Color.orange()
            )
            embedelement.add_field(
                name="Pinged by " + ctx.message.author.mention,
                value="Pong",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )
            return

        @self.bot.command()
        @commands.has_any_role(staffrole)
        async def status(ctx, statustype, *args, **kwargs):
            message = " ".join([arg for arg in args])
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
                embedelement = discord.Embed(
                    title="Status Command",
                    description="Changes the Skytec City bot status",
                    color=discord.Color.green()
                )
                embedelement.add_field(
                    name="Status was not changed",
                    value="Invalid Status Type [" + statustype + "] Please choose from [Playing/Watching/Listening/Streaming/Custom]",
                    inline=False
                )
                await ctx.channel.send(
                    content=None,
                    embed=embedelement
                )
            embedelement = discord.Embed(
                title="Status Command",
                description="Changes the Skytec City bot status",
                color=discord.Color.green()
            )
            embedelement.add_field(
                name="Status changed by " + ctx.message.author.mention,
                value="Status changed to type [" + statustype + "] with message [" + message + "]",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )

        @self.bot.command()
        @commands.has_any_role(staffrole)
        async def kill(ctx):
            embedelement = discord.Embed(
                title="Kill Command",
                description="Shuts down the Skytec City bot for maintenance",
                color=discord.Color.red()
            )
            embedelement.add_field(
                name="Skytec City bot killed by " + ctx.message.author.mention,
                value="Skytec City bot is now shutting down for maintenance",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )
            print("Server killed by: " + ctx.message.author.name + ".")
            await self.bot.logout()

        @self.bot.command()
        async def help(ctx):
            embedelement = discord.Embed(
                title="Help Command",
                description="List of all Skytec City commands",
                color=discord.Color.purple()
            )
            for command in botcommands:
                embedelement.add_field(
                    name=command,
                    value=botcommands[command],
                    inline=False
                )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )

if __name__ == "__main__":

    try:
        main_bot = MainBot(os.environ["TOKEN"])
    except KeyError:
        print("Environment Variables not found. Unable to assign token.")
    Webserver.kill()