import asyncio
import collections
import os
import sys
from discord.ext import commands
from utils.allmsgs import *
import utils.settings

with open('config.json', 'r') as f:
    config = json.load(f)

extensions = ['utils.afk', 'utils.customcmds', 'utils.google', 'utils.mal', 'utils.misc', 'utils.userinfo']

utils.settings.selflog = collections.deque(maxlen=200)
isBot = config['bot_identifier'] + ' '
if isBot == ' ':
    isBot = ''
allLogs = {}

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


def load_config():
    with open('config.json') as f:
        return json.load(f)


# Restart selfbot
@bot.command(pass_context=True)
async def restart(ctx):
    await bot.edit_message(ctx.message, isBot + 'Restarting...')
    with open('restart.txt', 'w') as re:
        re.write(str(ctx.message.channel.id))
    python = sys.executable
    os.execl(python, python, *sys.argv)


# On all messages sent (for quick commands, custom commands, and logging messages)
@bot.event
async def on_message(message):

    # Sets status to idle when I go offline (won't trigger while I'm online so this prevents me from appearing online all the time)
    await bot.change_presence(status='invisible', afk=True)

    # If the message was sent by me
    if message.author.id == config['my_id']:
        utils.settings.selflog.append(message)
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

    await bot.process_commands(message)


if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    bot.run(config['token'], bot=False)
