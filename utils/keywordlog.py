from discord.ext import commands
from appuselfbot import isBot
import json

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
