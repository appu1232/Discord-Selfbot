import datetime
import random
import requests
import json
import discord
import git
import os
from PythonGists import PythonGists
from discord.ext import commands
from cogs.utils.checks import embed_perms, cmd_prefix_len, parse_prefix

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
            await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        else:
            await self.bot.send_message(ctx.message.channel, 'https://github.com/appu1232/Selfbot-for-Discord')
        await self.bot.delete_message(ctx.message)

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
        for server in self.bot.servers:
            channel_count += len(server.channels)
        if embed_perms(ctx.message):
            em = discord.Embed(title='Bot Stats', color=0x32441c)
            em.add_field(name=u'\U0001F553 Uptime', value=time, inline=False)
            em.add_field(name=u'\U0001F4E4 Msgs sent', value=str(self.bot.icount))
            em.add_field(name=u'\U0001F4E5 Msgs received', value=str(self.bot.message_count))
            em.add_field(name=u'\u2757 Mentions', value=str(self.bot.mention_count))
            em.add_field(name=u'\u2694 Servers', value=str(len(self.bot.servers)))
            em.add_field(name=u'\ud83d\udcd1 Channels', value=str(channel_count))
            em.add_field(name=u'\u270F Keywords logged', value=str(self.bot.keyword_log))
            g = u'\U0001F3AE Game'
            if '=' in game: g = '\ud83c\udfa5 Stream'
            em.add_field(name=g, value=game)
            mem_usage = '{:.2f} MiB'.format(__import__('psutil').Process().memory_full_info().uss / 1024 ** 2)
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
            await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        else:
            msg = '**Bot Stats:** ```Uptime: %s\nMessages Sent: %s\nMessages Received: %s\nMentions: %s\nServers: %s\nKeywords logged: %s\nGame: %s```' % (
            time, str(self.bot.icount), str(self.bot.message_count), str(self.bot.mention_count),
            str(len(self.bot.servers)), str(self.bot.keyword_log), game)
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + msg)
        await self.bot.delete_message(ctx.message)

    # Embeds the message
    @commands.command(pass_context=True)
    async def embed(self, ctx, *, msg: str = None):
        """Embed given text. Ex: Do >embed for more help

        Example: >embed title=test this | description=some words | color=3AB35E | field=name=test value=test

        You do NOT need to specify every property, only the ones you want.

        **All properties and the syntax (put your custom stuff in place of the <> stuff):
        - title=<words>
        - description=<words>
        - color=<hex_value>
        - image=<url_to_image> (must be https)
        - thumbnail=<url_to_image>
        - author=<words> **OR** author=name=<words> icon=<url_to_image>
        - footer=<words> **OR** footer=name=<words> icon=<url_to_image>
        - field=name=<words> value=<words> (you can add as many fields as you want)
        - ptext=<words>
        - timestamp (no values accepted, shows current timestamp in the embed)

        NOTE: After the command is sent, the bot will delete your message and replace it with the embed. Make sure you have it saved or else you'll have to type it all again if the embed isn't how you want it.
        PS: Hyperlink text like so: [text](https://www.whateverlink.com)
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
                        timestamp = ctx.message.timestamp
                    else:
                        if description is None and not i.strip().lower().startswith('field='):
                            description = i.strip()

                if color:
                    if color.startswith('#'):
                        color = color[1:]
                    if not color.startswith('0x'):
                        color = '0x' + color

                if ptext is title is description is image is thumbnail is color is footer is author is None and 'field=' not in msg:
                    await self.bot.delete_message(ctx.message)
                    return await self.bot.send_message(ctx.message.channel, content=None,
                                                       embed=discord.Embed(description=msg))

                if color:
                    em = discord.Embed(timestamp=timestamp, title=title, description=description, color=int(color, 16))
                else:
                    em = discord.Embed(timestamp=timestamp, title=title, description=description)
                for i in embed_values:
                    if i.strip().lower().startswith('field='):
                        field_inline = True
                        field = i.strip().split('field=')[1]
                        field_name, field_value = field.split('value=')
                        if 'inline=' in field_value:
                            field_value, field_inline = field_value.split('inline=')
                            if 'false' in field_inline.lower() or 'no' in field_inline.lower():
                                field_inline = False
                        field_name = field_name.split('name=')[1]
                        em.add_field(name=field_name.strip(), value=field_value.strip(), inline=field_inline)
                if author:
                    if 'icon=' in author:
                        text, icon = author.split('icon=')
                        if 'url=' in icon:
                            print("here")
                            em.set_author(name=text.strip()[5:], icon_url=icon.split('url=')[0].strip(), url=icon.split('url=')[1].strip())
                        else:
                            em.set_author(name=text.strip()[5:], icon_url=icon)
                    else:
                        if 'url=' in author:
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
                await self.bot.send_message(ctx.message.channel, content=ptext, embed=em)
            else:
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'No embed permissions in this channel.')
        else:
            msg = '```How to use the >embed command:\nExample: >embed title=test this | description=some words | color=3AB35E | field=name=test value=test\n\nYou do NOT need to specify every property, only the ones you want.' \
                  '\nAll properties and the syntax (put your custom stuff in place of the <> stuff):\ntitle=<words>\ndescription=<words>\ncolor=<hex_value>\nimage=<url_to_image> (must be https)\nthumbnail=<url_to_image>\nauthor=<words> **OR** author=name=<words> icon=<url_to_image>\nfooter=<words> ' \
                  '**OR** footer=name=<words> icon=<url_to_image>\nfield=name=<words> value=<words> (you can add as many fields as you want)\nptext=<words>\n\nNOTE: After the command is sent, the bot will delete your message and replace it with ' \
                  'the embed. Make sure you have it saved or else you\'ll have to type it all again if the embed isn\'t how you want it.\nPS: Hyperlink text like so: [text](https://www.whateverlink.com)\nPPS: Force a field to go to the next line with the added parameter inline=False```'
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + msg)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass

    @commands.command(pass_context=True)
    async def editembed(self, ctx, msg_id):
        """Edit an embedded message."""
        await self.bot.delete_message(ctx.message)
        async for message in self.bot.logs_from(ctx.message.channel, 100):
            if message.id == msg_id:
                msg = message
                break
        if not msg:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "That message couldn't be found.")
        else:
            try:
                fields = msg.embeds[0].pop("fields")
            except KeyError:
                fields = False
            msg.embeds[0].pop("type")
            try:
                color = msg.embeds[0].pop("color")
            except KeyError:
                color = False
            result = []
            for field in msg.embeds[0]:
                result.append("{}={}".format(field, msg.embeds[0][field]))
            if fields:
                for field in fields:
                    result.append("field=name={} value={} inline={}".format(field["name"], field["value"], field["inline"]))
            if color:
                result.append("color={}".format(hex(color)))
            if msg.content:
                result.append("ptext={}".format(msg.content))
            await self.bot.edit_message(msg, " | ".join(result))
            info_msg = await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "Embed has been turned back into its command form. Make your changes, then type `done` to finish editing.")
            confirmation_msg = await self.bot.wait_for_message(author=self.bot.user, content="done")
            await self.bot.delete_message(info_msg)
            await self.bot.delete_message(confirmation_msg)
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
            # need to get the edited message again
            async for message in self.bot.logs_from(ctx.message.channel, 100):
                if message.id == msg_id:
                    msg = message
                    break
            embed_values = msg.content.split('|')
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
            print(ptext)
            if not ptext:
                await self.bot.edit_message(msg, "ᅠ", embed=em)
            else:
                await self.bot.edit_message(msg, ptext, embed=em)

    @commands.command(pass_context=True)
    async def embedcolor(self, ctx, *, color: str = None):
        """Set color (hex) of a embeds. Ex: >embedcolor 000000"""
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
                    return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Invalid color.')
                opt['embed_color'] = color
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Successfully set color for embeds.')
            else:
                opt['embed_color'] = ""
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Set default embed color off for embed command. You will now need to specify the color parameter if you want your embed to be colored when using the embed command.')

            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    @commands.command(pass_context=True, aliases=['stream'])
    async def game(self, ctx, *, game: str = None):
        """Set game/stream. Ex: >game napping >help game for more info

        Your game/stream status will not show for yourself, only other people can see it. This is a limitation of how the client works and how the api interacts with the client.

        --Setting game--
        To set a rotating game status, do >game game1 | game2 | game3 | etc.
        It will then prompt you with an interval in seconds to wait before changing the game and after that the order in which to change (in order or random)
        Ex: >game with matches | sleeping | watching anime

        --Setting stream--
        Same as above but you also need a link to the stream. (must be a valid link to a stream or else the status will not show as streaming).
        Add the link like so: <words>=<link>
        Ex: >stream Underwatch=https://www.twitch.tv/a_seagull
        or >stream Some moba=https://www.twitch.tv/doublelift | Underwatch=https://www.twitch.tv/a_seagull"""
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
                await self.bot.send_message(ctx.message.channel,
                                            self.bot.bot_prefix + 'Input interval in seconds to wait before changing to the next {} (``n`` to cancel):'.format(
                                                status_type.lower()))

                def check(msg):
                    return msg.content.isdigit() or msg.content.lower().strip() == 'n'

                def check2(msg):
                    return msg.content == 'random' or msg.content.lower().strip() == 'r' or msg.content.lower().strip() == 'order' or msg.content.lower().strip() == 'o'

                reply = await self.bot.wait_for_message(author=ctx.message.author, check=check, timeout=60)
                if not reply:
                    return
                if reply.content.lower().strip() == 'n':
                    return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Cancelled')
                elif reply.content.strip().isdigit():
                    interval = int(reply.content.strip())
                    if interval >= 10:
                        self.bot.game_interval = interval
                        games = game.split(' | ')
                        if len(games) != 2:
                            await self.bot.send_message(ctx.message.channel,
                                                        self.bot.bot_prefix + 'Change {} in order or randomly? Input ``o`` for order or ``r`` for random:'.format(
                                                            status_type.lower()))
                            s = await self.bot.wait_for_message(author=ctx.message.author, check=check2, timeout=60)
                            if not s:
                                return
                            if s.content.strip() == 'r' or s.content.strip() == 'random':
                                await self.bot.send_message(ctx.message.channel,
                                                            self.bot.bot_prefix + '{status} set. {status} will randomly change every ``{time}`` seconds'.format(
                                                                status=status_type, time=reply.content.strip()))
                                loop_type = 'random'
                            else:
                                loop_type = 'ordered'
                        else:
                            loop_type = 'ordered'

                        if loop_type == 'ordered':
                            await self.bot.send_message(ctx.message.channel,
                                                        self.bot.bot_prefix + '{status} set. {status} will change every ``{time}`` seconds'.format(
                                                            status=status_type, time=reply.content.strip()))

                        stream = 'yes' if is_stream else 'no'
                        games = {'games': game.split(' | '), 'interval': interval, 'type': loop_type, 'stream': stream}
                        with open('settings/games.json', 'w') as g:
                            json.dump(games, g, indent=4)

                        self.bot.game = game.split(' | ')[0]

                    else:
                        return await self.bot.send_message(ctx.message.channel,
                                                           self.bot.bot_prefix + 'Cancelled. Interval is too short. Must be at least 10 seconds.')

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
                    await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Stream set as: ``Streaming %s``' % g)
                    await self.bot.change_presence(game=discord.Game(name=g, type=1, url=url))
                else:
                    await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Game set as: ``Playing %s``' % game)
                    await self.bot.change_presence(game=discord.Game(name=game))

        # Remove game status.
        else:
            self.bot.game_interval = None
            self.bot.game = None
            self.bot.is_stream = False
            await self.bot.change_presence(game=None)
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Set playing status off')
            if os.path.isfile('settings/games.json'):
                os.remove('settings/games.json')

    @commands.group(aliases=['avatars'], pass_context=True)
    async def avatar(self, ctx):
        """Rotate avatars. See wiki for more info."""

        if ctx.invoked_subcommand is None:
            with open('settings/avatars.json', 'r+') as a:
                avi_config = json.load(a)
            if avi_config['password'] == '':
                return await self.bot.send_message(ctx.message.channel,
                                                   self.bot.bot_prefix + 'Cycling avatars requires you to input your password. Your password will not be sent anywhere and no one will have access to it. '
                                                                'Enter your password with``>avatar password <password>`` Make sure you are in a private channel where no one can see!')
            if avi_config['interval'] != '0':
                self.bot.avatar = None
                self.bot.avatar_interval = None
                avi_config['interval'] = '0'
                with open('settings/avatars.json', 'w') as avi:
                    json.dump(avi_config, avi, indent=4)
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Disabled cycling of avatars.')
            else:
                if os.listdir('avatars'):
                    await self.bot.send_message(ctx.message.channel,
                                                self.bot.bot_prefix + 'Enabled cycling of avatars. Input interval in seconds to wait before changing avatars (``n`` to cancel):')

                    def check(msg):
                        return msg.content.isdigit() or msg.content.lower().strip() == 'n'

                    def check2(msg):
                        return msg.content == 'random' or msg.content.lower().strip() == 'r' or msg.content.lower().strip() == 'order' or msg.content.lower().strip() == 'o'

                    interval = await self.bot.wait_for_message(author=ctx.message.author, check=check, timeout=60)
                    if not interval:
                        return
                    if interval.content.lower().strip() == 'n':
                        return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Cancelled.')
                    elif int(interval.content) < 1800:
                        return await self.bot.send_message(ctx.message.channel,
                                                           self.bot.bot_prefix + 'Cancelled. Interval is too short. Must be at least 1800 seconds (30 minutes).')
                    else:
                        avi_config['interval'] = int(interval.content)
                    if len(os.listdir('avatars')) != 2:
                        await self.bot.send_message(ctx.message.channel,
                                                    self.bot.bot_prefix + 'Change avatars in order or randomly? Input ``o`` for order or ``r`` for random:')
                        cycle_type = await self.bot.wait_for_message(author=ctx.message.author, check=check2,
                                                                     timeout=60)
                        if not cycle_type:
                            return
                        if cycle_type.content.strip() == 'r' or cycle_type.content.strip() == 'random':
                            await self.bot.send_message(ctx.message.channel,
                                                        self.bot.bot_prefix + 'Avatar cycling enabled. Avatar will randomly change every ``%s`` seconds' % interval.content.strip())
                            loop_type = 'random'
                        else:
                            loop_type = 'ordered'
                    else:
                        loop_type = 'ordered'
                    avi_config['type'] = loop_type
                    if loop_type == 'ordered':
                        await self.bot.send_message(ctx.message.channel,
                                                    self.bot.bot_prefix + 'Avatar cycling enabled. Avatar will change every ``%s`` seconds' % interval.content.strip())
                    with open('settings/avatars.json', 'r+') as avi:
                        avi.seek(0)
                        avi.truncate()
                        json.dump(avi_config, avi, indent=4)
                    self.bot.avatar_interval = interval.content
                    self.bot.avatar = random.choice(os.listdir('avatars'))

                else:
                    await self.bot.send_message(ctx.message.channel,
                                                self.bot.bot_prefix + 'No images found under ``avatars``. Please add images (.jpg .jpeg and .png types only) to that folder and try again.')

    @avatar.command(aliases=['pass', 'pw'], pass_context=True)
    async def password(self, ctx, *, msg):
        """Set your discord acc password to rotate avatars. See wiki for more info."""
        with open('settings/avatars.json', 'r+') as a:
            avi_config = json.load(a)
            avi_config['password'] = msg.strip().strip('"').lstrip('<').rstrip('>')
            a.seek(0)
            a.truncate()
            json.dump(avi_config, a, indent=4)
        await self.bot.delete_message(ctx.message)
        return await self.bot.send_message(ctx.message.channel,
                                           self.bot.bot_prefix + 'Password set. Do ``>avatar`` to toggle cycling avatars.')

    @commands.command(pass_context=True)
    async def setavatar(self, ctx, *, msg):
        """
        Set an avatar from a URL: Usage >setavatar <url_to_image>
        Image must be a .png or a .jpg
        """
        url = msg
        response = requests.get(url, stream=True)
        name = url.split('/')[-1]
        with open(name, 'wb') as img:

            for block in response.iter_content(1024):
                if not block:
                    break

                img.write(block)

        if url:
            with open(name, 'rb') as fp:
                e = fp.read()
                with open('settings/avatars.json', 'r+') as fp:
                        opt = json.load(fp)
                        if opt['password']:
                            if opt['password'] == "":
                                await self.bot.send_message(ctx.message.channel,"You have not set your password yet in `settings/avatars.json` Please do so and try again")
                            else:
                                pw = opt['password']
                                await self.bot.edit_profile(password=pw, avatar=e)
                                await self.bot.send_message(ctx.message.channel, "Your avatar has been set to the specified image")
                        else:
                            opt['password'] = ""
                            await self.bot.send_message(ctx.message.channel,"You have not set your password yet in `settings/avatars.json` Please do so and try again")
            os.remove(name)
        elif not embed_perms(ctx.message) and url:
            await self.bot.send_message(ctx.message.channel, url)
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Could not find image.')

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Get response time."""
        msgtime = ctx.message.timestamp.now()
        await (await self.bot.ws.ping())
        now = datetime.datetime.now()
        ping = now - msgtime
        if embed_perms(ctx.message):
            pong = discord.Embed(title='Pong! Response Time:', description=str(ping.microseconds / 1000.0) + ' ms',
                                 color=0x7A0000)
            pong.set_thumbnail(url='http://odysseedupixel.fr/wp-content/gallery/pong/pong.jpg')
            await self.bot.send_message(ctx.message.channel, content=None, embed=pong)
        else:
            await self.bot.send_message(ctx.message.channel,
                                        self.bot.bot_prefix + '``Response Time: %s ms``' % str(ping.microseconds / 1000.0))

    @commands.command(pass_context=True)
    async def quotecolor(self, ctx, *, msg):
        '''Set color (hex) of a quote embed.\n`>quotecolor 000000` to set the quote color to black.\n´>quotecolor auto´ to set it to the color of the highest role the quoted person has.'''
        if msg:
            if msg == "auto":
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Successfully set color for quote embeds.')
            else:
                try:
                    msg = msg.lstrip('#')
                    int(msg, 16)
                    await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Successfully set color for quote embeds.')
                except:
                    await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Invalid color.')
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Use this command to set color to quote embeds. Usage is `>quotecolor <hex_color_value>`')
            return
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            opt['quoteembed_color'] = msg
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    @commands.command(aliases=['q'], pass_context=True)
    async def quote(self, ctx, *, msg: str = None):
        """Quote a message. >help quote for more info.
        >quote - quotes the last message sent in the channel.
        >quote <words> - tries to search for a message in the server that contains the given words and quotes it.
        >quote <message_id> - quotes the message with the given message id. Ex: >quote 302355374524644290(Enable developer mode to copy message ids).
        >quote <words> | channel=<channel_name> - quotes the message with the given words from the channel name specified in the second argument
        >quote <message_id> | channel=<channel_name> - quotes the message with the given message id in the given channel name"""
        result = channel = None
        pre = cmd_prefix_len()
        await self.bot.delete_message(ctx.message)
        if msg:
            try:
                length = len(self.bot.all_log[ctx.message.channel.id + ' ' + ctx.message.server.id])
                if length < 201:
                    size = length
                else:
                    size = 200
                for channel in ctx.message.server.channels:
                    if str(channel.type) == 'text':
                        if channel.id + ' ' + ctx.message.server.id in self.bot.all_log:
                            for i in range(length - 2, length - size, -1):
                                try:
                                    search = self.bot.all_log[channel.id + ' ' + ctx.message.server.id][i]
                                except:
                                    continue
                                if (msg.lower().strip() in search[0].content.lower() and (
                                        search[0].author != ctx.message.author or search[0].content[pre:7] != 'quote ')) or (
                                    ctx.message.content[6:].strip() == search[0].id):
                                    result = search[0]
                                    break
                            if result:
                                break
            except KeyError:
                pass

            if not result:
                if " | channel=" in msg:
                    channelList = []
                    for channels in self.bot.get_all_channels():
                        if channels.name == msg.split("| channel=")[1]:
                            channelList.append(channels)
                    msg = msg.split(" | channel=")[0]
                    for channel in channelList:
                        if str(channel.type) == 'text':
                            if channel.id + ' ' + ctx.message.server.id in self.bot.all_log:
                                for i in range(length - 2, length - size, -1):
                                    try:
                                        search = self.bot.all_log[channel.id + ' ' + ctx.message.server.id][i]
                                    except:
                                        continue
                                    if (msg.lower().strip() in search[0].content.lower() and (
                                            search[0].author != ctx.message.author or search[0].content[
                                                                                      pre:7] != 'quote ')) or (
                                        ctx.message.content[6:].strip() == search[0].id):
                                        result = search[0]
                                        break
                                if result:
                                    break
                    if not result:
                        for channel in channelList:
                            try:
                                async for sent_message in self.bot.logs_from(channel, limit=500):
                                    if (msg.lower().strip() in sent_message.content and (
                                            sent_message.author != ctx.message.author or sent_message.content[
                                                                                         pre:7] != 'quote ')) or (msg.strip() == sent_message.id):
                                        result = sent_message
                                        break
                            except:
                                pass
                            if result:
                                break
            if not result:
                for channel in ctx.message.server.channels:
                    try:
                        async for sent_message in self.bot.logs_from(channel, limit=500):
                            if (msg.lower().strip() in sent_message.content and (
                                    sent_message.author != ctx.message.author or sent_message.content[
                                                                                 pre:7] != 'quote ')) or (msg.strip() == sent_message.id):
                                result = sent_message
                                break
                    except:
                        pass
                    if result:
                        break

        else:
            channel = ctx.message.channel
            search = self.bot.all_log[ctx.message.channel.id + ' ' + ctx.message.server.id][-2]
            result = search[0]
        if result:
            sender = result.author.nick if result.author.nick else result.author.name
            if embed_perms(ctx.message) and result.content:
                em = discord.Embed(description=result.content, timestamp=result.timestamp)
                with open('settings/optional_config.json') as fp:
                    opt = json.load(fp)
                try:
                    embed_color = opt['quoteembed_color']
                    if embed_color == "auto":
                        em.color = result.author.top_role.color
                    else:
                        em.color = int('0x' + embed_color, 16)
                except:
                    em.color = 0xbc0b0b
                em.set_author(name=sender, icon_url=result.author.avatar_url)
                if channel != ctx.message.channel:
                    em.set_footer(text='#{} | {} '.format(channel.name, channel.server.name))
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                await self.bot.send_message(ctx.message.channel,
                                            '%s - %s```%s```' % (sender, result.timestamp, result.content))
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'No quote found.')

    @commands.command(pass_context=True)
    async def afk(self, ctx, txt: str = None):
        """Set your Discord status for when you aren't online. Ex: >afk idle"""
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
                    return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Invalid status. %s' % info)
            else:
                return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + info)
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)
            await self.bot.send_message(ctx.message.channel,
                                        self.bot.bot_prefix + 'Set default afk status. You will now appear as ``{}`` when not on Discord.'.format(
                                            opt['default_status']))


def setup(bot):
    bot.add_cog(Misc(bot))
