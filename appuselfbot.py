import asyncio
import os
import sys
import math
import time
import datetime
import collections
import gc
import traceback
from datetime import timezone
from discord.ext import commands
from utils.allmsgs import *


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

extensions = ['utils.afk', 'utils.customcmds', 'utils.google', 'utils.keywordlog', 'utils.mal', 'utils.misc', 'utils.spellcheck', 'utils.userinfo']

isBot = config['bot_identifier'] + ' '
if isBot == ' ':
    isBot = ''


def hasPassed(oldtime):
    if time.time() - 10 < oldtime:
        return False
    bot.refresh_time = time.time()
    return True


bot = commands.Bot(command_prefix=config['cmd_prefix'][0], description='''Selfbot by appu1232''', self_bot=True)

# Startup
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    if not hasattr(bot, 'subprocesses'):
        bot.subprocesses = 0
    if not hasattr(bot, 'running_procs'):
        bot.running_procs = []
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.now()
    if not hasattr(bot, 'icount'):
        bot.icount = 0
    if not hasattr(bot, 'message_count'):
        bot.message_count = 0
    if not hasattr(bot, 'mention_count'):
        bot.mention_count = 0
    if not hasattr(bot, 'self_log'):
        bot.self_log = collections.deque(maxlen=200)
    if not hasattr(bot, 'all_log'):
        bot.all_log = {}
    if not hasattr(bot, 'keyword_log'):
        bot.keyword_log = 0
    if not hasattr(bot, 'refresh_time'):
        bot.refresh_time = time.time()
    if not hasattr(bot, 'game'):
        bot.game = None
    if os.path.isfile('restart.txt'):
        with open('restart.txt', 'r') as re:
            channel = bot.get_channel(re.readline())
            await bot.send_message(channel, isBot + 'Bot has restarted.')
        os.remove('restart.txt')


# Restart selfbot
@bot.command(pass_context=True)
async def restart(ctx):
    await bot.edit_message(ctx.message, isBot + 'Restarting...')
    with open('restart.txt', 'w') as re:
        re.write(str(ctx.message.channel.id))
    python = sys.executable
    os.execl(python, python, *sys.argv)

@bot.command(pass_context=True)
async def quit(ctx):
    await bot.send_message(ctx.message.channel, isBot + 'Bot has been killed.')
    exit()

# Comment out these two functions if you want to see full traceback for errors
# @bot.event
# async def on_error(event, *args):
#     if event is ConnectionAbortedError or event is ConnectionError or event is ConnectionRefusedError or event is ConnectionResetError:
#         gc.collect()
#         sys.exit(1)
#
# # Comment out to see the traceback
# @bot.event
# async def on_command_error(error, ctx):
#     if isinstance(error, commands.NoPrivateMessage):
#         await bot.send_message(ctx.message.channel, 'This command is not supported in direct messages.')

# On all messages sent (for quick commands, custom commands, and logging messages)
@bot.event
async def on_message(message):

    await bot.wait_until_ready()
    await bot.wait_until_login()
    if hasattr(bot, 'message_count'):
        bot.message_count += 1

    # Sets status to idle when I go offline (won't trigger while I'm online so this prevents me from appearing online all the time)
    if hasattr(bot, 'refresh_time'):
        if hasPassed(bot.refresh_time):
            if bot.game is None:
                await bot.change_presence(status='invisible', afk=True)
            else:
                await bot.change_presence(game=discord.Game(name=bot.game), status='invisible', afk=True)

    # If the message was sent by me
    if message.author.id == config['my_id']:
        bot.icount += 1
        bot.self_log.append(message)
        if message.content.startswith(config['customcmd_prefix'][0]):
            response = custom(message.content.lower().strip())
            if response is None:
                pass
            else:
                if response[0] == 'embed' and message.author.permissions_in(message.channel).attach_files:
                    await bot.send_message(message.channel, content=None, embed=discord.Embed(colour=0x27007A).set_image(url=response[1]))
                else:
                    await bot.send_message(message.channel, response[1])
                await asyncio.sleep(2)
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
        wordfound = False
        with open('utils/log.json', 'r') as log:
            loginfo = json.load(log)
        if loginfo['allservers'] == 'True':
            add_alllog(message.channel.id, message.server.id, message)
            for word in loginfo['keywords']:
                if word.lower() in message.content.lower() and message.author.id != config['my_id']:
                    wordfound = True
                    break
        else:
            if str(message.server.id) in loginfo['servers']:
                add_alllog(message.channel.id, message.server.id, message)
                for word in loginfo['keywords']:
                    if word.lower() in message.content.lower() and message.author.id != config['my_id']:
                        wordfound = True
                        break

        if wordfound is True:
            location = loginfo['log_location'].split()
            server = bot.get_server(location[1])
            if message.channel.id != location[0] and message.server.id != location[1]:
                msg = message.clean_content.replace('`', '')

                try:
                    context = []
                    for i in range(0, int(loginfo['context_len'])):
                        context.append(bot.all_log[message.channel.id + ' ' + message.server.id][len(bot.all_log[message.channel.id + ' ' + message.server.id])-i-2])
                    msg = ''
                    for i in range(0, int(loginfo['context_len'])):
                        temp = context[len(context)-i-1][0]
                        msg += 'User: %s | %s\n' % (temp.author.name, temp.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + temp.clean_content.replace('`', '') + '\n\n'
                    msg += 'User: %s | %s\n' % (message.author.name, message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + message.clean_content.replace('`', '')
                    success = True
                except:
                    success = False
                    msg = 'User: %s | %s\n' % (message.author.name, message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + msg

                part = int(math.ceil(len(msg) / 1950))
                if part == 1 and success is True:
                    em = discord.Embed(timestamp=message.timestamp, color=0xbc0b0b, title='%s mentioned: %s' % (message.author.name, word), description='Server: ``%s``\nChannel: ``%s``\n\n**Context:**' % (str(message.server), str(message.channel)))
                    for i in range(0, int(loginfo['context_len'])):
                        temp = context.pop()
                        em.add_field(name='%s' % temp[0].author.name, value=temp[0].clean_content, inline=False)
                    em.add_field(name='%s' % message.author.name, value=message.clean_content, inline=False)
                    try:
                        em.set_thumbnail(url=message.author.avatar_url)
                    except:
                        pass
                    await bot.send_message(server.get_channel(location[0]), embed=em)
                else:
                    splitList = [msg[i:i + 1950] for i in range(0, len(msg), 1950)]
                    allWords = []
                    splitmsg = ''
                    for i, blocks in enumerate(splitList):
                        for b in blocks.split('\n'):
                            splitmsg += b + '\n'
                        allWords.append(splitmsg)
                        splitmsg = ''
                    for b,i in enumerate(allWords):
                        if b == 0:
                            await bot.send_message(server.get_channel(location[0]), isBot + 'Keyword ``%s`` mentioned in server: ``%s`` Context: ```Channel: %s\n\n%s```' % (word, str(message.server), str(message.channel), i))
                        else:
                            await bot.send_message(server.get_channel(location[0]), '```%s```' % i)
                bot.keyword_log += 1

    except:
        pass

    await bot.process_commands(message)


def add_alllog(channel, server, message):
    if channel + ' ' + server in bot.all_log:
        bot.all_log[channel + ' ' + server].append((message, message.clean_content))
    else:
        with open('utils/log.json') as f:
            config = json.load(f)
            bot.all_log[channel + ' ' + server] = collections.deque(maxlen=int(config['log_size']))
            bot.all_log[channel + ' ' + server].append((message, message.clean_content))


def remove_alllog(channel, server):
    del bot.all_log[channel + ' ' + server]


if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    bot.run(config['token'], bot=False)
