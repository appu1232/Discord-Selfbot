from discord.ext import commands
from appuselfbot import isBot
import utils.settings
import json
import math
import os
import io
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
            with open('utils/log.json', 'r+') as log:
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
                msg = msg[:-2] + '\n\nServers: '
                if settings['allservers'] == 'False':
                    for i in settings['servers']:
                        server = self.bot.get_server(i)
                        msg += str(server) + ', '
                    msg = msg[:-2]
                else:
                    msg += 'All Servers'
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
                        fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Saving messages...')
                    else:
                        await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax.')
                        return
                else:
                    await self.bot.send_message(ctx.message.channel, isBot + 'Invalid syntax.')
                    return
            else:
                save = False
                fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Fetching messages...')
                size = ctx.message.content.strip()[12:]
            if size.isdigit:
                size = int(size)
                msg = ''
                comments = utils.settings.alllog[ctx.message.channel.id + ' ' + ctx.message.server.id]
                if len(comments)-2 < size:
                    size = len(comments)-2
                    if size < 0:
                        size = 0
                for i in range(len(comments)-size-2, len(comments)-2):
                    msg += 'User: %s  |  %s\r\n' % (comments[i].author.name,
                                     comments[i].timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__(
                                             '%x @ %X')) + comments[i].clean_content.replace('`', '') + '\r\n\r\n'
                if save is True:
                    with open('saved_chat.txt', 'w') as file:
                        msg = 'Server: %s\r\nChannel: %s\r\nTime:%s\r\n\r\n' % (ctx.message.server.name, ctx.message.channel.name, ctx.message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + msg
                        file.write(msg)
                    with open('saved_chat.txt', 'rb') as file:
                        await self.bot.send_file(ctx.message.channel, file)
                    os.remove('saved_chat.txt')
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
        with open('utils/log.json', 'r+') as log:
            settings = json.load(log)
            settings['log_location'] = ctx.message.channel.id + ' ' + ctx.message.server.id
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, isBot + 'Set log location to this channel.')

    @log.command(pass_context=True)
    async def toggle(self, ctx):
        with open('utils/log.json', 'r+') as log:
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
                    with open('utils/log.json', 'r+') as log:
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
        with open('utils/log.json', 'r+') as log:
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
        with open('utils/log.json', 'r+') as log:
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
        with open('utils/log.json', 'r+') as log:
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
        with open('utils/log.json', 'r+') as log:
            settings = json.load(log)
            if msg in settings['keywords']:
                settings['keywords'].remove(msg)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, isBot + 'Removed keyword ``%s`` from the logger.' % msg)
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'This keyword ``%s`` is not in the logger.' % msg)


def setup(bot):
    bot.add_cog(Userinfo(bot))
