import os
from os import path
from os import listdir
from os.path import join, isfile
import datetime
import re
import time
from enum import Enum
import subprocess
import signal

from _thread import start_new_thread
from threading import Lock

import tailer
from system_hotkey import SystemHotkey

from hslog import LogParser
from hslog.export import FriendlyPlayerExporter
from libs.hslog_exporters import LastTurnExporter


from libs import screen
from libs.template import create_battlefield

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
        self.collector = BaseCollector(self)
        self.lock = Lock()
        self.p = None
        self.running = True
        self.hk = SystemHotkey()
        self.hk.register(('control', 'alt', 'z'), callback=self.delete_last_img)
        self.images = []

    def delete_last_img(self, evnt):
        if self.images:
            os.remove(self.images[-1])
            os.remove(self.images[-1].replace(".png", ".xml"))
            if self.p:
                self.p.terminate()
                self.p.wait()
            self.images.pop(-1)
            if self.images and self.images[-1]:
                self.p = subprocess.Popen(["python3", "labelImg/labelImg.py", self.images[-1]])


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
            self.collector = BaseCollector(self)

    def show_img(self, path):
        self.images.append(path)
        if(len(self.images) >= 5):
            self.images.remove(self.images[0])
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

    def terminate(self, signal, frame):
        self.lock.acquire()
        self.running = False
        self.p.terminate()
        self.p.wait()
        self.lock.release()
        if self.p:
            self.p.terminate()
            self.p.wait()
        exit()


    def run_collector(self):
        while(self.running):
            self.lock.acquire()
            self.collector.run()
            self.lock.release()


class BaseCollector:
    def __init__(self, game):
        self.game = game
    def run(self):
        pass

class CollectionCollertor(BaseCollector):
    def __init__(self, game):
        super().__init__(game)
        game.hk.register(('controll', 'alt', 'g'), callback=self.start)
        game.hk.register(('controll', 'alt', 's'), callback=self.stop)
        print("CollectionCollertor: Start process with ctrl+alt+g")
        print("CollectionCollertor: Stop process with ctrl+alt+s")

    def start(self):
        print("Start CollectionCollertor ...")
        self.running = True

    def stop(self):
        print("Stop CollectionCollertor ...")
        self.running = False

    def run(self):
        if(self.running):
            print("running ...")
            ## take sc
            ## build xml
            ## click next


class ArenaCollector(BaseCollector):
    pass

class BattlefieldCollector(BaseCollector):
    def __init__(self, game):
        super().__init__(game)
        self.path = path.join(game.path, "Power.log")
        print(game.path)
        self.last_ts = datetime.time(0)
        self.last_turn = None
        self.parser = LogParser()

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
                time.sleep(1.2)
                img = screen.shot()
                print("EMinions {}  - PMinions {}  - HandCards {}".format(turn.enemy_minions, turn.player_minions, turn.hand_cards))

                base_name = "em{}_pm{}_hc{}".format(turn.enemy_minions, turn.player_minions, turn.hand_cards)

                count = len([f for f in listdir("images") if isfile(join("images", f)) and base_name in f])
                if(count > 3):
                    count = 3
                base_name = "images/{}_{}".format(count, base_name)

                img_name = base_name + ".png"
                xml_name = base_name + ".xml"

                temp = create_battlefield(img, turn.hand_cards, turn.enemy_minions, turn.player_minions, turn.enemy_power, turn.player_power)
                temp.save(xml_name)

                screen.save(img, img_name)
                self.game.show_img(img_name)
                self.last_turn = turn


game = Game("/home/dee/.PlayOnLinux/wineprefix/hs/drive_c/Program Files/Hearthstone/Logs/")
# signal.signal(signal.SIGINT, game.terminate)
game.run()
