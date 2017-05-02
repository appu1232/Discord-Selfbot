import spice_api as spice
import requests
import re
import discord
import asyncio
import gc
from discord.ext import commands
from bs4 import BeautifulSoup
from appuselfbot import bot_prefix
from cogs.utils.checks import *

'''Module for MyAnimeList search of anime, manga, and light novels.'''


class Mal:

    def __init__(self, bot):
        self.bot = bot

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
    async def anime(self, ctx, *, msg: str):
        """Search the anime database. Ex: >mal anime Steins;Gate"""
        loop = asyncio.get_event_loop()
        config = load_optional_config()
        fetch = await self.bot.send_message(ctx.message.channel, bot_prefix + 'Searching...')
        try:
            link = False
            try:

                if msg.startswith('[link]'):
                    msg = msg[6:]
                    link = True
                # Search google for the anime under site:myanimelist.net
                searchUrl = "https://www.googleapis.com/customsearch/v1?q=site:myanimelist.net anime " + msg.strip() + "&start=" + '1' + "&key=" + \
                            config['google_api_key'] + "&cx=" + config[
                                'custom_search_engine']
                r = requests.get(searchUrl)
                response = r.content.decode('utf-8')
                result = json.loads(response)
                animeID = re.findall('/anime/(.*)/', str(result['items'][0]['link']))
                results = await loop.run_in_executor(None, spice.search_id, int(animeID[0]), spice.get_medium('anime'),
                                       spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()

                # If no results found or daily api limit exceeded, use spice's search
                if not results:
                    allresults = await loop.run_in_executor(None, spice.search, msg.strip(), spice.get_medium('anime'),
                                           spice.init_auth(config['mal_username'], config['mal_password']))
                    gc.collect()
                    results = allresults[0]

            # On any exception, search spice instead
            except:
                allresults = await loop.run_in_executor(None, spice.search, msg.strip(), spice.get_medium('anime'),
                                       spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()
                results = allresults[0]

            # No results found for specified tags
            if not results:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'No results.')
                await self.bot.delete_message(fetch)
                await self.bot.delete_message(ctx.message)
                return

            if not embed_perms(ctx.message) or link is True:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'https://myanimelist.net/anime/%s' % results.id)
                await self.bot.delete_message(fetch)
                await self.bot.delete_message(ctx.message)
                return

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

            await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.delete_message(fetch)
            await self.bot.delete_message(ctx.message)
        except:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'No results')
            await self.bot.delete_message(fetch)

    # Manga search for Mal
    @mal.command(pass_context=True)
    async def manga(self, ctx, *, msg: str):
        """Search the manga database. Ex: >mal manga Boku no Hero Academia"""
        loop = asyncio.get_event_loop()
        config = load_optional_config()
        fetch = await self.bot.send_message(ctx.message.channel, bot_prefix + 'Searching...')
        try:
            link = False
            try:

                if msg.startswith('[link]'):
                    msg = msg[6:]
                    link = True
                config = load_optional_config()
                # Search google for the manga under site:myanimelist.net
                searchUrl = "https://www.googleapis.com/customsearch/v1?q=site:myanimelist.net manga " + msg.strip() + "&start=" + '1' + "&key=" + \
                            config['google_api_key'] + "&cx=" + config[
                                'custom_search_engine']
                r = requests.get(searchUrl)
                response = r.content.decode('utf-8')
                result = json.loads(response)
                mangaID = re.findall('/manga/(.*)/', str(result['items'][0]['link']))
                results = await loop.run_in_executor(None, spice.search_id, int(mangaID[0]), spice.get_medium('manga'), spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()

                # If no results found or daily api limit exceeded, use spice's search
                if not results:
                    allresults = await loop.run_in_executor(None, spice.search, msg.strip(), spice.get_medium('manga'),
                                           spice.init_auth(config['mal_username'], config['mal_password']))
                    gc.collect()
                    results = allresults[0]

            # On any exception, search spice instead
            except:
                allresults = await loop.run_in_executor(None, spice.search, msg.strip(), spice.get_medium('manga'),
                                       spice.init_auth(config['mal_username'], config['mal_password']))
                gc.collect()
                results = allresults[0]

            # No results found for specified tags
            if not results:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'No results.')
                await self.bot.delete_message(fetch)
                await self.bot.delete_message(ctx.message)
                return

            if not embed_perms(ctx.message) or link is True:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'https://myanimelist.net/manga/%s' % results.id)
                await self.bot.delete_message(fetch)
                await self.bot.delete_message(ctx.message)
                return

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
            await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.delete_message(fetch)
            await self.bot.delete_message(ctx.message)
        except:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'No results')
            await self.bot.delete_message(fetch)


def setup(bot):
    bot.add_cog(Mal(bot))
