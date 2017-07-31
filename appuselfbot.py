import collections
import datetime
import math
import subprocess
import asyncio
import random
import glob
import gc
import psutil
import sys
import re
import traceback
import argparse
import os
import logging
import logging.handlers
from json import load, dump
from datetime import timezone
from cogs.utils.allmsgs import custom, quickcmds
from discord_webhooks import Webhook
from cogs.utils.checks import *
from cogs.utils.config import *
from discord.ext import commands

def parse_cmd_arguments(): # allows for arguments
    parser = argparse.ArgumentParser(description="Discord-Selfbot")
    parser.add_argument("-test", "--test-run", # test run flag for Travis
                        action="store_true",
                        help="Makes the bot quit before trying to log in")
    parser.add_argument("--force-mac", # Allows for Testing of mac related code
                        action="store_true",
                        help="Forces to run the Mac checks")
    parser.add_argument("--reset-config", # Allows for Testing of mac related code
                        action="store_true",
                        help="Reruns the setup")
    parser.add_argument("-s", "--silent", # Allows for Testing of mac related code
                        action="store_true",
                        help="Supresses all errors")
    return parser

args = parse_cmd_arguments().parse_args()
_test_run = args.test_run
_force_mac = args.force_mac
_reset_cfg = args.reset_config
_silent = args.silent
_force_admin = False


if _test_run:
    try:
        samples = os.listdir('settings') # generating the config files from sample while building
        for f in samples:
            if f.endswith('sample') and f[:-7] not in samples:
                with open('settings/%s' % f, 'r', encoding="utf8") as template:
                    with open('settings/%s' % f[:-7], 'w', encoding="utf8") as g:
                        fields = json.load(template)
                        json.dump(fields, g, sort_keys=True, indent=4)
    except:
        print('Something when wrong. Check for missing sample files') # only visible in Travis
        pass # duo to some sample files sometimes missing passing it will make sure nothing goes wrong
    print("Quitting: test run")
    exit(0)

if sys.platform == 'darwin' or _force_mac:
    if subprocess.getstatusoutput('brew')[0] == 1:
        print('You do not have brew installed.\nThere are known issues with out of date binaries which can be updated using brew.\nFollow https://brew.sh to install brew.\n\nEnter \'I understand!\' to continue')
        inp = input('>')
        if inp != 'I understand!':
            print('Exiting...')
            exit(0)

def Wizard():
    # setup wizard
    if _silent:
        print('Cannot use setup Wizard becaue of silent mode')
        exit(0)
    config = {}
    print("Welcome to Appu's Discord Selfbot!\n")
    print("Go into your Discord window and press Ctrl+Shift+I (Ctrl+Opt+I can also work on macOS)")
    print("Then, go into the Applications tab (you may have to click the arrow at the top right to get there), expand the 'Local Storage' dropdown, select discordapp, and then grab the token value at the bottom. Here's how it looks: https://imgur.com/h3g9uf6")
    print("Paste the contents of that entry below.")
    print("-------------------------------------------------------------")
    config["token"] = input("| ").strip().strip('"')
    print("\nEnter the command prefix you want to use for main commands (eg. if you enter > you will use commands like so: >about).")
    print("-------------------------------------------------------------")
    config["cmd_prefix"] = input("| ").strip()
    print("\nEnter the command prefix you want to use for custom commands (commands that you add to the bot yourself with custom replies). Using the same prefix as the main command prefix is allowed but not recommended.")
    print("-------------------------------------------------------------")
    config["customcmd_prefix"] = input("| ").strip()
    print("\nEnter something that will precede every response from the bot. This is to identify messages that came from the bot vs. just you talking. Ex: Entering :robot: will make the bot respond with the robot emoji at the front of every message it sends. Recommended but if you don't want anything, press enter to skip.")
    print("-------------------------------------------------------------")
    config["bot_identifier"] = input("| ").strip()
    input("\nThis concludes the setup wizard. For further setup options (ex. setting up google image search), refer to the Discord Selfbot wiki.\n\nPress Enter to start the bot....\n")
  
    print("Starting up...")
    with open('settings/config.json', encoding='utf-8', mode="w") as f:
        dump(config, f, sort_keys=True, indent=4)

if _reset_cfg:
    Wizard()
else:
    try:
        with open('settings/config.json', encoding='utf-8', mode="r") as f:
            data = load(f) # checks if the settings file is valid json file
    except IOError:
        Wizard()

shutdown = False
if os.name == 'nt':
    try:
        # only windows users with admin privileges can read the C:\windows\temp
        temp = os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\\windows'),'temp']))
    except:
        shutdown = False
    else:
        shutdown = True
else:
    if os.geteuid() == 0:
        shutdown = True
    else:
        shutdown = False
        
if shutdown == True and not _force_admin:
    if os.name == 'nt':
        print('It is not advised to run the bot as Admin.\nContinuing logging in...')
    else:
        print('It is not advised to run the bot with root privileges.\nContinuing logging in...')
    # exit(0)

def set_log():
    errformat = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    logger = logging.getLogger("red")
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    errhandler = logging.handlers.RotatingFileHandler(
        filename='settings/bot.log', encoding='utf-8', mode='a',
        maxBytes=10**7, backupCount=5)
    errhandler.setFormatter(errformat)

    logger.addHandler(errhandler)
    logger.addHandler(stdout_handler)

    return logger

logger = set_log()

samples = os.listdir('settings')
for f in samples:
    if f.endswith('sample') and f[:-7] not in samples:
        with open('settings/%s' % f, 'r', encoding="utf8") as template:
            with open('settings/%s' % f[:-7], 'w', encoding="utf8") as g:
                fields = json.load(template)
                json.dump(fields, g, sort_keys=True, indent=4)


bot = commands.Bot(command_prefix=get_config_value('config', 'cmd_prefix'), description='''Selfbot by appu1232''', self_bot=True)

if __name__ == "__main__":
    _runs_in_loop = False
else:
    _runs_in_loop = True

bot.bot_prefix = get_config_value('config', 'bot_identifier')
if bot.bot_prefix != '':
    bot.bot_prefix += ' '

bot.cmd_prefix = get_config_value('config', 'cmd_prefix')
bot.customcmd_prefix = get_config_value('config', 'customcmd_prefix')

# Startup
@bot.event
async def on_ready():
    print('Logged in as')
    try:
        print(bot.user.name)
    except:
        pass
    print('User id:' + str(bot.user.id))
    print('------')
    bot.uptime = datetime.datetime.now()
    bot.icount = bot.message_count = bot.mention_count = bot.keyword_log = 0
    bot.self_log = bot.all_log = {}
    bot.imagedumps = []
    bot.default_status = ''
    bot.is_stream = False
    bot.game = bot.game_interval = bot.avatar = bot.avatar_interval = bot.subpro = bot.keyword_found = None
    bot.game_time = bot.avatar_time = bot.gc_time = bot.refresh_time = time.time()
    bot.notify = load_notify_config()
    if not os.path.isfile('settings/ignored.json'):
        with open('settings/ignored.json', 'w', encoding="utf8") as fp:
            json.dump({'servers': []}, fp, indent=4)
    with open('settings/ignored.json', encoding="utf8") as fp:
        bot.ignored_servers = json.load(fp)

    if os.path.isfile('restart.txt'):
        with open('restart.txt', 'r', encoding="utf8") as re:
            channel = bot.get_channel(re.readline())
            print('Bot has restarted.')
            await bot.send_message(channel, bot.bot_prefix + 'Bot has restarted.')
        os.remove('restart.txt')
    bot.log_conf = load_log_config()
    bot.key_users = bot.log_conf['keyusers']

    if os.path.isfile('settings/games.json'):
        with open('settings/games.json', 'r+', encoding="utf8") as g:
            games = json.load(g)
            if type(games['games']) is list:
                bot.game = games['games'][0]
                bot.game_interval = games['interval']
            else:
                bot.game = games['games']
            if 'stream' not in games:
                games['stream'] = 'no'
            if games['stream'] == 'yes':
                bot.is_stream = True
            g.seek(0)
            g.truncate()
            json.dump(games, g, indent=4)

    # Dealing with old versions updating
    if not os.path.isfile('settings/moderation.json'):
        with open('settings/moderation.json', 'w', encoding="utf8") as m:
            mod = {}
            json.dump(mod, m, indent=4)
    if not os.path.isfile('settings/todo.json'):
        with open('settings/todo.json', 'w', encoding="utf8") as t:
            todo = {}
            json.dump(todo, t, indent=4)

    if os.path.isfile('cogs/online_users.py'):
        os.remove('cogs/online_users.py')
    if not os.path.exists('avatars'):
        os.makedirs('avatars')
    if not os.path.isfile('settings/avatars.json'):
        with open('settings/avatars.json', 'w', encoding="utf8") as avis:
            json.dump({'password': '', 'interval': '0', 'type': 'random'}, avis, indent=4)
    with open('settings/avatars.json', 'r', encoding="utf8") as g:
        avatars = json.load(g)
    bot.avatar_interval = avatars['interval']
    if os.listdir('avatars') and avatars['interval'] != '0':
        all_avis = os.listdir('avatars')
        all_avis.sort()
        avi = random.choice(all_avis)
        bot.avatar = avi
    if not os.path.isfile('settings/optional_config.json'):
        conf = load_config()
        o_conf = {'google_api_key': conf['google_api_key'], 'custom_search_engine': conf['custom_search_engine'], 'mal_username': conf['mal_username'], 'mal_password': conf['mal_password']}
        with open('settings/optional_config.json', 'w', encoding="utf8") as oc:
            json.dump(o_conf, oc, indent=4)
    with open('settings/optional_config.json', 'r+', encoding="utf8") as fp:
        opt = json.load(fp)
        if 'embed_color' not in opt:
            opt['embed_color'] = ''
        if 'quoteembed_color' not in opt:
            opt['quoteembed_color'] = 'bc0b0b'
        if 'customcmd_color' not in opt:
            opt['customcmd_color'] = '27007A'
        if 'rich_embed' not in opt:
            opt['rich_embed'] = 'on'
        if 'default_status' not in opt:
            opt['default_status'] = 'idle'
        if 'ascii_font' not in opt:
            opt['ascii_font'] = 'big'
        if 'online_stats' not in opt:
            opt['online_stats'] = 'on'
        fp.seek(0)
        fp.truncate()
        json.dump(opt, fp, indent=4)

    if not os.path.isfile('settings/github.json'):
        with open('settings/github.json', 'w', encoding="utf8") as fp:
            git = {}
            json.dump(git, fp, indent=4)
    with open('settings/github.json', 'r+', encoding="utf8") as fp:
        opt = json.load(fp)
        if 'username' not in opt:
            opt['username'] = ''
        if 'password' not in opt:
            opt['password'] = ''
        if 'reponame' not in opt:
            opt['reponame'] = ''
        fp.seek(0)
        fp.truncate()
        json.dump(opt, fp, indent=4)

    notif = load_notify_config()
    if notif['type'] == 'dm':
        if os.path.exists('notifier.txt'):
            pid = open('notifier.txt', 'r', encoding="utf8").read()
            try:
                p = psutil.Process(int(pid))
                p.kill()
            except:
                pass
            os.remove('notifier.txt')
        bot.subpro = subprocess.Popen([sys.executable, 'cogs/utils/notify.py'])
        with open('notifier.txt', 'w', encoding="utf8") as fp:
            fp.write(str(bot.subpro.pid))

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.CheckFailure):
        await bot.send_message(ctx.message.channel, bot.bot_prefix + "You don't have permissions to use that command.")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel, bot.bot_prefix + "You are missing required arguments.\n" + formatter.format_help_for(ctx, ctx.command)[0])
    else:
        if _silent:
            await bot.send_message(ctx.message.channel, bot.bot_prefix + "An error occurred with the `{}` command.".format(ctx.command.name))
        else:
            await bot.send_message(ctx.message.channel, bot.bot_prefix + "An error occurred with the `{}` command. Check the console for details.".format(ctx.command.name))
            print("Ignoring exception in command {}".format(ctx.command.name))
            trace = traceback.format_exception(type(error), error, error.__traceback__)
            print("".join(trace))

@bot.command(pass_context=True, aliases=['reboot'])
async def restart(ctx):
    """Restarts the bot."""
    def check(msg):
        if msg:
            return msg.content.lower().strip() == 'y' or msg.content.lower().strip() == 'n'
        else:
            return False

    latest = update_bot(True)
    if latest:
        await bot.send_message(ctx.message.channel, bot.bot_prefix + 'There is an update available for the bot. Download and apply the update on restart? (y/n)')
        reply = await bot.wait_for_message(timeout=10, author=ctx.message.author, check=check)
        with open('restart.txt', 'w', encoding="utf8") as re:
            re.write(str(ctx.message.channel.id))
        if not reply or reply.content.lower().strip() == 'n':
            print('Restarting...')
            await bot.send_message(ctx.message.channel, bot.bot_prefix + 'Restarting...')
        else:
            await bot.send_message(ctx.message.channel, content=None, embed=latest)
            with open('quit.txt', 'w', encoding="utf8") as q:
                q.write('update')
            print('Downloading update and restarting...')
            await bot.send_message(ctx.message.channel, bot.bot_prefix + 'Downloading update and restarting (check your console to see the progress)...')

    else:
        print('Restarting...')
        with open('restart.txt', 'w', encoding="utf8") as re:
            re.write(str(ctx.message.channel.id))
        await bot.send_message(ctx.message.channel, bot.bot_prefix + 'Restarting...')

    if bot.subpro:
        bot.subpro.kill()
    os._exit(0)


@bot.command(pass_context=True, aliases=['upgrade'])
async def update(ctx, msg: str = None):
    """Update the bot if there is an update available."""
    if msg:
        latest = update_bot(False) if msg == 'show' else update_bot(True)
    else:
        latest = update_bot(True)
    if latest:
        if not msg == 'show':
            if embed_perms(ctx.message):
                await bot.send_message(ctx.message.channel, content=None, embed=latest)
            await bot.send_message(ctx.message.channel, bot.bot_prefix + 'There is an update available. Downloading update and restarting (check your console to see the progress)...')
        else:
            await bot.send_message(ctx.message.channel, content=None, embed=latest)
            return
        with open('quit.txt', 'w', encoding="utf8") as q:
            q.write('update')
        with open('restart.txt', 'w', encoding="utf8") as re:
            re.write(str(ctx.message.channel.id))
        if bot.subpro:
            bot.subpro.kill()
        os._exit(0)
    else:
        await bot.send_message(ctx.message.channel, bot.bot_prefix + 'The bot is up to date.')


@bot.command(pass_context=True, aliases=['stop', 'shutdown'])
async def quit(ctx):
    """Quits the bot."""
    print('Bot exiting...')
    if bot.subpro:
        bot.subpro.kill()
    open('quit.txt', 'a', encoding="utf8").close()
    await bot.send_message(ctx.message.channel, bot.bot_prefix + 'Bot shut down.')
    os._exit(0)


@bot.command(pass_context=True)
async def reload(ctx, txt: str = None):
    """Reloads all modules."""
    await bot.delete_message(ctx.message)
    if txt:
        bot.unload_extension(txt)
        try:
            bot.load_extension(txt)
        except Exception as e:
            try:
                txt = 'cogs.'+txt
                bot.load_extension(txt)
            except:
                await bot.send_message(ctx.message.channel, '``` {}: {} ```'.format(type(e).__name__, e))
                return
    else:
        utils = []
        for i in bot.extensions:
            utils.append(i)
        fail = False
        l = len(utils)
        for i in utils:
            bot.unload_extension(i)
            try:
                bot.load_extension(i)
            except Exception as e:
                await bot.send_message(ctx.message.channel, '{}Failed to reload module `{}` ``` {}: {} ```'.format(bot.bot_prefix, i, type(e).__name__, e))
                fail = True
                l -= 1
        await bot.send_message(ctx.message.channel, bot.bot_prefix + 'Reloaded {} of {} modules.'.format(l, len(utils)))


# On all messages sent (for quick commands, custom commands, and logging messages)
@bot.event
async def on_message(message):

    await bot.wait_until_ready()
    await bot.wait_until_login()

    if hasattr(bot, 'message_count'):
        bot.message_count += 1

    # If the message was sent by me
    if message.author.id == bot.user.id:
        if hasattr(bot, 'icount'):
            bot.icount += 1
        try:
            if hasattr(bot, 'ignored_servers'):
                if any(message.server.id == server_id for server_id in bot.ignored_servers['servers']):
                    return
        except AttributeError:  # Happens when it's a direct message.
            pass
        if hasattr(bot, 'self_log'):
            if message.channel.id not in bot.self_log:
                bot.self_log[message.channel.id] = collections.deque(maxlen=100)
            bot.self_log[message.channel.id].append(message)
            if message.content.startswith(bot.customcmd_prefix):
                response = custom(message.content.lower().strip())
                if response:
                    await bot.delete_message(message)
                    if get_config_value('optional_config', 'rich_embed') == 'on':
                        if response[0] == 'embed' and embed_perms(message):
                            try:
                                if get_config_value('optional_config', 'customcmd_color'):
                                    color = int('0x' + get_config_value('optional_config', 'customcmd_color'), 16)
                                    await bot.send_message(message.channel, content=None, embed=discord.Embed(colour=color).set_image(url=response[1]))
                                else:
                                    await bot.send_message(message.channel, content=None, embed=discord.Embed().set_image(url=response[1]))
                            except:
                                await bot.send_message(message.channel, response[1])
                        else:
                            await bot.send_message(message.channel, response[1])
                    else:
                        await bot.send_message(message.channel, response[1])
            else:
                response = quickcmds(message.content.lower().strip())
                if response:
                    await bot.delete_message(message)
                    await bot.send_message(message.channel, response)

    notified = message.mentions
    if notified:
        for i in notified:
            if i.id == bot.user.id:
                bot.mention_count += 1

    if not hasattr(bot, 'log_conf'):
        bot.log_conf = load_log_config()

    # Keyword logging.
    if bot.log_conf['keyword_logging'] == 'on':

        try:
            word_found = False
            if (bot.log_conf['allservers'] == 'True' or str(message.server.id) in bot.log_conf['servers']) and (message.server.id not in bot.log_conf['blacklisted_servers'] and message.channel.id not in bot.log_conf['blacklisted_channels']):
                add_alllog(message.channel.id, message.server.id, message)
                if message.author.id != bot.user.id and (not message.author.bot and not any(x in message.author.id for x in bot.log_conf['blacklisted_users'])):
                    for word in bot.log_conf['keywords']:
                        if ' [server]' in word:
                            word, server = word.split(' [server]')
                            if message.server.id != server:
                                continue
                        elif ' [channel]' in word:
                            word, channel = word.split(' [channel]')
                            if message.channel.id != channel:
                                continue
                        if word.startswith('[isolated]'):
                            word = word[10:].lower()
                            found = re.findall('\\b' + word + '\\b', message.content.lower())
                            if found:
                                word_found = True
                                break
                        else:
                            if word.lower() in message.content.lower():
                                word_found = True
                                break

                    for x in bot.log_conf['blacklisted_words']:
                        if '[server]' in x:
                            bword, id = x.split('[server]')
                            if bword.strip().lower() in message.content.lower() and message.server.id == id:
                                word_found = False
                                break
                        elif '[channel]' in x:
                            bword, id = x.split('[channel]')
                            if bword.strip().lower() in message.content.lower() and message.channel.id == id:
                                word_found = False
                                break
                        if x.lower() in message.content.lower():
                            word_found = False
                            break

            user_found = False
            if bot.log_conf['user_logging'] == 'on':
                if '{} {}'.format(str(message.author.id), str(message.server.id)) in bot.log_conf['keyusers']:
                    if user_post(bot, '{} {}'.format(str(message.author.id), str(message.server.id))):
                        user_found = message.author.name

                elif '{} all'.format(str(message.author.id)) in bot.log_conf['keyusers']:
                    if user_post(bot, '{} all'.format(str(message.author.id))):
                        user_found = message.author.name

            if word_found is True or user_found:
                if bot.log_conf['user_location'] != bot.log_conf['log_location'] and bot.log_conf['user_location'] != '' and not word_found:
                    location = bot.log_conf['user_location'].split()
                    is_separate = True
                else:
                    location = bot.log_conf['log_location'].split()
                    is_separate = False
                server = bot.get_server(location[1])
                if message.channel.id != location[0]:
                    msg = message.clean_content.replace('`', '')

                    context = []
                    try:
                        for i in range(0, int(bot.log_conf['context_len'])):
                            context.append(bot.all_log[message.channel.id + ' ' + message.server.id][len(bot.all_log[message.channel.id + ' ' + message.server.id])-i-2])
                        msg = ''
                        for i in range(0, int(bot.log_conf['context_len'])):
                            temp = context[len(context)-i-1][0]
                            if temp.clean_content:
                                msg += 'User: %s | %s\n' % (temp.author.name, temp.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + temp.clean_content.replace('`', '') + '\n\n'
                        msg += 'User: %s | %s\n' % (message.author.name, message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + message.clean_content.replace('`', '')
                        success = True
                    except:
                        success = False
                        msg = 'User: %s | %s\n' % (message.author.name, message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + msg

                    part = int(math.ceil(len(msg) / 1950))
                    if user_found:
                        title = '%s posted' % user_found
                    else:
                        title = '%s mentioned: %s' % (message.author.name, word)
                    if part == 1 and success is True:
                        em = discord.Embed(timestamp=message.timestamp, color=0xbc0b0b, title=title, description='Server: ``%s``\nChannel: <#%s> | %s\n\n**Context:**' % (str(message.server), str(message.channel.id), message.channel.name))
                        for i in range(0, int(bot.log_conf['context_len'])):
                            temp = context.pop()
                            if temp[0].clean_content:
                                em.add_field(name='%s' % temp[0].author.name, value=temp[0].clean_content, inline=False)
                        em.add_field(name='%s' % message.author.name, value=message.clean_content, inline=False)
                        try:
                            em.set_thumbnail(url=message.author.avatar_url)
                        except:
                            pass
                        if bot.notify['type'] == 'msg':
                            await webhook(em, 'embed', is_separate)
                        elif bot.notify['type'] == 'ping':
                            await webhook(em, 'embed ping', is_separate)
                        else:
                            await bot.send_message(server.get_channel(location[0]), embed=em)
                    else:
                        split_list = [msg[i:i + 1950] for i in range(0, len(msg), 1950)]
                        all_words = []
                        split_msg = ''
                        for i, blocks in enumerate(split_list):
                            for b in blocks.split('\n'):
                                split_msg += b + '\n'
                            all_words.append(split_msg)
                            split_msg = ''
                        if user_found:
                            logged_msg = '``%s`` posted' % user_found
                        else:
                            logged_msg = '``%s`` mentioned' % word
                        for b, i in enumerate(all_words):
                            if b == 0:
                                if bot.notify['type'] == 'msg':
                                    await webhook(bot.bot_prefix + '%s in server: ``%s`` Context: Channel: <#%s> | %s\n\n```%s```' % (logged_msg, str(message.server), str(message.channel.id), message.channel.name, i), 'message', is_separate)
                                elif bot.notify['type'] == 'ping':
                                    await webhook(bot.bot_prefix + '%s in server: ``%s`` Context: Channel: <#%s> | %s\n\n```%s```' % (logged_msg, str(message.server), str(message.channel.id), message.channel.name, i), 'message ping', is_separate)
                                else:
                                    await bot.send_message(server.get_channel(location[0]), bot.bot_prefix + '%s in server: ``%s`` Context: Channel: <#%s>\n\n```%s```' % (logged_msg, str(message.server), str(message.channel.id), i))
                            else:
                                if bot.notify['type'] == 'msg':
                                    await webhook('```%s```' % i, 'message', is_separate)
                                elif bot.notify['type'] == 'ping':
                                    await webhook('```%s```' % i, 'message ping', is_separate)
                                else:
                                    await bot.send_message(server.get_channel(location[0]), '```%s```' % i)
                    bot.keyword_log += 1

        # Bad habit but this is for skipping errors when dealing with Direct messages, blocked users, etc. Better to just ignore.
        except (AttributeError, discord.errors.HTTPException):
            pass

    await bot.process_commands(message)


def add_alllog(channel, server, message):
    if not hasattr(bot, 'all_log'):
        bot.all_log = {}
    if channel + ' ' + server in bot.all_log:
        bot.all_log[channel + ' ' + server].append((message, message.clean_content))
    else:
        bot.all_log[channel + ' ' + server] = collections.deque(maxlen=int(get_config_value('log', 'log_size', 25)))
        bot.all_log[channel + ' ' + server].append((message, message.clean_content))


def remove_alllog(channel, server):
    del bot.all_log[channel + ' ' + server]


# Webhook for keyword notifications
async def webhook(keyword_content, send_type, is_separate):
    if not is_separate:
        temp = bot.log_conf['webhook_url'].split('/')
    else:
        temp = bot.log_conf['webhook_url2'].split('/')
    channel = temp[len(temp) - 2]
    token = temp[len(temp) - 1]
    webhook_class = Webhook(bot)
    request_webhook = webhook_class.request_webhook
    if send_type.startswith('embed'):
        if 'ping' in send_type:
            await request_webhook('/{}/{}'.format(channel, token), embeds=[keyword_content.to_dict()], content=bot.user.mention)
        else:
            await request_webhook('/{}/{}'.format(channel, token), embeds=[keyword_content.to_dict()], content=None)
    else:
        if 'ping' in send_type:
            await request_webhook('/{}/{}'.format(channel, token), content=keyword_content + '\n' + bot.user.mention, embeds=None)
        else:
            await request_webhook('/{}/{}'.format(channel, token), content=keyword_content, embeds=None)

# Set/cycle game
async def game_and_avatar(bot):
    await bot.wait_until_ready()
    current_game = next_game = current_avatar = next_avatar = 0
    while not bot.is_closed:

        # Cycles game if game cycling is enabled.
        if hasattr(bot, 'game_time') and hasattr(bot, 'game'):
            if bot.game:
                if bot.game_interval:
                    if game_time_check(bot, bot.game_time, bot.game_interval):
                        with open('settings/games.json', encoding="utf8") as g:
                            games = json.load(g)
                        if games['type'] == 'random':
                            while next_game == current_game:
                                next_game = random.randint(0, len(games['games']) - 1)
                            current_game = next_game
                            bot.game = games['games'][next_game]
                            if bot.is_stream and '=' in games['games'][next_game]:
                                g, url = games['games'][next_game].split('=')
                                await bot.change_presence(game=discord.Game(name=g, type=1,
                                                                            url=url),
                                                          status=set_status(bot), afk=True)
                            else:
                                await bot.change_presence(game=discord.Game(name=games['games'][next_game]), status=set_status(bot), afk=True)
                        else:
                            if next_game+1 == len(games['games']):
                                next_game = 0
                            else:
                                next_game += 1
                            bot.game = games['games'][next_game]
                            if bot.is_stream and '=' in games['games'][next_game]:
                                g, url = games['games'][next_game].split('=')
                                await bot.change_presence(game=discord.Game(name=g, type=1, url=url), status=set_status(bot), afk=True)
                            else:
                                await bot.change_presence(game=discord.Game(name=games['games'][next_game]), status=set_status(bot), afk=True)

                else:
                    if game_time_check(bot, bot.game_time, 180):
                        with open('settings/games.json', encoding="utf8") as g:
                            games = json.load(g)

                        bot.game = games['games']
                        if bot.is_stream and '=' in games['games']:
                            g, url = games['games'].split('=')
                            await bot.change_presence(game=discord.Game(name=g, type=1, url=url), status=set_status(bot), afk=True)
                        else:
                            await bot.change_presence(game=discord.Game(name=games['games']), status=set_status(bot), afk=True)

        # Cycles avatar if avatar cycling is enabled.
        if hasattr(bot, 'avatar_time') and hasattr(bot, 'avatar'):
            if bot.avatar:
                if bot.avatar_interval:
                    if avatar_time_check(bot, bot.avatar_time, bot.avatar_interval):
                        with open('settings/avatars.json', encoding="utf8") as g:
                            avi_config = json.load(g)
                        all_avis = glob.glob('avatars/*.jpg')
                        all_avis.extend(glob.glob('avatars/*.jpeg'))
                        all_avis.extend(glob.glob('avatars/*.png'))
                        all_avis = os.listdir('avatars')
                        all_avis.sort()
                        if avi_config['type'] == 'random':
                            while next_avatar == current_avatar:
                                next_avatar = random.randint(0, len(all_avis) - 1)
                            current_avatar = next_avatar
                            bot.avatar = all_avis[next_avatar]
                            with open('avatars/%s' % bot.avatar, 'rb', encoding="utf8") as fp:
                                await bot.edit_profile(password=avi_config['password'], avatar=fp.read())
                        else:
                            if next_avatar + 1 == len(all_avis):
                                next_avatar = 0
                            else:
                                next_avatar += 1
                            bot.avatar = all_avis[next_avatar]
                            with open('avatars/%s' % bot.avatar, 'rb', encoding="utf8") as fp:
                                await bot.edit_profile(password=avi_config['password'], avatar=fp.read())

        # Sets status to default status when user goes offline (client status takes priority when user is online)
        if hasattr(bot, 'refresh_time'):
            if has_passed(bot, bot.refresh_time):
                if bot.game and bot.is_stream and '=' in bot.game:
                    g, url = bot.game.split('=')
                    await bot.change_presence(game=discord.Game(name=g, type=1, url=url), status=set_status(bot), afk=True)
                elif bot.game and not bot.is_stream:
                    await bot.change_presence(game=discord.Game(name=bot.game),
                                              status=set_status(bot), afk=True)
                else:
                    await bot.change_presence(status=set_status(bot), afk=True)

        if hasattr(bot, 'gc_time'):
            if gc_clear(bot, bot.gc_time):
                gc.collect()

        await asyncio.sleep(5)

if __name__ == '__main__':
    for extension in os.listdir("cogs"):
        if extension.endswith('.py'):
            try:
                bot.load_extension("cogs." + extension[:-3])
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.loop.create_task(game_and_avatar(bot))

    while True:
        try:
            try:
                bot.run(get_config_value('config', 'token'), bot=False)
            except (KeyError, discord.errors.LoginFailure):
                bot.run(os.environ['TOKEN'], bot=False)
        except (KeyError, discord.errors.LoginFailure):
            if _silent:
                print('Cannot use setup Wizard becaue of silent mode')
                exit(0)
            print("It seems the token you entered is incorrect or has changed. If you changed your password or enabled/disabled 2fa, your token will change. Grab your new token. Here's how you do it:\n")
            print("Go into your Discord window and press Ctrl+Shift+I (Ctrl+Opt+I can also work on macOS)")
            print("Then, go into the Applications tab (you may have to click the arrow at the top right to get there), expand the 'Local Storage' dropdown, select discordapp, and then grab the token value at the bottom. Here's how it looks: https://imgur.com/h3g9uf6")
            print("Paste the contents of that entry below.")
            print("-------------------------------------------------------------")
            token = input("| ").strip('"')
            with open("settings/config.json", "r+", encoding="utf8") as fp:
                config = json.load(fp)
                config["token"] = token
                fp.seek(0)
                fp.truncate()
                json.dump(config, fp, indent=4)
            continue
        break
