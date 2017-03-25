import os
import math
import subprocess
import datetime
import collections
from datetime import timezone
from discord.ext import commands
from cogs.utils.allmsgs import *
from cogs.utils.checks import *


def load_config():
    with open('settings/config.json', 'r') as f:
        return json.load(f)

config = load_config()

isBot = config['bot_identifier'] + ' '
if isBot == ' ':
    isBot = ''

bot = commands.Bot(command_prefix=config['cmd_prefix'][0], description='''Selfbot by appu1232''', self_bot=True)


# Startup
@bot.event
async def on_ready():
    print('Logging in...')
    try:
        print(bot.user.name)
    except:
        print(bot.user.name.encode("utf-8"))
    print(bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.now()
    if not hasattr(bot, 'icount'):
        bot.icount = 0
    if not hasattr(bot, 'message_count'):
        bot.message_count = 0
    if not hasattr(bot, 'mention_count'):
        bot.mention_count = 0
    if not hasattr(bot, 'self_log'):
        bot.self_log = {}
    if not hasattr(bot, 'all_log'):
        bot.all_log = {}
    if not hasattr(bot, 'keyword_log'):
        bot.keyword_log = 0
    if not hasattr(bot, 'refresh_time'):
        bot.refresh_time = time.time()
    if not hasattr(bot, 'game'):
        bot.game = None
    if not hasattr(bot, 'game_interval'):
        bot.game_interval = None
    if not hasattr(bot, 'subpro'):
        bot.subpro = None
    if not hasattr(bot, 'log_conf'):
        with open('settings/log.json', 'r') as log:
            bot.log_conf = json.load(log)
    if os.path.isfile('restart.txt'):
        with open('restart.txt', 'r') as re:
            channel = bot.get_channel(re.readline())
            print('Bot has restarted.')
            await bot.send_message(channel, isBot + 'Bot has restarted.')
        os.remove('restart.txt')
    with open('settings/log.json', 'r+') as log:
        loginfo = json.load(log)
        try:
            if 'blacklisted_words' not in loginfo:
                loginfo['blacklisted_words'] = []
            if 'blacklisted_servers' not in loginfo:
                loginfo['blacklisted_servers'] = []
        except:
            pass
        log.seek(0)
        log.truncate()
        json.dump(loginfo, log, indent=4)
    with open('settings/notify.json', 'r') as n:
        notif = json.load(n)
    if notif['notify'] == 'on':
        try:
            bot.subpro = subprocess.Popen(['python3', 'cogs/utils/notify.py'])
        except (SyntaxError, FileNotFoundError):
            bot.subpro = subprocess.Popen(['python', 'cogs/utils/notify.py'])
        except:
            pass


@bot.command(pass_context=True, aliases=['reboot'])
async def restart(ctx):
    """Restarts the bot."""
    print('Restarting...')
    await bot.edit_message(ctx.message, isBot + 'Restarting...')
    if bot.subpro:
        bot.subpro.kill()
    with open('restart.txt', 'w') as re:
        re.write(str(ctx.message.channel.id))
    os._exit(0)


@bot.command(pass_context=True, aliases=['exit'])
async def quit(ctx):
    """Quits the bot."""
    print('Bot exiting...')
    if bot.subpro:
        bot.subpro.kill()
    with open('quit.txt', 'w') as q:
        q.write('.')
    await bot.send_message(ctx.message.channel, isBot + 'Bot shut down.')
    os._exit(0)


@bot.command(pass_context=True)
async def reload(ctx):
    """Reloads all modules."""
    utils = []
    for i in bot.extensions:
        utils.append(i)
    fail = False
    for i in utils:
        bot.unload_extension(i)
        try:
            bot.load_extension(i)
        except:
            await bot.send_message(ctx.message.channel, isBot + 'Failed to reload extension ``%s``' % i)
            fail = True
    if fail:
        await bot.send_message(ctx.message.channel, isBot + 'Reloaded remaining extensions.')
    else:
        await bot.send_message(ctx.message.channel, isBot + 'Reloaded all extensions.')


# On all messages sent (for quick commands, custom commands, and logging messages)
@bot.event
async def on_message(message):

    await bot.wait_until_ready()
    await bot.wait_until_login()
    if hasattr(bot, 'message_count'):
        bot.message_count += 1

    # Sets status to idle when I go offline (won't trigger while I'm online so this prevents me from appearing online all the time)
    if hasattr(bot, 'refresh_time'):
        if hasPassed(bot, bot.refresh_time) and not bot.game_interval:
            if bot.game is None:
                await bot.change_presence(game=discord.Game(name=None), status='invisible', afk=True)
            else:
                await bot.change_presence(game=discord.Game(name=bot.game.decode('utf-8')), status='invisible', afk=True)

    # If the message was sent by me
    if message.author.id == config['my_id']:
        if message.channel.id not in bot.self_log:
            bot.self_log[message.channel.id] = collections.deque(maxlen=100)
        bot.self_log[message.channel.id].append(message)
        bot.icount += 1
        if message.content.startswith(config['customcmd_prefix'][0]):
            response = custom(message.content.lower().strip())
            if response is None:
                pass
            else:
                if response[0] == 'embed' and embed_perms(message):
                    try:
                        await bot.send_message(message.channel, content=None, embed=discord.Embed(colour=0x27007A).set_image(url=response[1]))
                    except:
                        await bot.send_message(message.channel, response[1])
                else:
                    await bot.send_message(message.channel, response[1])
                await bot.delete_message(message)
        else:
            response = quickcmds(message.content.lower().strip())
            if response:
                await bot.delete_message(message)
                await bot.send_message(message.channel, response)

    notified = message.mentions
    if notified:
        for i in notified:
            if i.id == config['my_id']:
                bot.mention_count += 1
        response = afk(notified)
        if response:
            await bot.send_message(message.channel, response)

    try:
        word_found = False
        if not hasattr(bot, 'log_conf'):
            with open('settings/log.json', 'r') as log:
                bot.log_conf = json.load(log)
        if bot.log_conf['allservers'] == 'True' and message.server.id not in bot.log_conf['blacklisted_servers']:
            add_alllog(message.channel.id, message.server.id, message)
            for word in bot.log_conf['keywords']:
                if word.lower() in message.content.lower() and message.author.id != config['my_id']:
                    word_found = True
                    for x in bot.log_conf['blacklisted_users']:
                        if message.author.id == x:
                            word_found = False
                            break
                    for x in bot.log_conf['blacklisted_words']:
                        if '[server]' in x:
                            bword, id = x.split('[server]')
                            if bword.strip().lower() in message.content.lower() and message.server.id == id:
                                word_found = False
                                break
                        if x.lower() in message.content.lower():
                            word_found = False
                            break
                    break
        else:
            if str(message.server.id) in bot.log_conf['servers']:
                add_alllog(message.channel.id, message.server.id, message)
                for word in bot.log_conf['keywords']:
                    if word.lower() in message.content.lower() and message.author.id != config['my_id']:
                        word_found = True
                        for x in bot.log_conf['blacklisted_users']:
                            if message.author.id == x:
                                word_found = False
                                break
                        for x in bot.log_conf['blacklisted_words']:
                            if '[server]' in x:
                                bword, id = x.split('[server]')
                                if bword.strip().lower() in message.content.lower() and message.server.id == id:
                                    word_found = False
                                    break
                            if x.lower() in message.content.lower():
                                word_found = False
                                break
                        break

        if word_found is True:
            location = bot.log_conf['log_location'].split()
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
                if part == 1 and success is True:
                    em = discord.Embed(timestamp=message.timestamp, color=0xbc0b0b, title='%s mentioned: %s' % (message.author.name, word), description='Server: ``%s``\nChannel: ``%s``\n\n**Context:**' % (str(message.server), str(message.channel)))
                    for i in range(0, int(bot.log_conf['context_len'])):
                        temp = context.pop()
                        if temp[0].clean_content:
                            em.add_field(name='%s' % temp[0].author.name, value=temp[0].clean_content, inline=False)
                    em.add_field(name='%s' % message.author.name, value=message.clean_content, inline=False)
                    try:
                        em.set_thumbnail(url=message.author.avatar_url)
                    except:
                        pass
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
                    for b,i in enumerate(all_words):
                        if b == 0:
                            await bot.send_message(server.get_channel(location[0]), isBot + 'Keyword ``%s`` mentioned in server: ``%s`` Context: ```Channel: %s\n\n%s```' % (word, str(message.server), str(message.channel), i))
                        else:
                            await bot.send_message(server.get_channel(location[0]), '```%s```' % i)
                bot.keyword_log += 1

    except:
        pass

    await bot.process_commands(message)


def add_alllog(channel, server, message):
    if not hasattr(bot, 'all_log'):
        bot.all_log = {}
    if channel + ' ' + server in bot.all_log:
        bot.all_log[channel + ' ' + server].append((message, message.clean_content))
    else:
        with open('settings/log.json') as f:
            config = json.load(f)
            bot.all_log[channel + ' ' + server] = collections.deque(maxlen=int(config['log_size']))
            bot.all_log[channel + ' ' + server].append((message, message.clean_content))


def remove_alllog(channel, server):
    del bot.all_log[channel + ' ' + server]


if __name__ == '__main__':

    for extension in os.listdir("cogs"):
        if extension.endswith('.py'):
            try:
                bot.load_extension("cogs." + extension.rstrip(".py"))
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run(config['token'], bot=False)
