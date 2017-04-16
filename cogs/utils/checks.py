import json
import time
import git
import discord
import os


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


def user_post(bot, user):
    if time.time() - float(bot.key_users[user][0]) < float(bot.key_users[user][1]):
        bot.key_users[user] = [time.time(), bot.key_users[user][1]]
        return False
    with open('settings/log.json', 'r+') as log:
        settings = json.load(log)
        now = time.time()
        settings['keyusers'][user] = [now, bot.key_users[user][1]]
        log.seek(0)
        log.truncate()
        json.dump(settings, log, indent=4)
    bot.key_users[user] = [now, bot.key_users[user][1]]
    return True


def gc_clear(bot, gc_time):
    if time.time() - 1800 < gc_time:
        return False
    bot.gc_time = time.time()
    return True


def game_time_check(bot, oldtime, interval):
    if time.time() - float(interval) < oldtime:
        return False
    bot.game_time = time.time()
    return True


def avatar_time_check(bot, oldtime, interval):
    if time.time() - float(interval) < oldtime:
        return False
    bot.avatar_time = time.time()
    return True


def update_bot(message):
    g = git.cmd.Git(working_dir=os.getcwd())
    g.execute(["git", "fetch", "origin", "master"])
    update = g.execute(["git", "remote", "show", "origin"])
    if ('up to date' in update or 'fast-forward' in update) and message:
        return False
    else:
        if message is False:
            version = 4
        else:
            version = g.execute(["git", "rev-list", "--right-only", "--count", "master...origin/master"])
        version = str(int(version) + 1)
        if int(version) > 10:
            version = "10"
        commits = g.execute(["git", "rev-list", "--max-count=%s" % version, "origin/master"])
        commits = commits.split('\n')
        em = discord.Embed(color=0x24292E, title='Latest changes for the selfbot:')
        for i in range(int(version)-1):
            title = g.execute(["git", "log", "--format=%ar", "-n", "1", "%s" % commits[i]])
            field = g.execute(["git", "log", "--pretty=oneline", "--abbrev-commit", "--shortstat", "%s" % commits[i], "^%s" % commits[i+1]])
            field = field[8:].strip()
            link = 'https://github.com/appu1232/Discord-Selfbot/commit/%s' % commits[i]
            em.add_field(name=title, value='%s\n[Code changes](%s)' % (field, link), inline=False)
        em.set_thumbnail(url='https://image.flaticon.com/icons/png/512/25/25231.png')
        em.set_footer(text='Full project: https://github.com/appu1232/Discord-Selfbot')
        return em


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
