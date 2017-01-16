#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from game import Game

class Host(object):
    """host"""
    def __init__(self):
        self.logger = logging.getLogger('mafiapartygamebot.Host')
        self.logger.info('host initialized')
        self.games = []

    def create_game(self, chat_id, user):
        """create new game for chat"""
        game = self.get_game(chat_id)
        if game:
            self.logger.info('game for chat %s already exists', chat_id)
            return game

        game = Game(chat_id, user)
        self.games.append(game)
        self.logger.info('created new game for chat %s', chat_id)
        return game

    def get_game(self, chat_id):
        """get game for chat"""
        for game in self.games:
            if game.chat_id == chat_id:
                return game
        self.logger.info('no game found for chat %s', chat_id)
        return None

    def delete_game(self, chat_id):
        """delete game for chat"""
        game_to_delete = -1
        for idx, game in enumerate(self.games):
            if game.chat_id == chat_id:
                game_to_delete = idx
        if game_to_delete > -1:
            del self.games[game_to_delete]
            self.logger.info('deleted game for chat %s', chat_id)
