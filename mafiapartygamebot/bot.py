#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""mafia party game bot"""
import logging
import sys

from telegram.ext import Updater, CommandHandler
from host import Host
from game import GameStatus

token = sys.argv[1]

logging.basicConfig(filename='bot.log',level=logging.INFO)

logger = logging.getLogger('mafiapartygamebot')

logger.setLevel(logging.INFO)

logger.info('bot started')

host = Host()

def new(bot, update):
    """start new game"""
    game = host.get_game(update.message.chat_id)
    if game and game.state == GameStatus.waiting:
        bot.sendMessage(
            update.message.chat_id,
            'Мы уже ожидаем игроков! \r\n{} {}'
            .format(game.game_master.name, game.game_master.role))
    elif game and game.state == GameStatus.started:
        bot.sendMessage(
            update.message.chat_id,
            'А мы уже играем 😁 Чтобы завершить текущую игру, воспользуйтесь командой /cancel')
    else:
        game = host.create_game(update.message.chat_id, update.message.from_user)
        game_master = game.game_master
        bot.sendMessage(
            update.message.chat_id,
            'Начинаем новую игру, присоединяйся быстрее! \r\n{} {}'
            .format(game_master.name, game_master.role))

def join(bot, update):
    """join game"""
    game = host.get_game(update.message.chat_id)

    if game is None:
        bot.sendMessage(
            update.message.chat_id,
            'Для начала создайте новую игру при помощи команды /new')
    else:
        if game.game_master.identity == update.message.from_user.id:
            bot.sendMessage(
                update.message.chat_id,
                'Ведущий играет роль ведущего...')
        else:
            player = game.add_player(update.message.from_user)
            if player:
                bot.sendMessage(
                    update.message.chat_id,
                    'К игре присоединился {}'.format(player.name))

def play(bot, update):
    """play new game"""
    game = host.get_game(update.message.chat_id)

    if not game:
        bot.sendMessage(
            update.message.chat_id,
            'Сначала нужно создать игру при помощи команды /new')

    elif game and game.state == GameStatus.waiting:
        if game.game_master.identity != update.message.from_user.id:
            bot.sendMessage(
                update.message.chat_id,
                'Только ведущий может начать игру. \r\n{} {}'
                .format(game.game_master.name, game.game_master.role))
        else:
            game.start()
            game_master = game.game_master

            if len(game.players) == 0:
                bot.sendMessage(update.message.chat_id, 'Для игры в мафии нужны игроки 😊')
                return

            players = ['Роли игроков: \r\n']
            for player in game.players:
                players.append('{} {}'.format(player.role, player.name))
                bot.sendMessage(player.identity, '❗️ Твоя роль {}'.format(player.role))

            bot.sendMessage(game_master.identity, '\r\n'.join(players))

            bot.sendMessage(
                update.message.chat_id,
                'Город засыпает 💤 \r\n{} {}'.format(game_master.name, game_master.role))

    elif game and game.state == GameStatus.started:
        bot.sendMessage(
            update.message.chat_id,
            'А мы уже играем 😁 Чтобы завершить текущую игру, воспользуйтесь командой /cancel')

def cancel(bot, update):
    """cancel game"""
    game = host.get_game(update.message.chat_id)

    if game:
        game_master = game.game_master
        if game_master.identity != update.message.from_user.id:
            bot.sendMessage(
                update.message.chat_id,
                'Только ведущий может остановить игру. \r\n{} {}'
                .format(game_master.name, game_master.role))
        else:
            host.delete_game(update.message.chat_id)
            bot.sendMessage(update.message.chat_id, 'Игра остановлена 😐')
    else:
        bot.sendMessage(update.message.chat_id, 'Игра не найдена 😳')

def help(bot, update):
    """print help"""
    bot.sendMessage(update.message.chat_id,
                    '/new - создание новой игры \r\n'+
                    '/join - присоединиться к игре \r\n'+
                    '/play - город зассыпает... \r\n'+
                    '/cancel - закончить игру')

updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('new', new))
updater.dispatcher.add_handler(CommandHandler('join', join))
updater.dispatcher.add_handler(CommandHandler('play', play))
updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
updater.dispatcher.add_handler(CommandHandler('help', help))

updater.start_polling()

updater.idle()