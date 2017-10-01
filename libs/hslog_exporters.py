from hslog.export import EntityTreeExporter, FriendlyPlayerExporter
from hearthstone.enums import *

class LastTurnExporter(EntityTreeExporter):
    last_player = "Unknown"
    last_turn = 0
    player = None

    def __init__(self, packet_tree, last_turn, player_id):
        self.last_turn = last_turn
        self.player_id = player_id
        super().__init__(packet_tree)

    def handle_block(self, block):
        super(LastTurnExporter, self).handle_block(block)
        g = self.game
        card = [e for e in g.entities if(e.id == block.entity)]
        if card:
            card = card[0]
            if card.controller:
                self.last_player = "Player" if card.controller.player_id == self.player_id else "Enemy"
                if(card.controller.player_id != self.player_id):
                    self.enemy_id = card.controller.player_id
        for packet in block.packets:
            if "tag" in packet.__dict__ and type(packet.tag) is not int and packet.tag == GameTag.TURN:
                if(self.last_player == "Player"):
                    if(packet.ts >= self.last_turn):
                        self.last_turn = packet.ts
                        self.player = self.last_player
                        self.player_minions = len(self.get_board(self.player_id))
                        self.enemy_minions = len(self.get_board(self.enemy_id))
                        self.hand_cards = self.get_amount_handcards(self.player_id)
                        return self
        return self

    def get_board(self, player_id):
        return [e for e in self.game.entities if(e.zone == Zone.PLAY and
                                        e.type == CardType.MINION and
                                        e.controller.player_id == player_id)]

    def get_amount_handcards(self, player_id):
        return len([e for e in self.game.entities if(e.zone == Zone.HAND
                                             and e.controller.player_id == player_id)])
