from discord.ext import commands
from appuselfbot import bot_prefix
import json
import math
import os
import re
import subprocess
import psutil
import sys
from PythonGists import PythonGists
from datetime import timezone
from cogs.utils.checks import *

keywords = []
log_servers = []
val = 0
pre = ''

'''Module for the keyword logger and chat history.'''


class KeywordLogger:

    def __init__(self, bot):
        self.bot = bot

    async def log_location(self, ctx, msg):
        if msg:
            channel = self.bot.get_channel(msg)
            if not channel:
                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find specified channel. Are you entering in the channel id correctly? Example id: 299293492645986307')
        else:
            channel = ctx.message.channel
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            settings['log_location'] = channel.id + ' ' + channel.server.id
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set log location to channel: ``{}``.'.format(channel.name))
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    async def start_logger(self, ctx):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            settings['keyword_logging'] = 'on'
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Turned on the keyword logger.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    async def stop_logger(self, ctx):
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            settings['keyword_logging'] = 'off'
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Turned off the keyword logger.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    async def notify_off(self, ctx):
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            notify['type'] = 'off'
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        self.bot.notify = load_notify_config()
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Turned off notifications.')
        if self.bot.subpro:
            self.bot.subpro.kill()
        if os.path.exists('notifier.txt'):
            os.remove('notifier.txt')

    async def notify_ping(self, ctx):
        with open('settings/log.json', 'r+') as log:
            location = json.load(log)['log_location']
        if location == '':
            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set the channel where you want to keyword log first! See the **Keyword Logger** section in the README for instructions on how to set it up.')
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            notify['type'] = 'ping'
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        self.bot.notify = load_notify_config()
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set notification type to ``ping``. The webhook will ping you.')
        if self.bot.subpro:
            self.bot.subpro.kill()
        if os.path.exists('notifier.txt'):
            os.remove('notifier.txt')

    async def notify_msg(self, ctx):
        with open('settings/log.json') as l:
            location = json.load(l)['log_location']
        if location == '':
            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set the channel where you want to keyword log first! See the **Keyword Logger** section in the README for instructions on how to set it up.')
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            notify['type'] = 'msg'
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        self.bot.notify = load_notify_config()
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set notification type to ``msg``. The webhook will send notifications to your log location channel. Make sure you have notifications enabled for all messages in that channel.')
        if self.bot.subpro:
            self.bot.subpro.kill()
        if os.path.exists('notifier.txt'):
            os.remove('notifier.txt')

    async def notify_dm(self, ctx):
        with open('settings/log.json') as l:
            location = json.load(l)['log_location']
        if location == '':
            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set the channel where you want to keyword log first! See the **Keyword Logger** section in the README for instructions on how to set it up.')
        with open('settings/log.json') as l:
            location = json.load(l)['log_location'].split(' ')[0]
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            if notify['bot_token'] == '':
                return await self.bot.send_message(ctx.message.channel,
                                                   bot_prefix + 'Missing bot token. You must set up a second bot in order to receive notifications (selfbots can\'t ping themselves!). Read the ``Notifier Setup`` in the Keyword Logger section of the README for step-by-step instructions.')
            if notify['type'] == 'dm':
                return await self.bot.send_message(ctx.message.channel,
                                                   bot_prefix + 'Proxy notifier bot is already on.')
            notify['type'] = 'dm'
            channel = location
            notify['channel'] = channel
            notify['author'] = ctx.message.author.id
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        self.bot.notify = load_notify_config()
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set notification type to ``direct messages``. The proxy bot will direct message you.')
        if self.bot.subpro:
            self.bot.subpro.kill()
        if os.path.exists('notifier.txt'):
            pid = open('notifier.txt', 'r').read()
            try:
                p = psutil.Process(int(pid))
                p.kill()
            except:
                pass
            os.remove('notifier.txt')
        self.bot.subpro = subprocess.Popen([sys.executable, 'cogs/utils/notify.py'])
        with open('notifier.txt', 'w') as fp:
            fp.write(str(self.bot.subpro.pid))

    async def webhook_url(self, ctx, msg):
        with open('settings/log.json', 'r+') as l:
            log = json.load(l)
            if 'webhook_url' not in log:
                log['webhook_url'] = ''
            log['webhook_url'] = msg.lstrip('<').rstrip('>').strip('"')
            l.seek(0)
            l.truncate()
            json.dump(log, l, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set up webhook for keyword notifications!')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    async def bot_token(self, ctx, msg):
        msg = msg.strip('<').strip('>')
        with open('settings/log.json', 'r+') as l:
            settings = json.load(l)
            settings['notifier_bot_token'] = msg
            l.seek(0)
            l.truncate()
            json.dump(settings, l, indent=4)
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)
        with open('settings/notify.json', 'r+') as n:
            notify = json.load(n)
            notify['bot_token'] = msg
            n.seek(0)
            n.truncate()
            json.dump(notify, n, indent=4)
        self.bot.notify = load_notify_config()
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Notifier bot token set.')

    @commands.group(pass_context=True)
    async def log(self, ctx):
        """Get info about keyword logger. See the README for more info."""
        if ctx.invoked_subcommand is None:

            await self.bot.delete_message(ctx.message)
            pre = ctx.message.content.split('log')[0]
            val = 0

            def check(msg):
                if msg.content.isdigit():
                    return 0 < int(msg.content) < val
                elif msg.content.startswith(pre):
                    return True
                return False

            def not_block(msg):
                return '```' not in msg.content

            log_loc = 'Set log location.' if self.bot.log_conf['log_location'] == '' else 'Change log location.'
            notifier = 'Set up notifier to ping you for keywords logged.' if self.bot.log_conf['webhook_url'] == '' and self.bot.log_conf['notifier_bot_token'] == '' else 'Change settings for keyword notifier.'

            menu = await self.bot.send_message(ctx.message.channel, bot_prefix + '```\n\ud83d\udcdd Keyword Logger Settings. Enter a number:\n\n1. Turn on/off logger (currently {}).\n2. {}\n3. Add/remove a keyword.\n4. Blacklist words/users/server/channels.\n5. {}\n6. User following options.\n7. See all current settings.\n8. Help.```'.format(self.bot.log_conf['keyword_logging'], log_loc, notifier))

            val = 9
            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author, check=check)
            if reply and not reply.content.startswith(pre):
                await self.bot.delete_message(reply)

                if int(reply.content) > 2 and self.bot.log_conf['log_location'] == '':
                    return await self.bot.edit_message(menu, bot_prefix + 'Please set a log location (option 2) before setting up the notifier. See the help section (option 8) to for help on understanding the keyword logger better.')

                # Toggle keyword logging
                if reply.content == '1':
                    await self.bot.delete_message(menu)
                    return await self.stop_logger(ctx) if self.bot.log_conf['keyword_logging'] == 'on' else await self.start_logger(ctx)

                # Set log location
                elif reply.content == '2':
                    await self.bot.edit_message(menu,
                                                        bot_prefix + '```\n\ud83d\udd8a Enter the channel id of where you want to log keywords. Enter 1 for this channel. Channel id can be obtained by enabling developer mode (http://i.imgur.com/KMDS8cb.png) and then right clicking on the channel name > copy id.```')
                    reply = await self.bot.wait_for_message(author=ctx.message.author, check=not_block)
                    if reply and not reply.content.startswith(pre):
                        await self.bot.delete_message(reply)
                    if reply.content == '1':
                        await self.bot.delete_message(menu)
                        await self.log_location(ctx, None)
                    else:
                        await self.bot.delete_message(menu)
                        await self.log_location(ctx, reply.content)

                # Keyword options
                elif reply.content == '3':
                    val = 4
                    await self.bot.edit_message(menu,
                                                         bot_prefix + '```\n\ud83d\udd8a Enter a number:\n\n1. Add a keyword.\n2. Remove a keyword.\n3. Show current list of keywords.```')

                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author, check=check)

                    if reply and not reply.content.startswith(pre):
                        await self.bot.delete_message(reply)

                        if reply.content == '1':
                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd8a Note: If you don\'t want substrings to trigger the logger (i.e. your keyword is bill but you don\'t want billy to trigger the logger), enter your keyword in quotes. "bill" Phrases are also supported. Ex: "I love you"\n\nEnter the keyword (not case sensitive!):```')
                            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                    check=not_block)
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)

                                o_word = reply.content
                                word = '[isolated]' + reply.content[1:-1] if reply.content.startswith(
                                    '"') and reply.content.endswith('"') else reply.content

                                await self.bot.edit_message(menu,
                                                                     bot_prefix + '```\n\ud83d\udd8a Keyword is: {}\nWhere should this keyword be detected?\n1. Across all servers.\n2. Only this server.\n3. Only this channel.```'.format(
                                                                         reply.content))
                                reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                        check=check)
                                if reply and not reply.content.startswith(pre):
                                    await self.bot.delete_message(reply)
                                    if reply.content == '1':
                                        self.bot.log_conf['keywords'].append(word)
                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Keyword ``{}`` successfully set.'.format(
                                                                        o_word))
                                    elif reply.content == '2':
                                        self.bot.log_conf['keywords'].append(word + ' [server]{}'.format(ctx.message.server.id))
                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Keyword ``{}`` successfully set for this server.'.format(
                                                                        o_word))
                                    else:
                                        self.bot.log_conf['keywords'].append(
                                            word + ' [channel]{}'.format(ctx.message.channel.id))
                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Keyword ``{}`` successfully set for this channel.'.format(
                                                                        o_word))

                                    with open('settings/log.json', 'r+') as log:
                                        log.seek(0)
                                        log.truncate()
                                        json.dump(self.bot.log_conf, log, indent=4)
                                    with open('settings/log.json', 'r') as log:
                                        self.bot.log_conf = json.load(log)

                        # Show list of keywords in order to remove.
                        elif reply.content == '2':

                            msg = '1. '
                            count = 0
                            for count, word in enumerate(self.bot.log_conf['keywords']):
                                if ' [server]' in word:
                                    key, server = word.split(' [server]')
                                    server = self.bot.get_server(server)
                                    word = '{} in server: {}  {}. '.format(key, server, count + 2)
                                elif ' [channel]' in word:
                                    key, channel = word.split(' [channel]')
                                    channel = self.bot.get_channel(channel)
                                    word = '{} in channel: {}  {}. '.format(key, channel, count + 2)
                                else:
                                    word = '{}  {}. '.format(word, count + 2)
                                if word.startswith('[isolated]'):
                                    word = word[10:]

                                msg += word

                            msg = msg[:-(len(str(count + 2)) + 2)]

                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd8a Pick which keyword to remove (enter a number):\n\n{}```'.format(
                                                                    msg))

                            val = count + 3
                            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author, check=check)

                            # Remove specified keyword.
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)

                                index = int(reply.content) - 1
                                word = self.bot.log_conf['keywords'][index]
                                del self.bot.log_conf['keywords'][index]

                                with open('settings/log.json', 'r+') as log:
                                    log.seek(0)
                                    log.truncate()
                                    json.dump(self.bot.log_conf, log, indent=4)
                                with open('settings/log.json', 'r') as log:
                                    self.bot.log_conf = json.load(log)

                                await self.bot.edit_message(menu,
                                                            bot_prefix + 'Successfully removed ``{}`` from your keywords.'.format(
                                                                word))

                        # Show list of keywords
                        else:
                            msg = 'List of keywords:\n\n'
                            for word in self.bot.log_conf['keywords']:
                                if ' [server]' in word:
                                    key, server = word.split(' [server]')
                                    server = self.bot.get_server(server)
                                    word = '{} in server: {}, '.format(key, server)
                                elif ' [channel]' in word:
                                    key, channel = word.split(' [channel]')
                                    channel = self.bot.get_channel(channel)
                                    word = '{} in channel: {}, '.format(key, channel)
                                if word.startswith('[isolated]'):
                                    word = word[10:] + ', '
                                msg += word + ', '

                            msg = msg.rstrip(', ')
                            await self.bot.edit_message(menu, bot_prefix + '```{}```'.format(msg))

                # Blacklisting options
                elif reply.content == '4':
                    val = 6
                    await self.bot.edit_message(menu,
                                                         bot_prefix + '```\n\ud83d\udd8a Enter a number:\n\n1. Blacklist a word.\n2. Blacklist a user.\n3. Blacklist a server.\n4. Blacklist a channel.\n5. Remove a word/user/server/channel from the blacklist.```')

                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author, check=check)

                    if reply and not reply.content.startswith(pre):
                        await self.bot.delete_message(reply)

                        # Blacklisting word options
                        if reply.content == '1':
                            val = 4
                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd8a Info: Blacklisted items make it so that a message with a keyword does not trigger the keyword logger if it has the blacklisted item (word/by certain user/in server/in channel).\nEnter a number:\n\n1. Add a word to blacklist everywhere.\n2. Add a word to blacklist in a specific server.\n3. Add a word to blacklist in a specific channel.```')

                            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author, check=check)
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)
                                if reply.content == '1':
                                    await self.bot.edit_message(menu,
                                                                         bot_prefix + '```\n\ud83d\udd8a Enter a word to blacklist (not case sensitive):```')
                                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                            check=not_block)

                                    # After entering the blacklisted word
                                    if reply and not reply.content.startswith(pre):
                                        blacklisted_word = reply.content
                                        await self.bot.delete_message(reply)
                                        self.bot.log_conf['blacklisted_words'].append(blacklisted_word)
                                        with open('settings/log.json', 'r+') as log:
                                            log.seek(0)
                                            log.truncate()
                                            json.dump(self.bot.log_conf, log, indent=4)
                                        with open('settings/log.json', 'r') as log:
                                            self.bot.log_conf = json.load(log)
                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Done! Blacklisted ``{}``.'.format(
                                                                        blacklisted_word))

                                # Blacklist the word for a specific server
                                elif reply.content == '2':
                                    await self.bot.edit_message(menu,
                                                                         bot_prefix + '```\n\ud83d\udd8a Enter a word to blacklist (not case sensitive):```')
                                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                            check=not_block)

                                    # After entering in a blacklisted word, prompt server id
                                    if reply and not reply.content.startswith(pre):
                                        blacklisted_word = reply.content
                                        await self.bot.delete_message(reply)
                                        await self.bot.edit_message(menu,
                                                                            bot_prefix + '```\n\ud83d\udd8a Enter the server id where this word should be blacklisted. Enter 1 if it\'s this server.\nServer id can be obtained by enabling developer mode (http://i.imgur.com/KMDS8cb.png) and then right clicking on the server > copy id.```')
                                        reply = await self.bot.wait_for_message(timeout=120,
                                                                                author=ctx.message.author,
                                                                                check=not_block)

                                        # After entering the server id
                                        if reply and not reply.content.startswith(pre):
                                            await self.bot.delete_message(reply)
                                            server = ctx.message.server if reply.content == '1' else self.bot.get_server(
                                                reply.content)
                                            if not server:
                                                await self.bot.edit_message(menu,
                                                                            bot_prefix + 'Could not find the server.')
                                            else:
                                                self.bot.log_conf['blacklisted_words'].append(
                                                    '{} [server]{}'.format(blacklisted_word, server.id))
                                                with open('settings/log.json', 'r+') as log:
                                                    log.seek(0)
                                                    log.truncate()
                                                    json.dump(self.bot.log_conf, log, indent=4)
                                                with open('settings/log.json', 'r') as log:
                                                    self.bot.log_conf = json.load(log)
                                                await self.bot.edit_message(menu,
                                                                            bot_prefix + 'Added ``{}`` to the blacklist for server ``{}``.'.format(
                                                                                blacklisted_word, server.name))

                                # Blacklist the word for a specific channel
                                else:
                                    await self.bot.edit_message(menu,
                                                                         bot_prefix + '```\n\ud83d\udd8a Enter a word to blacklist (not case sensitive):```')
                                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                            check=not_block)

                                    # After entering in a blacklisted word, prompt channel id
                                    if reply and not reply.content.startswith(pre):
                                        blacklisted_word = reply.content
                                        await self.bot.delete_message(reply)
                                        await self.bot.edit_message(menu,
                                                                            bot_prefix + '```\n\ud83d\udd8a Enter the channel id where this word should be blacklisted. Enter 1 if it\'s this channel.\nChannel id can be obtained by enabling developer mode (http://i.imgur.com/KMDS8cb.png) and then right clicking on the channel name > copy id.```')
                                        reply = await self.bot.wait_for_message(timeout=120,
                                                                                author=ctx.message.author,
                                                                                check=not_block)

                                        # After entering the channel id
                                        if reply and not reply.content.startswith(pre):
                                            await self.bot.delete_message(reply)
                                            channel = ctx.message.channel if reply.content == '1' else self.bot.get_channel(
                                                reply.content)
                                            if not channel:
                                                await self.bot.edit_message(menu,
                                                                            bot_prefix + 'Could not find the channel.')
                                            else:
                                                self.bot.log_conf['blacklisted_words'].append(
                                                    '{} [channel]{}'.format(blacklisted_word, channel.id))
                                                with open('settings/log.json', 'r+') as log:
                                                    log.seek(0)
                                                    log.truncate()
                                                    json.dump(self.bot.log_conf, log, indent=4)
                                                with open('settings/log.json', 'r') as log:
                                                    self.bot.log_conf = json.load(log)
                                                await self.bot.edit_message(menu,
                                                                            bot_prefix + 'Added ``{}`` to the blacklist for channel ``{}``.'.format(
                                                                                blacklisted_word, channel.name))

                        # Blacklist a user
                        elif reply.content == '2':
                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd8a Blacklist a user.\nYou can mention the user, type out their full username + discriminator, or put their user id. They MUST be in the server you are using this command in.\n\nEnter the user:```')

                            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                    check=not_block)
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)
                                try:
                                    user = reply.mentions[0]
                                except:
                                    user = ctx.message.server.get_member_named(reply.content)
                                    if not user:
                                        user = ctx.message.server.get_member(reply.content)
                                if not user:
                                    await self.bot.edit_message(menu,
                                                                bot_prefix + 'Could not find the user. Are they in this server?')
                                else:
                                    self.bot.log_conf['blacklisted_users'].append(user.id)
                                    with open('settings/log.json', 'r+') as log:
                                        log.seek(0)
                                        log.truncate()
                                        json.dump(self.bot.log_conf, log, indent=4)
                                    with open('settings/log.json', 'r') as log:
                                        self.bot.log_conf = json.load(log)
                                    await self.bot.edit_message(menu,
                                                                bot_prefix + 'Blacklisted user ``{}``. This person cannot trigger the keyword logger now.'.format(
                                                                    user.name))

                        # Blacklist a server
                        elif reply.content == '3':
                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd8a Enter the server id. Enter 1 if it\'s this server.\nServer id can be obtained by enabling developer mode (http://i.imgur.com/KMDS8cb.png) and then right clicking on the server > copy id.```')

                            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                    check=not_block)
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)
                                server = ctx.message.server if reply.content == '1' else self.bot.get_server(
                                    reply.content)
                                if not server:
                                    await self.bot.edit_message(menu,
                                                                bot_prefix + 'Could not find the server.')
                                else:
                                    self.bot.log_conf['blacklisted_servers'].append(server.id)
                                    with open('settings/log.json', 'r+') as log:
                                        log.seek(0)
                                        log.truncate()
                                        json.dump(self.bot.log_conf, log, indent=4)
                                    with open('settings/log.json', 'r') as log:
                                        self.bot.log_conf = json.load(log)
                                    await self.bot.edit_message(menu,
                                                                bot_prefix + 'Blacklisted server ``{}``. The keyword logger will not trigger for messages from this server.'.format(
                                                                    server.name))

                        # Blacklist a channel
                        elif reply.content == '4':
                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd8a Enter the channel id. Enter 1 if it\'s this channel.\nChannel id can be obtained by enabling developer mode (http://i.imgur.com/KMDS8cb.png) and then right clicking on the channel name > copy id.```')

                            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                    check=not_block)
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)
                                channel = ctx.message.channel if reply.content == '1' else self.bot.get_channel(
                                    reply.content)
                                if not channel:
                                    await self.bot.edit_message(menu,
                                                                bot_prefix + 'Could not find the channel.')
                                else:
                                    self.bot.log_conf['blacklisted_channels'][channel.id] = channel.server.id
                                    with open('settings/log.json', 'r+') as log:
                                        log.seek(0)
                                        log.truncate()
                                        json.dump(self.bot.log_conf, log, indent=4)
                                    with open('settings/log.json', 'r') as log:
                                        self.bot.log_conf = json.load(log)
                                    await self.bot.edit_message(menu,
                                                                bot_prefix + 'Blacklisted channel ``{}`` in server ``{}``. The keyword logger will not trigger for messages from this channel.'.format(
                                                                    channel.name, channel.server.name))

                        # Remove an item from the blacklist
                        else:
                            val = 5
                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd8a Remove what from the blacklist? Enter a number.\n\n1. Word\n2. User\n3. Server\n4. Channel```')

                            reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                    check=check)
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)
                                msg = '\n1. '
                                count = 0

                                # Remove a blacklisted word
                                if reply.content == '1':
                                    for count, word in enumerate(self.bot.log_conf['blacklisted_words']):
                                        if ' [server]' in word:
                                            key, server = word.split(' [server]')
                                            server = self.bot.get_server(server)
                                            word = '{} in server: {}  {}. '.format(key, server, count + 2)
                                        elif ' [channel]' in word:
                                            key, channel = word.split(' [channel]')
                                            channel = self.bot.get_channel(channel)
                                            word = '{} in channel: {}  {}. '.format(key, channel, count + 2)
                                        else:
                                            word = '{}  {}. '.format(word, count + 2)
                                        if word.startswith('[isolated]'):
                                            word = word[10:]

                                        msg += word
                                    msg = msg[:-(len(str(count + 2)) + 2)]

                                    await self.bot.edit_message(menu,
                                                                         bot_prefix + '```\n\ud83d\udd8a Pick which blacklisted item to remove (enter a number):\n\n{}```'.format(
                                                                             msg))

                                    val = count + 3
                                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                            check=check)
                                    if reply and not reply.content.startswith(pre):
                                        await self.bot.delete_message(reply)

                                        index = int(reply.content) - 1
                                        word = self.bot.log_conf['blacklisted_words'][index]
                                        del self.bot.log_conf['blacklisted_words'][index]

                                        with open('settings/log.json', 'r+') as log:
                                            log.seek(0)
                                            log.truncate()
                                            json.dump(self.bot.log_conf, log, indent=4)
                                        with open('settings/log.json', 'r') as log:
                                            self.bot.log_conf = json.load(log)

                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Successfully removed ``{}`` from the blacklist.'.format(
                                                                        word))

                                # Remove a blacklisted user
                                elif reply.content == '2':
                                    for count, word in enumerate(self.bot.log_conf['blacklisted_users']):
                                        user = None
                                        for i in self.bot.servers:
                                            user = i.get_member(word)
                                            if user:
                                                user = '{}  {}. '.format(user.name + '#' + user.discriminator, count + 2)
                                                break
                                        if not user:
                                            user = 'User not found.   '

                                        msg += user
                                    msg = msg[:-(len(str(count + 2)) + 2)]

                                    await self.bot.edit_message(menu,
                                                                         bot_prefix + '```\n\ud83d\udd8a Pick which blacklisted item to remove (enter a number):\n\n{}```'.format(
                                                                             msg))

                                    val = count + 3
                                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                            check=check)
                                    if reply and not reply.content.startswith(pre):
                                        await self.bot.delete_message(reply)

                                        index = int(reply.content) - 1
                                        word = self.bot.log_conf['blacklisted_users'][index]
                                        del self.bot.log_conf['blacklisted_users'][index]

                                        with open('settings/log.json', 'r+') as log:
                                            log.seek(0)
                                            log.truncate()
                                            json.dump(self.bot.log_conf, log, indent=4)
                                        with open('settings/log.json', 'r') as log:
                                            self.bot.log_conf = json.load(log)

                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Successfully removed ``{}`` from the blacklist.'.format(
                                                                        word))

                                # Remove a blacklisted server
                                elif reply.content == '3':
                                    for count, word in enumerate(self.bot.log_conf['blacklisted_servers']):
                                        word = '{}  {}. '.format(self.bot.get_server(word), count + 2)

                                        msg += word
                                    msg = msg[:-(len(str(count + 2)) + 2)]

                                    await self.bot.edit_message(menu,
                                                                         bot_prefix + '```\n\ud83d\udd8a Pick which blacklisted item to remove (enter a number):\n\n{}```'.format(
                                                                             msg))

                                    val = count + 3
                                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                            check=check)
                                    if reply and not reply.content.startswith(pre):
                                        await self.bot.delete_message(reply)

                                        index = int(reply.content) - 1
                                        word = self.bot.log_conf['blacklisted_servers'][index]
                                        del self.bot.log_conf['blacklisted_servers'][index]

                                        with open('settings/log.json', 'r+') as log:
                                            log.seek(0)
                                            log.truncate()
                                            json.dump(self.bot.log_conf, log, indent=4)
                                        with open('settings/log.json', 'r') as log:
                                            self.bot.log_conf = json.load(log)

                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Successfully removed ``{}`` from the blacklist.'.format(
                                                                        word))

                                # Remove a blacklisted channel
                                else:
                                    list_of_channels = []
                                    for count, word in enumerate(self.bot.log_conf['blacklisted_channels']):
                                        list_of_channels.append(word)
                                        word = '{}  {}. '.format(self.bot.get_channel(word), count + 2)

                                        msg += word
                                    msg = msg[:-(len(str(count + 2)) + 2)]

                                    await self.bot.edit_message(menu,
                                                                         bot_prefix + '```\n\ud83d\udd8a Pick which blacklisted item to remove (enter a number):\n\n{}```'.format(
                                                                             msg))

                                    val = count + 3
                                    reply = await self.bot.wait_for_message(timeout=120, author=ctx.message.author,
                                                                            check=check)
                                    if reply and not reply.content.startswith(pre):
                                        await self.bot.delete_message(reply)

                                        index = int(reply.content) - 1
                                        word = self.bot.log_conf['blacklisted_channels'][list_of_channels[index]]
                                        del self.bot.log_conf['blacklisted_channels'][list_of_channels[index]]

                                        with open('settings/log.json', 'r+') as log:
                                            log.seek(0)
                                            log.truncate()
                                            json.dump(self.bot.log_conf, log, indent=4)
                                        with open('settings/log.json', 'r') as log:
                                            self.bot.log_conf = json.load(log)

                                        await self.bot.edit_message(menu,
                                                                    bot_prefix + 'Successfully removed ``{}`` from the blacklist.'.format(
                                                                        word))

                # Keyword notifier settings
                elif reply.content == '5':
                    val = 7
                    webhook_is_set = 'Set' if self.bot.log_conf['webhook_url'] == '' else 'Change'

                    bot_token_is_set = 'Set' if self.bot.log_conf['notifier_bot_token'] == '' else 'Change'

                    await self.bot.edit_message(menu,
                                                         bot_prefix + '```\n\u2757 Get notified when a keyword gets detected. How should you get notified? Enter a number:\n\n1. Get pinged in the log location channel.\n2. Send a message in the log location channel (no ping).\n3. Get notified via direct message.\n4. Turn off notifier.\n5. {} webhook url (for ping/message).\n6. {} proxy bot token (for direct message).```'.format(webhook_is_set, bot_token_is_set))

                    reply = await self.bot.wait_for_message(author=ctx.message.author,
                                                            check=check)

                    if reply and not reply.content.startswith(pre):
                        await self.bot.delete_message(reply)
                        webhook_info = '```\n\u2757 This requires you to set up a webhook which will notify you. Here\'s how you set it up:\n\n1. Go to the server where you want to receive notifications. (Your log location). You probably want this to be a private server that you own.\n2. Go to your Server Settings (here: https://imgur.com/PofYpiZ) and go to WebHooks near the bottom. Create a webhook.\n3. Give it whatever name and avatar you like and change the channel to the channel where you want to receive notifications. Copy the url and **make sure you hit save.** (should look like this: http://i.imgur.com/ndGSLSb.png).\n\nPaste the url below (if no confirmation is given, navigate back to this menu again and paste it.)```'
                        bot_token_info = '```\n\u2757 This requires a proxy bot. Here\'s how you can set that up:\n\n1. Create a Discord bot account and get the bot\'s token. Then add the bot to the server where you are logging. Follow these quick steps: https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token\n2. Make sure to give the bot read, send, edit messages, and embed permissions in the channel you are keyword logging in.\n\nPaste the **token** below (NOT the client secret!). Navigate back to this menu and paste the token again if no confirmation is given.```'
                        if reply.content == '1' or reply.content == '2':
                            # Set up webhook url
                            if self.bot.log_conf['webhook_url'] == '':
                                await self.bot.edit_message(menu,
                                                                    bot_prefix + webhook_info)
                                url = await self.bot.wait_for_message(author=ctx.message.author,
                                                                      check=not_block)
                                if url and not url.content.startswith(pre):
                                    await self.bot.delete_message(url)
                                    await self.webhook_url(ctx, url.content)

                                    # Set notifications to ping
                                    if reply.content == '1':
                                        await self.bot.delete_message(menu)
                                        await self.notify_ping(ctx)

                                    # Set notifications to msg
                                    elif reply.content == '2':
                                        await self.bot.delete_message(menu)
                                        await self.notify_msg(ctx)
                            else:
                                # Set notifications to ping
                                if reply.content == '1':
                                    await self.bot.delete_message(menu)
                                    await self.notify_ping(ctx)

                                # Set notifications to msg
                                elif reply.content == '2':
                                    await self.bot.delete_message(menu)
                                    await self.notify_msg(ctx)

                        # Set notifications to dm
                        elif reply.content == '3':
                            if self.bot.log_conf['notifier_bot_token'] == '':
                                await self.bot.edit_message(menu,
                                                                    bot_prefix + bot_token_info)
                                reply = await self.bot.wait_for_message(author=ctx.message.author,
                                                                        check=not_block)
                                if reply and not reply.content.startswith(pre):
                                    await self.bot.delete_message(reply)
                                    await self.bot.delete_message(menu)
                                    await self.bot_token(ctx, reply.content)
                                    await self.notify_dm(ctx)
                            else:
                                await self.bot.delete_message(menu)
                                await self.notify_dm(ctx)

                        # Turn off the notifier
                        elif reply.content == '4':
                            await self.bot.delete_message(menu)
                            await self.notify_off(ctx)

                        # Set webhook url
                        elif reply.content == '5':
                            await self.bot.edit_message(menu, bot_prefix + webhook_info)
                            url = await self.bot.wait_for_message(author=ctx.message.author,
                                                                check=not_block)

                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(menu)
                                await self.bot.delete_message(url)
                                await self.webhook_url(ctx, url.content)

                        # Set dm bot token
                        elif reply.content == '6':
                            await self.bot.edit_message(menu, bot_prefix + bot_token_info)
                            token = await self.bot.wait_for_message(author=ctx.message.author,
                                                                check=not_block)

                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(menu)
                                await self.bot.delete_message(token)
                                await self.bot_token(ctx, token.content)

                # User following options
                elif reply.content == '6':
                    val = 5
                    await self.bot.edit_message(menu,
                                                         bot_prefix + '```\n\ud83c\udfc3 Stalking people is fun! What are we doing? Enter a number.\n\n1. Turn on/off user following (currently {}).\n2. Add a person to follow.\n3. Remove a person that is being followed.\n4. View who you are following.```'.format(self.bot.log_conf['user_logging']))
                    reply = await self.bot.wait_for_message(author=ctx.message.author, check=check)
                    if reply and not reply.content.startswith(pre):
                        await self.bot.delete_message(reply)

                    if reply.content == '1':
                        with open('settings/log.json', 'r+') as log:
                            if self.bot.log_conf['user_logging'] == 'on':
                                self.bot.log_conf['user_logging'] = 'off'
                            else:
                                self.bot.log_conf['user_logging'] = 'on'
                            log.seek(0)
                            log.truncate()
                            json.dump(self.bot.log_conf, log, indent=4)
                        await self.bot.edit_message(menu, bot_prefix + 'Turned {} the user logger.'.format(self.bot.log_conf['user_logging']))
                        with open('settings/log.json', 'r') as log:
                            self.bot.log_conf = json.load(log)

                    elif reply.content == '2':
                        await self.bot.edit_message(menu,
                                                             bot_prefix + '```\n\ud83c\udfc3 Input the person you want to follow. Can be a mention, the user id, or the fullname + discriminator. User id can be obtained by enabling developer mode (http://i.imgur.com/KMDS8cb.png) and then right clicking on the user in chat > copy id.\n\nInput user:```')
                        reply = await self.bot.wait_for_message(author=ctx.message.author, check=not_block)
                        if reply and not reply.content.startswith(pre):
                            await self.bot.delete_message(reply)
                            try:
                                user = reply.mentions[0]
                            except:
                                user = None
                                for j in self.bot.servers:
                                    user = j.get_member_named(reply.content)
                                    if user:
                                        break
                                if not user:
                                    for j in self.bot.servers:
                                        user = j.get_member(reply.content)
                                        if user:
                                            break
                            if not user:
                                return await self.bot.edit_message(menu, bot_prefix + 'Could not find user.')
                            await self.bot.edit_message(menu,
                                                                bot_prefix + '```\n\ud83d\udd50 Input the number of minutes the user must go without sending a message before you can get a notification from him posting. This is basically a cooldown to prevent mass pings. Decimals are supported.\n\nInput number of minutes:```')
                            reply = await self.bot.wait_for_message(author=ctx.message.author, check=not_block)
                            if reply and not reply.content.startswith(pre):
                                await self.bot.delete_message(reply)
                                if reply.content.isdigit():
                                    self.bot.log_conf['keyusers']['{} all'.format(user.id)] = [0.0, float(reply.content) * 60.0]
                                else:
                                    return await self.bot.edit_message(menu, bot_prefix + 'Error, not a number.')
                                with open('settings/log.json', 'r+') as log:
                                    log.seek(0)
                                    log.truncate()
                                    json.dump(self.bot.log_conf, log, indent=4)
                                with open('settings/log.json', 'r') as log:
                                    self.bot.log_conf = json.load(log)
                                await self.bot.edit_message(menu, bot_prefix + 'Successfully added user: ``{}``'.format(user.name))

                    elif reply.content == '3':
                        msg = '1. '
                        count = 0
                        list_of_users = []
                        for count, user in enumerate(self.bot.log_conf['keyusers']):
                            try:
                                member = None
                                if ' all' in user:
                                    for server in self.bot.servers:
                                        member = server.get_member(user[:-4])
                                        if member:
                                            msg += '{} CD: {} mins  {}. '.format(str(member.name),
                                                                             str(self.bot.log_conf['keyusers'][user][1] / 60.0), count+2)
                                            list_of_users.append(user)
                                            break
                                    if not member:
                                        continue
                                else:
                                    try:
                                        server = self.bot.get_server(user.split(' ')[1])
                                        member = server.get_member(user.split(' ')[0])
                                        msg += '{} in server: {} CD: {} mins  {}. '.format(str(member.name),
                                                                                       str(server.name), str(
                                                self.bot.log_conf['keyusers'][user][1] / 60.0), count+2)
                                        list_of_users.append(user)
                                    except:
                                        continue
                            except:
                                pass

                        msg = msg[:-(len(str(count + 2)) + 2)]

                        val = count+2
                        await self.bot.edit_message(menu,
                                                            bot_prefix + '```\n\ud83c\udfc3 Enter the number to remove the user.\n\n{}```'.format(msg))
                        reply = await self.bot.wait_for_message(author=ctx.message.author, check=check)
                        if reply and not reply.content.startswith(pre):
                            await self.bot.delete_message(reply)
                            index = int(reply.content) - 1
                            word = self.bot.log_conf['keyusers'][list_of_users[index]]
                            del self.bot.log_conf['keyusers'][list_of_users[index]]

                            with open('settings/log.json', 'r+') as log:
                                log.seek(0)
                                log.truncate()
                                json.dump(self.bot.log_conf, log, indent=4)
                            with open('settings/log.json', 'r') as log:
                                self.bot.log_conf = json.load(log)

                            await self.bot.edit_message(menu,
                                                        bot_prefix + 'Successfully removed the user.'.format(
                                                            word))

                    elif reply.content == '4':
                        msg = ''
                        for user in self.bot.log_conf['keyusers']:
                            try:
                                member = None
                                if ' all' in user:
                                    for server in self.bot.servers:
                                        member = server.get_member(user[:-4])
                                        if member:
                                            msg += '{} CD: {} mins, '.format(str(member.name),
                                                                             str(self.bot.log_conf['keyusers'][user][1] / 60.0))
                                            break
                                    if not member:
                                        continue
                                else:
                                    try:
                                        server = self.bot.get_server(user.split(' ')[1])
                                        member = server.get_member(user.split(' ')[0])
                                        msg += '{} in server: {} CD: {} mins, '.format(str(member.name),
                                                                                       str(server.name), str(
                                                self.bot.log_conf['keyusers'][user][1] / 60.0))
                                    except:
                                        continue
                            except:
                                pass

                                msg = msg.rstrip(', ')

                        await self.bot.edit_message(menu,
                                                            bot_prefix + '```\n\ud83c\udfc3 List of users being followed:\n\n{}```'.format(
                                                                msg))

                # Show all settings
                elif reply.content == '7':
                    with open('settings/notify.json') as n:
                        notif = json.load(n)
                        notif_type = notif['type']
                        msg = 'Message logger info:\n```\n\ud83d\udcfa Keyword logging: %s\n\nNotification type: %s\n\nLog location: ' % (
                        self.bot.log_conf['keyword_logging'], notif_type)
                        if self.bot.log_conf['log_location'] == '':
                            msg += 'No log location set.\n\n'
                        else:
                            location = self.bot.log_conf['log_location'].split()
                            server = self.bot.get_server(location[1])
                            msg += '%s in server %s\n\n' % (str(server.get_channel(location[0])), str(server))
                        msg += 'Keywords: '
                        for word in self.bot.log_conf['keywords']:
                            if ' [server]' in word:
                                key, server = word.split(' [server]')
                                server = self.bot.get_server(server)
                                msg += '{} in server: {}, '.format(key, server)
                            elif ' [channel]' in word:
                                key, channel = word.split(' [channel]')
                                channel = self.bot.get_channel(channel)
                                msg += '{} in channel: {}, '.format(key, channel)
                            elif word.startswith('[isolated]'):
                                msg += word[10:] + ', '
                            else:
                                msg += word + ', '

                        msg = msg.rstrip(', ')
                        msg += '\n\nServers to log: '
                        if self.bot.log_conf['allservers'] == 'False':
                            server = ''
                            for i in self.bot.log_conf['servers']:
                                try:
                                    server = self.bot.get_server(i)
                                except:
                                    pass
                                msg += str(server) + ', '
                            msg = msg.rstrip(', ')
                        else:
                            msg += 'All Servers'
                        msg += '\n\nBlacklisted Words: '
                        for i in self.bot.log_conf['blacklisted_words']:
                            if '[server]' in i:
                                word, id = i.split('[server]')
                                name = self.bot.get_server(id)
                                if name:
                                    msg += word + '(for server: %s)' % str(name) + ', '
                            elif '[channel]' in i:
                                word, id = i.split('[channel]')
                                name = self.bot.get_channel(id)
                                if name:
                                    msg += word + '(for channel: %s)' % str(name) + ', '
                            else:
                                msg += i + ', '
                        msg = msg.rstrip(', ')
                        msg += '\n\nBlacklisted Users: '
                        names = []
                        for i in self.bot.servers:
                            for j in self.bot.log_conf['blacklisted_users']:
                                name = i.get_member(j)
                                if name:
                                    if name.name not in names:
                                        names.append(name.name)
                                        msg += name.name + ', '
                        msg = msg.rstrip(', ')
                        server = ''
                        msg += '\n\nBlacklisted Servers: '
                        for i in self.bot.log_conf['blacklisted_servers']:
                            try:
                                server = self.bot.get_server(i)
                            except:
                                pass
                            if server:
                                msg += str(server) + ', '
                        msg = msg.rstrip(', ')
                        channel = ''
                        msg += '\n\nBlacklisted Channels: '
                        for i in self.bot.log_conf['blacklisted_channels']:
                            try:
                                channel = self.bot.get_channel(i)
                                server = self.bot.get_server(self.bot.log_conf['blacklisted_channels'][i])
                            except:
                                pass
                            if channel:
                                msg += '{} in server: {}, '.format(str(channel), str(server))
                        msg = msg.rstrip(', ')
                        msg += '\n\nContext length: %s messages\n\nUser follows: ' % self.bot.log_conf['context_len']
                        for user in self.bot.log_conf['keyusers']:
                            try:
                                member = None
                                if ' all' in user:
                                    for server in self.bot.servers:
                                        member = server.get_member(user[:-4])
                                        if member:
                                            msg += '{} CD: {} mins, '.format(str(member.name),
                                                                             str(self.bot.log_conf['keyusers'][user][1] / 60.0))
                                            break
                                    if not member:
                                        continue
                                else:
                                    try:
                                        server = self.bot.get_server(user.split(' ')[1])
                                        member = server.get_member(user.split(' ')[0])
                                        msg += '{} in server: {} CD: {} mins, '.format(str(member.name),
                                                                                       str(server.name), str(
                                                self.bot.log_conf['keyusers'][user][1] / 60.0))
                                    except:
                                        continue
                            except:
                                pass
                        msg = msg.rstrip(', ') + '```'

                    if len(msg) > 1950 or 'gist' in ctx.message.content:
                        gist_log = PythonGists.Gist(description='Logging info.', content=msg, name='log.txt')
                        await self.bot.edit_message(menu, bot_prefix + gist_log)
                    else:
                        await self.bot.edit_message(menu, bot_prefix + msg)

                # Detailed information about the keyword logger/notifier
                else:
                    await self.bot.edit_message(menu, bot_prefix + '```The Keyword Logger/Notifier is a nice way to keep track of anything and everything that\'s going on in your Discord servers.\nWant to find out when people are talking about you? Add your name as a keyword!\nWant to know when someone is talking about your favorite character/game/whatever? Add the game as a keyword.\n\nFirst steps:\n1. Set up where you want the bot to log these messages that will contain your keywords. Set a log location via option 2 in the main menu.\n2. Set up a way to get notified when the messages get logged. This is done via option 5 in the main menu.\n3. Customize even more by blacklisting certain words, users, etc.\n\nFor more detailed information, view the wiki section: https://github.com/appu1232/Discord-Selfbot#keyword-notifier```')

    @log.command(pass_context=True)
    async def history(self, ctx, txt: str = None):
        """View the last n messages in this channel. Ex: >log history 20"""
        if txt:
            if txt.startswith('save'):
                if txt[5:].strip():
                    size = txt[5:].strip()
                    if size.isdigit():
                        save = True
                        skip = 0
                        fetch = await self.bot.send_message(ctx.message.channel, bot_prefix + 'Saving messages...')
                    else:
                        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax.')
                        return
                else:
                    await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax.')
                    return
            else:
                save = False
                skip = 2

                def check(msg):
                    if msg:
                        return msg.content.lower().strip() == 'y' or msg.content.lower().strip() == 'n'
                    else:
                        return False
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Are you sure you want to output all the messages here? ``(y/n)``.')
                reply = await self.bot.wait_for_message(timeout=10, author=ctx.message.author, check=check)
                if reply:
                    if reply.content.lower().strip() == 'n':
                        return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled.')
                else:
                    return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled.')
                fetch = await self.bot.send_message(ctx.message.channel, bot_prefix + 'Fetching messages...')
                size = txt
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
                                                    bot_prefix + 'Showing last ``%s`` messages: ```%s```' % (
                                                    txt, msg))
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
                                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Showing last ``%s`` messages: ```%s```' % (txt, i))
                            else:
                                await self.bot.send_message(ctx.message.channel, '```%s```' % i)
                        await self.bot.delete_message(fetch)
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax.')

    @log.command(pass_context=True)
    async def location(self, ctx, *, msg: str = None):
        """Set log location for keyword logging. See wiki for more info"""
        await self.log_location(ctx, msg)

    @log.command(pass_context=True)
    async def location2(self, ctx):
        """Set optional seperate location for user follows. See wiki for more info"""
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            settings['user_location'] = ctx.message.channel.id + ' ' + ctx.message.server.id
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        if settings['user_location'] == settings['log_location']:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'User follows and keywords will both log in this channel.')
        else:
            if settings['webhook_url2'] == "":
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'User follows will now log in this channel, however, you will need to set up a separate webhook for this. '
                                                                              'Follow the instructions on how to set up a webhook found in the keyword logger section and add it for the user follows with ``>webhook2 <webhook_url>``')
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'User follows will now log in this channel instead of the keyword logger channel.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    @log.command(pass_context=True)
    async def toggle(self, ctx):
        """Toggle logging of all servers or only added servers."""
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
        await self.bot.send_message(ctx.message.channel, bot_prefix + msg)
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    @log.command(aliases=['on'], pass_context=True)
    async def start(self, ctx):
        """Turn on keyword logging (on by default)."""
        await self.start_logger(ctx)

    @log.command(aliases=['off'], pass_context=True)
    async def stop(self, ctx):
        """Turn off keyword logging"""
        await self.stop_logger(ctx)

    @log.command(aliases=['useron'], pass_context=True)
    async def userstart(self, ctx):
        """Start user follows if off."""
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            settings['user_logging'] = 'on'
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Turned on the user logger.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    @log.command(aliases=['useroff'], pass_context=True)
    async def userstop(self, ctx):
        """Stop user follows."""
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            settings['user_logging'] = 'off'
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Turned off the user logger.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    @log.command(pass_context=True)
    async def refresh(self, ctx, *, user: str = None):
        """Refresh cooldown for user follows."""
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if user:
                for key in settings['keyusers']:
                    if user in key:
                        settings['keyusers'][key] = [0.0, settings['keyusers'][key][1]]
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Refreshed notification cooldown for this user.')
            else:
                for user in settings['keyusers']:
                    settings['keyusers'][user] = [0.0, settings['keyusers'][user][1]]
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Refreshed notification cooldown.')
            log.seek(0)
            log.truncate()
            json.dump(settings, log, indent=4)
        await self.bot.delete_message(ctx.message)
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)
            self.bot.key_users = self.bot.log_conf['keyusers']

    @log.command(pass_context=True)
    async def context(self, ctx, *, msg: str = None):
        """Set context length for keywords logged. See wiki for more info"""
        if msg:
            if msg.isdigit():
                if 0 < int(msg) < 21:
                    with open('settings/log.json', 'r+') as log:
                        settings = json.load(log)
                        settings['context_len'] = msg
                        log.seek(0)
                        log.truncate()
                        json.dump(settings, log, indent=4)
                    with open('settings/log.json', 'r') as log:
                        self.bot.log_conf = json.load(log)
                    await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set context length to ``%s``.' % msg)
                else:
                    await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid context length.')
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax.')
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax. No value given.')

    @log.command(pass_context=True)
    async def add(self, ctx):
        """Add a server to log from. See wiki for more info"""
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if ctx.message.server.id not in settings['servers']:
                settings['servers'].append(ctx.message.server.id)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Added server to logger.')
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'This server is already in the logger.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    @log.command(pass_context=True)
    async def remove(self, ctx):
        """Remove a server that is being logged. See wiki for more info"""
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if ctx.message.server.id in settings['servers']:
                settings['servers'].remove(ctx.message.server.id)
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Removed server from the logger.')
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'This server is not in the logger.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    @log.command(pass_context=True, aliases=['removekey', 'addblacklist', 'removeblacklist'])
    async def addkey(self, ctx):
        """Add a keyword to the keyword logger. See wiki for more info"""
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'This is no longer a command. Use ``>log`` instead to change keyword logger/notifier settings.')

    @log.command(pass_context=True)
    async def adduser(self, ctx, *, msg: str):
        """Add a user to follow. See wiki for more info"""
        if ' | ' in msg.strip():
            data = msg.strip().split(' | ')
            if len(data) == 2:
                id = data[0]
                stalk_servers = True
                interval = data[1]
            else:
                id = data[0]
                stalk_servers = self.bot.get_server(data[1])
                if not stalk_servers:
                    return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Server not found. Are you using the command right?\nSyntax:``>log adduser <user_id> | <minutes>``\nEx: ``>log adduser {} | 60``'.format(self.bot.user.id))
                interval = data[2]
            try:
                interval = float(interval)
            except:
                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid interval. Enter a number.\nSyntax:``>log adduser <user_id> | <minutes>``\nEx: ``>log adduser {} | 60``'.format(self.bot.user.id))
            user = None
            for server in self.bot.servers:
                user = server.get_member(id)
                if user:
                    break
            if not user:
                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find specified user. Are you using the command right?\nSyntax:``>log adduser <user_id> | <minutes>``\nEx: ``>log adduser {} | 60``'.format(self.bot.user.id))

            if stalk_servers is True:
                key = id + ' all'
            else:
                key = id + ' ' + stalk_servers.id

            with open('settings/log.json', 'r+') as log:
                settings = json.load(log)
                if msg not in settings['keywords'] and msg is not None:
                    settings['keyusers'][key] = [0.0, float(interval) * 60.0]
                    log.seek(0)
                    log.truncate()
                    json.dump(settings, log, indent=4)
            if stalk_servers is True:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Now ~~stalking~~ following ``{}``.'.format(user.name))
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Now ~~stalking~~ following ``{}`` in server ``{}``.'.format(user.name, self.bot.get_server(stalk_servers.id).name))
            with open('settings/log.json', 'r') as log:
                self.bot.log_conf = json.load(log)
                self.bot.key_users = self.bot.log_conf['keyusers']

        else:
            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax. Proper use: ``>log adduser <user_id> | <minutes>``\nEx: ``>log adduser {} | 60``'.format(self.bot.user.id))

    @log.command(pass_context=True)
    async def removeuser(self, ctx, *, msg: str):
        """Remove a user that is being followed. See wiki for more info"""
        if ' | ' in msg.strip():
            user = msg.strip().replace(' | ', ' ')
        else:
            user = msg.strip() + ' all'
        with open('settings/log.json', 'r+') as log:
            settings = json.load(log)
            if user in settings['keyusers']:
                del settings['keyusers'][user]
                log.seek(0)
                log.truncate()
                json.dump(settings, log, indent=4)
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Stopped following this user.')
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find user.')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)
            self.bot.key_users = self.bot.log_conf['keyusers']

    @commands.command(pass_context=True)
    async def webhook(self, ctx, *, msg):
        """Set up a webhook for keyword logging. See wiki for more info"""
        await self.webhook_url(ctx, msg)

    @commands.command(pass_context=True)
    async def webhook2(self, ctx, *, msg):
        """Set up optional second webhook for user follows. See wiki for more info"""
        with open('settings/log.json', 'r+') as l:
            log = json.load(l)
            if 'webhook_url' not in log:
                log['webhook_url2'] = ''
            log['webhook_url2'] = msg.lstrip('<').rstrip('>').strip('"')
            l.seek(0)
            l.truncate()
            json.dump(log, l, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Set up webhook for user follow notifications!')
        with open('settings/log.json', 'r') as log:
            self.bot.log_conf = json.load(log)

    @commands.group(pass_context=True)
    async def notify(self, ctx):
        """Manage notifier bot. See wiki for more info."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax. Possible commands:\n``>notify token <token>`` - Set the bot token for the proxy bot.\n``>notify msg`` - sends message to your keyword logger channel through webhook. (get notification if you have notification settings set to all messages in that server).\n``>notify ping`` - recieve notifications via mention in your keyword logger channel through webhook.\n``>notify dm`` - recieve notifications via direct message through proxy bot.\n``>notify off`` - Turn off all notifications.')

    # Set notifications to ping
    @notify.command(pass_context=True)
    async def ping(self, ctx):
        """Set to ping you when a keyword gets logged. See wiki for more info"""
        await self.notify_ping(ctx)

    # Set notifications to msg
    @notify.command(aliases=['message'], pass_context=True)
    async def msg(self, ctx):
        """Set to just send msg when keyword gets logged. See wiki for more info"""
        await self.notify_msg(ctx)

    # Set notifications to dm
    @notify.command(aliases=['pm', 'pms', 'direct message', 'direct messages', 'dms'], pass_context=True)
    async def dm(self, ctx):
        """Set to direct message you when keyword gets logged. See wiki for more info"""
        await self.notify_dm(ctx)

    # Set notifications to ping
    @notify.command(aliases=['none'], pass_context=True)
    async def off(self, ctx):
        """Turn off notifier for keyword logging. See wiki for more info"""
        await self.notify_off(ctx)

    # Set bot token
    @notify.command(pass_context=True)
    async def token(self, ctx, *, msg):
        """Set token for direct message bot. See wiki for more info"""
        await self.bot_token(ctx, msg)


def setup(bot):
    bot.add_cog(KeywordLogger(bot))
