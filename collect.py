from os import path
import datetime
import re
from enum import Enum
import tailer

from hslog import LogParser
from hslog.export import FriendlyPlayerExporter
from libs.hslog_exporters import LastTurnExporter

from _thread import start_new_thread
from threading import Lock

from libs import screen
from libs.template import create_battlefield
import subprocess


class Position(Enum):
    FATAL_ERROR = -1
    UNKNOWN = 0
    HUB = 1
    ADVENTURE = 2
    DRAFT = 3
    TAVERN_BRAWL = 4
    COLLECTIONMANAGER = 5
    PACKOPENING = 5
    GAMEPLAY = 6
    ARENA = 7
    TOURNAMENT = 8

class Game:
    position = Position.UNKNOWN
    path = None
    regex_loading = re.compile(r"LoadingScreen.OnSceneUnloaded\(\) - prevMode=.* nextMode=(.*) ")

    def __init__(self, log_path):
        self.thread = None
        self.path = log_path
        self.collector = BaseCollector()
        self.lock = Lock()
        self.p = None


    def get_position(self, lines):
        """ set self.position and returns true if the position is new"""
        for line in reversed(lines):
            match = self.regex_loading.search(line)
            if(match and self.position != Position[match.group(1)]):
                self.position = Position[match.group(1)]
                return True ## new position true
        return False ## not a new position

    def set_collector(self):
        if(self.position is Position.ARENA):
            self.collector = ArenaCollector(self)
        elif(self.position is Position.GAMEPLAY):
            self.collector = BattlefieldCollector(self)
        else:
            self.collector = BaseCollector()

    def show_img(self, path):
        if(self.p):
            self.p.terminate()
            self.p.wait()
        self.p = subprocess.Popen(["python3", "labelImg/labelImg.py", path])

    def run(self):
        ## get current position
        with open(path.join(self.path, "LoadingScreen.log")) as f:
            if self.get_position(f.readlines()):
                self.set_collector()

        start_new_thread(self.run_collector, ())

        # watch file
        for line in tailer.follow(open(path.join(self.path, "LoadingScreen.log"))):
            if self.get_position([line]):
                self.lock.acquire()
                self.set_collector()
                self.lock.release()

    def run_collector(self):
        while(True):
            self.lock.acquire()
            self.collector.run()
            self.lock.release()


class BaseCollector:
    def __init__(self):
        pass
    def run(self):
        pass

class ArenaCollector(BaseCollector):
    pass

class BattlefieldCollector(BaseCollector):
    def __init__(self, game):
        self.game = game
        self.path = path.join(game.path, "Power.log")
        print(game.path)
        self.last_ts = datetime.time(0)
        self.last_turn = None
        self.parser = LogParser()
        self.last_img = None

    def run(self):
        with open(self.path) as f:
            self.parser.read(f)
            self.parser.flush()
            tps = self.parser.games
            fp_id = FriendlyPlayerExporter(tps[-1]).export()
            turn = LastTurnExporter(tps[-1], self.last_ts, fp_id).export()
            if not self.last_turn:
                self.last_turn = turn
            if(turn.ts > self.last_turn.ts and turn.player):
                ## GET MINIONS / HAND_CARDS / HERO_POWERS
                print("EMinions {}  - PMinions {}  - HandCards {}".format(turn.enemy_minions, turn.player_minions, turn.hand_cards))
                ### build xml
                create_battlefield(self.last_img, turn.hand_cards, turn.enemy_minions, turn.player_minions, turn.enemy_power, turn.player_power)
                # self.last_img.add_random_img_with_xml(xml)
                screen.save(self.last_img, "test.png".format(turn.enemy_minions, turn.player_minions, turn.hand_cards))
                # screen.save(self.last_img, "images/em{}_pm{}_hc{}.png".format(turn.enemy_minions, turn.player_minions, turn.hand_cards))
                print("{} > TURN".format(turn.player))
                self.game.show_img("test.png")
                self.last_turn = turn
            self.last_img = screen.shot()


Game("/home/dee/.PlayOnLinux/wineprefix/hs/drive_c/Program Files/Hearthstone/Logs/").run()
