import datetime
import time
import random
import requests
import json
import discord
import git
import os
import io
from PythonGists import PythonGists
from discord.ext import commands
from cogs.utils.config import get_config_value
from cogs.utils.dataIO import dataIO
from cogs.utils.checks import embed_perms, cmd_prefix_len, parse_prefix, get_user

'''Module for miscellaneous commands'''


class Misc:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def about(self, ctx, txt: str = None):
        """Links to the bot's github page."""
        if embed_perms(ctx.message) and txt != 'short':
            em = discord.Embed(color=0xad2929, title='\ud83e\udd16 Appu\'s Discord Selfbot',
                               description='**Features:**\n- Custom commands/reactions\n- Save last x images in a channel to your computer\n- Keyword notifier\n'
                                           '- Set/cycle your game status and your avatar\n- Google web and image search\n- MyAnimeList search\n- Spoiler tagging\n'
                                           '- Server info commands\n- Quoting, calculator, creating polls, and much more')
            em.add_field(name='\ud83d\udd17 Link to download',
                         value='[Github link](https://github.com/appu1232/Discord-Selfbot/tree/master)')
            em.add_field(name='\ud83c\udfa5Quick examples:', value='[Simple commands](http://i.imgur.com/3H9zpop.gif)')
            if txt == 'link': em.add_field(name='👋 Discord Server', value='Join the official Discord server [here](https://discord.gg/FGnM5DM)!')
            em.set_footer(text='Made by appu1232#2569', icon_url='https://i.imgur.com/RHagTDg.png')
            await ctx.send(content=None, embed=em)
        else:
            await ctx.send('https://github.com/appu1232/Selfbot-for-Discord')
        await ctx.message.delete()

    @commands.group(aliases=['status'], pass_context=True)
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
        game = self.bot.game
        if not game:
            game = 'None'
        channel_count = 0
        for guild in self.bot.guilds:
            channel_count += len(guild.channels)
        if not self.bot.command_count:
            most_used_cmd = 'Not enough info'
        else:
            cmd_name = max(self.bot.command_count, key=self.bot.command_count.get)
            total_usage = self.bot.command_count[str(cmd_name)]
            plural = '' if total_usage == 1 else 's'
            most_used_cmd = '{} - {} use{}'.format(cmd_name, total_usage, plural)
        if embed_perms(ctx.message):
            em = discord.Embed(title='Bot Stats', color=0x32441c)
            em.add_field(name=u'\U0001F553 Uptime', value=time, inline=False)
            em.add_field(name=u'\u2328 Most Used Cmd', value=most_used_cmd, inline=False)
            em.add_field(name=u'\U0001F4E4 Msgs sent', value=str(self.bot.icount))
            em.add_field(name=u'\U0001F4E5 Msgs received', value=str(self.bot.message_count))
            em.add_field(name=u'\u2757 Mentions', value=str(self.bot.mention_count))
            em.add_field(name=u'\u2694 Servers', value=str(len(self.bot.guilds)))
            em.add_field(name=u'\ud83d\udcd1 Channels', value=str(channel_count))
            em.add_field(name=u'\u270F Keywords logged', value=str(self.bot.keyword_log))
            g = u'\U0001F3AE Game'
            if '=' in game: g = '\ud83c\udfa5 Stream'
            em.add_field(name=g, value=game)
            try:
                mem_usage = '{:.2f} MiB'.format(__import__('psutil').Process().memory_full_info().uss / 1024 ** 2)
            except AttributeError:
                # OS doesn't support retrieval of USS (probably BSD or Solaris)
                mem_usage = '{:.2f} MiB'.format(__import__('psutil').Process().memory_full_info().rss / 1024 ** 2)
            em.add_field(name=u'\U0001F4BE Memory usage:', value=mem_usage)
            try:
                g = git.cmd.Git(working_dir=os.getcwd())
                branch = g.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
                g.execute(["git", "fetch", "origin", branch])
                version = g.execute(["git", "rev-list", "--right-only", "--count", "{}...origin/{}".format(branch, branch)])
                if branch == "master":
                    branch_note = "."
                else:
                    branch_note = " (`" + branch + "` branch)."
                if version == '0':
                    status = 'Up to date%s' % branch_note
                else:
                    latest = g.execute(
                        ["git", "log", "--pretty=oneline", "--abbrev-commit", "--stat", "--pretty", "-%s" % version,
                         "origin/%s" % branch])
                    gist_latest = PythonGists.Gist(description='Latest changes for the selfbot.', content=latest,
                                                   name='latest.txt')
                    if version == '1':
                        status = 'Behind by 1 release%s [Latest update.](%s)' % (branch_note, gist_latest)
                    else:
                        status = '%s releases behind%s [Latest updates.](%s)' % (version, branch_note, gist_latest)
                em.add_field(name=u'\U0001f4bb Update status:', value=status)
            except:
                pass
            await ctx.send(content=None, embed=em)
        else:
            msg = '**Bot Stats:** ```Uptime: %s\nMessages Sent: %s\nMessages Received: %s\nMentions: %s\nguilds: %s\nKeywords logged: %s\nGame: %s```' % (
            time, str(self.bot.icount), str(self.bot.message_count), str(self.bot.mention_count),
            str(len(self.bot.guilds)), str(self.bot.keyword_log), game)
            await ctx.send(self.bot.bot_prefix + msg)
        await ctx.message.delete()

    # Embeds the message
    @commands.command(pass_context=True)
    async def embed(self, ctx, *, msg: str = None):
        """Embed given text. Ex: Do [p]embed for more help

        Example: [p]embed title=test this | description=some words | color=3AB35E | field=name=test value=test

        You do NOT need to specify every property, only the ones you want.

        **All properties and the syntax:**
        - title=<words>
        - description=<words>
        - color=<hex_value>
        - image=<url_to_image> (must be https)
        - thumbnail=<url_to_image>
        - author=<words> **OR** author=name=<words> icon=<url_to_image>
        - footer=<words> **OR** footer=name=<words> icon=<url_to_image>
        - field=name=<words> value=<words> (you can add as many fields as you want)
        - ptext=<words>

        NOTE: After the command is sent, the bot will delete your message and replace it with the embed. Make sure you have it saved or else you'll have to type it all again if the embed isn't how you want it.
        
        PS: Hyperlink text like so:
        \[text](https://www.whateverlink.com)

        PPS: Force a field to go to the next line with the added parameter inline=False"""
        if msg:
            if embed_perms(ctx.message):
                ptext = title = description = image = thumbnail = color = footer = author = None
                timestamp = discord.Embed.Empty
                embed_values = msg.split('|')
                for i in embed_values:
                    with open('settings/optional_config.json', 'r+') as fp:
                        opt = json.load(fp)
                        if opt['embed_color'] != "":
                            color = opt['embed_color']
                    if i.strip().lower().startswith('ptext='):
                        ptext = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('title='):
                        title = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('description='):
                        description = i.strip()[12:].strip()
                    elif i.strip().lower().startswith('desc='):
                        description = i.strip()[5:].strip()
                    elif i.strip().lower().startswith('image='):
                        image = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('thumbnail='):
                        thumbnail = i.strip()[10:].strip()
                    elif i.strip().lower().startswith('colour='):
                        color = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('color='):
                        color = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('footer='):
                        footer = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('author='):
                        author = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('timestamp'):
                        timestamp = ctx.message.created_at
                    else:
                        if description is None and not i.strip().lower().startswith('field='):
                            description = i.strip()

                if color:
                    if color.startswith('#'):
                        color = color[1:]
                    if not color.startswith('0x'):
                        color = '0x' + color

                if ptext is title is description is image is thumbnail is color is footer is author is None and 'field=' not in msg:
                    await ctx.message.delete()
                    return await ctx.send(content=None,
                                                       embed=discord.Embed(description=msg))

                if color:
                    em = discord.Embed(timestamp=timestamp, title=title, description=description, color=int(color, 16))
                else:
                    em = discord.Embed(timestamp=timestamp, title=title, description=description)
                for i in embed_values:
                    if i.strip().lower().startswith('field='):
                        field_inline = True
                        field = i.strip().lstrip('field=')
                        field_name, field_value = field.split('value=')
                        if 'inline=' in field_value:
                            field_value, field_inline = field_value.split('inline=')
                            if 'false' in field_inline.lower() or 'no' in field_inline.lower():
                                field_inline = False
                        field_name = field_name.strip().lstrip('name=')
                        em.add_field(name=field_name, value=field_value.strip(), inline=field_inline)
                if author:
                    if 'icon=' in author:
                        text, icon = author.split('icon=')
                        if 'url=' in icon:
                            em.set_author(name=text.strip()[5:], icon_url=icon.split('url=')[0].strip(), url=icon.split('url=')[1].strip())
                        else:
                            em.set_author(name=text.strip()[5:], icon_url=icon)
                    else:
                        if 'url=' in author:
                            em.set_author(name=author.split('url=')[0].strip()[5:], url=author.split('url=')[1].strip())
                        else:
                            em.set_author(name=author)

                if image:
                    em.set_image(url=image)
                if thumbnail:
                    em.set_thumbnail(url=thumbnail)
                if footer:
                    if 'icon=' in footer:
                        text, icon = footer.split('icon=')
                        em.set_footer(text=text.strip()[5:], icon_url=icon)
                    else:
                        em.set_footer(text=footer)
                await ctx.send(content=ptext, embed=em)
            else:
                await ctx.send(self.bot.bot_prefix + 'No embed permissions in this channel.')
        else:
            msg = '```How to use the >embed command:\nExample: >embed title=test this | description=some words | color=3AB35E | field=name=test value=test\n\nYou do NOT need to specify every property, only the ones you want.' \
                  '\nAll properties and the syntax (put your custom stuff in place of the <> stuff):\ntitle=<words>\ndescription=<words>\ncolor=<hex_value>\nimage=<url_to_image> (must be https)\nthumbnail=<url_to_image>\nauthor=<words> **OR** author=name=<words> icon=<url_to_image>\nfooter=<words> ' \
                  '**OR** footer=name=<words> icon=<url_to_image>\nfield=name=<words> value=<words> (you can add as many fields as you want)\nptext=<words>\n\nNOTE: After the command is sent, the bot will delete your message and replace it with ' \
                  'the embed. Make sure you have it saved or else you\'ll have to type it all again if the embed isn\'t how you want it.\nPS: Hyperlink text like so: [text](https://www.whateverlink.com)\nPPS: Force a field to go to the next line with the added parameter inline=False```'
            await ctx.send(self.bot.bot_prefix + msg)
        try:
            await ctx.message.delete()
        except:
            pass

    @commands.command(pass_context=True)
    async def editembed(self, ctx, msg_id : int):
        """Edit an embedded message."""
        msg = await ctx.history(limit=100).get(id=msg_id)
        if not msg:
            await ctx.send(self.bot.bot_prefix + "That message couldn't be found.")
        else:
            try:
                old_embed = msg.embeds[0]
            except IndexError:
                return await ctx.send("The message does not contain an embed.")
            fields = old_embed.fields
            result = []
            if old_embed.title:
                result.append("title={}".format(old_embed.title))
            if old_embed.description:
                result.append("description={}".format(old_embed.description))
            if old_embed.color:
                result.append("color={}".format(str(old_embed.color)[1:]))
            if old_embed.url:
                result.append("url={}".format(old_embed.url))
            if fields:
                for field in fields:
                    result.append("field=name={} value={} inline={}".format(field.name, field.value, field.inline))
            if msg.content:
                result.append("ptext={}".format(msg.content))
            await ctx.message.edit(content=" | ".join(result))
            info_msg = await ctx.send(self.bot.bot_prefix + "Embed has been turned back into its command form. Make your changes, then type `done` to finish editing.")
            def check(event_msg):
                return event_msg.content == "done" and event_msg.author == self.bot.user

            confirmation_msg = await self.bot.wait_for("message", check=check)
            await info_msg.delete()
            await confirmation_msg.delete()
            # not proud of this code
            ptext = ""
            title = ""
            description = ""
            image = ""
            thumbnail = ""
            color = ""
            footer = ""
            author = ""
            timestamp = discord.Embed().Empty

            embed_values = ctx.message.content.split('|')
            for i in embed_values:
                with open('settings/optional_config.json', 'r+') as fp:
                    opt = json.load(fp)
                    if opt['embed_color'] != "":
                        color = opt['embed_color']
                if i.strip().lower().startswith('ptext='):
                    ptext = i.strip()[6:].strip()
                elif i.strip().lower().startswith('title='):
                    title = i.strip()[6:].strip()
                elif i.strip().lower().startswith('description='):
                    description = i.strip()[12:].strip()
                elif i.strip().lower().startswith('desc='):
                    description = i.strip()[5:].strip()
                elif i.strip().lower().startswith('image='):
                    image = i.strip()[6:].strip()
                elif i.strip().lower().startswith('thumbnail='):
                    thumbnail = i.strip()[10:].strip()
                elif i.strip().lower().startswith('colour='):
                    color = i.strip()[7:].strip()
                elif i.strip().lower().startswith('color='):
                    color = i.strip()[6:].strip()
                elif i.strip().lower().startswith('footer='):
                    footer = i.strip()[7:].strip()
                elif i.strip().lower().startswith('author='):
                    author = i.strip()[7:].strip()
                elif i.strip().lower().startswith('timestamp'):
                    timestamp = ctx.message.timestamp
                else:
                    if description is None and not i.strip().lower().startswith('field='):
                        description = i.strip()

            if color:
                if color.startswith('#'):
                    color = color[1:]
                if not color.startswith('0x'):
                    color = '0x' + color

            if color:
                em = discord.Embed(timestamp=timestamp, title=title, description=description, color=int(color, 16))
            else:
                em = discord.Embed(timestamp=timestamp, title=title, description=description)
            for i in embed_values:
                if i.strip().lower().startswith('field='):
                    field_inline = True
                    field = i.strip().lstrip('field=')
                    field_name, field_value = field.split('value=')
                    if 'inline=' in field_value:
                        field_value, field_inline = field_value.split('inline=')
                        if 'false' in field_inline.lower() or 'no' in field_inline.lower():
                            field_inline = False
                    field_name = field_name.strip().lstrip('name=')
                    em.add_field(name=field_name, value=field_value.strip(), inline=field_inline)
            if author:
                if 'icon=' in author:
                    text, icon = author.split('icon=')
                    if 'url=' in icon:
                        print("here")
                        em.set_author(name=author.split('url=')[0].strip()[5:], url=author.split('url=')[1].strip())
                    else:
                        em.set_author(name=author)

            if image:
                em.set_image(url=image)
            if thumbnail:
                em.set_thumbnail(url=thumbnail)
            if footer:
                if 'icon=' in footer:
                    text, icon = footer.split('icon=')
                    em.set_footer(text=text.strip()[5:], icon_url=icon)
                else:
                    em.set_footer(text=footer)
            await ctx.message.delete()
            if not ptext:
                await msg.edit(content=None, embed=em)
            else:
                await msg.edit(content=ptext, embed=em)

    @commands.command(pass_context=True)
    async def embedcolor(self, ctx, *, color: str = None):
        """Set color (hex) of a embeds. Ex: [p]embedcolor 000000"""
        if color == 'auto':
            color = str(ctx.message.author.top_role.color)[1:]

        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            if color:
                try:
                    color = color.lstrip('#')
                    if color.startswith('0x'):
                        color = color[2:]
                    int(color, 16)
                except ValueError:
                    return await ctx.send(self.bot.bot_prefix + 'Invalid color.')
                opt['embed_color'] = color
                await ctx.send(self.bot.bot_prefix + 'Successfully set color for embeds.')
            else:
                opt['embed_color'] = ""
                await ctx.send(self.bot.bot_prefix + 'Set default embed color off for embed command. You will now need to specify the color parameter if you want your embed to be colored when using the embed command.')

            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    @commands.command(pass_context=True, aliases=['stream'])
    async def game(self, ctx, *, game: str = None):
        """Set game/stream. Ex: [p]game napping [p]help game for more info

        Your game/stream status will not show for yourself, only other people can see it. This is a limitation of how the client works and how the api interacts with the client.

        --Setting game--
        To set a rotating game status, do [p]game game1 | game2 | game3 | etc.
        It will then prompt you with an interval in seconds to wait before changing the game and after that the order in which to change (in order or random)
        Ex: [p]game with matches | sleeping | watching anime

        --Setting stream--
        Same as above but you also need a link to the stream. (must be a valid link to a stream or else the status will not show as streaming).
        Add the link like so: <words>=<link>
        Ex: [p]stream Underwatch=https://www.twitch.tv/a_seagull
        or [p]stream Some moba=https://www.twitch.tv/doublelift | Underwatch=https://www.twitch.tv/a_seagull"""
        pre = cmd_prefix_len()
        if ctx.message.content[pre:].startswith('game'):
            is_stream = False
            status_type = 'Game'
        else:
            is_stream = True
            status_type = 'Stream'
            self.bot.is_stream = True
        if game:

            # Cycle games if more than one game is given.
            if ' | ' in game:
                await ctx.send(self.bot.bot_prefix + 'Input interval in seconds to wait before changing to the next {} (``n`` to cancel):'.format(
                                                status_type.lower()))

                def check(msg):
                    return (msg.content.isdigit() or msg.content.lower().strip() == 'n') and msg.author == self.bot.user

                def check2(msg):
                    return (msg.content == 'random' or msg.content.lower().strip() == 'r' or msg.content.lower().strip() == 'order' or msg.content.lower().strip() == 'o') and msg.author == self.bot.user

                reply = await self.bot.wait_for("message", check=check)
                if not reply:
                    return
                if reply.content.lower().strip() == 'n':
                    return await ctx.send(self.bot.bot_prefix + 'Cancelled')
                elif reply.content.strip().isdigit():
                    interval = int(reply.content.strip())
                    if interval >= 10:
                        self.bot.game_interval = interval
                        games = game.split(' | ')
                        if len(games) != 2:
                            await ctx.send(self.bot.bot_prefix + 'Change {} in order or randomly? Input ``o`` for order or ``r`` for random:'.format(
                                                            status_type.lower()))
                            s = await self.bot.wait_for("message", check=check2)
                            if not s:
                                return
                            if s.content.strip() == 'r' or s.content.strip() == 'random':
                                await ctx.send(self.bot.bot_prefix + '{status} set. {status} will randomly change every ``{time}`` seconds'.format(
                                                                status=status_type, time=reply.content.strip()))
                                loop_type = 'random'
                            else:
                                loop_type = 'ordered'
                        else:
                            loop_type = 'ordered'

                        if loop_type == 'ordered':
                            await ctx.send(self.bot.bot_prefix + '{status} set. {status} will change every ``{time}`` seconds'.format(
                                                            status=status_type, time=reply.content.strip()))

                        stream = 'yes' if is_stream else 'no'
                        games = {'games': game.split(' | '), 'interval': interval, 'type': loop_type, 'stream': stream}
                        with open('settings/games.json', 'w') as g:
                            json.dump(games, g, indent=4)

                        self.bot.game = game.split(' | ')[0]

                    else:
                        return await ctx.send(self.bot.bot_prefix + 'Cancelled. Interval is too short. Must be at least 10 seconds.')

            # Set game if only one game is given.
            else:
                self.bot.game_interval = None
                self.bot.game = game
                stream = 'yes' if is_stream else 'no'
                games = {'games': str(self.bot.game), 'interval': '0', 'type': 'none', 'stream': stream}
                with open('settings/games.json', 'w') as g:
                    json.dump(games, g, indent=4)
                if is_stream and '=' in game:
                    g, url = game.split('=')
                    await ctx.send(self.bot.bot_prefix + 'Stream set as: ``Streaming %s``' % g)
                    await self.bot.change_presence(game=discord.Game(name=g, type=1, url=url))
                else:
                    await ctx.send(self.bot.bot_prefix + 'Game set as: ``Playing %s``' % game)
                    await self.bot.change_presence(game=discord.Game(name=game, type=0))

        # Remove game status.
        else:
            self.bot.game_interval = None
            self.bot.game = None
            self.bot.is_stream = False
            await self.bot.change_presence(game=None)
            await ctx.send(self.bot.bot_prefix + 'Set playing status off')
            if os.path.isfile('settings/games.json'):
                os.remove('settings/games.json')

    @commands.group(aliases=['avatars'], pass_context=True)
    async def avatar(self, ctx):
        """Rotate avatars. See wiki for more info."""

        if ctx.invoked_subcommand is None:
            with open('settings/avatars.json', 'r+') as a:
                avi_config = json.load(a)
            if avi_config['password'] == '':
                return await ctx.send(self.bot.bot_prefix + 'Cycling avatars requires you to input your password. Your password will not be sent anywhere and no one will have access to it. '
                                                                'Enter your password with``>avatar password <password>`` Make sure you are in a private channel where no one can see!')
            if avi_config['interval'] != '0':
                self.bot.avatar = None
                self.bot.avatar_interval = None
                avi_config['interval'] = '0'
                with open('settings/avatars.json', 'w') as avi:
                    json.dump(avi_config, avi, indent=4)
                await ctx.send(self.bot.bot_prefix + 'Disabled cycling of avatars.')
            else:
                if os.listdir('avatars'):
                    await ctx.send(self.bot.bot_prefix + 'Enabled cycling of avatars. Input interval in seconds to wait before changing avatars (``n`` to cancel):')

                    def check(msg):
                        return (msg.content.isdigit() or msg.content.lower().strip() == 'n') and msg.author == self.bot.user

                    def check2(msg):
                        return (msg.content == 'random' or msg.content.lower().strip() == 'r' or msg.content.lower().strip() == 'order' or msg.content.lower().strip() == 'o') and msg.author == self.bot.user

                    interval = await self.bot.wait_for("message", check=check)
                    if not interval:
                        return
                    if interval.content.lower().strip() == 'n':
                        return await ctx.send(self.bot.bot_prefix + 'Cancelled.')
                    elif int(interval.content) < 1800:
                        return await ctx.send(self.bot.bot_prefix + 'Cancelled. Interval is too short. Must be at least 1800 seconds (30 minutes).')
                    else:
                        avi_config['interval'] = int(interval.content)
                    if len(os.listdir('avatars')) != 2:
                        await ctx.send(self.bot.bot_prefix + 'Change avatars in order or randomly? Input ``o`` for order or ``r`` for random:')
                        cycle_type = await self.bot.wait_for("message", check=check2)
                        if not cycle_type:
                            return
                        if cycle_type.content.strip() == 'r' or cycle_type.content.strip() == 'random':
                            await ctx.send(self.bot.bot_prefix + 'Avatar cycling enabled. Avatar will randomly change every ``%s`` seconds' % interval.content.strip())
                            loop_type = 'random'
                        else:
                            loop_type = 'ordered'
                    else:
                        loop_type = 'ordered'
                    avi_config['type'] = loop_type
                    if loop_type == 'ordered':
                        await ctx.send(self.bot.bot_prefix + 'Avatar cycling enabled. Avatar will change every ``%s`` seconds' % interval.content.strip())
                    with open('settings/avatars.json', 'r+') as avi:
                        avi.seek(0)
                        avi.truncate()
                        json.dump(avi_config, avi, indent=4)
                    self.bot.avatar_interval = interval.content
                    self.bot.avatar_time = time.time()
                    self.bot.avatar = random.choice(os.listdir('avatars')) if loop_type == "random" else sorted(os.listdir('avatars'))[0]
                    with open('avatars/%s' % self.bot.avatar, 'rb') as fp:
                        await self.bot.user.edit(password=avi_config['password'], avatar=fp.read())

                else:
                    await ctx.send(self.bot.bot_prefix + 'No images found under ``avatars``. Please add images (.jpg .jpeg and .png types only) to that folder and try again.')

    @avatar.command(aliases=['pass', 'pw'], pass_context=True)
    async def password(self, ctx, *, msg):
        """Set your discord acc password to rotate avatars. See wiki for more info."""
        avi_config = dataIO.load_json('settings/avatars.json')
        avi_config['password'] = msg.strip().strip('"').lstrip('<').rstrip('>')
        dataIO.save_json('settings/avatars.json', avi_config)
        opt = dataIO.load_json('settings/optional_config.json')
        opt['password'] = avi_config['password']
        dataIO.save_json('settings/optional_config.json', opt)
        await ctx.message.delete()
        return await ctx.send(self.bot.bot_prefix + 'Password set. Do ``>avatar`` to toggle cycling avatars.')

    @commands.command(pass_context=True)
    async def setavatar(self, ctx, *, msg):
        """
        Set an avatar from a URL or user.
        Usage: [p]setavatar <url_to_image> or [p]seravatar <user> to copy that user's avi
        Image URL must be a .png, a .jpg, or a .gif (nitro only)
        """
        user = get_user(ctx.message, msg)
        if user:
            url = user.avatar_url_as(static_format='png')
        else:
            url = msg
        if ".gif" in url and not self.bot.user.premium:
            await ctx.send(self.bot.bot_prefix + "Warning: attempting to copy an animated avatar without Nitro. Only the first frame will be set.")
        response = requests.get(url, stream=True)
        img = io.BytesIO()
        for block in response.iter_content(1024):
            if not block:
                break

            img.write(block)

        if url:
            img.seek(0)
            imgbytes = img.read()
            img.close()
            with open('settings/avatars.json', 'r+') as fp:
                opt = json.load(fp)
                if opt['password']:
                    if opt['password'] == "":
                        await ctx.send(self.bot.bot_prefix + "You have not set your password yet in `settings/avatars.json` Please do so and try again")
                    else:
                        pw = opt['password']
                        try:
                            await self.bot.user.edit(password=pw, avatar=imgbytes)
                            await ctx.send(self.bot.bot_prefix + "Your avatar has been set to the specified image.")
                        except discord.errors.HTTPException:
                            await ctx.send(self.bot.bot_prefix + "You are being rate limited!")
                else:
                    await ctx.send("You have not set your password yet in `settings/avatars.json` Please do so and try again")
        else:
            await ctx.send(self.bot.bot_prefix + 'Could not find image.')


    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Get response time."""
        msgtime = ctx.message.created_at.now()
        await (await self.bot.ws.ping())
        now = datetime.datetime.now()
        ping = now - msgtime
        if embed_perms(ctx.message):
            pong = discord.Embed(title='Pong! Response Time:', description=str(ping.microseconds / 1000.0) + ' ms',
                                 color=0x7A0000)
            pong.set_thumbnail(url='http://odysseedupixel.fr/wp-content/gallery/pong/pong.jpg')
            await ctx.send(content=None, embed=pong)
        else:
            await ctx.send(self.bot.bot_prefix + '``Response Time: %s ms``' % str(ping.microseconds / 1000.0))

    @commands.command(pass_context=True)
    async def quotecolor(self, ctx, *, msg):
        '''Set color (hex) of a quote embed.\n`[p]quotecolor 000000` to set the quote color to black.\n`[p]quotecolor auto` to set it to the color of the highest role the quoted person has.'''
        if msg:
            if msg == "auto":
                await ctx.send(self.bot.bot_prefix + 'Successfully set color for quote embeds.')
            else:
                try:
                    msg = msg.lstrip('#')
                    int(msg, 16)
                    await ctx.send(self.bot.bot_prefix + 'Successfully set color for quote embeds.')
                except:
                    await ctx.send(self.bot.bot_prefix + 'Invalid color.')
        else:
            await ctx.send(self.bot.bot_prefix + 'Use this command to set color to quote embeds. Usage is `>quotecolor <hex_color_value>`')
            return
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            opt['quoteembed_color'] = msg
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    @commands.command(aliases=['q'], pass_context=True)
    async def quote(self, ctx, *, msg: str = ""):
        """Quote a message. [p]help quote for more info.
        [p]quote - quotes the last message sent in the channel.
        [p]quote <words> - tries to search for a message in the server that contains the given words and quotes it.
        [p]quote <message_id> - quotes the message with the given message ID. Ex: [p]quote 302355374524644290 (enable developer mode to copy message IDs)
        [p]quote <user_mention_name_or_id> - quotes the last message sent by a specific user
        [p]quote <words> | channel=<channel_name> - quotes the message with the given words in a specified channel
        [p]quote <message_id> | channel=<channel_name> - quotes the message with the given message ID in a specified channel
        [p]quote <user_mention_name_or_id> | channel=<channel_name> - quotes the last message sent by a specific user in a specified channel
        """
        
        await ctx.message.delete()
        result = None
        channels = [ctx.channel] + [x for x in ctx.guild.channels if x != ctx.channel and type(x) == discord.channel.TextChannel]
        
        args = msg.split(" | ")
        msg = args[0]
        if len(args) > 1:
            channel = args[1].split("channel=")[1]
            channels = []
            for chan in ctx.guild.channels:
                if chan.name == channel or str(chan.id) == channel:
                    channels.append(chan)
                    break
            else:
                for guild in self.bot.guilds:
                    for chan in guild.channels:
                        if chan.name == channel or str(chan.id) == channel and type(chan) == discord.channel.TextChannel:
                            channels.append(chan)
                            break
            if not channels:
                return await ctx.send(self.bot.bot_prefix + "The specified channel could not be found.")
            
        user = get_user(ctx.message, msg)

        async def get_quote(msg, channels, user):
            for channel in channels:
                try:
                    if user:
                        async for message in channel.history(limit=500):
                            if message.author == user:
                                return message
                    if len(msg) > 15 and msg.isdigit():
                        async for message in channel.history(limit=500):
                            if str(message.id) == msg:
                                return message
                    else:
                        async for message in channel.history(limit=500):
                            if msg in message.content:
                                return message
                except discord.Forbidden:
                    continue
            return None
            
        if msg:
            result = await get_quote(msg, channels, user)
        else:
            async for message in ctx.channel.history(limit=1):
                result = message
        
        if result:
            if type(result.author) == discord.User:
                sender = result.author.name
            else:
                sender = result.author.nick if result.author.nick else result.author.name
            if embed_perms(ctx.message) and result.content:
                color = get_config_value("optional_config", "quoteembed_color")
                if color == "auto":
                    color = result.author.top_role.color
                elif color == "":
                    color = 0xbc0b0b
                else:
                    color = int('0x' + color, 16)
                em = discord.Embed(color=color, description=result.content, timestamp=result.created_at)
                em.set_author(name=sender, icon_url=result.author.avatar_url)
                footer = ""
                if result.channel != ctx.channel:
                    footer += "#" + result.channel.name
                    
                if result.guild != ctx.guild:
                    footer += " | " + result.guild.name
                    
                if footer:
                    em.set_footer(text=footer)
                await ctx.send(embed=em)
            elif result.content:
                await ctx.send('%s - %s```%s```' % (sender, result.created_at, result.content))
            else:
                await ctx.send(self.bot.bot_prefix + "Embeds cannot be quoted.")
        else:
            await ctx.send(self.bot.bot_prefix + 'No quote found.')

    @commands.command(pass_context=True)
    async def afk(self, ctx, txt: str = None):
        """Set your Discord status for when you aren't online. Ex: [p]afk idle"""
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            info = parse_prefix(self.bot, 'Current status returned by Discord: `{}` | Current Default status: `{}`\n'.format(str(ctx.message.author.status).title(), opt['default_status'].title())+\
            'Options: ``idle``, ``dnd``, ``offline``. When the status is set, the bot will set you to this by default when you are not on Discord. Ex: [c]afk idle')
            info = parse_prefix(self.bot, info)
            if txt:
                if txt.strip() == 'idle':
                    opt['default_status'] = 'idle'
                    self.bot.default_status = 'idle'
                elif txt.strip() == 'dnd' or txt.strip() == 'do not disturb':
                    opt['default_status'] = 'dnd'
                    self.bot.default_status = 'dnd'
                elif txt.strip() == 'offline' or 'invis' in txt.strip() or txt.strip() == 'incognito':
                    opt['default_status'] = 'invisible'
                    self.bot.default_status = 'invisible'
                else:
                    return await ctx.send(self.bot.bot_prefix + 'Invalid status. %s' % info)
            else:
                return await ctx.send(self.bot.bot_prefix + info)
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)
            await ctx.send(self.bot.bot_prefix + 'Set default afk status. You will now appear as ``{}`` when not on Discord.'.format(
                                            opt['default_status']))


def setup(bot):
    bot.add_cog(Misc(bot))
