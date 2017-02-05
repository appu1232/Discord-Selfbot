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
                    await self.bot.send_message(ctx.message.channel, isBot + '**Google Search Result:**\n' + result['items'][0]['link'])
                except:
                    await self.bot.send_message(ctx.message.channel, isBot + 'No results.')
                finally:
                    await self.bot.delete_message(fetch)
                    return

            # >g <n> leads to nth result in google results.
            else:
                searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                            ctx.message.content[5:].strip() + "&start=" + '1' + "&key=" + config[
                                'google_api_key'] + "&cx=" + config['custom_search_engine']
                r = requests.get(searchUrl)
                response = r.content.decode('utf-8')
                result = json.loads(response)
                try:
                    await self.bot.send_message(ctx.message.channel, isBot + '**Google Search Result:**\n' + result['items'][int(ctx.message.content[3])]['link'])
                except:
                    await self.bot.send_message(ctx.message.channel, isBot + 'No results.')
                finally:
                    await self.bot.delete_message(fetch)
                    return

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
            try:
                perms = ctx.message.author.permissions_in(ctx.message.channel).attach_files and ctx.message.author.permissions_in(ctx.message.channel).embed_links
            except:
                perms = True
            if perms:
                await self.bot.send_message(ctx.message.channel, content=None,
                                   embed=em.set_image(url=result['items'][0]['link']))
            else:
                await self.bot.send_message(ctx.message.channel, result['items'][0]['link'])

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
            try:
                perms = ctx.message.author.permissions_in(ctx.message.channel).attach_files and ctx.message.author.permissions_in(ctx.message.channel).embed_links
            except:
                perms = True
            if perms:
                await self.bot.send_message(ctx.message.channel, content=None,
                                   embed=em.set_image(url=result['items'][int(ctx.message.content[5])]['link']))
            else:
                await self.bot.send_message(ctx.message.channel, result['items'][int(ctx.message.content[5])]['link'])
        await self.bot.delete_message(fetch)


def setup(bot):
    bot.add_cog(Google(bot))
