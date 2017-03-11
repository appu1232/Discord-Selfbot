from discord.ext import commands
from appuselfbot import isBot
import json
import math
import os
import re
import subprocess
from datetime import timezone

keywords = []
log_servers = []


class Userinfo:

    def __init__(self, bot):
        self.bot = bot

    # Get user info
    @commands.group(pass_context=True)
    async def log(self, ctx):
        if ctx.invoked_subcommand is None:
            with open('settings/log.json', 'r+') as log:
                settings = json.load(log)
                msg = 'Message logger info:```Log location: '
                if settings['log_location'] == '':
                    msg += 'No log location set.\n\n'
                else:
                    location = settings['log_location'].split()
                    server = self.bot.get_server(location[1])
                    msg += '%s in server %s\n\n' % (str(server.get_channel(location[0])), str(server))
                msg += 'Keywords: '
                for i in settings['keywords']:
                    msg += i + ', '
                msg = msg.rstrip(', ') + '\n\nServers: '
                if settings['allservers'] == 'False':
                    server = ''
                    for i in settings['servers']:
                        try:
                            server = self.bot.get_server(i)
                        except:
                            pass
                        msg += str(server) + ', '
                    msg = msg.rstrip(', ')
                else:
                    msg += 'All Servers'
                msg += '\n\nBlacklisted Words: '
                for i in settings['blacklisted_words']:
                    if '[server]' in i:
                        word, id = i.split('[server]')
                        name = self.bot.get_server(id)
                        msg += word + '(for server: %s)' % str(name) + ', '
                    else:
                        msg += i + ', '
                msg = msg.rstrip(', ')
                msg += '\n\nBlacklisted Users: '
                name = None
                names = []
                for i in self.bot.servers:
                    for j in settings['blacklisted_users']:
                        name = i.get_member(j)
                        if name:
                            if name.name not in names:
                                names.append(name.name)
                                msg += name.name + ', '
                msg = msg.rstrip(', ')
                server = ''
                msg += '\n\nBlacklisted Servers: '
                for i in settings['blacklisted_servers']:
                    try:
                        server = self.bot.get_server(i)
                    except:
                        pass
                    msg += str(server) + ', '
                msg = msg.rstrip(', ')
                msg += '\n\nContext length: %s messages```' % settings['context_len']
            await self.bot.send_message(ctx.message.channel, isBot + msg)


    @log.command(pass_context=True)
    async def history(self, ctx):
        if ctx.message.content.strip()[12:]:
            if ctx.message.content[12:].strip().startswith('save'):
                if ctx.message.content[17:].strip():
                    size = ctx.message.content[17:].strip()
                    if size.isdigit():
                        save = True
                        skip = 0
                        fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Saving messages...')
                    else:
                        await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax.')
                        return
                else:
                    await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax.')
                    return
            else:
                save = False
                skip = 2
                await self.bot.send_message(ctx.message.channel, isBot + 'Are you sure you want to output all the messages here? ``y/n``.')
                reply = await self.bot.wait_for_message(author=ctx.message.author)
                if reply.content.lower().strip() != 'y':
                    await self.bot.send_message(ctx.message.channel, isBot + 'Cancelled.')
                    return
                fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Fetching messages...')
                size = ctx.message.content.strip()[12:]
            if size.isdigit:
                size = int(size)
                msg = ''
                comments = self.bot.all_log[ctx.message.channel.id + ' ' + ctx.message.server.id]
                if len(comments)-2-skip < size:
                    size = len(comments)-2-skip
                    if size < 0:
                        size = 0
                for i in range(len(comments)-size-2-skip, len(comments)-2-skip):
                    attachments = '\r\n'
                    if comments[i][0].clean_content.replace('`', '') == comments[i][1].replace('`', ''):
                        if comments[i][0].attachments != [] or comments[i][0].embeds != []:
                            for j in comments[i][0].attachments:
                                attachments += 'Attachment: ' + j['url'] + '\r\n'
                            for j in comments[i][0].embeds:
                                embed = re.findall("'url': '(.*?)'", str(j))
                                attachments += 'Embed: ' + str(j) + '\r\n'
                        msg += 'User: %s  |  %s\r\n' % (comments[i][0].author.name,
                                     comments[i][0].timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__(
                                             '%x @ %X')) + comments[i][0].clean_content.replace('`', '') + attachments + '\r\n'
                    else:
                        msg += 'User: %s  |  %s\r\n[BEFORE EDIT]\r\n%s\r\n[AFTER EDIT]\r\n%s\r\n' % (comments[i][0].author.name,
                                                        comments[i][0].timestamp.replace(tzinfo=timezone.utc).astimezone(
                                                            tz=None).__format__('%x @ %X'), comments[i][1].replace('`', '') + attachments, comments[i][0].clean_content.replace('`', '') + attachments)
                if save is True:
                    save_file = 'saved_chat_%s_at_%s.txt' % (ctx.message.timestamp.__format__('%x').replace('/', '_'), ctx.message.timestamp.__format__('%X').replace(':', '_'))
                    with open(save_file, 'w') as file:
                        msg = 'Server: %s\r\nChannel: %s\r\nTime:%s\r\n\r\n' % (ctx.message.server.name, ctx.message.channel.name, ctx.message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + msg
                        file.write(msg)
                    with open(save_file, 'rb') as file:
                        await self.bot.send_file(ctx.message.channel, file)
                    os.remove(save_file)
                    await self.bot.delete_message(fetch)
                else:
                    part = int(math.ceil(len(msg) / 1950))
                    if part == 1:
                        await self.bot.send_message(ctx.message.channel,
                                                    isBot + 'Showing last ``%s`` messages: ```%s```' % (
                                                    ctx.message.content.strip()[12:], msg))
                        await self.bot.delete_message(fetch)
                    else:
                        splitList = [msg[i:i + 1950] for i in range(0, len(msg), 1950)]
                        allWords = []
                        splitmsg = ''
                        for i, blocks in enumerate(splitList):
                            for b in blocks.split('\n'):
                                splitmsg += b + '\n'
                            allWords.append(splitmsg)
                            splitmsg = ''
                        for b, i in enumerate(allWords):
                            if b == 0:
                                await self.bot.send_message(ctx.message.channel, isBot + 'Showing last ``%s`` messages: ```%s```' % (ctx.message.content.strip()[12:], i))
                            else:
                                await self.bot.send_message(ctx.message.channel, '```%s```' % i)
                        await self.bot.delete_message(fetch)
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax.')

    @log.command(pass_context=True)
    async def location(self, ctx):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            settings['log_location'] = ctx.message.channel.id + ' ' + ctx.message.server.id
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, isBot + 'Set log location to this channel.')

    @log.command(pass_context=True)
    async def toggle(self, ctx):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if settings['allservers'] == 'False':
                settings['allservers'] = 'True'
                msg = 'Logging enabled for all servers.'
            else:
                settings['allservers'] = 'False'
                msg = 'Logging enabled for only specified servers. See servers with ``>log``'
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, isBot + msg)

    @log.command(pass_context=True)
    async def context(self, ctx):
        if ctx.message.content[12:].strip():
            if ctx.message.content[12:].strip().isdigit():
                if 0 < int(ctx.message.content[12:].strip()) < 21:
                    with open('settings/log.json', 'r+') as log:
                        settings = json.load(log)
                        settings['context_len'] = ctx.message.content[12:].strip()
                        log.seek(0)
                        log.truncate()
                        json.dump(settings, log, indent=4)
                    await self.bot.send_message(ctx.message.channel, isBot + 'Set context length to ``%s``.' % ctx.message.content[12:])
                else:
                    await self.bot.send_message(ctx.message.channel, isBot + 'Invalid context length.')
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax.')
        else:
            await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax. No value given.')

    @log.command(pass_context=True)
    async def add(self, ctx):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if ctx.message.server.id not in settings['servers']:
                settings['servers'].append(ctx.message.server.id)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Added server to logger.')
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'This server is already in the logger.')

    @log.command(pass_context=True)
    async def remove(self, ctx):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if ctx.message.server.id in settings['servers']:
                settings['servers'].remove(ctx.message.server.id)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Removed server from the logger.')
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'This server is not in the logger.')

    @log.command(pass_context=True)
    async def addkey(self, ctx, *, msg: str):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if msg not in settings['keywords'] and msg is not None:
                settings['keywords'].append(msg)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                if ctx.message.mentions:
                    msg = ctx.message.mentions[0].name
                await self.bot.send_message(ctx.message.channel, isBot + 'Added keyword ``%s`` to logger.' % msg)
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'The keyword ``%s`` is already in the logger.' % msg)

    @log.command(pass_context=True)
    async def removekey(self, ctx, *, msg: str):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if msg in settings['keywords']:
                settings['keywords'].remove(msg)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Removed keyword ``%s`` from the logger.' % msg)
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'This keyword ``%s`` is not in the logger.' % msg)

    @log.command(pass_context=True)
    async def addblacklist(self, ctx, *, msg: str):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if msg.startswith('[user]'):
                msg = msg[6:].strip()
                try:
                    name = ctx.message.mentions[0].id
                except:
                    name = ctx.message.server.get_member_named(msg)
                    if not name:
                        name = ctx.message.server.get_member(msg)
                    if name:
                        name = name.id
                if not name:
                    return await self.bot.send_message(ctx.message.channel, isBot + 'Could not find user. They must be in the server you are currently using this command in.')
                if name in settings['blacklisted_users']:
                    return await self.bot.send_message(ctx.message.channel, isBot + 'User is already blacklisted from the keyword logger.')
                settings['blacklisted_users'].append(name)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                name = ctx.message.server.get_member(name)
                await self.bot.send_message(ctx.message.channel, isBot + 'Blacklisted user ``%s`` from the keyword logger.' % name)
            elif msg.startswith('[word]'):
                msg = msg[6:].strip()
                if msg.startswith('[here] '):
                    msg = msg[6:].strip()
                    msg += ' [server]' + ctx.message.server.id
                if 'blacklisted_words' not in settings:
                    settings['blacklisted_words'] = []
                if msg in settings['blacklisted_words']:
                    return await self.bot.send_message(ctx.message.channel, isBot + 'This word is already blacklisted.')
                settings['blacklisted_words'].append(msg)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                if ' [server]' in msg:
                    await self.bot.send_message(ctx.message.channel,
                                                isBot + 'Blacklisted the word ``%s`` for this server from the keyword logger.' % msg.split(' [server]')[0])
                else:
                    await self.bot.send_message(ctx.message.channel, isBot + 'Blacklisted the word ``%s`` from the keyword logger.' % msg)
            elif msg.startswith('[server]'):
                if 'blacklisted_servers' not in settings:
                    settings['blacklisted_servers'] = []
                if ctx.message.server.id in settings['blacklisted_servers']:
                    return await self.bot.send_message(ctx.message.channel, isBot + 'This server is already blacklisted.')
                if ctx.message.server.id in settings['servers']:
                    settings['servers'].remove(ctx.message.server.id)
                settings['blacklisted_servers'].append(ctx.message.server.id)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Server ``%s`` has been blacklisted from the keyword logger.' % ctx.message.server.name)
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax. Usage: ``>log addblacklist [user] someone#2341`` or ``>log addblacklist [word] word`` or ``>log addblacklist [server]``')

    @log.command(pass_context=True)
    async def removeblacklist(self, ctx, *, msg: str):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if msg.startswith('[user]'):
                msg = msg[6:].strip()
                try:
                    name = ctx.message.mentions[0].id
                except:
                    name = ctx.message.server.get_member_named(msg)
                    if not name:
                        name = ctx.message.server.get_member(msg)
                    if name:
                        name = name.id
                if not name:
                    await self.bot.send_message(ctx.message.channel, isBot + 'Could not find user. They must be in the server you are currently using this command in.')
                    return
                if name not in settings['blacklisted_users']:
                    return await self.bot.send_message(ctx.message.channel, isBot + 'User is not in the blacklist for the keyword logger.')
                settings['blacklisted_users'].remove(name)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                name = ctx.message.server.get_member(name)
                await self.bot.send_message(ctx.message.channel, isBot + 'Removed ``%s`` from the blacklist for the keyword logger.' % name)
            elif msg.startswith('[word]'):
                msg = msg[6:].strip()
                if msg.startswith('[here] '):
                    msg = msg[6:].strip()
                    msg += ' [server]' + ctx.message.server.id
                if 'blacklisted_words' not in settings:
                    settings['blacklisted_words'] = []
                if msg not in settings['blacklisted_words']:
                    return await self.bot.send_message(ctx.message.channel, isBot + 'This word is not blacklisted.')
                settings['blacklisted_words'].remove(msg)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                if ' [server]' in msg:
                    await self.bot.send_message(ctx.message.channel,
                                                isBot + '``%s`` removed from the blacklist for this server.' % msg.split(' [server]')[0])
                else:
                    await self.bot.send_message(ctx.message.channel, isBot + '``%s`` removed from the blacklist.' % msg)
            elif msg.startswith('[server]'):
                if 'blacklisted_servers' not in settings:
                    settings['blacklisted_servers'] = []
                if ctx.message.server.id not in settings['blacklisted_servers']:
                    return await self.bot.send_message(ctx.message.channel, isBot + 'This server is not blacklisted.')
                settings['blacklisted_servers'].remove(ctx.message.server.id)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Removed server ``%s`` from the blacklist.' % ctx.message.server.name)
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax. Usage: ``>log removeblacklist [user] someone#2341`` or ``>log removeblacklist [word] word`` or ``>log removeblacklist [server]``')

    # Notify bot
    @commands.group(pass_context=True)
    async def notify(self, ctx):
        if ctx.invoked_subcommand is None:
            error = 'Invalid syntax. Possible commands:\n``>notify token <token>`` - Set the bot token for the notifier bot.\n``>notify on/off`` - turn notifier on or off.\n``>notify dm`` - recieve notifications via direct message\n``>notify ping`` - recieve notifications via mention in your keyword logger channel.\n``>notify none`` - repost to keyword logger channel without any mention (get notification if you have notification settings set to all messages in that server).'
            if not ctx.message.content[8:].strip():
                await self.bot.send_message(ctx.message.channel, isBot + error)
            elif ctx.message.content[8:].strip() == 'ping':
                with open('settings/notify.json', 'r+') as n:
                    notify = json.load(n)
                    notify['type'] = 'ping'
                    n.seek(0)
                    n.truncate()
                    json.dump(notify, n, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Set notification type to ``ping``.')
            elif ctx.message.content[8:].lower().strip() == 'dm' or ctx.message.content[8:].lower().strip() == 'pm' or ctx.message.content[8:].lower().strip() == 'direct message':
                with open('settings/notify.json', 'r+') as n:
                    notify = json.load(n)
                    notify['type'] = 'dm'
                    n.seek(0)
                    n.truncate()
                    json.dump(notify, n, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Set notification type to ``direct messages``.')
            elif ctx.message.content[8:].strip() == 'none':
                with open('settings/notify.json', 'r+') as n:
                    notify = json.load(n)
                    notify['type'] = 'none'
                    n.seek(0)
                    n.truncate()
                    json.dump(notify, n, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Set notification type to ``none``.')
            else:
                await self.bot.send_message(ctx.message.channel, isBot + error)

    # Turn on the notifier
    @notify.command(pass_context=True)
    async def on(self, ctx):
        with open('settings/log.json', 'r+') as l:
            log = json.load(l)
        if log['log_location'] == '':
            return await self.bot.send_message(ctx.message.channel, isBot + 'Set the channel where you want to keyword log first! See the **Keyword Logger** section in the README for instructions on how to set it up.')
        channel = log['log_location'].split(' ')[0]
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            if notify['bot_token'] == '':
                return await self.bot.send_message(ctx.message.channel,
                                                   isBot + 'Missing bot token. You must set up a second bot in order to receive notifications (selfbots can\'t ping themselves!). Read the ``Notifier Setup`` in the Keyword Logger section of the README for step-by-step instructions.')
            if notify['notify'] == 'on':
                return await self.bot.send_message(ctx.message.channel,
                                            isBot + 'Notifier is already on.')
            notify['channel'] = channel
            notify['author'] = ctx.message.author.id
            notify['notify'] = 'on'
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        await self.bot.send_message(ctx.message.channel, isBot + 'Turned on notifications for the keyword logger.')
        try:
            self.bot.subpro = subprocess.Popen(['python3', 'cogs/utils/notify.py'])
        except (SyntaxError, FileNotFoundError):
            self.bot.subpro = subprocess.Popen(['python', 'cogs/utils/notify.py'])
        except:
            pass

    # Turn off the notifier
    @notify.command(pass_context=True)
    async def off(self, ctx):
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            notify['notify'] = 'off'
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        if self.bot.subpro:
            self.bot.subpro.kill()
        await self.bot.send_message(ctx.message.channel, isBot + 'Turned off notifications for the keyword logger.')

    # Set bot token
    @notify.command(pass_context=True)
    async def token(self, ctx, *, msg):
        msg = msg.strip('<').strip('>')
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            notify['bot_token'] = msg
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        await self.bot.send_message(ctx.message.channel, isBot + 'Notifier bot token set.')


def setup(bot):
    bot.add_cog(Userinfo(bot))
