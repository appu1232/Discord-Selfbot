import json
import time
from discord import utils


def load_config():
    with open('settings/config.json', 'r') as f:
        return json.load(f)


def hasPassed(bot, oldtime):
    if time.time() - 20 < oldtime:
        return False
    bot.refresh_time = time.time()
    return True


def embed_perms(message):
    try:
        check = message.author.permissions_in(message.channel).embed_links
    except:
        check = True

    return check


def attach_perms(message):
    return message.author.permissions_in(message.channel).attach_files