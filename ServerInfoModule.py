import requests
import json
import html
import html2text
import mcstatus
import copy

class Server:
    def __init__(self, ip, pl3xmapip=False, world=False):
        self.ip = ip
        self.pl3xmapip = pl3xmapip
        self.world = world
        self.info = {
            "players": {},
            "warps": {}
        }
    
    def update(self):
        info = {}

        for attempt in range(3):
            ping = {
                "pingexception": None
            }
            try:
                rawping = mcstatus.MinecraftServer.lookup(self.ip)
                ping = rawping.status().raw
                ping["pingexception"] = 200
                print("[Ping] On updating {}: Success".format(self.ip))
                break
            except Exception as e:
                ping["pingexception"] = e
                print("[Ping] On updating {}: Error - {}".format(self.ip, e))

        for element in ping:
            if element not in ["players"]:
                info[element] = ping[element]

        if "version" in ping:
            info["version"]["decoded"] = "".join([strip[1:] for strip in list(filter(("§").__ne__, ping["version"].get("name", "").split("§")))])

        if "description" in ping:
            info["motd"] = {
                "raw": ping["description"],
                "decoded": "".join([string.get("text", "") for string in ping["description"].get("extra", {})])
            }

        info["players"] = {
            "list": {}
        }

        for element in ping.get("players", {}):
            if element not in ["sample"]:
                info["players"][element] = ping["players"][element]
            elif element == "sample":
                info["players"]["list"] = {
                    player.get("name", ""): {
                        "type": ["Sample"],
                        "uuid": player.get("id", "")
                    } for player in ping["players"]["sample"]
                }
        
        info["icon"] = "https://api.mcsrvstat.us/icon/" + self.ip

        info["warps"] = {}

        if self.pl3xmapip != False:

            for attempt in range(3):
                pl3xmap = {
                    "pl3xmapstatuscode": None,
                    "pl3xmapexception": None
                }
                try:
                    rawpl3xmap = requests.get("https://" + self.pl3xmapip + "/tiles/players.json", timeout=5)
                    pl3xmap["pl3xmapstatuscode"] = rawpl3xmap.status_code
                    pl3xmap["pl3xmapexception"] = rawpl3xmap.status_code
                    if rawpl3xmap.status_code == 200:
                        pl3xmap.update(json.loads(rawpl3xmap.text))
                        print("[Pl3xmap] On updating {}: Success - 200".format(self.ip))
                        break
                    else:
                        print("[Pl3xmap] On updating {}: Error - {}".format(self.ip, rawpl3xmap.status_code))
                except Exception as e:
                    pl3xmap["pl3xmapexception"] = e
                    print("[Pl3xmap] On updating {}: Error - {}".format(self.ip, e))

            for element in pl3xmap:
                if element not in ["hasStorm", "isThundering", "players"]:
                    info[element] = pl3xmap[element]

            # if ("hasStorm" in pl3xmap) and ("isThundering" in pl3xmap):
            #     if pl3xmap["hasStorm"]:
            #         if pl3xmap["isThundering"]:
            #             info["weather"] = "Thunderstorm"
            #         else:
            #             info["weather"] = "Rain"
            #     else:
            #         info["weather"] = "Clear"

            if "players" in pl3xmap:
                for player in pl3xmap["players"]:
                    if player["name"] in info["players"]["list"]:
                        info["players"]["list"][player["name"]]["type"].append("Pl3xmap")
                    else:
                        info["players"]["list"][player["name"]] = {"type": ["Pl3xmap"]}
                    if "world" in player:
                        if player["world"] == self.world:
                            for element in player:
                                info["players"]["list"][player["name"]][element] = player[element]
                            info["players"]["list"][player["name"]]["dimension"] = "Overworld"
                        elif player["world"] == self.world + "_nether":
                            for element in player:
                                info["players"]["list"][player["name"]][element] = player[element]
                            info["players"]["list"][player["name"]]["dimension"] = "Nether"
                        else:
                            info["players"]["list"][player["name"]]["dimension"] = "End"
                    if "name" in player:
                        nickname = html2text.html2text(player["name"]).replace("\n", "")
                        if nickname != player["name"]:
                            info["players"]["list"][player["name"]]["nickname"] = nickname

            for attempt in range(3):
                markers = {
                    "markersstatuscode": None,
                    "markersexception": None
                }
                try:
                    rawmarkers = requests.get("https://" + self.pl3xmapip + "/tiles/" + self.world + "/markers.json", timeout=5)
                    markers["markersstatuscode"] = rawmarkers.status_code
                    markers["markersexception"] = rawmarkers.status_code
                    if rawmarkers.status_code == 200:
                        markers["content"] = json.loads(rawmarkers.text)
                        print("[Markers Overworld] On updating {}: Success - 200".format(self.ip))
                        break
                    else:
                        print("[Markers Overworld] On updating {}: Error - {}".format(self.ip, rawmarkers.status_code))
                except Exception as e:
                    markers["markersexception"] = e
                    print("[Markers Overworld] On updating {}: Error - {}".format(self.ip, e))

            for element in markers["content"]:
                if element.get("name", "") == "TownWarps":
                    if "markers" in element:
                        warps = element["markers"]

                        for warp in warps:
                            name = html.unescape(warp.get("tooltip", "").replace("<span style=\"font-weight:bold;\">", "").replace("</span>", "").replace("<br>", ""))
                            info["warps"][name] = {"dimension": "Overworld"}
                            for element in warp:
                                if element not in ["popup", "point"]:
                                    info["warps"][name][element] = warp[element]
                                elif element == "popup":
                                    info["warps"][name]["description"] = "".join(html.unescape(warp[element]).split("<span style=\"font-weight:bold;\">")[2:]).replace("</span>", "").replace("<br>", "")
                                elif element == "point":
                                    for axis in warp["point"]:
                                        info["warps"][name][axis] = warp["point"][axis]
            
            for attempt in range(3):
                markers.update({
                    "nethermarkersstatuscode": None,
                    "nethermarkersexception": None
                })
                try:
                    rawmarkers = requests.get("https://" + self.pl3xmapip + "/tiles/" + self.world + "_nether/markers.json", timeout=5)
                    markers["nethermarkersstatuscode"] = rawmarkers.status_code
                    markers["nethermarkersexception"] = rawmarkers.status_code
                    if rawmarkers.status_code == 200:
                        markers["content"] = json.loads(rawmarkers.text)
                        print("[Markers Nether] On updating {}: Success - 200".format(self.ip))
                        break
                    else:
                        print("[Markers Nether] On updating {}: Error - {}".format(self.ip, rawmarkers.status_code))
                except Exception as e:
                    markers["nethermarkersexception"] = e
                    print("[Markers Nether] On updating {}: Error - {}".format(self.ip, e))

            for element in markers["content"]:
                if element.get("name", "") == "TownWarps":
                    if "markers" in element:
                        warps = element["markers"]

                        for warp in warps:
                            name = html.unescape(warp.get("tooltip", "").replace("<span style=\"font-weight:bold;\">", "").replace("</span>", "").replace("<br>", ""))
                            info["warps"][name] = {"dimension": "Nether"}
                            for element in warp:
                                if element not in ["popup", "point"]:
                                    info["warps"][name][element] = warp[element]
                                elif element == "popup":
                                    info["warps"][name]["description"] = "".join(html.unescape(warp[element]).split("<span style=\"font-weight:bold;\">")[2:]).replace("</span>", "").replace("<br>", "")
                                elif element == "point":
                                    for axis in warp["point"]:
                                        info["warps"][name][axis] = warp["point"][axis]

        info["players"]["cachedlist"] = copy.deepcopy(info["players"]["list"])

        self.infolast = self.info
        self.info = info
