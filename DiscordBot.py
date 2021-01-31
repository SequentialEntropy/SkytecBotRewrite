import discord
from discord.ext import commands
import os
import asyncio
import datetime
import requests
import json

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

try:
    import ServerInfoModule
    servers = {
        "lobby": {
            "api": ServerInfoModule.Server("lobby.alttd.com"),
            "color": 0x969c9f
        },
        "valley": {
            "api": ServerInfoModule.Server("valley.alttd.com", "vmap.alttd.com", "115survival"),
            "color": 0xf700ff
        },
        "summit": {
            "api": ServerInfoModule.Server("summit.alttd.com", "smap.alttd.com", "115survival"),
            "color": 0x00c9ff
        },
        "meadow": {
            "api": ServerInfoModule.Server("meadow.alttd.com", "mmap.alttd.com", "115survival"),
            "color": 0x00fe5d
        },
        "atoll": {
            "api": ServerInfoModule.Server("atoll.alttd.com", "amap.alttd.com", "115survival"),
            "color": 0xe8ff00
        },
        "creative": {
            "api": ServerInfoModule.Server("creative.alttd.com"),
            "color": 0x969c9f
        },
        "events": {
            "api": ServerInfoModule.Server("events.alttd.com"),
            "color": 0x969c9f    
        }
    }
except FileNotFoundError:
    print("ServerInfoModule file not found. Bot will not ping servers.")

sizes = ["small", "medium", "large"]
staffrole = 653410679424024586

botcommands = {
    "-ping": "Sends a message back to the author",
    "-projects": "Shows a list of current Skytec City projects",
    "-status <type> <message>": "Changes the status of the Skytec City bot [Requires Staff Role]",
    "-kill": "Shuts down the Skytec City bot for maintenance [Requires Staff Role]",
    "-uptime": "Tells uptime information of the Skytec City bot",
    "-server <server (leave blank for all servers)>": "Get information about the Altitude servers",
    "-players <server (leave blank for all servers)>": "Get information about online players",
    "-warps <server (leave blank for all servers)>": "Get information about warps",
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
            await self.bot.change_presence(activity=discord.Activity(name='Soon™ -server command', type=discord.ActivityType.playing))

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
        async def server(ctx, server=None):

            if server in servers:
                queryservers = [server]
            else:
                queryservers = [element for element in servers]

            for server in queryservers:

                api = servers[server]["api"]
                api.update()

                if api.info["motd"]["decoded"] != None:
                    embedelement = discord.Embed(
                        title=server[0].upper() + server[1:],
                        description="```{}```".format("\n".join(api.info["motd"]["decoded"])),
                        color=servers[server]["color"]
                    )
                else:
                    embedelement = discord.Embed(
                        title=server[0].upper() + server[1:],
                        description="```Unable to fetch MOTD```",
                        color=servers[server]["color"]
                    )

                if (api.info["ip"] != None) and (api.info["port"] != None):
                    embedelement.add_field(
                        name="Address",
                        value="{}:{}".format(servers[server]["api"].info["ip"], str(servers[server]["api"].info["port"]))
                    )
                else:
                    embedelement.add_field(
                        name="Address",
                        value="Unable to fetch"
                    )
                
                if api.info["version"] != None:
                    if api.info["software"] != None:
                        embedelement.add_field(
                            name="Version",
                            value="{} ({})".format(api.info["version"], api.info["software"])
                        )
                    else:
                        embedelement.add_field(
                            name="Version",
                            value=api.info["version"]
                        )
                else:
                    embedelement.add_field(
                        name="Version",
                        value="Unable to fetch"
                    )
                
                if (api.info["players"]["online"] != None) and (api.info["players"]["max"] != None):
                    embedelement.add_field(
                        name="Players",
                        value="{} / {}".format(str(api.info["players"]["online"]), str(api.info["players"]["max"]))
                    )
                else:
                    embedelement.add_field(
                        name="Players",
                        value="Unable to fetch"
                    )
                
                if api.dynmapip != False:
                    if api.info["servertime"] != None:
                        embedelement.add_field(
                            name="Server Time",
                            value=str(api.info["servertime"])
                        )
                    else:
                        embedelement.add_field(
                            name="Server Time",
                            value="Unable to fetch"
                        )
                    if api.info["weather"] != None:
                        embedelement.add_field(
                            name="Weather",
                            value=api.info["weather"]
                        )
                    else:
                        embedelement.add_field(
                            name="Weather",
                            value="Unable to fetch"
                        )

                    embedelement.add_field(
                        name="Warps",
                        value=str(len(api.info["warps"]))
                    )

                embedelement.set_thumbnail(url=api.info["icon"])

                await ctx.channel.send(
                    content=None,
                    embed=embedelement
                )

        @self.bot.command()
        async def players(ctx, server=None):
            if server in servers:
                queryservers = [server]
            else:
                queryservers = [element for element in servers]

            for server in queryservers:

                api = servers[server]["api"]

                api.update()

                playeritems = [item for item in api.info["players"]["list"].items()]

                playerpergroup = 20

                groupedplayers = [{keyvalue[0]:keyvalue[1] for keyvalue in playeritems[group:group + playerpergroup]} for group in range(0, len(playeritems), playerpergroup)]

                if len(api.info["players"]["list"]) == 0:
                    embedelement = discord.Embed(
                        title=server[0].upper() + server[1:],
                        description="No Players Online",
                        color=servers[server]["color"]
                    )
                    embedelement.set_thumbnail(url=api.info["icon"])
                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

                for pagenumber in range(0, len(groupedplayers)):
                    group = groupedplayers[pagenumber]
                    embedelement = discord.Embed(
                        title=server[0].upper() + server[1:],
                        description="Players {} - {} / {}\nPage {} / {}".format(
                            str(pagenumber * playerpergroup + 1),
                            str(pagenumber * playerpergroup + len(group)),
                            str(len(api.info["players"]["list"])),
                            str(pagenumber + 1),
                            str(len(groupedplayers))
                        ),
                        color=servers[server]["color"]
                    )

                    embedelement.set_thumbnail(url=api.info["icon"])

                    for player in group:
                        if group[player]["nickname"] != None:
                            nick = "{} ({})".format(player, group[player]["nickname"])
                        else:
                            nick = player

                        if group[player]["dimension"] == "Overworld":
                            dimension = "Overworld"
                            fetched = True
                            for axis in group[player]["position"]:
                                if axis == None:
                                    fetched = False
                            if fetched:
                                position = "({}, {}, {})".format(int(group[player]["position"]["x"]), int(group[player]["position"]["y"]), int(group[player]["position"]["z"]))
                            else:
                                position = "Unable to fetch"
                        elif group[player]["dimension"] == "Nether or End":
                            dimension = "Nether or End"
                            position = "Unable to fetch - Player not in Overworld"
                        else:
                            dimension = "Unable to fetch"
                            position = "Unable to fetch - Player not on Dynmap"

                        embedelement.add_field(
                            name=nick,
                            value="Dimension: {}\nPosition: {}".format(dimension, position),
                            inline=False
                        )

                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

        @self.bot.command()
        async def warps(ctx, server=None):
            if server in servers:
                queryservers = [server]
            else:
                queryservers = [element for element in servers]

            for server in queryservers:

                api = servers[server]["api"]

                api.update()

                warpitems = [item for item in api.info["warps"].items()]

                warppergroup = 20

                groupedwarps = [{keyvalue[0]:keyvalue[1] for keyvalue in warpitems[group:group + warppergroup]} for group in range(0, len(warpitems), warppergroup)]

                if len(api.info["warps"]) == 0:
                    embedelement = discord.Embed(
                        title=server[0].upper() + server[1:],
                        description="No Warps on this Server",
                        color=servers[server]["color"]
                    )
                    embedelement.set_thumbnail(url=api.info["icon"])
                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

                for pagenumber in range(0, len(groupedwarps)):
                    group = groupedwarps[pagenumber]
                    embedelement = discord.Embed(
                        title=server[0].upper() + server[1:],
                        description="Warps {} - {} / {}\nPage {} / {}".format(
                            str(pagenumber * warppergroup + 1),
                            str(pagenumber * warppergroup + len(group)),
                            str(len(api.info["warps"])),
                            str(pagenumber + 1),
                            str(len(groupedwarps))
                        ),
                        color=servers[server]["color"]
                    )

                    embedelement.set_thumbnail(url=api.info["icon"])

                    for warp in group:
                        if group[warp]["owner"] != None:
                            owner = group[warp]["owner"]
                        else:
                            owner = "Unable to fetch"
                        
                        if group[warp]["description"] != None:
                            description = group[warp]["description"]

                        fetched = True
                        for axis in group[warp]["position"]:
                            if axis == None:
                                fetched = False
                        if fetched:
                            position = "({}, {}, {})".format(int(group[warp]["position"]["x"]), int(group[warp]["position"]["y"]), int(group[warp]["position"]["z"]))
                        else:
                            position = "Unable to fetch"
                        

                        embedelement.add_field(
                            name=warp,
                            value="Owner: {}\nPosition: {}\nDescription: {}".format(owner, position, description),
                            inline=False
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