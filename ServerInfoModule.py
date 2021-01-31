import requests
import json
import html
import html2text

class Server:
    def __init__(self, ip, dynmapip=False, world=False):
        self.ip = ip
        self.dynmapip = dynmapip
        self.world = world
        self.info = {}
    
    def update(self):
        info = {}

        ping = json.loads(requests.get("https://api.mcsrvstat.us/2/" + self.ip).text)
        sample = json.loads(requests.get("https://api.mcsrvstat.us/ping/" + self.ip).text)

        for element in ["online", "ip", "port", "version", "software"]:
            if element in ping:
                info[element] = ping[element]
            else:
                info[element] = None

        if "motd" in ping:
            info["motd"] = {}
            for element in ["raw", "clean", "html"]:
                if element in ping["motd"]:
                    info["motd"][element] = ping["motd"][element]
                else:
                    info["motd"][element] = [
                        None
                    ]
            if "clean" in ping["motd"]:
                info["motd"]["decoded"] = [html.unescape(line) for line in ping["motd"]["clean"]]
            else:
                info["motd"]["decoded"] = None
        else:
            info["motd"] = {
                "raw": [
                    None
                ],
                "clean": [
                    None
                ],
                "html": [
                    None
                ],
                "decoded": [
                    None
                ]
            }
        
        info["players"] = {}

        if "players" in ping:
            if "uuid" in ping["players"]:
                info["players"]["list"] = {
                    player: {
                        "dimension": None,
                        "position": {
                            "x": None,
                            "y": None,
                            "z": None
                        },
                        "nickname": None
                    } for player in ping["players"]["uuid"]
                }
            else:
                info["players"]["list"] = {}
        else:
            info["players"]["list"] = {}

        for element in sample["players"]:
            if element in ["online", "max"]:
                info["players"][element] = sample["players"][element]
        
        info["icon"] = "https://api.mcsrvstat.us/icon/" + self.ip

        if self.dynmapip != False:
            dynmap = json.loads(requests.get("https://" + self.dynmapip + "/standalone/dynmap_" + self.world + ".json").text)
            if ("hasStorm" in dynmap) and ("isThundering" in dynmap):
                if dynmap["hasStorm"]:
                    if dynmap["isThundering"]:
                        info["weather"] = "Thunderstorm"
                    else:
                        info["weather"] = "Rain"
                else:
                    info["weather"] = "Clear"
            else:
                info["weather"] = None

            if "servertime" in dynmap:
                info["servertime"] = dynmap["servertime"]
            else:
                info["servertime"] = None

            if "players" in dynmap:
                for player in dynmap["players"]:
                    if player["account"] not in info["players"]["list"]:
                        info["players"]["list"][player["account"]] = {
                            "dimension": None,
                            "position": {
                                "x": None,
                                "y": None,
                                "z": None
                            },
                            "nickname": None
                        }
                    if "world" in player:
                        if player["world"] == self.world:
                            info["players"]["list"][player["account"]]["dimension"] = "Overworld"
                            for element in player:
                                if element in ["x", "y", "z"]:
                                    info["players"]["list"][player["account"]]["position"][element] = player[element]
                        else:
                            info["players"]["list"][player["account"]]["dimension"] = "Nether or End"
                            info["players"]["list"][player["account"]]["position"] = {
                                "x": None,
                                "y": None,
                                "z": None
                            }
                    if "name" in player:
                        nickname = html2text.html2text(player["name"]).replace("\n", "")
                        if nickname != player["account"]:
                            info["players"]["list"][player["account"]]["nickname"] = nickname
            
            markers = json.loads(requests.get("https://" + self.dynmapip + "/tiles/_markers_/marker_" + self.world + ".json").text)

            info["warps"] = {}

            if "sets" in markers:
                if "TownWarpsPlugin" in markers["sets"]:
                    if "markers" in markers["sets"]["TownWarpsPlugin"]:
                        
                        warps = markers["sets"]["TownWarpsPlugin"]["markers"]

                        for warp in warps:
                            if "label" in warps[warp]:
                                name = html.unescape(warps[warp]["label"])
                                info["warps"][name] = {
                                    "position": {
                                        "x": None,
                                        "y": None,
                                        "z": None
                                    },
                                    "owner": None,
                                    "description": None
                                }
                                for element in warps[warp]:
                                    if element in ["x", "y", "z"]:
                                        info["warps"][name]["position"][element] = warps[warp][element]
                                    elif element == "desc":
                                        info["warps"][name]["description"] = html.unescape(warps[warp][element]).split("<br />Description: ")[1].replace("<br />", " ")
                                        info["warps"][name]["owner"] = html.unescape(warps[warp][element]).split("<br />Description: ")[0].split("<br />Owner: ")[1]

        else:
            info["weather"] = None
            info["servertime"] = None
            info["warps"] = {}

        self.info = info