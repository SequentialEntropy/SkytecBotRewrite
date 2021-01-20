import discord
from discord.ext import commands
import os
import asyncio
import datetime
from mcstatus import MinecraftServer

try:
    from SetEnviron import environ
    environ()
except FileNotFoundError:
    print("SetEnviron file not found. Make sure a .env file is present or environment variables are set instead.")

try:
    import Webserver
    Webserver.server()
except FileNotFoundError:
    print("Webserver file not found. Bot will not be able to stay online nor receive data from the database.")

sizes = ["small", "medium", "large"]
staffrole = 653410679424024586

botcommands = {
    "-ping": "Sends a message back to the author",
    "-projects": "Shows a list of current Skytec City projects",
    "-status <type> <message>": "Changes the status of the Skytec City bot [Requires Staff Role]",
    "-kill": "Shuts down the Skytec City bot for maintenance [Requires Staff Role]",
    "-uptime": "Tells uptime information of the Skytec City bot",
    "-getinfo <server>": "Get information about the Altitude servers",
    "-help": "Sends a list of all Skytec City commands"
}

class MainBot:

    def __init__(self, token):
        self.bot = commands.Bot(command_prefix=("-"))
        self.bot.remove_command("help")
        self.token = token
        self.startup = datetime.datetime.now()
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
                title="Ping Command",
                description="Sends a message back to the author",
                color=discord.Color.teal()
            )
            embedelement.add_field(
                name="Pinged by " + ctx.message.author.display_name,
                value="Pong",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )
            return

        @self.bot.command()
        async def projects(ctx):
            global updateprojects
            embedelement = discord.Embed(
                title="Projects Command",
                description="Shows a list of current Skytec City projects",
                color=discord.Color.dark_blue()
            )
            for project in range(0, len(Webserver.updatedprojects)):
                text = "Description: {}\nEstimate Time Completion: {}".format(str(Webserver.updatedprojects[project]["description"]), str(Webserver.updatedprojects[project]["estimated-time"].strftime("%b %d %Y")))
                embedelement.add_field(
                    name=str(Webserver.updatedprojects[project]["name"]),
                    value=text,
                    inline=False
                )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )


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
                    color=discord.Color.blue()
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
                return
            embedelement = discord.Embed(
                title="Status Command",
                description="Changes the Skytec City bot status",
                color=discord.Color.blue()
            )
            embedelement.add_field(
                name="Status changed by " + ctx.message.author.display_name,
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
                name="Skytec City bot killed by " + ctx.message.author.display_name,
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
        async def uptime(ctx):
            embedelement = discord.Embed(
                title="Uptime Command",
                description="Tells uptime information",
                color=discord.Color.gold()
            )
            embedelement.add_field(
                name="Skytec City bot startup time",
                value="Skytec City bot started up on [" + self.startup.strftime("%b %d %Y %H:%M:%S") + "]",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )

        @self.bot.command()
        async def getinfo(ctx, server):
            if server in ["valley", "summit", "meadow", "atoll", "creative"]:
                server = MinecraftServer.lookup(server + ".alttd.com")
                status = server.status()
                embedelement = discord.Embed(
                    title="Server Status",
                    description="Information of the server",
                    color=discord.Color.green()
                )
                for information in server:
                    embedelement.add_field(
                    name=information,
                    value=server[information],
                    inline=False
                )
                await ctx.channel.send(
                    content=None,
                    embed=embedelement
                )
            else:
                embedelement = discord.Embed(
                    title="Server Status",
                    description="Information of the Server",
                    color=discord.Color.green()
                )
                embedelement.add_field(
                    name="Failed to Get Information",
                    value="Invalid Server Name [" + server + "] Please choose from [valley/summit/meadow/atoll/creative]"
                )
                await ctx.channel.send(
                    content=None,
                    embed=embedelement
                )

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
    except SyntaxError:
        print("Syntax Error")
    Webserver.kill()