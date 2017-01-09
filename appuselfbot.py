import discord, datetime, traceback, re, asyncio, mimetypes, collections, math
import subprocess, sys
from discord.ext import commands
import json
import spice_api as spice
import urllib.request, urllib.parse, requests
from random import randint
from bs4 import BeautifulSoup

# Discord Logger
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)
# bot = discord.bot()

with open('config.json', 'r') as f:
    config = json.load(f)

selflog = collections.deque(maxlen=5)

bot = commands.Bot(command_prefix='>', description='''Selfbot by appu1232''', self_bot=True)

# Startup
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# Restart selfbot
@bot.command(pass_context=True)
async def restart(ctx):
    await bot.edit_message(ctx.message, 'Restarting...')
    subprocess.call(['python3', __file__])

# Simple calculator
@bot.command(pass_context=True)
async def calc(ctx):
    if ctx.message.author.id == config['my_id']:
        equation = ctx.message.content[5:].strip()
        if '=' in equation:
            left = eval(equation.split('=')[0])
            right = eval(equation.split('=')[1])
            await bot.send_message(ctx.message.channel, str(left == right))
        else:
            await bot.send_message(ctx.message.channel, str(eval(equation)))

# Get response time
@bot.command(pass_context=True)
async def ping(ctx):
    if ctx.message.author.id == config['my_id']:
        msgTime = ctx.message.timestamp.now()
        await bot.send_message(ctx.message.channel, 'pong')
        now = datetime.datetime.now()
        ping = now - msgTime
        pong = discord.Embed(title='Response Time:', description=str(ping), color=0x7A0000)
        pong.set_thumbnail(url='http://odysseedupixel.fr/wp-content/gallery/pong/pong.jpg')
        await bot.send_message(ctx.message.channel, content=None, embed=pong)

# Mal search (chained with either anime or manga)
@bot.group(pass_context=True)
async def mal(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.bot.send_message(ctx.message.channel, "```Invalid Command. Use $help for more info```")


# Anime search for Mal
@mal.command(pass_context=True)
async def anime(ctx):
    try:

        # Search google for the anime under site:myanimelist.net
        searchUrl = "https://www.googleapis.com/customsearch/v1?q=site:myanimelist.net anime " + ctx.message.content[
                    11:] + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config[
                        'custom_search_engine']
        r = requests.get(searchUrl)
        response = r.content.decode('utf-8')
        result = json.loads(response)
        animeName = re.findall('<title>\n(.*) - MyAnimeList', str(urllib.request.urlopen(result['items'][0]['link']).read().decode('utf-8')))
        results = spice.search(animeName[0], spice.get_medium('anime'),
                               spice.init_auth(config['mal_username'], config['mal_password']))

        # If no results found or daily api limit exceeded, use spice's search
        if not results:
            results = spice.search(ctx.message.content[11:], spice.get_medium('anime'),
                                   spice.init_auth(config['mal_username'], config['mal_password']))

    # On any exception, search spice instead
    except:
        results = spice.search(ctx.message.content[11:], spice.get_medium('anime'),
                               spice.init_auth(config['mal_username'], config['mal_password']))

    # No results found for specified tags
    if not results:
        await ctx.send_message(ctx.message.channel, 'No results.')
        return

    # Formatting embed
    selection = results[0]
    synopsis = BeautifulSoup(selection.synopsis, 'lxml')
    urlcontent = urllib.request.urlopen("https://myanimelist.net/anime/%s" % selection.id).read()
    imgurls = re.findall('img .*?src="(.*?)"', str(urlcontent))
    em = discord.Embed(title=selection.title, description = '''\n{link}\n\n**Episodes:** {episodes}\n**Avg Score:** {score}/10\n**Synopsis:**{synopsis}\n'''.format(link="https://myanimelist.net/anime/%s" % selection.id, title=selection.title, episodes=selection.episodes, score=selection.score, synopsis="\n" + synopsis.get_text()[:400] + '...[more](https://myanimelist.net/anime/%s)' % selection.id), colour=0x0066CC)
    for i in imgurls:
        if '/images/anime/' in i:
            em.set_thumbnail(url=i)
            break
    try:
        em.add_field(name='Type', value = selection.anime_type, inline=True)
        em.add_field(name='English', value=selection.english, inline=True)
        em.add_field(name='Status:', value=selection.status, inline=True)
        em.add_field(name='Airing Time:', value=selection.dates[0] + "  -  " + selection.dates[1], inline=True)
        em.set_author(name='MyAnimeList', icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
    except:
        pass
    await bot.send_message(ctx.message.channel, embed=em)

# Manga search for Mal
@mal.command(pass_context=True)
async def manga(ctx):
    try:

        # Search google for the manga under site:myanimelist.net
        searchUrl = "https://www.googleapis.com/customsearch/v1?q=site:myanimelist.net manga " + ctx.message.content[
                    11:] + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config[
                        'custom_search_engine']
        r = requests.get(searchUrl)
        response = r.content.decode('utf-8')
        result = json.loads(response)
        mangaName = re.findall('<title>\n(.*) - MyAnimeList', str(urllib.request.urlopen(result['items'][0]['link']).read().decode('utf-8')))
        results = spice.search(mangaName[0][:-7], spice.get_medium('manga'),
                               spice.init_auth(config['mal_username'], config['mal_password']))

        # If no results found or daily api limit exceeded, use spice's search
        if not results:
            results = spice.search(ctx.message.content[11:], spice.get_medium('manga'),
                                   spice.init_auth(config['mal_username'], config['mal_password']))

    # On any exception, search spice instead
    except:
        results = spice.search(ctx.message.content[11:], spice.get_medium('manga'),
                               spice.init_auth(config['mal_username'], config['mal_password']))

    # No results found for specified tags
    if not results:
        await ctx.bot.send_message(ctx.message.channel, 'No results.')
        return

    # Formatting
    selection = results[0]
    synopsis = BeautifulSoup(selection.synopsis, 'lxml')
    urlcontent = urllib.request.urlopen("https://myanimelist.net/manga/%s" % selection.id).read()
    imgurls = re.findall('img .*?src="(.*?)"', str(urlcontent))
    em = discord.Embed(title=selection.title, description = '''\n{link}\n\n**Chapters:** {chapters}\n**Avg Score:** {score}/10\n**Synopsis:**{synopsis}\n'''.format(link="https://myanimelist.net/manga/%s" % selection.id, title=selection.title, chapters=selection.chapters, score=selection.score, synopsis="\n" + synopsis.get_text()[:400] + '...[more](https://myanimelist.net/manga/%s)' % selection.id), colour=0x0066CC)
    for i in imgurls:
        if '/images/manga/' in i:
            em.set_thumbnail(url=i)
            break
    try:
        em.add_field(name='Type', value=selection.manga_type, inline=True)
        em.add_field(name='English', value=selection.english, inline=True)
        em.add_field(name='Status:', value=selection.status, inline=True)
        em.add_field(name='Publishing Time:', value=selection.dates[0] + "  -  " + selection.dates[1], inline=True)
        em.set_author(name='MyAnimeList', icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
    except:
        pass
    await bot.send_message(ctx.message.channel, embed=em)

# Google search
@bot.group(pass_context=True)
async def g(ctx):
    if ctx.message.author.id == config['my_id'] and not ctx.message.content[2:].startswith(' i '):

        # If >g then google web search with specified words
        if ctx.invoked_subcommand is None:
            searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                        ctx.message.content[
                        3:].strip() + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine']
            r = requests.get(searchUrl)
            response = r.content.decode('utf-8')
            result = json.loads(response)
            try:
                webpage = urllib.request.urlopen(result['items'][0]['link']).read()
                try:
                    title = str(webpage).split('<title>')[1].split('</title>')[0]
                except:
                    title = ''
                em = discord.Embed(title=result['items'][0]['link'], description=title, colour=0x2D5AF9)
                em.set_author(name='Google Results:\n\n')
                await bot.send_message(ctx.message.channel, embed=em)
            except Exception as e:
                await bot.send_message(ctx.message.channel, 'Error on reading url: %s. Error: %s.' % (result['items'][0]['link'], e))

        # >g <n> leads to nth result in google results.
        else:
            searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                        ctx.message.content[5:].strip() + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine']
            r = requests.get(searchUrl)
            response = r.content.decode('utf-8')
            result = json.loads(response)
            webpage = urllib.request.urlopen(result['items'][int(ctx.message.content[3])]['link']).read()
            try:
                title = str(webpage).split('<title>')[1].split('</title>')[0]
            except:
                title = ''
            em = discord.Embed(title=result['items'][int(ctx.message.content[3])]['link'], description=title, colour=0x2D5AF9)
            em.set_author(name='Google Results:\n\n')
            await bot.send_message(ctx.message.channel, embed=em)

@g.command(pass_context=True)
async def i(ctx):
    if ctx.message.author.id == config['my_id']:

        # If >g i then google image search with specified words
        if not ctx.message.content[5].isdigit():
            searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                        ctx.message.content[
                        5:].strip() + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine'] + \
                        "&searchType=image"
            r = requests.get(searchUrl)
            response = r.content.decode('utf-8')
            result = json.loads(response)

            # Send as embed
            em=discord.Embed()
            await bot.send_message(ctx.message.channel, content=None, embed=em.set_image(url=result['items'][0]['link']))

        # >g i <n> leads to nth result in google image results.
        else:
            searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                        ctx.message.content[
                        7:].strip() + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine'] + \
                        "&searchType=image"
            r = requests.get(searchUrl)
            response = r.content.decode('utf-8')
            result = json.loads(response)

            # Send as embed
            em = discord.Embed()
            await bot.send_message(ctx.message.channel, content=None, embed=em.set_image(url=result['items'][int(ctx.message.content[5])]['link']))

# Sends a googleitfor.me link with the specified tags
@bot.command(pass_context=True)
async def l2g(ctx):
    if ctx.message.author.id == config['my_id']:
        lmgtfy = 'http://googleitfor.me/?q='
        words = ctx.message.content[5:].lower().strip().split(' ')
        for word in words:
            lmgtfy += word + '+'
        await bot.send_message(ctx.message.channel, lmgtfy[:-1])

# Set afk status on or off. If on, pinging will lead to an automated response.
@bot.command(pass_context=True)
async def setafk(ctx):
    if ctx.message.content[7:].lower().strip() == 'on':
        with open('config.json', 'r+') as conf:
            cf = json.load(conf)
            cf['set_afk'] = 'on'
            conf.seek(0)
            conf.truncate()
            json.dump(cf, conf, indent=4)
        await bot.send_message(ctx.message.channel, 'AFK on')
    elif ctx.message.content[7:].lower().strip() == 'off':
        with open('config.json', 'r+') as conf:
            cf = json.load(conf)
            cf['set_afk'] = 'off'
            conf.seek(0)
            conf.truncate()
            json.dump(cf, conf, indent=4)
        await bot.send_message(ctx.message.channel, 'AFK off')
    else:
        await bot.send_message(ctx.message.channel, 'Invalid argument.')

# Set afk message
@bot.command(pass_context=True)
async def setafkmsg(ctx):
    with open('config.json', 'r+') as conf:
        cf = json.load(conf)
        cf['afk_message'] = ctx.message.content[10:]
        conf.seek(0)
        conf.truncate()
        json.dump(cf, conf, indent=4)
        await bot.send_message(ctx.message.channel, 'Set afk message to: %s' % cf['afk_message'])

# List all custom commands
@bot.command(pass_context=True)
async def customcmds(ctx):
    if ctx.message.author.id == config['my_id']:
        with open('commands.json', 'r') as commands:
            cmds = json.load(commands)
        msg = '```json\nList of Custom Commands: {\n'
        for cmd in cmds:
            msg += '"' + cmd + '" : "'
            if type(cmds[cmd]) == list:
                for i in cmds[cmd]:
                    msg += str(i) + ', '
                msg = msg[:-2] + '",\n\n'
            else:
                msg += str(cmds[cmd]) + '",\n\n'
        msg = msg[:-3]
        msg += '}```'
        part = int(math.ceil(len(msg) / 1900))
        if part == 1:
            await bot.send_message(ctx.message.channel, msg)
        else:
            msg = msg[7:-3]
            splitList = [msg[i:i + 1900] for i in range(0, len(msg), 1900)]
            allWords = []
            splitmsg = ''
            for i, blocks in enumerate(splitList):
                splitmsg += 'List of Custom Commands: %s of %s\n' % (i + 1, part)
                for b in blocks.split('\n'):
                    splitmsg += b + '\n'
                allWords.append(splitmsg)
                splitmsg = ''
            for i in allWords:
                await bot.send_message(ctx.message.channel, '```%s```' % i)

# Add a custom command
@bot.command(pass_context=True)
async def add(ctx):
    if ctx.message.author.id == config['my_id']:
        words = ctx.message.content[5:].strip()

        with open('commands.json', 'r') as commands:
            cmds = json.load(commands)

        try:

            # If there are quotes in the message (meaning multiple words for each param)
            if '"' in words:
                entry = re.findall('"([^"]+)"', words)

                # Item for key is list
                if len(entry) == 3:

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            entries.append(tuple((i[0], i[1])))
                        entries.append(tuple([entry[1], entry[2]]))
                        cmds[entry[0]] = entries
                    else:
                        cmds[entry[0]] = [(entry[1], entry[2])]

                # Item for key is string
                else:
                    cmds[entry[0]] = entry[1]

            # No quotes so spaces seperate params
            else:

                # Item for key is list
                if len(words.split(' ')) == 3:
                    entry = words.split(' ', 2)

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            entries.append(tuple((i[0], i[1])))
                        entries.append(tuple([entry[1], entry[2]]))
                        cmds[entry[0]] = entries
                    else:
                        cmds[entry[0]] = [(entry[1], entry[2])]

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    cmds[entry[0]] = entry[1]

            await bot.send_message(ctx.message.channel, 'Successfully added ``%s`` to ``%s``' % (entry[1], entry[0]))

        except Exception as e:
            await bot.send_message(ctx.message.channel, 'Error, seomthing went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)

# Remove a custom command
@bot.command(pass_context=True)
async def remove(ctx):
    if ctx.message.author.id == config['my_id']:
        words = ctx.message.content[8:].strip()

        with open('commands.json', 'r') as commands:
            cmds = json.load(commands)

        try:

            # If there are quotes in the message (meaning multiple words for each param)
            success = False
            if '"' in words:
                entry = re.findall('"([^"]+)"', words)

                # Item for key is list
                if len(entry) == 2:

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            if entry[1] == i[0]:
                                cmds[entry[0]].remove(i)
                                await bot.send_message(ctx.message.channel, 'Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            await bot.send_message(ctx.message.channel, 'Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))


                # Item for key is string
                else:
                    if entry[0] in cmds:
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        await bot.send_message(ctx.message.channel, 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            # No quotes so spaces seperate params
            else:

                # Item for key is list
                if len(words.split(' ')) == 2:
                    entry = words.split(' ')

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            if entry[1] == i[0]:
                                cmds[entry[0]].remove(i)
                                await bot.send_message(ctx.message.channel, 'Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            await bot.send_message(ctx.message.channel, 'Successfully removed ``%s`` from %``s``' % (entry[1], entry[0]))

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    if entry[0] in cmds:
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        await bot.send_message(ctx.message.channel, 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            if success == False:
                await bot.send_message(ctx.message.channel, 'Could not find specified command.')

        except Exception as e:
            await bot.send_message(ctx.message.channel, 'Error, something went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)

# Deletes previous message immediately or after specified number of seconds (because why not)
@bot.command(pass_context=True)
async def d(ctx):
    if ctx.message.author.id == config['my_id']:

        # If number of seconds are specified
        if len(ctx.message.content.lower().strip()) > 2:
            killMsg = selflog[len(selflog) - 2]
            timer = int(ctx.message.content[2:].lower().strip())

            # Animated countdown because screw rate limit amirite
            destroy = await bot.edit_message(ctx.message, 'The above message will self-destruct in:')
            msg = await bot.send_message(ctx.message.channel, '``%s  |``' % timer)
            for i in range(0, timer, 4):
                if timer - 1 - i == 0:
                    await bot.delete_message(destroy)
                    msg = await bot.edit_message(msg, '``0``')
                    break
                else:
                    msg = await bot.edit_message(msg, '``%s  |``' % int(timer - 1 - i))
                    await asyncio.sleep(1)
                if timer - 1 - i != 0:
                    if timer - 2 - i == 0:
                        await bot.delete_message(destroy)
                        msg = await bot.edit_message(msg, '``0``')
                        break
                    else:
                        msg = await bot.edit_message(msg, '``%s  /``' % int(timer - 2 - i))
                        await asyncio.sleep(1)
                if timer - 2 - i != 0:
                    if timer - 3 - i == 0:
                        await bot.delete_message(destroy)
                        msg = await bot.edit_message(msg, '``0``')
                        break
                    else:
                        msg = await bot.edit_message(msg, '``%s  -``' % int(timer - 3 - i))
                        await asyncio.sleep(1)
                if timer - 3 - i != 0:
                    if timer - 4 - i == 0:
                        await bot.delete_message(destroy)
                        msg = await bot.edit_message(msg, '``0``')
                        break
                    else:
                        msg = await bot.edit_message(msg, '``%s  \ ``' % int(timer - 4 - i))
                        await asyncio.sleep(1)
            await bot.edit_message(msg, ':bomb:')
            await asyncio.sleep(.5)
            await bot.edit_message(msg, ':fire:')
            await bot.edit_message(killMsg, ':fire:')
            await asyncio.sleep(.5)
            await bot.delete_message(msg)
            await bot.delete_message(killMsg)

        # If no number specified, delete message immediately
        else:
            await bot.delete_message(ctx.message)
            await bot.delete_message(selflog[len(selflog)-2])

# On all messages sent (will be used for logging/stats)
@bot.event
async def on_message(message):

    # Sets status to idle when I go offline (won't trigger while I'm online so this prevents me from appearing online all the time)
    await bot.change_presence(status='idle', afk=True)

    # If the message was sent by me
    if message.author.id == config['my_id']:
        selflog.append(message)
        success = False

        # Quick cmds for da memes
        if message.content.lower().strip() == 'shrug':
            await bot.delete_message(message)
            await bot.send_message(message.channel, '¯\_(ツ)_/¯')
        elif message.content.lower().strip() == 'flip':
            await bot.delete_message(message)
            await bot.send_message(message.channel, '(╯°□°）╯︵ ┻━┻')
        elif message.content.lower().strip() == 'unflip':
            await bot.delete_message(message)
            await bot.send_message(message.channel, '┬─┬﻿ ノ( ゜-゜ノ)')
        elif message.content.lower().startswith("lenny"):
            await bot.delete_message(message)
            await bot.send_message(message.channel, '( ͡° ͜ʖ ͡°)')
        elif message.content.lower().startswith('comeatmebro'):
            await bot.send_message(message.channel, '(ง’̀-‘́)ง')
        elif message.content.startswith('.'):
            success = False
            with open('commands.json', 'r') as f:
                commands = json.load(f)
                file = discord.Embed(colour=0x27007A)
            for i in commands:
                if message.content[1:].lower().startswith(i):
                    success = True

                    # If the commands resulting reply is a list instead of a str
                    if type(commands[i]) is list:
                        try:

                            # If index from list is specified, get that result.
                            if message.content[len(i)+1:].strip().isdigit():
                                index = int(message.content[len(i)+1:].strip())
                            else:
                                title = message.content[len(i)+1:].strip()
                                for b,j in enumerate(commands[i]):
                                    if j[0] == title:
                                        index = int(b)
                                        break
                            mimetype, encoding = mimetypes.guess_type(commands[i][index][1])

                            # If value is an image, send as embed
                            if mimetype and mimetype.startswith('image'):
                                await bot.send_message(message.channel, content=None, embed=file.set_image(url=commands[i][index][1]))
                            else:
                                await bot.send_message(message.channel, commands[i][index][1])
                        except:

                            # If the index is not specified, get a random index from list
                            index = randint(0, len(commands[i])-1)
                            mimetype, encoding = mimetypes.guess_type(commands[i][index][1])

                            # If value is an image, send as embed
                            if mimetype and mimetype.startswith('image'):
                                await bot.send_message(message.channel, content=None, embed=file.set_image(url=commands[i][index][1]))
                            else:
                                await bot.send_message(message.channel, commands[i][index][1])
                    else:
                        mimetype, encoding = mimetypes.guess_type(commands[i])

                        # If value is an image, send as embed
                        if mimetype and mimetype.startswith('image'):
                            await bot.send_message(message.channel, content=None, embed=file.set_image(url=commands[i]))
                        else:
                            await bot.send_message(message.channel, commands[i])
        if success == True:
            await asyncio.sleep(2)
            await bot.delete_message(message)
    notified = message.mentions
    for i in notified:
        if i.id == config['my_id']:
            if config['set_afk'] == 'on':
                await bot.send_message(message.channel, config['afk_message'])


    await bot.process_commands(message)

bot.run(config['token'], bot=False)