import discord
import datetime
import asyncio
import os
import prettytable
import strawpy
from appuselfbot import isBot
from discord.ext import commands
from cogs.utils.checks import *


class Misc:

    def __init__(self, bot):
        self.bot = bot

    # Links to the Selfbot project on Github
    @commands.command(pass_context=True)
    async def about(self, ctx):
        await self.bot.send_message(ctx.message.channel, 'https://github.com/appu1232/Selfbot-for-Discord')
        await self.bot.delete_message(ctx.message)

    # Bot stats, thanks IgneelDxD for the design
    @commands.command(pass_context=True)
    async def stats(self, ctx):
        uptime = (datetime.datetime.now() - self.bot.uptime)
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            time = '%s days, %s hours, %s minutes, and %s seconds' % (days, hours, minutes, seconds)
        else:
            time = '%s hours, %s minutes, and %s seconds' % (hours, minutes, seconds)
        if not ctx.message.author.game:
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

    #Embed text
    @commands.command(pass_context=True)
    async def embed(self, ctx, *, msg):
        em = discord.Embed(description=msg)
        await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        await self.bot.delete_message(ctx.message)

    # Stats about current server
    @commands.group(pass_context=True)
    async def server(self, ctx):
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
        msg = ''
        for i in ctx.message.server.emojis:
            msg += str(i)
        await self.bot.send_message(ctx.message.channel, msg)
        await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def avi(self, ctx):
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

    #
    # @server.group(pass_context=True)
    # async def role(self, ctx):
    #     pass
    #
    # @server.group(pass_context=True)
    # async def member(self, ctx):
    #     pass
    #
    # @server.group(pass_context=True)
    # async def channel(self, ctx):
    #     pass

    @server.group(pass_context=True)
    async def members(self, ctx):
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

    # Set playing status. Note: this won't be visible to you but everyone else can see it.
    @commands.command(pass_context=True)
    async def game(self, ctx):
        if ctx.message.content[6:]:
            await self.bot.change_presence(game=discord.Game(name=ctx.message.content[6:].strip()))
            self.bot.game = ctx.message.content[6:].strip()
            await self.bot.send_message(ctx.message.channel, isBot + 'Game set as: ``Playing %s``' % ctx.message.content[6:])
            with open('game.txt', 'w') as g:
                g.write(ctx.message.content[6:])
        else:
            await self.bot.change_presence(game=None)
            self.bot.game = None
            await self.bot.send_message(ctx.message.channel, isBot + 'Set playing status off')
            if os.path.isfile('game.txt'):
                os.remove('game.txt')
        await self.bot.delete_message(ctx.message)

    # Get url of emoji
    @commands.command(pass_context=True)
    async def emoji(self, ctx):
        if ctx.message.content[6:]:
            emoji = ctx.message.content[6:].split(':')
            success = False
            emoji_url = None
            for i in self.bot.servers:
                try:
                    emoji_url = discord.Emoji(id=emoji[2][:-1], server=i).url
                except:
                    pass
            if emoji_url:
                await self.bot.send_message(ctx.message.channel, emoji_url)
            else:
                await self.bot.send_message(ctx.message.channel, isBot + 'Could not find emoji.')
        else:
            await self.bot.send_message(ctx.message.channel, isBot + 'Specify an emoji.')
        await self.bot.delete_message(ctx.message)

    # Get response time
    @commands.command(pass_context=True)
    async def ping(self, ctx):
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

    # Quote someone in said channel
    @commands.command(pass_context=True)
    async def quote(self, ctx):
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

    # Creates a strawpoll with the given options
    @commands.command(pass_context=True)
    async def poll(self, ctx, *, msg):
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

    # Simple calculator
    @commands.command(pass_context=True)
    async def calc(self, ctx, *, msg):
        equation = msg.strip()
        if '=' in equation:
            left = eval(equation.split('=')[0])
            right = eval(equation.split('=')[1])
            await self.bot.send_message(ctx.message.channel, isBot + str(left == right))
        else:
            await self.bot.send_message(ctx.message.channel, isBot + str(eval(equation)))

    # Sends a googleitfor.me link with the specified tags
    @commands.command(pass_context=True)
    async def l2g(self, ctx, *, msg: str):
        lmgtfy = 'http://googleitfor.me/?q='
        words = msg.lower().strip().split(' ')
        for word in words:
            lmgtfy += word + '+'
        await self.bot.send_message(ctx.message.channel, isBot + lmgtfy[:-1])
        await self.bot.delete_message(ctx.message)

    # Deletes previous message immediately or after specified number of seconds (because why not)
    @commands.command(pass_context=True)
    async def d(self, ctx):

        # If number of seconds/messages are specified
        if len(ctx.message.content.lower().strip()) > 2:
            if ctx.message.content[3] == '!':
                killmsg = self.bot.self_log[len(self.bot.self_log) - 2]
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
                await self.bot.delete_message(self.bot.self_log.pop())
                for i in range(0, int(ctx.message.content[3:])):
                    try:
                        await self.bot.delete_message(self.bot.self_log.pop())
                    except:
                        pass

        # If no number specified, delete message immediately
        else:
            await self.bot.delete_message(self.bot.self_log.pop())
            await self.bot.delete_message(self.bot.self_log.pop())



def setup(bot):
    bot.add_cog(Misc(bot))
