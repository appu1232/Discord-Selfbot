import requests
import json
import discord
import prettytable
import string
from urllib import parse
from PythonGists import PythonGists
from appuselfbot import bot_prefix
from discord.ext import commands
from cogs.utils.checks import *

'''Urban dictionary discord.py scraper written by Archit Date.'''


class Urban:

    def __init__(self, bot):
        self.bot = bot

    # Urban dictionary
    @commands.command(pass_context=True)
    async def ud(self, ctx, *, msg):
        """Pull data from Urban Dictionary. Use >help ud for more information.
        Usage: >ud <term> - Search for a term on Urban Dictionary. 
        You can pick a specific result to use with >ud <term> | <result>.
        If no result is specified, the first result will be used.
        """
        number = 1
        if " | " in msg:
            msg, number = msg.rsplit(" | ", 1)
        search = ""
        search = parse.quote(msg)
        response = requests.get("http://api.urbandictionary.com/v0/define?term={}".format(search)).text
        result = json.loads(response)
        if result["result_type"] == "no_results":
            await self.bot.say(bot_prefix + "{} couldn't be found on Urban Dictionary.".format(msg))
        else:
            try:
                top_result = result["list"][int(number)-1]
                embed = discord.Embed(title=top_result["word"], description=top_result["definition"], url=top_result["permalink"])
                embed.add_field(name="Example:", value=top_result["example"])
                embed.add_field(name="Tags:", value=" ".join(result["tags"]))
                embed.set_author(name=top_result["author"], icon_url="https://lh5.ggpht.com/oJ67p2f1o35dzQQ9fVMdGRtA7jKQdxUFSQ7vYstyqTp-Xh-H5BAN4T5_abmev3kz55GH=w300")          
                number = str(int(number)+1)
                embed.set_footer(text="{} results were found. To see a different result, use >ud {} | {}.".format(len(result["list"]), msg, number))
                await self.bot.say("", embed=embed)
            except IndexError:
                await self.bot.say(bot_prefix + "That result doesn't exist! Try >ud {}.".format(msg))
def setup(bot):
    bot.add_cog(Urban(bot))
