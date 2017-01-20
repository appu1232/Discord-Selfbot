import discord
import requests
import json
import urllib
from discord.ext import commands
from appuselfbot import isBot, load_config


class Google:

    def __init__(self, bot):
        self.bot = bot

    # Google search
    @commands.group(pass_context=True)
    async def g(self, ctx):
        # If >g then google web search with specified words
        config = load_config()
        if ctx.invoked_subcommand is None:
            fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Searching...')
            if not ctx.message.content[3].isdigit():
                searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                            ctx.message.content[
                            3:].strip() + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config[
                                'custom_search_engine']
                r = requests.get(searchUrl)
                response = r.content.decode('utf-8')
                result = json.loads(response)
                try:
                    webpage = urllib.request.urlopen(result['items'][0]['link']).read()
                except:
                    await self.bot.send_message(ctx.message.channel, isBot + 'No results.')
                    return
                try:
                    title = str(webpage).split('<title>')[1].split('</title>')[0]
                except:
                    title = ''
                em = discord.Embed(title=result['items'][0]['link'], description=title, colour=0x2D5AF9)
                em.set_author(name='Google Results:\n\n')
                await self.bot.send_message(ctx.message.channel, embed=em)

            # >g <n> leads to nth result in google results.
            else:
                searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                            ctx.message.content[5:].strip() + "&start=" + '1' + "&key=" + config[
                                'google_api_key'] + "&cx=" + config['custom_search_engine']
                r = requests.get(searchUrl)
                response = r.content.decode('utf-8')
                result = json.loads(response)
                try:
                    webpage = urllib.request.urlopen(result['items'][int(ctx.message.content[3])]['link']).read()
                except:
                    await self.bot.send_message(ctx.message.channel, isBot + 'No results.')
                    return
                try:
                    title = str(webpage).split('<title>')[1].split('</title>')[0]
                except:
                    title = ''
                em = discord.Embed(title=result['items'][int(ctx.message.content[3])]['link'], description=title,
                                   colour=0x2D5AF9)
                em.set_author(name='Google Results:\n\n')
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.delete_message(fetch)

    @g.command(pass_context=True)
    async def i(self, ctx):
        # If >g i then google image search with specified words
        fetch = await self.bot.send_message(ctx.message.channel, isBot + 'Searching...')
        config = load_config()
        if not ctx.message.content[5].isdigit():
            searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                        ctx.message.content[
                        5:].strip() + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config[
                            'custom_search_engine'] + \
                        "&searchType=image"
            r = requests.get(searchUrl)
            response = r.content.decode('utf-8')
            result = json.loads(response)

            # Send as embed
            em = discord.Embed()
            await self.bot.send_message(ctx.message.channel, content=None,
                                   embed=em.set_image(url=result['items'][0]['link']))

        # >g i <n> leads to nth result in google image results.
        else:
            searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                        ctx.message.content[
                        7:].strip() + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config[
                            'custom_search_engine'] + \
                        "&searchType=image"
            r = requests.get(searchUrl)
            response = r.content.decode('utf-8')
            result = json.loads(response)

            # Send as embed
            em = discord.Embed()
            await self.bot.send_message(ctx.message.channel, content=None,
                                   embed=em.set_image(url=result['items'][int(ctx.message.content[5])]['link']))
        await self.bot.delete_message(fetch)


def setup(bot):
    bot.add_cog(Google(bot))
