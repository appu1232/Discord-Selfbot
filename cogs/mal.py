import sys
import subprocess
import os
import requests
import re
import asyncio
import gc
import tokage
import discord
import pytz
import json
from datetime import datetime, timedelta
from discord.ext import commands
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from cogs.utils.checks import load_optional_config, get_google_entries, embed_perms

'''Module for MyAnimeList search of anime, manga, and light novels.'''


class Mal:

    def __init__(self, bot):
        self.bot = bot
        self.t_client = tokage.Client()

    # Taken from https://stackoverflow.com/questions/2659900/python-slicing-a-list-into-n-nearly-equal-length-partitions
    def partition(self, lst, n):
        if n > 1:
            division = len(lst) / n
            return [lst[round(division * i):round(division * (i + 1))] for i in range(n)]
        else:
            return [lst]

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
        """Search MyAnimeList for an anime/manga. Ex: [p]mal anime Steins;Gate
        
        For [p]mal anime and [p]mal manga, put [link] after the anime/manga part to just get the link instead of the full info.
        Ex: [p]mal anime [link] Steins;Gate

        For [p]mal va, put [more] to get some more info. (Takes more time) Ex: [p]mal va [more] saori hayami"""
        if ctx.invoked_subcommand is None:
            await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. See `>help mal` for more info on how to use this command.')



    # Anime search for Mal
    @mal.command(pass_context=True)
    async def anime(self, ctx, *, msg: str = None):
        """Search the anime database. Ex: [p]mal anime Steins;Gate"""
        if msg:
            fetch = await ctx.send(self.bot.bot_prefix + 'Searching...')
            if msg.startswith('[link]'):
                msg = msg[6:]
                link = True
            else:
                link = False

            found, result = await self.google_results('anime', msg)

            if found:
                anime_id = re.findall('/anime/(.*)/', result)
                try:
                    results = await self.t_client.get_anime(int(anime_id[0]))
                except IndexError:
                    return await ctx.send(self.bot.bot_prefix + 'No results.')
                finally:
                    gc.collect()

            else:
                await ctx.send(self.bot.bot_prefix + 'No results.')
                await fetch.delete()
                return await ctx.message.delete()

            if not embed_perms(ctx.message) or link is True:
                await ctx.send(self.bot.bot_prefix + 'https://myanimelist.net/anime/%s' % results.id)
                await fetch.delete()
                return await ctx.message.delete()

            # Formatting embed
            selection = results
            synopsis = BeautifulSoup(selection.synopsis, 'html.parser')

            em = discord.Embed(description='{}'.format('https://myanimelist.net/anime/%s' % selection.id),
                               colour=0x0066CC)

            try:
                english = selection.english
                if english:
                    em.add_field(name='English Title', value=english, inline=False)
            except:
                pass
            em.add_field(name='Type', value=selection.type)
            episodes = 'Unknown' if selection.episodes == '0' else selection.episodes
            em.add_field(name='Episodes', value=episodes)
            score = '?' if selection.score[0] == 0 else str(selection.score[0]) + '/10'
            em.add_field(name='Score', value=score)
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

            em.add_field(name='Airing Time:', value=selection.air_time)
            em.set_thumbnail(url=selection.image)
            em.set_author(name=selection.title,
                          icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            em.set_footer(text='MyAnimeList Anime Search')

            await ctx.send(embed=em)
            await fetch.delete()
            await ctx.message.delete()
        else:
            await ctx.send(self.bot.bot_prefix + 'Specify an anime to search for.')

    # Manga search for Mal
    @mal.command(pass_context=True)
    async def manga(self, ctx, *, msg: str = None):
        """Search the manga database. Ex: [p]mal manga Boku no Hero Academia"""
        if msg:
            fetch = await ctx.send(self.bot.bot_prefix + 'Searching...')
            if msg.startswith('[link]'):
                msg = msg[6:]
                link = True
            else:
                link = False

            found, result = await self.google_results('manga', msg)

            if found:
                manga_id = re.findall('/manga/(.*)/', result)
                try:
                    results = await self.t_client.get_manga(int(manga_id[0]))
                except IndexError:
                    return await ctx.send(self.bot.bot_prefix + 'No results.')
                gc.collect()

            else:
                await ctx.send(self.bot.bot_prefix + 'No results.')
                await fetch.delete()
                return await ctx.message.delete()

            if not embed_perms(ctx.message) or link is True:
                await ctx.send(self.bot.bot_prefix + 'https://myanimelist.net/manga/%s' % results.id)
                await fetch.delete()
                return await ctx.message.delete()

            # Formatting embed
            selection = results
            synopsis = BeautifulSoup(selection.synopsis, 'html.parser')

            em = discord.Embed(description='{}'.format('https://myanimelist.net/manga/%s' % selection.id),
                               colour=0x0066CC)

            try:
                english = selection.english
                if english:
                    em.add_field(name='English Title', value=english, inline=False)
            except:
                pass
            em.add_field(name='Type', value=selection.type)
            chapters = 'Unknown' if selection.chapters == '0' else selection.chapters
            em.add_field(name='Chapters', value=chapters)
            score = '?' if selection.score[0] == 0 else str(selection.score[0]) + '/10'
            em.add_field(name='Score', value=score)
            em.add_field(name='Status', value=selection.status)
            try:
                synop = synopsis.get_text()[:400].split('.')
                text = ''
                for i in range(0, len(synop)-1):
                    text += synop[i] + '.'
            except:
                text = synopsis.get_text()
            em.add_field(name='Synopsis',
                         value=text + ' [Read more »](https://myanimelist.net/manga/%s)' % selection.id)

            em.add_field(name='Airing Time:', value=selection.publish_time)
            em.set_thumbnail(url=selection.image)
            em.set_author(name=selection.title,
                          icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
            em.set_footer(text='MyAnimeList Manga Search')

            await ctx.send(embed=em)
            await fetch.delete()
            await ctx.message.delete()
        else:
            await ctx.send(self.bot.bot_prefix + 'No results')

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
            return '6 Days {} Hours and {} Minutes.'.format(remaining.seconds // 3600, (remaining.seconds // 60) % 60)
        else:
            return '{} Days {} Hours and {} Minutes.'.format(remaining.days, remaining.seconds // 3600, (remaining.seconds // 60) % 60)

    @mal.command(pass_context=True, alias=['character'])
    async def char(self, ctx, *, query):
        """Finds specified character actor on MyAnimeList"""
        fetch = await ctx.send(self.bot.bot_prefix + 'Searching...')
        found, result = await self.google_results('character', query)
        if found:
            char_id = re.findall('/character/(.*)/', result)
        else:
            await fetch.delete()
            await ctx.message.delete()
            return await ctx.send(self.bot.bot_prefix + 'No results.')
        try:
            selection = await self.t_client.get_character(char_id[0])
        except IndexError:
            return await ctx.send(self.bot.bot_prefix + 'No results.')
        em = discord.Embed(description='{}'.format('https://myanimelist.net/character/%s' % selection.id),
                           colour=0x0066CC)
        em.add_field(name='Anime', value=selection.animeography[0]['name'], inline=False)
        if len(selection.raw_voice_actors) > 1:
            va = None
            for actor in selection.raw_voice_actors:
                if actor['language'] == 'Japanese':
                    va = actor['name']
                    break
            if not va:
                va = selection.raw_voice_actors[0]['name']
        else:
            va = selection.raw_voice_actors[0]['name']
        em.add_field(name='Voice Actor', value=va)
        em.add_field(name='Favorites', value=selection.favorites)
        em.set_image(url=selection.image)
        em.set_author(name=selection.name,
                      icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
        em.set_footer(text='MyAnimeList Character Search')
        await ctx.send(content=None, embed=em)
        await fetch.delete()
        await ctx.message.delete()

    ### Temporarily removed b/c of known issue with mal api
    @mal.command(pass_context=True, alias=['actor', 'voiceactor', 'person', 'voice'])
    async def va(self, ctx, *, query):
        """Finds specified voice actor on MyAnimeList"""
        if query.startswith('[more] '):
            query = query[7:]
            more_info = True
        else:
            more_info = False
        fetch = await ctx.send(self.bot.bot_prefix + 'Searching...')
        found, result = await self.google_results('people', query)
        if found:
            va_id = re.findall('/people/(.*)/', result)
        else:
            await fetch.delete()
            await ctx.message.delete()
            return await ctx.send(self.bot.bot_prefix + 'No results.')

        # No way to get va name so must parse html and grab name from title -_-
        request_headers = {
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "http://thewebsite.com",
            "Connection": "keep-alive"
        }
        loop = asyncio.get_event_loop()
        try:
            req = Request(result, headers=request_headers)
            webpage = await loop.run_in_executor(None, urlopen, req)
        except:
            return await ctx.send(self.bot.bot_prefix + 'Exceeded daily request limit. Try again tomorrow, sorry!')
        soup = BeautifulSoup(webpage, 'html.parser')
        va_name = soup.title.string.split(' - MyAnimeList')[0]

        try:
            selection = await self.t_client.get_person(va_id[0])
        except IndexError:
            return await ctx.send(self.bot.bot_prefix + 'No results.')
        em = discord.Embed(description='{}'.format('https://myanimelist.net/people/%s' % selection.id),
                           colour=0x0066CC)
        em.add_field(name='Favorites', value=selection.favorites)
        if more_info:
            em.add_field(name='Total Roles', value='Fetching...')
            em.add_field(name='Most Popular Role', value='Fetching...', inline=False)
        em.set_image(url=selection.image)
        em.set_author(name=va_name,
                      icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
        em.set_footer(text='MyAnimeList Voice Actor Search')
        va_info = await ctx.send(content=None, embed=em)
        await fetch.delete()
        await ctx.message.delete()

        # get_char on each character in the va role list
        if more_info:
            all_chars = []
            for character in selection.voice_acting:
                id = character['character']['link'].split('/')[2]
                all_chars.append(id)
            print(all_chars)
            try:
                chunk_generator = self.partition(all_chars, int(len(all_chars)/5))
                chunk_list = [chunk for chunk in chunk_generator]
                args = [sys.executable, 'cogs/utils/mal_char_find.py']
                self.bot.mal_finder = []
                for chunk in chunk_list:
                    p = subprocess.Popen(args + chunk, stdout=subprocess.PIPE)
                    self.bot.mal_finder.append(p)

                while all(None is p.poll() for p in self.bot.mal_finder):
                    await asyncio.sleep(1)

                txt = ''
                for p in self.bot.mal_finder:
                    txt += p.communicate()[0].decode('utf-8')
                all_roles = []
                role_list = txt.split('\n')
                for role in role_list:
                    if ' | ' in role:
                        char, favs = role.split(' | ')
                        all_roles.append((char.strip(), int(favs.strip())))
                all_roles = sorted(all_roles, key=lambda x: x[1], reverse=True)
                unique_roles = set(tup[0] for tup in all_roles)
                em.set_field_at(index=1, name='Roles', value=str(len(unique_roles)))
                em.set_field_at(index=2, name='Most Popular Role', value=all_roles[0][0] + '\nFavorites: ' + str(all_roles[0][1]), inline=False)
            except ZeroDivisionError:
                em.set_field_at(index=1, name='Roles', value='None')
                em.set_field_at(index=2, name='Most Popular Role', value='None', inline=False)
            await va_info.edit(content=None, embed=em)

    @mal.command(pass_context=True, name="next")
    async def next_(self, ctx, *, query):
        """Time till next episode air date for specified anime"""
        search = await ctx.send(self.bot.bot_prefix + "Searching...")
        found, result = await self.google_results('anime', query)
        if found:
            anime_id = re.findall('/anime/(.*)/', result)[0]
            try:
                anime = await self.t_client.get_anime(anime_id)
            except Exception as e:
                await ctx.send(self.bot.bot_prefix + ":exclamation: Oops!\n {}: {}".format(type(e).__name__, e))
                await search.delete()
                return await ctx.message.delete()
        else:
            await ctx.send(self.bot.bot_prefix + 'Failed to find given anime.')
            await search.delete()
            return await ctx.message.delete()
        if anime.status == "Finished Airing":
            remaining = "This anime has finished airing!\n" + anime.air_time
        else:
            remaining = await self.get_remaining_time(anime)
        embed = discord.Embed(title=anime.title, color=0x0066CC)
        embed.add_field(name="Next Episode", value=remaining)
        embed.set_footer(text='MyAnimeList Episode Time Search')
        embed.set_author(name='MyAnimeList', icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
        embed.set_thumbnail(url=anime.image)
        await search.delete()
        await ctx.message.delete()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Mal(bot))
