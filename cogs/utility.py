import datetime
import asyncio
import strawpy
import pytz
import re
import requests
import aiohttp
import json
import discord
import os
import glob
import git
import io
from PIL import Image
from PythonGists import PythonGists
from discord.ext import commands
from cogs.utils.checks import *
from bs4 import BeautifulSoup
from urllib import parse
from urllib.request import Request, urlopen
import math
from math import sqrt
from cogs.utils.dataIO import dataIO
from cogs.utils.config import write_config_value

'''Module for fun/meme commands commands'''


class Utility:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop, headers={"User-Agent": "AppuSelfBot"})

    @staticmethod
    def get_datetime():
        a = None
        tzerror = False
        opt = dataIO.load_json('settings/optional_config.json')
        try:
            if opt['timezone']:
                tz = opt['timezone']
                a = pytz.timezone(tz)
        except IndexError:
            # Timezone entry missing in configuration file
            pass
        except pytz.exceptions.UnknownTimeZoneError:
            tzerror = True
        return datetime.datetime.now(a), tzerror

    @commands.command(pass_context=True)
    async def now(self, ctx):
        """Date time module."""
        opt = dataIO.load_json('settings/optional_config.json')
        thebool = True
        try:
            if opt['24hours'] == "true":
                thebool = True
            else:
                thebool = False
        except IndexError:
            # No 24 hour bool given so default to true
            pass
        dandt, tzerror = self.get_datetime()
        if embed_perms(ctx.message):
            em = discord.Embed(color=discord.Color.blue())
            if thebool:
                em.add_field(name=u'\u23F0 Time', value="{:%H:%M:%S}".format(dandt), inline=False)
            else:
                em.add_field(name=u'\u23F0 Time', value="{:%I:%M:%S %p}".format(dandt), inline=False)
            em.add_field(name=u'\U0001F4C5 Date', value="{:%d %B %Y}".format(dandt), inline=False)
            if tzerror:
                em.add_field(name=u'\u26A0 Warning', value="Invalid timezone specified, system timezone was used instead.", inline=False)

            await ctx.send(content=None, embed=em)
        else:
            msg = '**Local Date and Time:** ```{:Time: %H:%M:%S\nDate: %Y-%m-%d```}'.format(dandt)
            await ctx.send(self.bot.bot_prefix + msg)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def time(self, ctx):
        """Show current time"""
        opt = dataIO.load_json('settings/optional_config.json')
        thebool = True
        try:
            if opt['24hours'] == "true":
                thebool = True
            else:
                thebool = False
        except IndexError:
            # No 24 hour bool given so default to true
            pass
        await ctx.message.delete()
        dandt, tzerror = self.get_datetime()
        if thebool:
            returnstring = '{:Time: `%H:%M:%S`}'.format(dandt)
        else:
            returnstring = '{:Time: `%I:%M:%S %p`}'.format(dandt)
        msg = returnstring
        await ctx.send(self.bot.bot_prefix + msg)

    @commands.command(pass_context=True)
    async def date(self, ctx):
        """Show current date"""
        await ctx.message.delete()
        dandt, tzerror = self.get_datetime()
        msg = '{:Date: `%d %B %Y`}'.format(dandt)
        await ctx.send(self.bot.bot_prefix + msg)

    @commands.command(pass_context=True)
    async def code(self, ctx, *, msg):
        """Write text in code format."""
        await ctx.message.delete()
        await ctx.send("```" + msg.replace("`", "") + "```")
    
    @commands.command(pass_context=True)
    async def toggletime(self, ctx):
        """Toggle between 24 hours time and 12 hours time"""
        opt = dataIO.load_json('settings/optional_config.json')
        try:
            if opt['24hours'] == "true":
                write_config_value("optional_config", "24hours", "false")
                await ctx.send(self.bot.bot_prefix + "Set time to `12 hour` clock")
            else:
                write_config_value("optional_config", "24hours", "true")
                await ctx.send(self.bot.bot_prefix + "Set time to `24 hour` clock")
        except:
            # Nothing was set, so changing the default to 12hrs
            write_config_value("optional_config", "24hours", "false")
            await ctx.send(self.bot.bot_prefix + "Set time to `12 hour` clock")

    @commands.command(pass_context=True)
    async def timezone(self, ctx, *, msg):
        """Set preferred timezone. Use the timezonelist for a full list of timezones."""
        write_config_value("optional_config", "timezone", msg)
        await ctx.send(self.bot.bot_prefix + 'Preferred timezone has been set.')

    @commands.command(pass_context=True)
    async def timezonelist(self, ctx):
        """List all available timezones for the timezone command."""
        await ctx.message.delete()
        embed = discord.Embed()
        embed.description = "[List of valid timezones](https://gist.github.com/anonymous/67129932414d0b82f58758a699a5a0ef)"
        await ctx.send("", embed=embed)

    @commands.command(pass_context=True)
    async def cmdprefix(self, ctx, *, msg):
        """Set your command prefix for normal commands. Requires a reboot."""
        write_config_value("config", "cmd_prefix", msg)
        await ctx.send(self.bot.bot_prefix + 'Prefix changed. Use `restart` to reboot the bot for the updated prefix.')

    @commands.command(pass_context=True)
    async def customcmdprefix(self, ctx, *, msg):
        """Set your command prefix for custom commands."""
        write_config_value("config", "customcmd_prefix", msg)
        self.bot.customcmd_prefix = msg
        await ctx.send(self.bot.bot_prefix + 'Prefix changed.')

    @commands.command(pass_context=True)
    async def botprefix(self, ctx, *, msg):
        """Set bot prefix"""
        write_config_value("config", "bot_identifier", msg)
        self.bot.bot_prefix = msg + ' '
        await ctx.send(self.bot.bot_prefix + 'Prefix changed.')

    @commands.command(pass_context=True)
    async def calc(self, ctx, *, msg):
        """Simple calculator. Ex: [p]calc 2+2"""
        equation = msg.strip().replace('^', '**').replace('x', '*')
        try:
            if '=' in equation:
                left = eval(equation.split('=')[0], {"__builtins__": None}, {"sqrt": sqrt})
                right = eval(equation.split('=')[1], {"__builtins__": None}, {"sqrt": sqrt})
                answer = str(left == right)
            else:
                answer = str(eval(equation, {"__builtins__": None}, {"sqrt": sqrt}))
        except TypeError:
            return await ctx.send(self.bot.bot_prefix + "Invalid calculation query.")
        if embed_perms(ctx.message):
            em = discord.Embed(color=0xD3D3D3, title='Calculator')
            em.add_field(name='Input:', value=msg.replace('**', '^').replace('x', '*'), inline=False)
            em.add_field(name='Output:', value=answer, inline=False)
            await ctx.send(content=None, embed=em)
            await ctx.message.delete()
        else:
            await ctx.send(self.bot.bot_prefix + answer)

    @commands.command(aliases=['sd'], pass_context=True)
    async def selfdestruct(self, ctx, *, amount):
        """Builds a self-destructing message. Ex: [p]sd 5"""
        async for message in ctx.message.channel.history():
            if message.id == ctx.message.id:
                continue
            if message.author == ctx.message.author:
                killmsg = message
                break
        timer = int(amount.strip())
        # Animated countdown because screw rate limit amirite
        destroy = ctx.message
        await ctx.message.edit(content=self.bot.bot_prefix + 'The above message will self-destruct in:')
        msg = await ctx.send('``%s  |``' % timer)
        for i in range(0, timer, 4):
            if timer - 1 - i == 0:
                await destroy.delete()
                await msg.edit(content='``0``')
                break
            else:
                await msg.edit(content='``%s  |``' % int(timer - 1 - i))
                await asyncio.sleep(1)
            if timer - 1 - i != 0:
                if timer - 2 - i == 0:
                    await destroy.delete()
                    await msg.edit(content='``0``')
                    break
                else:
                    await msg.edit(content='``%s  /``' % int(timer - 2 - i))
                    await asyncio.sleep(1)
            if timer - 2 - i != 0:
                if timer - 3 - i == 0:
                    await destroy.delete()
                    await msg.edit(content='``0``')
                    break
                else:
                    await msg.edit(content='``%s  -``' % int(timer - 3 - i))
                    await asyncio.sleep(1)
            if timer - 3 - i != 0:
                if timer - 4 - i == 0:
                    await destroy.delete()
                    await msg.edit(content='``0``')
                    break
                else:
                    await msg.edit(content='``%s  \ ``' % int(timer - 4 - i))
                    await asyncio.sleep(1)
        await msg.edit(content=':bomb:')
        await asyncio.sleep(.5)
        await msg.edit(content=':fire:')
        await killmsg.edit(content=':fire:')
        await asyncio.sleep(.5)
        await msg.delete()
        await killmsg.delete()

    @commands.command(aliases=['d'], pass_context=True)
    async def delete(self, ctx, txt=None, channel=None):
        """Deletes the last message sent or n messages sent. Ex: [p]d 5"""
        if txt:  # If number of seconds/messages are specified
            await ctx.message.delete()
            deleted = 0
            if txt == "all":
                limit = 1000
            else:
                txt = int(txt)
                limit = 200
                if txt > 200: 
                    txt = 200
            if channel:
                channel = find_channel(ctx.message.guild.channels, channel)
                if not channel: 
                    channel = find_channel(self.bot.get_all_channels(), channel)
            else: 
                channel = ctx.message.channel
            async for sent_message in channel.history():
                if sent_message.author == ctx.message.author:
                    try:
                        await sent_message.delete()
                        deleted += 1
                    except: 
                        pass
                    if deleted == txt: 
                        break
        else: # If no number specified, delete last message immediately
            msg = await ctx.message.channel.history(before=ctx.message).get(author=ctx.message.author)
            await ctx.message.delete()
            try:
                await msg.delete()
            except:
                pass

    @commands.command(pass_context=True)
    async def spoiler(self, ctx, *, msg: str):
        """Spoiler tag. Ex: [p]spoiler Some book | They get married."""
        try:
            if " | " in msg:
                spoiled_work, spoiler = msg.lower().split(" | ", 1)
            else:
                spoiled_work = msg
                spoiler = msg
            await ctx.message.edit(content=self.bot.bot_prefix + 'Spoiler for `' + spoiled_work + '`: \n`'
                                        + ''.join(
                map(lambda c: chr(ord('a') + (((ord(c) - ord('a')) + 13) % 26)) if c >= 'a' and c <= 'z' else c,
                    spoiler))
                                        + '`\n' + self.bot.bot_prefix + 'Use http://rot13.com to decode')
        except:
            await ctx.send(self.bot.bot_prefix + 'Could not encrypt spoiler.')

    @commands.group(pass_context=True)
    async def gist(self, ctx):
        """Posts to gist"""
        if ctx.invoked_subcommand is None:
            pre = cmd_prefix_len()
            url = PythonGists.Gist(
                description='Created in channel: {} in server: {}'.format(ctx.message.channel, ctx.message.guild),
                content=ctx.message.content[4 + pre:].strip(), name='Output')
            await ctx.send(self.bot.bot_prefix + 'Gist output: ' + url)
            await ctx.message.delete()

    @gist.command(pass_context=True)
    async def file(self, ctx, *, msg):
        """Create gist of file"""
        try:
            with open(msg) as fp:
                output = fp.read()
                url = PythonGists.Gist(
                    description='Created in channel: {} in server: {}'.format(ctx.message.channel, ctx.message.guild),
                    content=output, name=msg.replace('/', '.'))
                await ctx.send(self.bot.bot_prefix + 'Gist output: ' + url)
        except:
            await ctx.send(self.bot.bot_prefix + 'File not found.')
        finally:
            await ctx.message.delete()

    @commands.command(pass_context=True)
    async def uni(self, ctx, *, msg: str):
        """Convert to unicode emoji if possible. Ex: [p]uni :eyes:"""
        await ctx.send("`" + msg.replace("`", "") + "`")

    @commands.command(pass_context=True)
    async def poll(self, ctx, *, msg):
        """Create a strawpoll. Ex: [p]poll Favorite color = Blue | Red | Green"""
        loop = asyncio.get_event_loop()
        try:
            options = [op.strip() for op in msg.split('|')]
            if '=' in options[0]:
                title, options[0] = options[0].split('=')
                options[0] = options[0].strip()
            else:
                title = 'Poll by %s' % ctx.message.author.name
        except:
            return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. Example use: ``>poll Favorite color = Blue | Red | Green | Purple``')

        poll = await loop.run_in_executor(None, strawpy.create_poll, title.strip(), options)
        await ctx.send(self.bot.bot_prefix + poll.url)

    @commands.command(pass_context=True, aliases=['source'])
    async def sauce(self, ctx, *, txt: str = None):
        """Find source of image. Ex: [p]sauce http://i.imgur.com/NIq2U67.png"""
        if not txt:
            return await ctx.send(self.bot.bot_prefix + 'Input a link to check the source. Ex: ``>sauce http://i.imgur.com/NIq2U67.png``')
        await ctx.message.delete()
        sauce_nao = 'http://saucenao.com/search.php?db=999&url='
        request_headers = {
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "http://thewebsite.com",
            "Connection": "keep-alive"
        }
        loop = asyncio.get_event_loop()
        try:
            req = Request(sauce_nao + txt, headers=request_headers)
            webpage = await loop.run_in_executor(None, urlopen, req)
        except:
            return await ctx.send(self.bot.bot_prefix + 'Exceeded daily request limit. Try again tomorrow, sorry!')
        soup = BeautifulSoup(webpage, 'html.parser')
        pretty_soup = soup.prettify()
        em = discord.Embed(color=0xaa550f, description='**Input:**\n{}\n\n**Results:**'.format(txt))
        try:
            em.set_thumbnail(url=txt)
        except:
            pass
        match = re.findall(r'(?s)linkify" href="(.*?)"', str(soup.find('div', id='middle')))
        title = re.findall(r'(?s)<div class="resulttitle">(.*?)</td', str(soup.find('div', id='middle')))
        similarity_percent = re.findall(r'(?s)<div class="resultsimilarityinfo">(.*?)<',
                                        str(soup.find('div', id='middle')))
        ti = ''
        if title and float(similarity_percent[0][:-1]) > 60.0:
            title = title[0].strip().replace('<br/>', '\n').replace('<strong>', '').replace('</strong>', '').replace(
                '<div class="resultcontentcolumn">', '').replace('<span class="subtext">', '\n').replace('<small>',
                                                                                                         '').replace(
                '</span>', ' ').replace('</small>', '').replace('</tr>', '').replace('</td>', '').replace('</table>',
                                                                                                          '').replace(
                '</div>', '').split('\n')
            ti = '\n'.join([i.strip() for i in title if i.strip() != ''])
            if '</a>' not in ti:
                em.add_field(name='Source', value=ti)

            try:
                pretty_soup = pretty_soup.split('id="result-hidden-notification"', 1)[0]
            except:
                pass
            episode = re.findall(r'(?s)<span class="subtext">\n EP(.*?)<div', pretty_soup)
            ep = ''
            if episode:
                episode = episode[0].strip().replace('<br/>', '').replace('<strong>', '**').replace('</strong>',
                                                                                                    '**').replace(
                    '<span class="subtext">', '').replace('</span>', '').replace('</tr>', '').replace('</td>',
                                                                                                      '').replace(
                    '</table>', '').replace('</div>', '').split('\n')

                ep = ' '.join([j.strip() for j in episode if j.strip() != ''])
                ep = ep.replace('Est Time:', '\nEst Time:')
                em.add_field(name='More Info', value='**Episode** ' + ep, inline=False)
            est_time = re.findall(r'(?s)Est Time:(.*?)<div', pretty_soup)
            if est_time and 'Est Time:' not in ep:
                est_time = est_time[0].strip().replace('<br/>', '').replace('<strong>', '').replace('</strong>',
                                                                                                    '').replace(
                    '<span class="subtext">', '').replace('</span>', '').replace('</tr>', '').replace('</td>',
                                                                                                      '').replace(
                    '</table>', '').replace('</div>', '').split('\n')

                est = ' '.join([j.strip() for j in est_time if j.strip() != ''])
                est = est.replace('Est Time:', '\nEst Time:')
                em.add_field(name='More Info', value='**Est Time:** ' + est, inline=False)

        sources = ''
        count = 0
        source_sites = {'www.pixiv.net': 'pixiv', 'danbooru': 'danbooru', 'seiga.nicovideo': 'nico nico seiga',
                        'yande.re': 'yande.re', 'openings.moe': 'openings.moe', 'fakku.net': 'fakku',
                        'gelbooru': 'gelbooru',
                        'deviantart': 'deviantart', 'bcy.net': 'bcy.net', 'konachan.com': 'konachan',
                        'anime-pictures.net': 'anime-pictures.net', 'drawr.net': 'drawr'}
        for i in match:
            if not i.startswith('http://saucenao.com'):
                if float(similarity_percent[count][:-1]) > 60.0:
                    link_to_site = '{} - {}, '.format(i, similarity_percent[count])
                    for site in source_sites:
                        if site in i:
                            link_to_site = '[{}]({}) - {}, '.format(source_sites[site], i, similarity_percent[count])
                            break
                    sources += link_to_site
                    count += 1

            if count == 4:
                break
        sources = sources.rstrip(', ')

        material = re.search(r'(?s)Material:(.*?)</div', str(soup.find('div', id='middle')))
        if material and ('Materials:' not in ti and 'Material:' not in ti):
            material_list = material.group(1).strip().replace('<br/>', '\n').replace('<strong>', '').replace(
                '</strong>', '').split('\n')
            mat = ', '.join([i.strip() for i in material_list if i.strip() != ''])
            em.add_field(name='Material(s)', value=mat)

        characters = re.search(r'(?s)Characters:(.*?)</div', str(soup.find('div', id='middle')))
        if characters and ('Characters:' not in ti and 'Character:' not in ti):
            characters_list = characters.group(1).strip().replace('<br/>', '\n').replace('<strong>', '').replace(
                '</strong>', '').split('\n')
            chars = ', '.join([i.strip() for i in characters_list if i.strip() != ''])
            em.add_field(name='Character(s)', value=chars)

        creator = re.search(r'(?s)Creator:(.*?)</div', str(soup.find('div', id='middle')))
        if creator and ('Creators:' not in ti and 'Creator:' not in ti):
            creator_list = creator.group(1).strip().replace('<br/>', '\n').replace('<strong>', '').replace('</strong>',
                                                                                                           '').split(
                '\n')
            creat = ', '.join([i.strip() for i in creator_list if i.strip() != ''])
            em.add_field(name='Creator(s)', value=creat)

        if sources != '' and sources:
            em.add_field(name='Source sites - percent similarity', value=sources, inline=False)

        if not sources and not creator and not characters and not material and not title or float(
                similarity_percent[0][:-1]) < 60.0:
            em = discord.Embed(color=0xaa550f, description='**Input:**\n{}\n\n**No results found.**'.format(txt))

        await ctx.send(content=None, embed=em)

    @commands.has_permissions(change_nickname=True)
    @commands.command(aliases=['nick'], pass_context=True, no_pm=True)
    async def nickname(self, ctx, *, txt=None):
        """Change your nickname on a server. Leave empty to remove nick."""
        await ctx.message.delete()
        await ctx.message.author.edit(nick=txt)
        await ctx.send(self.bot.bot_prefix + 'Changed nickname to: `%s`' % txt)

    @commands.command(pass_context=True)
    async def ud(self, ctx, *, msg):
        """Pull data from Urban Dictionary. Use [p]help ud for more information.
        Usage: [p]ud <term> - Search for a term on Urban Dictionary.
        You can pick a specific result to use with [p]ud <term> | <result>.
        If no result is specified, the first result will be used.
        """
        await ctx.message.delete()
        number = 1
        if " | " in msg:
            msg, number = msg.rsplit(" | ", 1)
        search = parse.quote(msg)
        async with self.session.get("http://api.urbandictionary.com/v0/define", params={"term": search}) as resp:
            result = await resp.json()
        if result["result_type"] == "no_results":
            await ctx.send(self.bot.bot_prefix + "{} couldn't be found on Urban Dictionary.".format(msg))
        else:
            try:
                top_result = result["list"][int(number) - 1]
                embed = discord.Embed(title=top_result["word"], description=top_result["definition"],
                                      url=top_result["permalink"])
                if top_result["example"]:
                    embed.add_field(name="Example:", value=top_result["example"])
                if result["tags"]:
                    embed.add_field(name="Tags:", value=" ".join(result["tags"]))
                embed.set_author(name=top_result["author"],
                                 icon_url="https://lh5.ggpht.com/oJ67p2f1o35dzQQ9fVMdGRtA7jKQdxUFSQ7vYstyqTp-Xh-H5BAN4T5_abmev3kz55GH=w300")
                number = str(int(number) + 1)
                embed.set_footer(text="{} results were found. To see a different result, use >ud {} | {}.".format(
                    len(result["list"]), msg, number))
                await ctx.send("", embed=embed)
            except IndexError:
                await ctx.send(self.bot.bot_prefix + "That result doesn't exist! Try >ud {}.".format(msg))

    @commands.command(pass_context=True, aliases=['yt', 'vid', 'video'])
    async def youtube(self, ctx, *, msg):
        """Search for videos on YouTube."""
        search = parse.quote(msg)
        youtube_regex = re.compile('\/watch\?v=[\d\w\-]*')
        async with self.session.get("https://www.youtube.com/results", params={"search_query": search}) as resp:
            response = await resp.text()
        await ctx.message.delete()
        url = youtube_regex.findall(response)[0]
        await ctx.send("https://www.youtube.com{}".format(url))

    @commands.command(pass_context=True)
    async def xkcd(self, ctx, *, comic=""):
        """Pull comics from xkcd."""
        if comic == "random":
            randcomic = requests.get("https://c.xkcd.com/random/comic/".format(comic))
            comic = randcomic.url.split("/")[-2]
        site = requests.get("https://xkcd.com/{}/info.0.json".format(comic))
        if site.status_code == 404:
            site = None
            found = None
            search = parse.quote(comic)
            async with self.session.get("https://www.google.co.nz/search?&q={}+site:xkcd.com".format(search)) as resp:
                result = await resp.text()
            soup = BeautifulSoup(result, "html.parser")
            links = soup.find_all("cite")
            for link in links:
                if link.text.startswith("https://xkcd.com/"):
                    found = link.text.split("/")[3]
                    break
            if not found:
                await ctx.send(self.bot.bot_prefix + "That comic doesn't exist!")
            else:
                site = requests.get("https://xkcd.com/{}/info.0.json".format(found))
                comic = found
        if site:
            json = site.json()
            embed = discord.Embed(title="xkcd {}: {}".format(json["num"], json["title"]), url="https://xkcd.com/{}".format(comic))
            embed.set_image(url=json["img"])
            embed.set_footer(text="{}".format(json["alt"]))
            await ctx.send("", embed=embed)

    @commands.command(pass_context=True)
    async def hastebin(self, ctx, *, data):
        """Post to Hastebin."""
        await ctx.message.delete()
        async with self.session.post("https://hastebin.com/documents", data=data) as resp:
            post = await resp.text()
        try:
            await ctx.send(self.bot.bot_prefix + "Succesfully posted to Hastebin:\nhttps://hastebin.com/{}.txt".format(json.loads(post)["key"]))
        except json.JSONDecodeError:
            await ctx.send(self.bot.bot_prefix + "Failed to post to Hastebin. The API may be down right now.")

    @commands.command(pass_context=True)
    async def whoisplaying(self, ctx, *, game):
        """Check how many people are playing a certain game."""
        msg = ""
        for guild in self.bot.guilds:
            for user in guild.members:
                if user.game is not None:
                    if user.game.name is not None:
                        if user.game.name.lower() == game.lower():
                            msg += "{}#{}\n".format(user.name, user.discriminator)
        msg = "\n".join(set(msg.split("\n")))  # remove dupes
        if len(msg) > 1500:
            gist = PythonGists.Gist(description="Number of people playing {}".format(game), content=msg, name="Output")
            await ctx.send("{}Large output posted to Gist: {}".format(self.bot.bot_prefix, gist))
        elif len(msg) == 0:
            await ctx.send(self.bot.bot_prefix + "Nobody is playing that game!")
        else:
            embed = discord.Embed(title="Number of people playing {}".format(game), description=msg)
            await ctx.send("", embed=embed)
            
    @commands.command(pass_context=True, aliases=['anim'])
    async def animate(self, ctx, animation):
        """Play an animation from a text file. [p]help animate for more details.
        [p]animate <animation> - Animate a text file.
        Animation text files are stored in the anims folder. Each frame of animation is put on a new line.

        An example text file looks like this:
        family
        fam ily
        fam i ly
        fam i love y
        fam i love you

        You can additionally add a number to the top of the file to denote the delay between each frame. The default is 0.2 seconds.
        1
        fam
        fam i
        fam i love
        fam i love you
        """
        try:
            with open("anims/{}.txt".format(animation), encoding="utf-8") as f:
                anim = f.read().split("\n")
        except IOError:
            return await ctx.send(self.bot.bot_prefix + "You don't have that animation in your `anims` folder!")
        if anim:
            try:
                delay = float(anim[0])
                for frame in anim[1:]:
                    await ctx.message.edit(content=frame)
                    await asyncio.sleep(delay)
            except ValueError:
                for frame in anim:
                    await ctx.message.edit(content=frame)
                    await asyncio.sleep(0.2)

    @commands.command(pass_context=True)
    async def roles(self, ctx, *, user=None):
        """Check the roles of a user."""
        await ctx.message.delete()
        if not user:
            member = ctx.message.author
        else:
            member = get_user(ctx.message, user)
        if not member:
            await ctx.send(self.bot.bot_prefix + "That user couldn't be found. Please check your spelling and try again.")
        elif len(member.roles[1:]) >= 1:
            embed = discord.Embed(title="{}'s roles".format(member.name), description="\n".join([x.name for x in member.roles[1:]]), colour=member.colour)
            await ctx.send("", embed=embed)
        else:
            await ctx.send(self.bot.bot_prefix + "That user has no roles!")

    @commands.command(pass_context=True)
    async def messagedump(self, ctx, limit, filename, details="yes", reverse="no"):
        """Dump messages."""
        await ctx.message.delete()
        await ctx.send(self.bot.bot_prefix + "Downloading messages...")
        if not os.path.isdir('message_dump'):
            os.mkdir('message_dump')
        with open("message_dump/" + filename.rsplit('.', 1)[0] + ".txt", "w+", encoding="utf-8") as f:
            if reverse == "yes":
                if details == "yes":
                    async for message in ctx.message.channel.history(limit=int(limit)):
                        f.write("<{} at {} on {}> {}\n".format(message.author.name, message.created_at.strftime('%d %b %Y'), message.created_at.strftime('%H:%M:%S'), message.content))

                else:
                    async for message in ctx.message.channel.history(limit=int(limit)):
                        f.write(message.content + "\n")
            else:
                if details == "yes":
                    async for message in ctx.message.channel.history(limit=int(limit), reverse=True):
                        f.write("<{} at {} on {}> {}\n".format(message.author.name, message.created_at.strftime('%d %b %Y'), message.created_at.strftime('%H:%M:%S'), message.content))

                else:
                    async for message in ctx.message.channel.history(limit=int(limit), reverse=True):
                        f.write(message.content + "\n")
        await ctx.send(self.bot.bot_prefix + "Finished downloading!")

    @commands.group(pass_context=True)
    async def link(self, ctx):
        """Shorten/lengthen URLs"""
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send(self.bot.bot_prefix + "Usage: `link <shorten/lengthen> <url>`")

    @link.command(pass_context=True)
    async def shorten(self, ctx, url):
        try:
            r = requests.get(url).status_code
        except requests.exceptions.RequestException:
            r = 404
        if r == 200:
            params = {
                "access_token": "757c24db53fac6a6a994439da41bdbbe325dfb99",
                "longUrl": url
            }
            response = requests.get("https://api-ssl.bitly.com/v3/shorten", params=params)
            if response.status_code == 200:
                await ctx.send(self.bot.bot_prefix + "<{}>".format(response.json()["data"]["url"]))
            else:
                await ctx.send(self.bot.bot_prefix + "There was an error shortening your URL.")
        else:
            await ctx.send(self.bot.bot_prefix + "You did not enter a valid URL.")

    @link.command(pass_context=True)
    async def lengthen(self, ctx, url):
        try:
            r = requests.get(url).status_code
        except requests.exceptions.RequestException:
            r = 404
        if r == 200:
            await ctx.send(self.bot.bot_prefix + "<{}>".format(requests.get(url).url))
        else:
            await ctx.send(self.bot.bot_prefix + "You did not enter a valid URL.")

    @commands.command(pass_context=True, aliases=['getcolor'])
    async def getcolour(self, ctx, *, colour_codes):
        """Posts color of given hex"""
        await ctx.message.delete()
        colour_codes = colour_codes.split()
        size = (60, 80) if len(colour_codes) > 1 else (200, 200)
        if len(colour_codes) > 5:
            return await ctx.send(self.bot.bot_prefix + "Sorry, 5 colour codes maximum")
        for colour_code in colour_codes:
            if not colour_code.startswith("#"):
                colour_code = "#" + colour_code
            image = Image.new("RGB", size, colour_code)
            with io.BytesIO() as file:
                image.save(file, "PNG")
                file.seek(0)
                await ctx.send("Colour with hex code {}:".format(colour_code), file=discord.File(file, "colour_file.png"))
            await asyncio.sleep(1)  # Prevent spaminess

    @commands.has_permissions(add_reactions=True)
    @commands.command(pass_context=True)
    async def rpoll(self, ctx, *, msg):
        """Create a poll using reactions. >help rpoll for more information.
        [p]rpoll <question> | <answer> | <answer> - Create a poll. You may use as many answers as you want, placing a pipe | symbol in between them.
        Example:
        [p]rpoll What is your favorite anime? | Steins;Gate | Naruto | Attack on Titan | Shrek
        You can also use the "time" flag to set the amount of time in seconds the poll will last for.
        Example:
        [p]rpoll What time is it? | HAMMER TIME! | SHOWTIME! | time=10
        """
        await ctx.message.delete()
        options = msg.split(" | ")
        time = [x for x in options if x.startswith("time=")]
        if time:
            time = time[0]
        if time:
            options.remove(time)
        if len(options) <= 1:
            raise commands.errors.MissingRequiredArgument
        if len(options) >= 11:
            return await ctx.send(self.bot.bot_prefix + "You must have 9 options or less.")
        if time:
            time = int(time.strip("time="))
        else:
            time = 30
        emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']
        to_react = []
        confirmation_msg = "**{}?**:\n\n".format(options[0].rstrip("?"))
        for idx, option in enumerate(options[1:]):
            confirmation_msg += "{} - {}\n".format(emoji[idx], option)
            to_react.append(emoji[idx])
        confirmation_msg += "\n\nYou have {} seconds to vote!".format(time)
        poll_msg = await ctx.send(confirmation_msg)
        for emote in to_react:
            await poll_msg.add_reaction(emote)
        await asyncio.sleep(time)
        async for message in ctx.message.channel.history():
            if message.id == poll_msg.id:
                poll_msg = message
        results = {}
        for reaction in poll_msg.reactions:
            if reaction.emoji in to_react:
                results[reaction.emoji] = reaction.count - 1
        end_msg = "The poll is over. The results:\n\n"
        for result in results:
            end_msg += "{} {} - {} votes\n".format(result, options[emoji.index(result)+1], results[result])
        top_result = max(results, key=lambda key: results[key])
        if len([x for x in results if results[x] == results[top_result]]) > 1:
            top_results = []
            for key, value in results.items():
                if value == results[top_result]:
                    top_results.append(options[emoji.index(key)+1])
            end_msg += "\nThe victory is tied between: {}".format(", ".join(top_results))
        else:
            top_result = options[emoji.index(top_result)+1]
            end_msg += "\n{} is the winner!".format(top_result)
        await ctx.send(end_msg)

    @commands.command(pass_context=True)
    async def cogs(self, ctx):
        """Shows loaded/unloaded cogs"""
        await ctx.message.delete()
        cogs = ["cogs." + os.path.splitext(f)[0] for f in [os.path.basename(f) for f in glob.glob("cogs/*.py")]]
        cogs.extend(["custom_cogs." + os.path.splitext(f)[0] for f in [os.path.basename(f) for f in glob.glob("custom_cogs/*.py")]])
        loaded = [x.__module__.split(".")[1] for x in self.bot.cogs.values()]
        unloaded = [c.split(".")[1] for c in cogs
                    if c.split(".")[1] not in loaded]
        embed = discord.Embed(title="List of installed cogs")
        if loaded:
            embed.add_field(name="Loaded", value="\n".join(sorted(loaded)), inline=True)
        else:
            embed.add_field(name="Loaded", value="None!", inline=True)
        if unloaded:
            embed.add_field(name="Not Loaded", value="\n".join(sorted(unloaded)), inline=True)
        else:
            embed.add_field(name="Not Loaded", value="None!", inline=True)
        embed.set_footer(text="Were you looking for >cog?")
        await ctx.send("", embed=embed)

    @commands.command(pass_context=True, aliases=['clearconsole', 'cc', 'clear'])
    async def cleartrace(self, ctx):
        global git
        """Clear the console."""
        if os.name == 'nt':
            os.system('cls')
        else:
            try:
                os.system('clear')
            except:
                await ctx.send(self.bot.bot_prefix + 'Could not clear console, continuing anyways')

        print('Logged in as')
        try:
            print(self.bot.user.name)
        except:
            pass
        print('User id: ' + str(self.bot.user.id))
        g = git.cmd.Git(working_dir=os.getcwd())
        branch = g.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        print('Current branch is: ' + branch)
        print('------')
        await ctx.send(self.bot.bot_prefix + 'Console cleared successfully.')
        
    @commands.command(aliases=['ra'])
    async def readall(self, ctx):
        """Marks everything as read."""
        await ctx.message.delete()
        for guild in self.bot.guilds:
            await guild.ack()
        await ctx.send(self.bot.bot_prefix + "Marked {} guilds as read.".format(len(self.bot.guilds))) 


def setup(bot):
    bot.add_cog(Utility(bot))
