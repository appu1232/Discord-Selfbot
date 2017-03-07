import discord
import json
import mimetypes
from random import randint

quick = [('shrug', '¯\_(ツ)_/¯'), ('flip', '(╯°□°）╯︵ ┻━┻'), ('unflip', '┬─┬﻿ ノ( ゜-゜ノ)'), ('lenny', '( ͡° ͜ʖ ͡°)'), ('comeatmebro', '(ง’̀-‘́)ง')]

def afk(notified):
    with open('settings/config.json') as f:
        config = json.load(f)
    for i in notified:
        if i.id == config['my_id'] and config['set_afk'] == 'on':
            return config['afk_message']


# Quick cmds for da memes
def quickcmds(message):

    for i in quick:
        if message == i[0]:
            return i[1]
    return None


# Searches commands.json for the inputted command. If exists, return the response associated with the command.
def custom(message):

    success = False

    with open('settings/config.json') as f:
        config = json.load(f)
    if message.startswith(config['customcmd_prefix'][0]):
        with open('settings/commands.json', 'r') as f:
            commands = json.load(f)
            file = discord.Embed(colour=0x27007A)
        for i in commands:
            if message[1:].startswith(i.lower()):
                success = True

                # If the commands resulting reply is a list instead of a str
                if type(commands[i]) is list:
                    try:
                        # If index from list is specified, get that result.
                        if message[len(i) + 1:].isdigit():
                            index = int(message.content[len(i) + 1:].strip())
                        else:
                            title = message[len(i) + 1:]
                            for b, j in enumerate(commands[i]):
                                if j[0] == title.strip():
                                    index = int(b)
                                    break
                        mimetype, encoding = mimetypes.guess_type(commands[i][index][1])

                        # If value is an image, send as embed
                        if mimetype and mimetype.startswith('image'):
                            return 'embed', commands[i][index][1]
                        else:
                            return 'message', commands[i][index][1]
                    except:

                        # If the index is not specified, get a random index from list
                        index = randint(0, len(commands[i]) - 1)
                        mimetype, encoding = mimetypes.guess_type(commands[i][index][1])

                        # If value is an image, send as embed
                        if mimetype and mimetype.startswith('image'):
                            return 'embed', commands[i][index][1]
                        else:
                            return 'message', commands[i][index][1]
                else:
                    mimetype, encoding = mimetypes.guess_type(commands[i])

                    # If value is an image, send as embed
                    if mimetype and mimetype.startswith('image'):
                        return 'embed', commands[i]
                    else:
                        return 'message', commands[i]
    if success is True:
        return None
