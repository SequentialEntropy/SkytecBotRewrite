import discord
from discord.ext import commands
import os
import datetime

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
            await self.bot.change_presence(activity=discord.Activity(name="Bot Maintenance", type=discord.ActivityType.playing))
            #await self.bot.change_presence(activity=discord.Streaming(name="Bot Maintenance", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

        @self.bot.command()
        async def ping(ctx):
            embedelement = discord.Embed(
                title="Ping Command",
                description="Sends a message back to the author",
                color=discord.Color.teal()
            )
            embedelement.add_field(
                name="Pinged by {}".format(ctx.message.author.display_name),
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
                    value="Invalid Status Type [{}] Please choose from [Playing/Watching/Listening/Streaming/Custom]".format(statustype),
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
                name="Status changed by {}".format(ctx.message.author.display_name),
                value="Status changed to type [{}] with message [{}]".format(statustype, message),
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
                name="Skytec City bot killed by {}".format(ctx.message.author.display_name),
                value="Skytec City bot is now shutting down for maintenance",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )
            print("Server killed by: {}.".format(ctx.message.author.name))
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
                value="Skytec City bot started up on [{}]".format(self.startup.strftime("%b %d %Y %H:%M:%S")),
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )

        @self.bot.command()
        async def server(ctx, server=None):

            if server in Webserver.servers:
                queryservers = [server]
            else:
                queryservers = [element for element in Webserver.servers]

            for server in queryservers:

                api = Webserver.servers[server]["api"]

                embedelement = discord.Embed(
                    title="{}{}".format(server[0].upper(), server[1:]),
                    description="```{}```".format(
                        "\n".join(
                        api.info.get(
                            "motd", {}
                            ).get(
                                "decoded", ["Unable to fetch MOTD"]
                                ))),
                    color=Webserver.servers[server]["color"]
                )

                if ("ip" in api.info) and ("port" in api.info):
                    embedelement.add_field(
                        name="Address",
                        value="{}:{}".format(api.info["ip"], str(api.info["port"]))
                    )
                else:
                    embedelement.add_field(
                        name="Address",
                        value="Unable to fetch"
                    )
                
                if "software" in api.info:
                    embedelement.add_field(
                        name="Version",
                        value="{} ({})".format(api.info.get("version", "Unable to fetch"), api.info["software"])
                    )
                else:
                    embedelement.add_field(
                        name="Version",
                        value=api.info.get("version", "Unable to fetch")
                    )

                embedelement.add_field(
                    name="Players",
                    value="{} / {}".format(str(api.info["players"].get("online", "Unable to fetch")), str(api.info["players"].get("max", "Unable to fetch")))
                )

                if api.dynmapip != False:
                    embedelement.add_field(
                        name="Server Time",
                        value=str(api.info.get("servertime", "Unable to fetch"))
                    )
                    embedelement.add_field(
                        name="Weather",
                        value=str(api.info.get("weather", "Unable to fetch"))
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
            if server in Webserver.servers:
                queryservers = [server]
            else:
                queryservers = [element for element in Webserver.servers]

            for server in queryservers:

                api = Webserver.servers[server]["api"]

                playeritems = [item for item in api.info["players"]["list"].items()]

                playerpergroup = 20

                groupedplayers = [{keyvalue[0]:keyvalue[1] for keyvalue in playeritems[group:group + playerpergroup]} for group in range(0, len(playeritems), playerpergroup)]

                if len(api.info["players"]["list"]) == 0:
                    
                    if api.info.get("pingexception", None) != 200 or (api.info.get("dynmapexception", None) != 200 and api.dynmapip != False):
                        embedelement = discord.Embed(
                            title="{}{}".format(server[0].upper(), server[1:]),
                            description="Unable to fetch Players - Error:\nPing - {}\nDynmap - {}".format(
                                str(api.info.get("pingexception", "No error message given")),
                                str(api.info.get("dynmapexception", "No error message given"))
                                ),
                            color=Webserver.servers[server]["color"]
                        )
                    else:
                        embedelement = discord.Embed(
                            title="{}{}".format(server[0].upper(), server[1:]),
                            description="No Players Online",
                            color=Webserver.servers[server]["color"]
                        )
                    embedelement.set_thumbnail(url=api.info["icon"])
                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

                for pagenumber in range(0, len(groupedplayers)):
                    group = groupedplayers[pagenumber]
                    embedelement = discord.Embed(
                        title="{}{}".format(server[0].upper(), server[1:]),
                        description="Players {} - {} / {}\nPage {} / {}".format(
                            str(pagenumber * playerpergroup + 1),
                            str(pagenumber * playerpergroup + len(group)),
                            str(len(api.info["players"]["list"])),
                            str(pagenumber + 1),
                            str(len(groupedplayers))
                        ),
                        color=Webserver.servers[server]["color"]
                    )

                    embedelement.set_thumbnail(url=api.info["icon"])

                    for player in group:
                        if "nickname" in group[player]:
                            nick = "{} ({})".format(player.replace("_", "\_"), group[player]["nickname"].replace("_", "\_"))
                        else:
                            nick = player.replace("_", "\_")

                        if "dimension" in group[player]:
                            if group[player]["dimension"] == "Overworld":
                                position = "(X: {}, Y: {}, Z: {})".format(int(group[player].get("x", "Unable to fetch")), int(group[player].get("y", "Unable to fetch")), int(group[player].get("z", "Unable to fetch")))
                            else:
                                position = "Unable to fetch - Player not in Overworld"
                        else:
                            position = "Unable to fetch - Player not on Dynmap"

                        embedelement.add_field(
                            name=nick,
                            value="**Dimension:** {}\n**Position:** {}".format(group[player].get("dimension", "Unable to fetch"), position),
                            inline=False
                        )

                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

        @self.bot.command()
        async def warps(ctx, server=None):
            if server in Webserver.servers:
                queryservers = [server]
            else:
                queryservers = [element for element in Webserver.servers]

            for server in queryservers:

                api = Webserver.servers[server]["api"]

                warpitems = [item for item in api.info["warps"].items()]

                warppergroup = 20

                groupedwarps = [{keyvalue[0]:keyvalue[1] for keyvalue in warpitems[group:group + warppergroup]} for group in range(0, len(warpitems), warppergroup)]
                
                if len(api.info["warps"]) == 0:
                    if api.dynmapip != False:
                        if api.info.get("markersexception", None) == 200:
                            embedelement = discord.Embed(
                                title="{}{}".format(server[0].upper(), server[1:]),
                                description="No Warps on this Server",
                                color=Webserver.servers[server]["color"]
                            )
                        else:
                            embedelement = discord.Embed(
                                title="{}{}".format(server[0].upper(), server[1:]),
                                description="Unable to fetch Warps - Error: {}".format(str(api.info.get("markersexception", "No error message given"))),
                                color=Webserver.servers[server]["color"]
                            )
                        embedelement.set_thumbnail(url=api.info["icon"])
                        await ctx.channel.send(
                            content=None,
                            embed=embedelement
                        )
                    elif len(queryservers) == 1:
                        embedelement = discord.Embed(
                            title="{}{}".format(server[0].upper(), server[1:]),
                            description="Warps are not enabled on this Server",
                            color=Webserver.servers[server]["color"]
                        )
                        embedelement.set_thumbnail(url=api.info["icon"])
                        await ctx.channel.send(
                            content=None,
                            embed=embedelement
                        )

                for pagenumber in range(0, len(groupedwarps)):
                    group = groupedwarps[pagenumber]
                    embedelement = discord.Embed(
                        title="{}{}".format(server[0].upper(), server[1:]),
                        description="Warps {} - {} / {}\nPage {} / {}".format(
                            str(pagenumber * warppergroup + 1),
                            str(pagenumber * warppergroup + len(group)),
                            str(len(api.info["warps"])),
                            str(pagenumber + 1),
                            str(len(groupedwarps))
                        ),
                        color=Webserver.servers[server]["color"]
                    )

                    embedelement.set_thumbnail(url=api.info["icon"])

                    for warp in group:
                        embedelement.add_field(
                            name=warp,
                            value="**Owner:** {}\n**Position:** {}\n**Description:** {}".format(
                                group[warp].get("owner", "Unable to fetch").replace("_", "\_"),
                                "(X: {}, Y: {}, Z: {})".format(int(group[warp].get("x", "Unable to fetch")), int(group[warp].get("y", "Unable to fetch")), int(group[warp].get("z", "Unable to fetch"))),
                                group[warp].get("description", "Unable to fetch")
                                ),
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