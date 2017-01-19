import asyncio
import os
import sys
import math
import time
from datetime import timezone
from discord.ext import commands
from utils.allmsgs import *
import utils.settings


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

extensions = ['utils.afk', 'utils.customcmds', 'utils.google', 'utils.keywordlog', 'utils.mal', 'utils.misc', 'utils.userinfo']

utils.settings.keywordlog = {}
isBot = config['bot_identifier'] + ' '
if isBot == ' ':
    isBot = ''
allLogs = {}


def hasPassed(oldtime):
    if time.time() - 10 < oldtime:
        return False
    utils.settings.oldtime = time.time()
    return True


bot = commands.Bot(command_prefix=config['cmd_prefix'][0], description='''Selfbot by appu1232''', self_bot=True)

# Startup
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
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

# @bot.event
# async def on_error(event, args):
#     pass
#     if event is ConnectionResetError or ConnectionRefusedError or ConnectionError or ConnectionAbortedError or TimeoutError:
#         sys.exit(1)


# On all messages sent (for quick commands, custom commands, and logging messages)
@bot.event
async def on_message(message):

    # Sets status to idle when I go offline (won't trigger while I'm online so this prevents me from appearing online all the time)
    if hasPassed(utils.settings.oldtime):
        await bot.change_presence(status='invisible', afk=True)
    # if message.channel.id not in utils.settings.load_config():
    #     utils.settings.alllog[message.channel.id] = collections.deque(maxlen=500)
    # utils.settings.alllog[message.channel.id]

    # If the message was sent by me
    if message.author.id == config['my_id']:
        utils.settings.add_selflog(message)
        if message.content.startswith(config['customcmd_prefix'][0]):
            response = custom(message.content.lower().strip())
            if response is None:
                pass
            else:
                if response[0] == 'embed':
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
        response = afk(notified)
        if response:
            await bot.send_message(message.channel, response)

    try:
        wordfound = False
        with open('utils/log.json', 'r') as log:
            loginfo = json.load(log)
        if loginfo['allservers'] == 'True':
            utils.settings.add_alllog(message.channel.id, message.server.id, message)
            for word in loginfo['keywords']:
                if word.lower() in message.content.lower() and message.author.id != config['my_id']:
                    wordfound = True
                    break
        else:
            if str(message.server.id) in loginfo['servers']:
                utils.settings.add_alllog(message.channel.id, message.server.id, message)
                for word in loginfo['keywords']:
                    if word.lower() in message.content.lower() and message.author.id != config['my_id']:
                        wordfound = True
                        break

        if wordfound is True:
            location = loginfo['log_location'].split()
            server = bot.get_server(location[1])
            if message.channel.id != location[0] and message.server.id != location[1]:
                msg = message.clean_content.replace('`', '')
                if word.startswith('<@'):
                    user = message.server.get_member(word[2:-1])
                    user = user.name
                    word = user

                try:
                    context = []
                    for i in range(0, int(loginfo['context_len'])):
                        context.append(utils.settings.alllog[message.channel.id + ' ' + message.server.id][len(utils.settings.alllog[message.channel.id + ' ' + message.server.id])-i-2])
                    msg = ''
                    for i in range(0, int(loginfo['context_len'])):
                        temp = context[len(context)-i-1]
                        msg += 'User: %s | %s\n' % (temp.author.name, temp.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + temp.clean_content + '\n\n'
                    msg += 'User: %s | %s\n' % (message.author.name, message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + message.clean_content
                    success = True
                except:
                    success = False
                    msg = 'User: %s | %s\n' % (message.author.name, message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + msg

                part = int(math.ceil(len(msg) / 1950))
                if part == 1 and success is True:
                    em = discord.Embed(timestamp=message.timestamp, color=0xbc0b0b, title='%s mentioned: %s' % (message.author.name, word), description='Server: ``%s``\nChannel: ``%s``\n\n**Context:**' % (str(message.server), str(message.channel)))
                    for i in range(0, int(loginfo['context_len'])):
                        temp = context.pop()
                        em.add_field(name='%s' % temp.author.name, value=temp.clean_content, inline=False)
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

    except:
        pass

    await bot.process_commands(message)


if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    bot.run(config['token'], bot=False)
