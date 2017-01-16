#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import json
import os
from player import Player, roles
from enum import Enum

class GameStatus(Enum):
    """game status enum"""
    waiting = 1
    started = 2

class Game(object):
    """the game"""
    def __init__(self, chat_id, user=None):
        self.chat_id = chat_id
        self.state = GameStatus.waiting
        if user:
            self.game_master = Player(user, game_master=True)
        self.players = []
        self.logger = logging.getLogger('mafiapartygamebot.Game')

    def __eq__(self, other):
        return self.chat_id == other.chat_id

    def add_player(self, user):
        """add player to game"""
        if self.game_master.identity == user.id:
            return None
        if not self.get_player(user):
            player = Player(user)
            self.players.append(player)
            self.logger.info('added player %s to game in chat %s', player.name, self.chat_id)
            return player

    def get_player(self, user):
        """get player by user"""
        for player in self.players:
            if player.identity == user.id:
                return player
        return None

    def start(self):
        """start game"""
        if self.state == GameStatus.started:
            self.logger.info('cannot start already started game in chat %s', self.chat_id)
            return

        players_count = len(self.players)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        rules_file_path = os.path.join(current_dir, 'rules.json')
        with open(rules_file_path, 'r') as data_file:
            rules = json.load(data_file)


        if str(players_count) not in rules:
            self.logger.info(
                'no rules for %s players for game in chat %s', players_count, self.chat_id)
            return

        random.shuffle(self.players)
        rules = rules[str(players_count)]

        start_index = 0
        end_index = 0

        for key in rules:
            end_index = start_index + rules[key]
            for i in range(start_index, end_index):
                self.players[i].role = roles[key]
            start_index = end_index

        self.logger.info('starting game with %s players in chat %s', players_count, self.chat_id)
        self.state = GameStatus.started

        return self.players





  