import spice_api as spice
import requests
import re
import asyncio
import gc
import tokage
import discord
import pytz
from datetime import datetime, timedelta
from discord.ext import commands
from bs4 import BeautifulSoup
from appuselfbot import bot_prefix
from cogs.utils.checks import *

'''Module for MyAnimeList search of anime, manga, and light novels.'''


class Mal:

    def __init__(self, bot):
        self.bot = bot
        self.t_client = tokage.Client()

    @staticmethod
    async def google_results(type, query):
        loop = asyncio.get_event_loop()
        config = load_optional_config()
        try:
            entries, root = await get_google_entries('site:myanimelist.net {} {}'.format(type, query))
            result = entries[0]
        except RuntimeError:
            try:
                search_url = "https://www.googleapis.com/customsearch/v1?q=site:myanimelist.net {} {} ".format(type, query) + "&start=" + '1' + "&key=" + \
                            config['google_api_key'] + "&cx=" + config[
                                'custom_search_engine']
                r = await loop.run_in_executor(None, requests.get, search_url)
                response = r.content.decode('utf-8')
                result = json.loads(response)['items'][0]['link']
            except:
                return False, None

        return True, result

    # Mal search (chained with either anime or manga)
    @commands.group(pass_context=True)
    async def mal(self, ctx):
        """Search MyAnimeList for an anime/manga. Ex: >mal anime Steins;Gate
        
        Optionally, put [link] after the anime/manga part to just get the link instead of the full info.
        Ex: >mal anime [link] Steins;Gate"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(ctx.message.channel,
                                       bot_prefix + 'Invalid Syntax. Example use: ``>mal anime steins;gate`` or ``>mal manga boku no hero academia``')

    # Anime search for Mal
    @mal.command(pass_context=True)
    async def anime(self, ctx, *, msg: str = None):
        """Search the anime database. Ex: >mal anime Steins;Gate"""
        if msg:
            loop = asyncio.get_event_loop()
            config = load_optional_config()
            fetch = await self.bot.send_message(ctx.message.channel, bot_prefix + 'Searching...')
            if msg.startswith('[link]'):
                msg = msg[6:]
                link = True
            else:
                link = False

            found, result = await self.google_results('anime', msg)

            if found:
                anime_id = re.findall('/anime/(.*)/', result)
                results = await loop.run_in_executor(None, spice.search_id, int(anime_id[0]), spice.get_medium('anime'),
                                                     spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()

            else:
                allresults = await loop.run_in_executor(None, spice.search, msg.strip(), spice.get_medium('anime'),
                                                        spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()
                results = allresults[0]

            # No results found for specified tags
            if not results:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'No results.')
                await self.bot.delete_message(fetch)
                return await self.bot.delete_message(ctx.message)

            if not embed_perms(ctx.message) or link is True:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'https://myanimelist.net/anime/%s' % results.id)
                await self.bot.delete_message(fetch)
                return await self.bot.delete_message(ctx.message)

            # Formatting embed
            selection = results
            synopsis = BeautifulSoup(selection.synopsis, 'lxml')

            em = discord.Embed(description='{}'.format('https://myanimelist.net/anime/%s' % selection.id),
                               colour=0x0066CC)

            try:
                english = selection.english
                if english:
                    em.add_field(name='English Title', value=english, inline=False)
            except:
                pass
            em.add_field(name='Type', value=selection.anime_type)
            if selection.episodes == '0':
                episodes = 'Unknown'
            else:
                episodes = selection.episodes
            em.add_field(name='Episodes', value=episodes)
            em.add_field(name='Score', value=selection.score + '/10')
            em.add_field(name='Status', value=selection.status)
            try:
                synop = synopsis.get_text()[:400].split('.')
                text = ''
                for i in range(0, len(synop)-1):
                    text += synop[i] + '.'
            except:
                text = synopsis.get_text()
            em.add_field(name='Synopsis',
                         value=text + ' [Read more »](https://myanimelist.net/anime/%s)' % selection.id)

            if selection.status == "Publishing":
                date = selection.raw_data.start_date.text + " -"
            else:
                date = selection.raw_data.start_date.text + "  -  " + selection.raw_data.end_date.text
            if date:
                em.add_field(name='Airing Time:', value=date)
            em.set_thumbnail(url=selection.image_url)
            em.set_author(name=selection.title,
                          icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            em.set_footer(text='MyAnimeList')

            await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.delete_message(fetch)
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Specify an anime to search for.')

    # Manga search for Mal
    @mal.command(pass_context=True)
    async def manga(self, ctx, *, msg: str = None):
        """Search the manga database. Ex: >mal manga Boku no Hero Academia"""
        if msg:
            loop = asyncio.get_event_loop()
            config = load_optional_config()
            fetch = await self.bot.send_message(ctx.message.channel, bot_prefix + 'Searching...')
            if msg.startswith('[link]'):
                msg = msg[6:]
                link = True
            else:
                link = False

            found, result = await self.google_results('manga', msg)

            if found:
                manga_id = re.findall('/manga/(.*)/', result)
                results = await loop.run_in_executor(None, spice.search_id, int(manga_id[0]), spice.get_medium('manga'),
                                                     spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()

            else:
                allresults = await loop.run_in_executor(None, spice.search, msg.strip(), spice.get_medium('manga'),
                                                        spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()
                results = allresults[0]

            # No results found for specified tags
            if not results:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'No results.')
                await self.bot.delete_message(fetch)
                return await self.bot.delete_message(ctx.message)

            if not embed_perms(ctx.message) or link is True:
                await self.bot.send_message(ctx.message.channel,
                                            bot_prefix + 'https://myanimelist.net/manga/%s' % results.id)
                await self.bot.delete_message(fetch)
                return await self.bot.delete_message(ctx.message)
            # Formatting
            selection = results
            synopsis = BeautifulSoup(selection.synopsis, 'lxml')
            em = discord.Embed(description='{}'.format('https://myanimelist.net/manga/%s' % selection.id),
                               colour=0x0066CC)

            em.add_field(name='Type', value=selection.manga_type)
            if selection.chapters == '0':
                chapters = 'Unknown'
            else:
                chapters = selection.chapters
            em.add_field(name='Chapters', value=chapters)
            em.add_field(name='Score', value=selection.score + '/10')
            try:
                english = selection.english
                if english:
                    em.add_field(name='English Title', value=english, inline=False)
            except:
                pass

            em.add_field(name='Status', value=selection.status)
            try:
                synop = synopsis.get_text()[:400].split('.')
                text = ''
                for i in range(0, len(synop) - 1):
                    text += synop[i] + '.'
            except:
                text = synopsis.get_text()
            em.add_field(name='Synopsis',
                         value=text + ' [Read more »](https://myanimelist.net/manga/%s)' % selection.id)

            if selection.status == "Publishing":
                date = selection.raw_data.start_date.text + " -"
            else:
                date = selection.raw_data.start_date.text + "  -  " + selection.raw_data.end_date.text
            if date:
                em.add_field(name='Publishing Time:', value=date)
            em.set_thumbnail(url=selection.image_url)
            em.set_author(name=selection.title,
                          icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            em.set_footer(text='MyAnimeList')

            await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.delete_message(fetch)
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'No results')

    @staticmethod
    async def get_next_weekday(startdate, day):
        days = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }
        weekday = days[day]
        d = datetime.strptime(startdate, '%Y-%m-%d')
        t = timedelta((7 + weekday - d.weekday()) % 7)
        return (d + t).strftime('%Y-%m-%d')
    
    async def get_remaining_time(self, anime):
        day = anime.broadcast.split(" at ")[0][:-1]
        hour = anime.broadcast.split(" at ")[1].split(" ")[0]
        jp_time = datetime.now(pytz.timezone("Japan"))
        air_date = await self.get_next_weekday(jp_time.strftime('%Y-%m-%d'), day)
        time_now = jp_time.replace(tzinfo=None)
        show_airs = datetime.strptime('{} - {}'.format(air_date, hour.strip()), '%Y-%m-%d - %H:%M')
        remaining = show_airs - time_now
        if remaining.days < 0:
            return '6 Days {} Hours and {} Minutes.'.format(remaining.seconds // 3600, (remaining.seconds // 60)%60)
        else:
            return '{} Days {} Hours and {} Minutes.'.format(remaining.days, remaining.seconds // 3600, (remaining.seconds // 60)%60)
    
    @mal.command(pass_context=True, name="next")
    async def next_(self, ctx, *, query):
        search = await self.bot.say(bot_prefix + "Searching...")
        found, result = await self.google_results('anime', query)
        if found:
            anime_id = re.findall('/anime/(.*)/', result)[0]
            try:
                anime = await self.t_client.get_anime(anime_id)
            except Exception as e:
                await self.bot.send_message(ctx.message.channel, bot_prefix + ":exclamation: Oops!\n {}: {}".format(type(e).__name__, e))
                await self.bot.delete_message(search)
                return await self.bot.delete_message(ctx.message)
        else:
            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Failed to find given anime.')
        if anime.status == "Finished Airing":
            remaining = "This anime has finished airing!\n" + anime.air_time
        else:
            remaining = await self.get_remaining_time(anime)
        embed = discord.Embed(title=anime.title, color=0x0066CC)
        embed.add_field(name="Next Episode", value=remaining)
        embed.set_footer(text='MyAnimeList')
        embed.set_author(name='MyAnimeList', icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
        embed.set_thumbnail(url=anime.image)
        await self.bot.delete_message(search)
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(Mal(bot))
