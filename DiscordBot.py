import discord
from discord.ext import commands
import os
import datetime
import json
import asyncio
import requests
import json

try:
    from SetEnviron import environ
    environ()
except FileNotFoundError:
    print("SetEnviron file not found. Make sure a .env file is present or environment variables are set instead.")

try:
    import Webserver
except FileNotFoundError:
    print("Webserver file not found. Bot will not be able to stay online nor receive data from the database.")

import FirebaseConnection

staffrole = 653410679424024586

with open("./Commands.json", "r") as reader:
    strcommands = reader.read()

botcommands = json.loads(strcommands)

class MainBot:

    def __init__(self, token):
        self.fetch_notifications()
        self.flaskserver = Webserver.FlaskWebserver(parent=self)
        self.bot = commands.Bot(command_prefix=("-"))
        self.bot.remove_command("help")
        self.token = token
        self.startup = datetime.datetime.now()
        self.define_commands()
        self.event_loop = asyncio.get_event_loop()
        self.bot.run(self.token)

    async def serverupdate(self):
        print("Bot detected project update.")

        channel = self.bot.get_channel(817008411001749555)

        servers = self.flaskserver.servers

        allplayers = {}
        allplayersjoined = {}
        allplayersleft = {}

        for server in servers:
            playerslast = servers[server]["api"].info.get("players", {}).get("cachedlist", {})
            playersnow = servers[server]["api"].infolast.get("players", {}).get("cachedlist", {})
            playersjoined = set(playerslast) - set(playersnow)
            playersleft = set(playersnow) - set(playerslast)
            allplayers.update({player: server for player in playersnow})
            allplayersjoined.update({player: server for player in playersjoined})
            allplayersleft.update({player: server for player in playersleft})

        popnotifications = []

        for notification in self.notifications:

            exception = None
            for attempt in range(3):
                try:
                    rawnames = requests.get("https://api.mojang.com/user/profiles/{}/names".format(self.notifications[notification]["mcuuid"]), timeout=5)
                    statuscode = rawnames.status_code
                    exception = statuscode
                    if statuscode == 200:
                        names = json.loads(rawnames.text)
                        break
                    else:
                        exception = statuscode
                except Exception as e:
                    exception = e

            if exception == 200:

                highesttimestamp = 0

                decrement = False

                for namedict in names:
                    if namedict.get("changedToAt", 1) > highesttimestamp:
                        highesttimestamp = namedict.get("changedToAt", 0)
                        currentname = namedict["name"]
                
                if self.notifications[notification]["server"] == "all":
                    notifserver = [server for server in servers]
                else:
                    notifserver = [self.notifications[notification]["server"]]

                if (currentname in allplayersjoined) and (currentname in allplayersleft) and (self.notifications[notification]["type"] in ["all", "join", "leave"]) and ((allplayersjoined.get(currentname, None) in notifserver) or (allplayersleft.get(currentname, None) in notifserver)):
                    
                    embedelement = discord.Embed(
                        title="Notification",
                        description="Notifies player events",
                        color=discord.Color.orange()
                    )

                    embedelement.add_field(
                        name="Player moved servers",
                        value="**{}** moved from the server **{}** to the server **{}**.".format(currentname, allplayersleft[currentname].capitalize(), allplayersjoined[currentname].capitalize())
                    )

                    user = await self.bot.fetch_user(self.notifications[notification]["dcuser"])

                    await channel.send(
                        content=user.mention,
                        embed=embedelement
                    )

                    decrement = True

                elif (currentname in allplayersjoined) and (self.notifications[notification]["type"] in ["all", "join"]) and (allplayersjoined.get(currentname, None) in notifserver):

                    embedelement = discord.Embed(
                        title="Notification",
                        description="Notifies player events",
                        color=discord.Color.orange()
                    )

                    embedelement.add_field(
                        name="Player joined a server",
                        value="**{}** joined the server **{}**.".format(currentname, allplayersjoined[currentname].capitalize())
                    )

                    user = await self.bot.fetch_user(self.notifications[notification]["dcuser"])

                    await channel.send(
                        content=user.mention,
                        embed=embedelement
                    )          

                    decrement = True
                
                elif (currentname in allplayersleft) and (self.notifications[notification]["type"] in ["all", "leave"]) and (allplayersleft.get(currentname, None) in notifserver):

                    embedelement = discord.Embed(
                        title="Notification",
                        description="Notifies player events",
                        color=discord.Color.orange()
                    )

                    embedelement.add_field(
                        name="Player left a server",
                        value="**{}** left the server **{}**.".format(currentname, allplayersleft[currentname].capitalize())
                    )

                    user = await self.bot.fetch_user(self.notifications[notification]["dcuser"])

                    await channel.send(
                        content=user.mention,
                        embed=embedelement
                    )                    

                    decrement = True

                if decrement:
                    if self.notifications[notification]["amount"] == 1:
                        FirebaseConnection.firebasedelete("notifications", notification)
                        popnotifications.append(notification)
                    elif self.notifications[notification]["amount"] > 1:
                        FirebaseConnection.firebaseincrement("notifications", notification, "amount", -1)
                        self.notifications[notification]["amount"] -= 1

        for notification in popnotifications:
            self.notifications.pop(notification)

    def fetch_notifications(self):
        self.notifications = FirebaseConnection.firebasefetch("notifications")

    def define_commands(self):

        @self.bot.event
        async def on_ready():

            settings = FirebaseConnection.firebasefetch("settings")
            statustype = settings["status"]["statustype"]
            args = settings["status"]["args"]

            if statustype == "playing":
                message = " ".join([arg for arg in args])
                await self.bot.change_presence(activity=discord.Game(name=message))

            elif statustype == "streaming":
                message = " ".join([arg for arg in args[1:]])
                await self.bot.change_presence(activity=discord.Streaming(name=message, url=args[0]))

            elif statustype == "listening":
                message = " ".join([arg for arg in args])
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=message))

            elif statustype == "watching":
                message = " ".join([arg for arg in args])
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=message))

            print("Bot is ready.")

        @self.bot.command()
        async def ping(ctx):
            embedelement = discord.Embed(
                title="Ping Command",
                description="Sends a message back to the author",
                color=discord.Color.teal()
            )
            embedelement.add_field(
                name="Pinged by {}".format(ctx.message.author.display_name),
                value="Pong!",
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
            for project in self.flaskserver.updatedprojects:
                text = "Description: {}\nEstimate Time Completion: {}".format(str(self.flaskserver.updatedprojects[project]["description"]), str(self.flaskserver.updatedprojects[project]["estimated-time"].strftime("%b %d %Y")))
                embedelement.add_field(
                    name=str(self.flaskserver.updatedprojects[project]["name"]),
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

            if statustype == "playing":
                message = " ".join([arg for arg in args])
                await self.bot.change_presence(activity=discord.Game(name=message))

            elif statustype == "streaming":
                message = " ".join([arg for arg in args[1:]])
                await self.bot.change_presence(activity=discord.Streaming(name=message, url=args[0]))

            elif statustype == "listening":
                message = " ".join([arg for arg in args])
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=message))

            elif statustype == "watching":
                message = " ".join([arg for arg in args])
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=message))
                
            else:
                embedelement = discord.Embed(
                    title="Status Command",
                    description="Changes the Skytec City bot status",
                    color=discord.Color.blue()
                )
                embedelement.add_field(
                    name="Status was not changed",
                    value="Invalid Status Type [{}]. Please choose from [playing/watching/listening/streaming].".format(statustype),
                    inline=False
                )
                await ctx.channel.send(
                    content=None,
                    embed=embedelement
                )
                return

            FirebaseConnection.firebasenew("settings", "status",
                {
                    "statustype": statustype,
                    "args": [arg for arg in args]
                }
            )

            embedelement = discord.Embed(
                title="Status Command",
                description="Changes the Skytec City bot status",
                color=discord.Color.blue()
            )

            if statustype == "streaming":
                embedelement.add_field(
                    name="Status changed by {}".format(ctx.message.author.display_name),
                    value="Status changed to type [{}] with url [{}] with message [{}].".format(statustype, args[0], message),
                    inline=False
                )
            else:
                embedelement.add_field(
                    name="Status changed by {}".format(ctx.message.author.display_name),
                    value="Status changed to type [{}] with message [{}].".format(statustype, message),
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
                value="Skytec City bot is now shutting down for maintenance.",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )
            print("Server killed by: {}.".format(ctx.message.author.name))
            await self.bot.logout()

        @self.bot.command()
        @commands.has_any_role(staffrole)
        async def clear(ctx, amount=1):
            if amount < 100:
                await ctx.channel.purge(limit=amount + 1)

        @self.bot.command()
        async def uptime(ctx):

            difference = datetime.datetime.now() - self.startup

            seconds = difference.seconds

            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)

            embedelement = discord.Embed(
                title="Uptime Command",
                description="Tells uptime information",
                color=discord.Color.gold()
            )
            embedelement.add_field(
                name="Startup Time",
                value=self.startup.strftime("%b %d %Y %H:%M:%S"),
                inline=False
            )
            embedelement.add_field(
                name="Time Elapsed",
                value=f"{days} Days {hours} Hours {minutes} Minutes {seconds} Seconds",
                inline=False
            )
            await ctx.channel.send(
                content=None,
                embed=embedelement
            )

        @self.bot.command()
        async def server(ctx, server=None):

            if server in self.flaskserver.servers:
                queryservers = [server]
            else:
                queryservers = [element for element in self.flaskserver.servers]

            for server in queryservers:

                api = self.flaskserver.servers[server]["api"]

                embedelement = discord.Embed(
                    title=server.capitalize(),
                    description="```{}```".format(
                        api.info.get(
                            "motd", {}
                            ).get(
                                "decoded", "Unable to fetch MOTD"
                                )),
                    color=self.flaskserver.servers[server]["color"]
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
                
                embedelement.add_field(
                    name="Version",
                    value=api.info.get("version", {}).get("decoded", "Unable to fetch")
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

                embedelement.set_thumbnail(url=api.info.get("icon", ""))

                await ctx.channel.send(
                    content=None,
                    embed=embedelement
                )

        @self.bot.command()
        async def players(ctx, server=None):
            if server in self.flaskserver.servers:
                queryservers = [server]
            else:
                queryservers = [element for element in self.flaskserver.servers]

            for server in queryservers:

                api = self.flaskserver.servers[server]["api"]

                playeritems = [item for item in api.info["players"]["cachedlist"].items()]

                playerpergroup = 20

                groupedplayers = [{keyvalue[0]:keyvalue[1] for keyvalue in playeritems[group:group + playerpergroup]} for group in range(0, len(playeritems), playerpergroup)]

                if len(api.info["players"]["cachedlist"]) == 0:
                    
                    if api.info.get("pingexception", None) != 200 or (api.info.get("dynmapexception", None) != 200 and api.dynmapip != False):
                        embedelement = discord.Embed(
                            title=server.capitalize(),
                            description="Unable to fetch Players - Error:\nPing - {}\nDynmap - {}".format(
                                str(api.info.get("pingexception", "No error message given")),
                                str(api.info.get("dynmapexception", "No error message given"))
                                ),
                            color=self.flaskserver.servers[server]["color"]
                        )
                    else:
                        embedelement = discord.Embed(
                            title=server.capitalize(),
                            description="No Players Online",
                            color=self.flaskserver.servers[server]["color"]
                        )
                    embedelement.set_thumbnail(url=api.info.get("icon", ""))
                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

                for pagenumber in range(0, len(groupedplayers)):
                    group = groupedplayers[pagenumber]
                    embedelement = discord.Embed(
                        title=server.capitalize(),
                        description="Players {} - {} / {}\nPage {} / {}".format(
                            str(pagenumber * playerpergroup + 1),
                            str(pagenumber * playerpergroup + len(group)),
                            str(len(api.info["players"]["cachedlist"])),
                            str(pagenumber + 1),
                            str(len(groupedplayers))
                        ),
                        color=self.flaskserver.servers[server]["color"]
                    )

                    embedelement.set_thumbnail(url=api.info.get("icon", ""))

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
                            value="**Dimension:** {}\n**Position:** {}".format(group[player].get("dimension", "Unable to fetch - Player not on Dynmap"), position),
                            inline=False
                        )

                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

        @self.bot.command()
        async def warps(ctx, server=None):
            if server in self.flaskserver.servers:
                queryservers = [server]
            else:
                queryservers = [element for element in self.flaskserver.servers]

            for server in queryservers:

                api = self.flaskserver.servers[server]["api"]

                warpitems = [item for item in api.info["warps"].items()]

                warppergroup = 20

                groupedwarps = [{keyvalue[0]:keyvalue[1] for keyvalue in warpitems[group:group + warppergroup]} for group in range(0, len(warpitems), warppergroup)]
                
                if len(api.info["warps"]) == 0:
                    if api.dynmapip != False:
                        if api.info.get("markersexception", None) == 200:
                            embedelement = discord.Embed(
                                title=server.capitalize(),
                                description="No Warps on this Server",
                                color=self.flaskserver.servers[server]["color"]
                            )
                        else:
                            embedelement = discord.Embed(
                                title=server.capitalize(),
                                description="Unable to fetch Warps - Error: {}".format(str(api.info.get("markersexception", "No error message given"))),
                                color=self.flaskserver.servers[server]["color"]
                            )
                        embedelement.set_thumbnail(url=api.info.get("icon", ""))
                        await ctx.channel.send(
                            content=None,
                            embed=embedelement
                        )
                    elif len(queryservers) == 1:
                        embedelement = discord.Embed(
                            title=server.capitalize(),
                            description="Warps are not enabled on this Server",
                            color=self.flaskserver.servers[server]["color"]
                        )
                        embedelement.set_thumbnail(url=api.info.get("icon", ""))
                        await ctx.channel.send(
                            content=None,
                            embed=embedelement
                        )

                for pagenumber in range(0, len(groupedwarps)):
                    group = groupedwarps[pagenumber]
                    embedelement = discord.Embed(
                        title=server.capitalize(),
                        description="Warps {} - {} / {}\nPage {} / {}".format(
                            str(pagenumber * warppergroup + 1),
                            str(pagenumber * warppergroup + len(group)),
                            str(len(api.info["warps"])),
                            str(pagenumber + 1),
                            str(len(groupedwarps))
                        ),
                        color=self.flaskserver.servers[server]["color"]
                    )

                    embedelement.set_thumbnail(url=api.info.get("icon", ""))

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
        async def playernotify(ctx, username, notiftype, amount, server):
            exception = None
            for attempt in range(3):
                try:
                    rawuuid = requests.get("https://api.mojang.com/users/profiles/minecraft/" + username, timeout=5)
                    statuscode = rawuuid.status_code
                    exception = statuscode
                    if statuscode == 200:
                        uuiddict = json.loads(rawuuid.text)
                        uuid = uuiddict["id"]
                        break
                    else:
                        exception = statuscode
                except Exception as e:
                    exception = e
            if notiftype in ["all", "join", "leave"]:
                try:
                    amount = int(amount)
                    if amount >= 0:
                        if (server in self.flaskserver.servers) or (server == "all"):
                            if exception == 200:

                                data = {
                                    "dcuser": str(ctx.message.author.id),
                                    "mcuuid": uuid,
                                    "type": notiftype,
                                    "amount": amount,
                                    "server": server
                                }
                                docid = FirebaseConnection.firebasenew("notifications", None, data)
                                self.notifications.update({docid: data})

                                if notiftype == "all":
                                    when = "**joins or leaves**"
                                else:
                                    when = "**{}**".format(notiftype)

                                if amount == 0:
                                    times = "**every time**"
                                elif amount == 1:
                                    times = "**once**"
                                else:
                                    times = "up to **{} times**".format(amount)

                                if server == "all":
                                    where = "**any** server"
                                else:
                                    where = "the server **{}**".format(server.capitalize())

                                embedelement = discord.Embed(
                                    title="Notification Command",
                                    description="Create a player notification",
                                    color=discord.Color.dark_orange()
                                )

                                embedelement.add_field(
                                    name="Notification successfully created",
                                    value="Notifying {} when **{}** {} {} {}.".format(ctx.message.author.mention, username, when, where, times)
                                )

                                await ctx.channel.send(
                                    content=None,
                                    embed=embedelement
                                )
                                

                            elif exception == 204:

                                embedelement = discord.Embed(
                                    title="Notification Command",
                                    description="Create a player notification",
                                    color=discord.Color.dark_orange()
                                )

                                embedelement.add_field(
                                    name="Notification was not created",
                                    value="Player [{}] does not exist.".format(username)
                                )

                                await ctx.channel.send(
                                    content=None,
                                    embed=embedelement
                                )

                            else:

                                embedelement = discord.Embed(
                                    title="Notification Command",
                                    description="Create a player notification",
                                    color=discord.Color.dark_orange()
                                )

                                embedelement.add_field(
                                    name="Notification was not created",
                                    value="Error - " + str(exception)
                                )

                                await ctx.channel.send(
                                    content=None,
                                    embed=embedelement
                                )
                        else:

                            embedelement = discord.Embed(
                                title="Notification Command",
                                description="Create a player notification",
                                color=discord.Color.dark_orange()
                            )

                            embedelement.add_field(
                                name="Notification was not created",
                                value="Invalid server [{}]. Please choose from [{}].".format(server, "/".join([server for server in self.flaskserver.servers]))
                            )

                            await ctx.channel.send(
                                content=None,
                                embed=embedelement
                            )
                        
                    else:

                        embedelement = discord.Embed(
                            title="Notification Command",
                            description="Create a player notification",
                            color=discord.Color.dark_orange()
                        )

                        embedelement.add_field(
                            name="Notification was not created",
                            value="Invalid amount [{}]. Amount must be 0 or larger.".format(amount)
                        )

                        await ctx.channel.send(
                            content=None,
                            embed=embedelement
                        )               

                except ValueError:

                    embedelement = discord.Embed(
                        title="Notification Command",
                        description="Create a player notification",
                        color=discord.Color.dark_orange()
                    )

                    embedelement.add_field(
                        name="Notification was not created",
                        value="Invalid amount [{}]. Amount must be an integer.".format(amount)
                    )

                    await ctx.channel.send(
                        content=None,
                        embed=embedelement
                    )

            else:

                embedelement = discord.Embed(
                    title="Notification Command",
                    description="Create a player notification",
                    color=discord.Color.dark_orange()
                )

                embedelement.add_field(
                    name="Notification was not created",
                    value="Invalid notification type [{}]. Please choose from [all/join/leave].".format(notiftype)
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
    main_bot.flaskserver.kill()