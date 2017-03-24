import discord
import datetime
import asyncio
import os
import prettytable
import strawpy
import random
import psutil
from appuselfbot import isBot
from discord.ext import commands
from cogs.utils.checks import *

'''Module for miscellaneous commands including game set, server commands, and more.'''

class Misc:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def about(self, ctx):
        """Links to the bot's github page."""
        await self.bot.send_message(ctx.message.channel, 'https://github.com/appu1232/Selfbot-for-Discord')
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        """Bot stats."""
        uptime = (datetime.datetime.now() - self.bot.uptime)
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            time = '%s days, %s hours, %s minutes, and %s seconds' % (days, hours, minutes, seconds)
        else:
            time = '%s hours, %s minutes, and %s seconds' % (hours, minutes, seconds)
        if not ctx.message.author.game or ctx.message.author.game is not str:
            game = 'None'
        else:
            game = ctx.message.author.game
        if embed_perms(ctx.message):
            em = discord.Embed(title='Bot Stats', color=0x32441c)
            em.add_field(name=u'\U0001F553 Uptime', value=time, inline=False)
            em.add_field(name=u'\U0001F4E4 Messages sent', value=str(self.bot.icount))
            em.add_field(name=u'\U0001F4E5 Messages recieved', value=str(self.bot.message_count))
            em.add_field(name=u'\u2757 Mentions', value=str(self.bot.mention_count))
            em.add_field(name=u'\u2694 Servers', value=str(len(self.bot.servers)))
            em.add_field(name=u'\u270F Keywords logged', value=str(self.bot.keyword_log))
            em.add_field(name=u'\U0001F3AE Game', value=game)
            await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        else:
            msg = '**Bot Stats:** ```Uptime: %s\nMessages Sent: %s\nMessages Recieved: %s\nMentions: %s\nServers: %s\nKeywords logged: %s\nGame: %s```' % (time, str(self.bot.icount), str(self.bot.message_count), str(self.bot.mention_count), str(len(self.bot.servers)), str(self.bot.keyword_log), game)
            await self.bot.send_message(ctx.message.channel, isBot + msg)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def embed(self, ctx, *, msg):
        """Embed given text. Ex: >embed some stuff"""
        em = discord.Embed(description=msg)
        await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        await self.bot.delete_message(ctx.message)

    # Stats about current server
    @commands.group(pass_context=True)
    async def server(self, ctx):
        """Various info about the server. See the README for more info."""
        if ctx.invoked_subcommand is None:
            if ctx.message.content[7:]:
                server = None
                for i in self.bot.servers:
                    if i.name.lower() == ctx.message.content[7:].lower().strip():
                        server = i
                        break
                if not server:
                    await self.bot.send_message(ctx.message.channel, isBot + 'Could not find server. Note: You must be a member of the server you are trying to search.')
                    return
            else:
                server = ctx.message.server

            online = 0
            for i in server.members:
                if str(i.status) == 'online':
                    online += 1
            if embed_perms(ctx.message):
                em = discord.Embed(color=0xea7938)
                em.add_field(name='Name', value=server.name)
                em.add_field(name='Owner', value=server.owner, inline=False)
                em.add_field(name='Members', value=server.member_count)
                em.add_field(name='Currently Online', value=online)
                em.add_field(name='Region', value=server.region)
                em.add_field(name='Verification Level', value=str(server.verification_level))
                em.add_field(name='Highest role:', value=server.role_hierarchy[0])
                em.add_field(name='Default Channel', value=server.default_channel)
                em.add_field(name='Created At', value=server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.set_thumbnail(url=server.icon_url)
                em.set_author(name='Server Info', icon_url='https://i.imgur.com/RHagTDg.png')
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                msg = '**Server Info:** ```Name: %s\nOwner: %s\nMembers: %s\nCurrently Online: %s\nRegion: %s\nVerification Level: %s\nHighest Role: %s\nDefault Channel: %s\nCreated At: %s\nServer avatar: : %s```' % (server.name, server.owner, server.member_count, online, server.region, str(server.verification_level), server.role_hierarchy[0], server.default_channel, server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), server.icon_url)
                await self.bot.send_message(ctx.message.channel, isBot + msg)
            await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def emojis(self, ctx):
        """List all emojis in this server."""
        msg = ''
        for i in ctx.message.server.emojis:
            msg += str(i)
        await self.bot.send_message(ctx.message.channel, msg)
        await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def avi(self, ctx):
        """Get server avatar image link."""
        if ctx.message.content[11:]:
            server = None
            for i in self.bot.servers:
                if i.name.lower() == ctx.message.content[11:].lower().strip():
                    server = i
                    break
            if not server:
                await self.bot.send_message(ctx.message.channel, isBot + 'Could not find server. Note: You must be a member of the server you are trying to search.')
                return
        else:
            server = ctx.message.server
        if embed_perms(ctx.message):
            em = discord.Embed()
            em.set_image(url=server.icon_url)
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            await self.bot.send_message(ctx.message.channel, isBot + server.icon_url)
        await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def role(self, ctx, *, msg):
        await self.bot.delete_message(ctx.message)
        for role in ctx.message.server.roles:
            if msg == role.name:
                role_count = 0
                for user in ctx.message.server.members:
                    if role in user.roles:
                        role_count += 1
                em = discord.Embed(title='Role Info', color=role.color)
                em.add_field(name='Name', value=role.name)
                em.add_field(name='ID', value=role.id, inline=False)
                em.add_field(name='Members in this role', value=role_count)
                em.add_field(name='Role color hex value', value=str(role.color))
                em.add_field(name='Role color rgb value', value=role.color.to_tuple())
                em.add_field(name='Mentionable', value=role.mentionable)
                em.add_field(name='Created at', value=role.created_at.__format__('%x at %X'))
                return await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        await self.bot.send_message(ctx.message.channel, isBot + 'Could not find role ``%s``' % msg)

    @server.group(pass_context=True)
    async def members(self, ctx):
        """List of members in the server."""
        msg = prettytable.PrettyTable(['User', 'Nickname', 'Join Date', 'Account Created', 'Color', 'Top Role', 'Is bot', 'Avatar url', 'All Roles'])
        for i in ctx.message.server.members:
            roles = ''
            for j in i.roles:
                if j.name != '@everyone':
                    roles += j.name + ', '
            if i.avatar_url[60:].startswith('a_'):
                avi = 'https://images.discordapp.net/avatars/' + i.avatar_url[33:][:18] + i.avatar_url[59:-3] + 'gif'
            else:
                avi = i.avatar_url
            try:
                join = i.joined_at.__format__('%x at %X')
            except:
                join = 'N/A'
            try:
                create = i.created_at.__format__('%x at %X')
            except:
                create = 'N/A'
            msg.add_row([str(i.name), i.nick, join, create, i.color, i.top_role, str(i.bot), avi, roles[:-2]])
        name = ctx.message.server.name
        keep_characters = (' ', '.', '_')
        name = ''.join(c for c in name if c.isalnum() or c in keep_characters).rstrip()
        name = name.replace(' ', '_')
        save_file = '%s_members.txt' % name
        try:
            msg = msg.get_string(sortby='User')
        except:
            pass
        with open(save_file, 'w') as file:
            file.write(str(msg))
        with open(save_file, 'rb') as file:
            await self.bot.send_file(ctx.message.channel, file)
        os.remove(save_file)

    @commands.command(pass_context=True)
    async def game(self, ctx):
        """Set playing status. Ex: >game napping"""
        if ctx.message.content[6:]:
            game = ctx.message.clean_content[6:].encode('utf-8')

            # Cycle games if more than one game is given.
            if ' | ' in ctx.message.content[6:]:
                self.bot.game = game
                await self.bot.send_message(ctx.message.channel, isBot + 'Input interval in seconds to wait before changing to the next game (``n`` to cancel):')

                def check(msg):
                    return msg.content.isdigit() or msg.content.lower().strip() == 'n'

                def check2(msg):
                    return msg.content == 'random' or msg.content.lower().strip() == 'r' or msg.content.lower().strip() == 'order' or msg.content.lower().strip() == 'o'

                reply = await self.bot.wait_for_message(author=ctx.message.author, check=check, timeout=60)
                if reply.content.lower().strip() == 'n':
                    self.bot.game = None
                    await self.bot.change_presence(game=discord.Game(name=None))
                    return await self.bot.send_message(ctx.message.channel, isBot + 'Cancelled')
                elif reply.content.strip().isdigit():
                    interval = int(reply.content.strip())
                    if interval >= 10:
                        self.bot.game_interval = interval
                        games = self.bot.game.decode('utf-8').split(' | ')
                        if len(games) != 2:
                            await self.bot.send_message(ctx.message.channel, isBot + 'Changes games in order or randomly? Input ``o`` for order or ``r`` for random:')
                            s = await self.bot.wait_for_message(author=ctx.message.author, check=check2, timeout=60)
                            if s.content.strip() == 'r' or s.content.strip() == 'random':
                                await self.bot.send_message(ctx.message.channel,
                                                            isBot + 'Game set. Game will randomly change every ``%s`` seconds' % reply.content.strip())
                                random = True
                            else:
                                random = False
                        else:
                            random = False

                        if not random:
                            await self.bot.send_message(ctx.message.channel,
                                                        isBot + 'Game set. Game will change every ``%s`` seconds' % reply.content.strip())

                        current_game = len(games)
                        next_game = current_game

                        while self.bot.game_interval:
                            if random:
                                while next_game == current_game:
                                    next_game = random.randint(0, len(games) - 1)
                                current_game = next_game
                                await self.bot.change_presence(game=discord.Game(name=games[current_game]))
                                await asyncio.sleep(interval)
                            else:
                                for j in games:
                                    await self.bot.change_presence(game=discord.Game(name=j))
                                    await asyncio.sleep(interval)
                                    if not self.bot.game_interval:
                                        break
                        return
                    else:
                        return await self.bot.send_message(ctx.message.channel, isBot + 'Interval is too short. Must be at least 10 seconds.')

            # Set game if only one game is given.
            else:
                self.bot.game = game
                self.bot.game_interval = None
                await self.bot.change_presence(game=discord.Game(name=game.decode('utf-8')))
                await self.bot.send_message(ctx.message.channel, isBot + 'Game set as: ``Playing %s``' % ctx.message.content[6:])

        # Remove game status.
        else:
            self.bot.game = None
            self.bot.game_interval = None
            await self.bot.change_presence(game=None)
            await self.bot.send_message(ctx.message.channel, isBot + 'Set playing status off')
            if os.path.isfile('game.txt'):
                os.remove('game.txt')
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def choose(self, ctx, *, choices: str):
        """Choose randomly from the options you give. >choose this | that"""
        await self.bot.send_message(ctx.message.channel, isBot + 'I choose: ``{}``'.format(random.choice(choices.split("|"))))

    @commands.command(pass_context=True)
    async def emoji(self, ctx, *, msg):
        """Get url of emoji (across any server). Ex: >emoji :smug:"""
        url = None
        exact_match = False
        for server in self.bot.servers:
            for emoji in server.emojis:
                if msg.strip().lower() in str(emoji):
                    url = emoji.url
                if msg.strip() == str(emoji).split(':')[1]:
                    url = emoji.url
                    exact_match = True
                    break
            if exact_match:
                break
        if embed_perms(ctx.message) and url:
            em = discord.Embed()
            em.set_image(url=url)
            await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        elif not embed_perms(ctx.message) and url:
            await self.bot.send_message(ctx.message.channel, url)
        else:
            await self.bot.send_message(ctx.message.channel, isBot + 'Could not find emoji.')

        return await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Get response time."""
        msgtime = ctx.message.timestamp.now()
        await self.bot.send_message(ctx.message.channel, isBot + ' pong')
        now = datetime.datetime.now()
        ping = now - msgtime
        if embed_perms(ctx.message):
            pong = discord.Embed(title='Response Time:', description=str(ping), color=0x7A0000)
            pong.set_thumbnail(url='http://odysseedupixel.fr/wp-content/gallery/pong/pong.jpg')
            await self.bot.send_message(ctx.message.channel, content=None, embed=pong)
        else:
            await self.bot.send_message(ctx.message.channel, isBot + '``Response Time: %s``' % str(ping))

    @commands.command(pass_context=True)
    async def quote(self, ctx):
        """Quote the last message sent in the channel."""
        result = None
        if ctx.message.content[6:]:
            length = len(self.bot.all_log[ctx.message.channel.id + ' ' + ctx.message.server.id])
            if length < 201:
                size = length
            else:
                size = 200

            for i in range(length-2, length-size, -1):
                search = self.bot.all_log[ctx.message.channel.id + ' ' + ctx.message.server.id][i]
                if ctx.message.clean_content[6:].lower().strip() in search[0].clean_content.lower() and (search[0].author != ctx.message.author or search[0].content[:7] != '>quote '):
                    result = [search[0], search[0].author, search[0].timestamp]
                    break
                if ctx.message.clean_content[6:].strip() == search[0].id:
                    result = [search[0], search[0].author, search[0].timestamp]
                    break
        else:
            search = self.bot.all_log[ctx.message.channel.id + ' ' + ctx.message.server.id][-2]
            result = [search[0], search[0].author, search[0].timestamp]
        if result:
            await self.bot.delete_message(ctx.message)
            if embed_perms(ctx.message) and result[0].content:
                em = discord.Embed(description=result[0].clean_content, timestamp=result[2], color=0xbc0b0b)
                em.set_author(name=result[1].name, icon_url=result[1].avatar_url)
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                await self.bot.send_message(ctx.message.channel, '%s - %s```%s```' % (result[1].name, result[2], result[0].clean_content))
        else:
            await self.bot.send_message(ctx.message.channel, isBot + 'No quote found.')
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def poll(self, ctx, *, msg):
        """Create a strawpoll. Ex: >poll Favorite color = Blue | Red | Green"""
        try:
            options = [op.strip() for op in msg.split('|')]
            if '=' in options[0]:
                title, options[0] = options[0].split('=')
                options[0] = options[0].strip()
            else:
                title = 'Poll by %s' % ctx.message.author.name
        except:
            return await self.bot.send_message(ctx.message.channel, isBot + 'Invalid Syntax. Example use: ``>poll Favorite color = Blue | Red | Green | Purple``')

        poll = strawpy.create_poll(title.strip(), options)
        await self.bot.send_message(ctx.message.channel, isBot + poll.url)

    @commands.command(pass_context=True)
    async def calc(self, ctx, *, msg):
        """Simple calculator. Ex: >calc 2+2"""
        equation = msg.strip().replace('^', '**')
        if '=' in equation:
            left = eval(equation.split('=')[0])
            right = eval(equation.split('=')[1])
            answer = str(left == right)
        else:
            answer = str(eval(equation))
        if embed_perms(ctx.message):
            em = discord.Embed(color=0xD3D3D3, title='Calculator')
            em.add_field(name='Input:', value=msg.replace('**', '^'), inline=False)
            em.add_field(name='Output:', value=answer, inline=False)
            await self.bot.send_message(ctx.message.channel, content=None, embed=em)
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.send_message(ctx.message.channel, isBot + answer)

    @commands.command(pass_context=True)
    async def l2g(self, ctx, *, msg: str):
        """Creates a googleitfor.me link. Ex: >l2g how do i become cool."""
        lmgtfy = 'http://googleitfor.me/?q='
        words = msg.lower().strip().split(' ')
        for word in words:
            lmgtfy += word + '+'
        await self.bot.send_message(ctx.message.channel, isBot + lmgtfy[:-1])
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def d(self, ctx):
        """Deletes the last message sent or n messages sent. Ex: >d 5"""

        # If number of seconds/messages are specified
        if len(ctx.message.content.lower().strip()) > 2:
            if ctx.message.content[3] == '!':
                killmsg = self.bot.self_log[ctx.message.channel.id][len(self.bot.self_log[ctx.message.channel.id]) - 2]
                timer = int(ctx.message.content[4:].lower().strip())

                # Animated countdown because screw rate limit amirite
                destroy = await self.bot.edit_message(ctx.message, isBot + 'The above message will self-destruct in:')
                msg = await self.bot.send_message(ctx.message.channel, '``%s  |``' % timer)
                for i in range(0, timer, 4):
                    if timer - 1 - i == 0:
                        await self.bot.delete_message(destroy)
                        msg = await self.bot.edit_message(msg, '``0``')
                        break
                    else:
                        msg = await self.bot.edit_message(msg, '``%s  |``' % int(timer - 1 - i))
                        await asyncio.sleep(1)
                    if timer - 1 - i != 0:
                        if timer - 2 - i == 0:
                            await self.bot.delete_message(destroy)
                            msg = await self.bot.edit_message(msg, '``0``')
                            break
                        else:
                            msg = await self.bot.edit_message(msg, '``%s  /``' % int(timer - 2 - i))
                            await asyncio.sleep(1)
                    if timer - 2 - i != 0:
                        if timer - 3 - i == 0:
                            await self.bot.delete_message(destroy)
                            msg = await self.bot.edit_message(msg, '``0``')
                            break
                        else:
                            msg = await self.bot.edit_message(msg, '``%s  -``' % int(timer - 3 - i))
                            await asyncio.sleep(1)
                    if timer - 3 - i != 0:
                        if timer - 4 - i == 0:
                            await self.bot.delete_message(destroy)
                            msg = await self.bot.edit_message(msg, '``0``')
                            break
                        else:
                            msg = await self.bot.edit_message(msg, '``%s  \ ``' % int(timer - 4 - i))
                            await asyncio.sleep(1)
                await self.bot.edit_message(msg, ':bomb:')
                await asyncio.sleep(.5)
                await self.bot.edit_message(msg, ':fire:')
                await self.bot.edit_message(killmsg, ':fire:')
                await asyncio.sleep(.5)
                await self.bot.delete_message(msg)
                await self.bot.delete_message(killmsg)
            else:
                await self.bot.delete_message(self.bot.self_log[ctx.message.channel.id].pop())
                for i in range(0, int(ctx.message.content[3:])):
                    try:
                        await self.bot.delete_message(self.bot.self_log[ctx.message.channel.id].pop())
                    except:
                        pass

        # If no number specified, delete message immediately
        else:
            await self.bot.delete_message(self.bot.self_log[ctx.message.channel.id].pop())
            await self.bot.delete_message(self.bot.self_log[ctx.message.channel.id].pop())
    
    @commands.command(pass_context=True)
    async def spoiler(self, ctx, *, msg : str):
        """Spoiler tags the message using rot13. Ex: >spoiler Some book | They get married."""
        try:
            if " | " in msg:
                spoiled_work, spoiler = msg.lower().split(" | ", 1)
            else:
                spoiled_work, _, spoiler = msg.lower().partition(" ")
            await self.bot.edit_message(ctx.message, isBot + 'Spoiler for `' + spoiled_work + '`: \n`'
            + ''.join(map(lambda c: chr(ord('a') + (((ord(c) - ord('a')) + 13) % 26)) if c >= 'a' and c <= 'z' else c, spoiler))
            + '`\n' + isBot + 'Use http://rot13.com to decode')
        except:
            await self.bot.send_message(ctx.message.channel, isBot + 'Could not encrypt spoiler.')


def setup(bot):
    bot.add_cog(Misc(bot))
