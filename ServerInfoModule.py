import requests
import json
import html
import html2text

class Server:
    def __init__(self, ip, dynmapip=False, world=False):
        self.ip = ip
        self.dynmapip = dynmapip
        self.world = world
        self.info = {
            "players": {},
            "warps": {}
        }
    
    def update(self):
        info = {}

        for attempt in range(3):
            ping = {
                "pingstatuscode": None,
                "pingexception": None
            }
            try:
                rawping = requests.get("https://api.mcsrvstat.us/2/" + self.ip, timeout=5)
                ping["pingstatuscode"] = rawping.status_code
                ping["pingexception"] = rawping.status_code
                if rawping.status_code == 200:
                    ping.update(json.loads(rawping.text))
                    if not ping.get("online", False):
                        ping["pingexception"] = "Server offline"
                    print("[Ping] On updating {}: Success - 200".format(self.ip))
                    break
                else:
                    print("[Ping] On updating {}: Error - {}".format(self.ip, rawping.status_code))
            except Exception as e:
                ping["pingexception"] = e
                print("[Ping] On updating {}: Error - {}".format(self.ip, e))

        for attempt in range(3):
            sample = {
                "samplestatuscode": None,
                "sampleexception": None
            }
            try:
                rawsample = requests.get("https://api.mcsrvstat.us/ping/" + self.ip, timeout=5)
                sample["samplestatuscode"] = rawsample.status_code
                sample["sampleexception"] = rawsample.status_code
                if rawsample.status_code == 200:
                    sample.update(json.loads(rawsample.text))
                    print("[Sample] On updating {}: Success - 200".format(self.ip))
                    break
                else:
                    print("[Sample] On updating {}: Error - {}".format(self.ip, rawsample.status_code))
            except Exception as e:
                sample["sampleexception"] = e
                print("[Sample] On updating {}: Error - {}".format(self.ip, e))
            if ping["pingexception"] == "Server offline":
                sample["sampleexception"] = "Server offline"

        for element in ping:
            if element not in ["players"]:
                info[element] = ping[element]

        if "motd" in ping:
            info["motd"] = {}
            for element in ping["motd"]:
                info["motd"][element] = ping["motd"][element]
            if "clean" in ping["motd"]:
                info["motd"]["decoded"] = [html.unescape(line) for line in ping["motd"]["clean"]]

        info["players"] = {}

        if "players" in sample:
            for element in sample["players"]:
                info["players"][element] = sample["players"][element]

        if "players" in ping:
            if "uuid" in ping["players"]:
                info["players"]["list"] = {
                    player: {"type": ["Sample"]} for player in ping["players"]["uuid"]
                }
            else:
                info["players"]["list"] = {}
        else:
            info["players"]["list"] = {}
        
        info["icon"] = "https://api.mcsrvstat.us/icon/" + self.ip

        info["warps"] = {}

        if self.dynmapip != False:

            for attempt in range(3):
                dynmap = {
                    "dynmapstatuscode": None,
                    "dynmapexception": None
                }
                try:
                    rawdynmap = requests.get("https://" + self.dynmapip + "/standalone/dynmap_" + self.world + ".json", timeout=5)
                    dynmap["dynmapstatuscode"] = rawdynmap.status_code
                    dynmap["dynmapexception"] = rawdynmap.status_code
                    if rawdynmap.status_code == 200:
                        dynmap.update(json.loads(rawdynmap.text))
                        print("[Dynmap] On updating {}: Success - 200".format(self.ip))
                        break
                    else:
                        print("[Dynmap] On updating {}: Error - {}".format(self.ip, rawdynmap.status_code))
                except Exception as e:
                    dynmap["dynmapexception"] = e
                    print("[Dynmap] On updating {}: Error - {}".format(self.ip, e))

            for element in dynmap:
                if element not in ["hasStorm", "isThundering", "players"]:
                    info[element] = dynmap[element]

            if ("hasStorm" in dynmap) and ("isThundering" in dynmap):
                if dynmap["hasStorm"]:
                    if dynmap["isThundering"]:
                        info["weather"] = "Thunderstorm"
                    else:
                        info["weather"] = "Rain"
                else:
                    info["weather"] = "Clear"

            if "players" in dynmap:
                for player in dynmap["players"]:
                    if player["account"] in info["players"]["list"]:
                        info["players"]["list"][player["account"]]["type"].append("Dynmap")
                    else:
                        info["players"]["list"][player["account"]] = {"type": ["Dynmap"]}
                    if "world" in player:
                        if player["world"] == self.world:
                            for element in player:
                                info["players"]["list"][player["account"]][element] = player[element]
                            info["players"]["list"][player["account"]]["dimension"] = "Overworld"
                        else:
                            info["players"]["list"][player["account"]]["dimension"] = "Nether or End"
                    if "name" in player:
                        nickname = html2text.html2text(player["name"]).replace("\n", "")
                        if nickname != player["account"]:
                            info["players"]["list"][player["account"]]["nickname"] = nickname

            for attempt in range(3):
                markers = {
                    "markersstatuscode": None,
                    "markersexception": None
                }
                try:
                    rawmarkers = requests.get("https://" + self.dynmapip + "/tiles/_markers_/marker_" + self.world + ".json", timeout=5)
                    markers["markersstatuscode"] = rawmarkers.status_code
                    markers["markersexception"] = rawmarkers.status_code
                    if rawmarkers.status_code == 200:
                        markers.update(json.loads(rawmarkers.text))
                        print("[Markers] On updating {}: Success - 200".format(self.ip))
                        break
                    else:
                        print("[Markers] On updating {}: Error - {}".format(self.ip, rawmarkers.status_code))
                except Exception as e:
                    markers["markersexception"] = e
                    print("[Markers] On updating {}: Error - {}".format(self.ip, e))

            for element in markers:
                if element not in ["sets"]:
                    info[element] = markers[element]

            if "sets" in markers:
                if "TownWarpsPlugin" in markers["sets"]:
                    if "markers" in markers["sets"]["TownWarpsPlugin"]:
                        
                        warps = markers["sets"]["TownWarpsPlugin"]["markers"]

                        for warp in warps:
                            if "label" in warps[warp]:
                                name = html.unescape(warps[warp]["label"])
                                info["warps"][name] = {}
                                for element in warps[warp]:
                                    if element not in ["desc"]:
                                        info["warps"][name][element] = warps[warp][element]
                                    elif element == "desc":
                                        info["warps"][name]["description"] = html.unescape(warps[warp][element]).split("<br />Description: ")[1].replace("<br />", " ")
                                        info["warps"][name]["owner"] = html.unescape(warps[warp][element]).split("<br />Description: ")[0].split("<br />Owner: ")[1]

        self.infolast = self.info
        self.info = info
