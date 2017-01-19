import spice_api as spice
import urllib
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
        urlcontent = urllib.request.urlopen("https://myanimelist.net/anime/%s" % selection.id).read()
        imgurls = re.findall('img .*?src="(.*?)"', str(urlcontent))

        em = discord.Embed(title=selection.title,
                           description='''\n{link}\n\n**Episodes:** {episodes}\n**Avg Score:** {score}/10\n**Synopsis:**{synopsis}\n'''.format(
                               link="https://myanimelist.net/anime/%s" % selection.id, title=selection.title,
                               episodes=selection.episodes, score=selection.score, synopsis="\n" + synopsis.get_text()[
                                                                                                   :400] + '...[more](https://myanimelist.net/anime/%s)' % selection.id),
                           colour=0x0066CC)
        try:
            em.add_field(name='Type', value=selection.anime_type, inline=True)
            em.add_field(name='English', value=selection.english, inline=True)
            em.add_field(name='Status:', value=selection.status, inline=True)
            em.add_field(name='Airing Time:', value=selection.dates[0] + "  -  " + selection.dates[1], inline=True)
        except:
            pass
        em.set_thumbnail(url=selection.image_url)
        em.set_author(name='MyAnimeList',
                      icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
        try:
            await self.bot.send_message(ctx.message.channel, embed=em)

        # Yea, I know this is weird but it had to be done. Blame the mal api.
        except:
            em = discord.Embed(title=selection.title,
                               description='''\n{link}\n\n**Episodes:** {episodes}\n**Avg Score:** {score}/10\n**Synopsis:**{synopsis}\n'''.format(
                                   link="https://myanimelist.net/anime/%s" % selection.id, title=selection.title,
                                   episodes=selection.episodes, score=selection.score,
                                   synopsis="\n" + synopsis.get_text()[
                                                   :400] + '...[more](https://myanimelist.net/anime/%s)' % selection.id),
                               colour=0x0066CC)
            em.add_field(name='Type', value=selection.anime_type, inline=True)
            em.add_field(name='Status:', value=selection.status, inline=True)
            em.set_thumbnail(url=selection.image_url)
            em.set_author(name='MyAnimeList', icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            await self.bot.send_message(ctx.message.channel, embed=em)


    # Manga search for Mal
    @mal.command(pass_context=True)
    async def manga(self, ctx, *, msg: str):
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
        em = discord.Embed(title=selection.title,
                           description='''\n{link}\n\n**Chapters:** {chapters}\n**Avg Score:** {score}/10\n**Synopsis:**{synopsis}\n'''.format(
                               link="https://myanimelist.net/manga/%s" % selection.id, title=selection.title,
                               chapters=selection.chapters, score=selection.score, synopsis="\n" + synopsis.get_text()[
                                                                                                   :400] + '...[more](https://myanimelist.net/manga/%s)' % selection.id),
                           colour=0x0066CC)
        try:
            em.add_field(name='Type', value=selection.manga_type, inline=True)
            em.add_field(name='English', value=selection.english, inline=True)
            em.add_field(name='Status:', value=selection.status, inline=True)
            em.add_field(name='Publishing Time:', value=selection.dates[0] + "  -  " + selection.dates[1], inline=True)
        except:
            pass
        em.set_thumbnail(url=selection.image_url)
        em.set_author(name='MyAnimeList',
                      icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
        try:
            await self.bot.send_message(ctx.message.channel, embed=em)

        # Again, really weird but it had to be done. Blame the mal api.
        except:
            em = discord.Embed(title=selection.title,
                               description='''\n{link}\n\n**Chapters:** {chapters}\n**Avg Score:** {score}/10\n**Synopsis:**{synopsis}\n'''.format(
                                   link="https://myanimelist.net/manga/%s" % selection.id, title=selection.title,
                                   chapters=selection.chapters, score=selection.score,
                                   synopsis="\n" + synopsis.get_text()[
                                                   :400] + '...[more](https://myanimelist.net/manga/%s)' % selection.id),
                               colour=0x0066CC)
            em.add_field(name='Type', value=selection.manga_type, inline=True)
            em.add_field(name='Status:', value=selection.status, inline=True)
            em.set_thumbnail(url=selection.image_url)
            em.set_author(name='MyAnimeList', icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            await self.bot.send_message(ctx.message.channel, embed=em)


def setup(bot):
    bot.add_cog(Mal(bot))
