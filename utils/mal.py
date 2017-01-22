import spice_api as spice
import json
import requests
import re
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from appuselfbot import isBot, config

class Mal:

    def __init__(self, bot):
        self.bot = bot

    # Mal search (chained with either anime or manga)
    @commands.group(pass_context=True)
    async def mal(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(ctx.message.channel,
                                       isBot + 'Invalid Syntax. Example use: ``>mal anime steins;gate`` or ``>mal manga kaguya wants to be confessed to``')

    # Anime search for Mal
    @mal.command(pass_context=True)
    async def anime(self, ctx, *, msg: str):
        try:
            fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Searching...')
            try:

                # Search google for the anime under site:myanimelist.net
                searchUrl = "https://www.googleapis.com/customsearch/v1?q=site:myanimelist.net anime " + msg.strip() + "&start=" + '1' + "&key=" + \
                            config['google_api_key'] + "&cx=" + config[
                                'custom_search_engine']
                r = requests.get(searchUrl)
                response = r.content.decode('utf-8')
                result = json.loads(response)
                animeID = re.findall('/anime/(.*)/', str(result['items'][0]['link']))
                results = spice.search_id(int(animeID[0]), spice.get_medium('anime'),
                                       spice.init_auth(config['mal_username'], config['mal_password']))

                # If no results found or daily api limit exceeded, use spice's search
                if not results:
                    allresults = spice.search(msg.strip(), spice.get_medium('anime'),
                                           spice.init_auth(config['mal_username'], config['mal_password']))
                    results = allresults[0]

            # On any exception, search spice instead
            except:
                allresults = spice.search(msg.strip(), spice.get_medium('anime'),
                                       spice.init_auth(config['mal_username'], config['mal_password']))
                results = allresults[0]

            # No results found for specified tags
            if not results:
                await self.bot.send_message(ctx.message.channel, isBot + 'No results.')
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
            em.add_field(name='Type', value=selection.anime_type, inline=True)
            if selection.episodes == '0':
                episodes = 'Unknown'
            else:
                episodes = selection.episodes
            em.add_field(name='Episodes', value=episodes, inline=True)
            em.add_field(name='Score', value=selection.score + '/10', inline=True)
            em.add_field(name='Status', value=selection.status, inline=True)
            try:
                synop = synopsis.get_text()[:400].split('.')
                text = ''
                for i in range(0, len(synop)-1):
                    text += synop[i] + '.'
            except:
                text = synopsis.get_text()
            em.add_field(name='Synopsis',
                         value=text + ' [Read more »](https://myanimelist.net/anime/%s)' % selection.id)
            try:
                if selection.dates[1] == '0000-00-00':
                    date = selection.dates[0] + "  -  "
                else:
                    date = selection.dates[0] + "  -  " + selection.dates[1]
                if date:
                    em.add_field(name='Airing Time:', value=date, inline=True)
            except:
                pass
            em.set_thumbnail(url=selection.image_url)
            em.set_author(name=selection.title,
                          icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.delete_message(fetch)
        except:
            await self.bot.send_message(ctx.message.channel, isBot + 'No results')
            await self.bot.delete_message(fetch)

    # Manga search for Mal
    @mal.command(pass_context=True)
    async def manga(self, ctx, *, msg: str):
        try:
            fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Searching...')
            try:

                # Search google for the manga under site:myanimelist.net
                searchUrl = "https://www.googleapis.com/customsearch/v1?q=site:myanimelist.net manga " + msg.strip() + "&start=" + '1' + "&key=" + \
                            config['google_api_key'] + "&cx=" + config[
                                'custom_search_engine']
                r = requests.get(searchUrl)
                response = r.content.decode('utf-8')
                result = json.loads(response)
                mangaID = re.findall('/manga/(.*)/', str(result['items'][0]['link']))
                results = spice.search_id(int(mangaID[0]), spice.get_medium('manga'), spice.init_auth(config['mal_username'], config['mal_password']))

                # If no results found or daily api limit exceeded, use spice's search
                if not results:
                    allresults = spice.search(msg.strip(), spice.get_medium('manga'),
                                           spice.init_auth(config['mal_username'], config['mal_password']))
                    results = allresults[0]

            # On any exception, search spice instead
            except:
                allresults = spice.search(msg.strip(), spice.get_medium('manga'),
                                       spice.init_auth(config['mal_username'], config['mal_password']))
                results = allresults[0]

            # No results found for specified tags
            if not results:
                await self.bot.send_message(ctx.message.channel, isBot + 'No results.')
                return

            # Formatting
            selection = results
            synopsis = BeautifulSoup(selection.synopsis, 'lxml')
            em = discord.Embed(description='{}'.format('https://myanimelist.net/manga/%s' % selection.id),
                               colour=0x0066CC)

            em.add_field(name='Type', value=selection.manga_type, inline=True)
            if selection.chapters == '0':
                chapters = 'Unknown'
            else:
                chapters = selection.chapters
            em.add_field(name='Chapters', value=chapters, inline=True)
            print(selection.chapters)
            print(type(selection.chapters))
            em.add_field(name='Score', value=selection.score + '/10', inline=True)
            try:
                english = selection.english
                if english:
                    em.add_field(name='English Title', value=english, inline=False)
            except:
                pass

            em.add_field(name='Status', value=selection.status, inline=True)
            try:
                synop = synopsis.get_text()[:400].split('.')
                text = ''
                for i in range(0, len(synop) - 1):
                    text += synop[i] + '.'
            except:
                text = synopsis.get_text()
            em.add_field(name='Synopsis',
                         value=text + ' [Read more »](https://myanimelist.net/anime/%s)' % selection.id)
            try:
                if selection.dates[1] == '0000-00-00':
                    date = selection.dates[0] + "  -  "
                else:
                    date = selection.dates[0] + "  -  " + selection.dates[1]
                if date:
                    em.add_field(name='Publishing Time:', value=date, inline=True)
            except:
                pass

            em.set_thumbnail(url=selection.image_url)
            em.set_author(name=selection.title,
                          icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.delete_message(fetch)
        except:
            await self.bot.send_message(ctx.message.channel, isBot + 'No results')
            await self.bot.delete_message(fetch)


def setup(bot):
    bot.add_cog(Mal(bot))
