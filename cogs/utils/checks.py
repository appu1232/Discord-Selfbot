import json
import time


def load_config():
    with open('settings/config.json', 'r') as f:
        return json.load(f)


def load_optional_config():
    with open('settings/optional_config.json', 'r') as f:
        return json.load(f)


def load_notify_config():
    with open('settings/notify.json', 'r') as f:
        return json.load(f)


def has_passed(bot, oldtime):
    if time.time() - 20 < oldtime:
        return False
    bot.refresh_time = time.time()
    return True


def game_time_check(bot, oldtime, interval):
    if time.time() - interval < oldtime:
        return False
    bot.game_time = time.time()
    return True


def avatar_time_check(bot, oldtime, interval):
    if time.time() - interval < oldtime:
        return False
    bot.avatar_time = time.time()
    return True


def embed_perms(message):
    try:
        check = message.author.permissions_in(message.channel).embed_links
    except:
        check = True

    return check


def attach_perms(message):
    return message.author.permissions_in(message.channel).attach_files


def add_reaction_perms(message):
    return message.author.permissions_in(message.channel).add_reactions
