import requests
import discord
import json
import codecs
from urllib import parse
from bs4 import BeautifulSoup
from discord.ext import commands


'''Translator cog - Love Archit & Lyric'''


class Translate:

    def __init__(self, bot):
        self.bot = bot

    # Thanks to lyric for helping me in making this possible. You are not so bad afterall :] ~~jk~~
    @commands.command(pass_context=True)
    async def translate(self, ctx, to_language, *, msg):
        """Translates words from one language to another. Do >help translate for more information.
        Usage:
        >translate <new language> <words> - Translate words from one language to another. Full language names must be used.
        The original language will be assumed automatically.
        """
        await ctx.message.delete()
        if to_language == "rot13":  # little easter egg
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name="Original", value=msg, inline=False)
            embed.add_field(name="ROT13", value=codecs.encode(msg, "rot_13"), inline=False)
            return await ctx.send("", embed=embed)
        codes = requests.get("http://lyricly.tk/langs.json").text
        lang_codes = json.loads(codes)
        real_language = False
        to_language = to_language.lower()
        for entry in lang_codes:
            if to_language in lang_codes[entry]["name"].replace(";", "").replace(",", "").lower().split():
                language = lang_codes[entry]["name"].replace(";", "").replace(",", "").split()[0]
                to_language = entry
                real_language = True
        if real_language:
            translate = requests.get("https://translate.google.com/m?hl={}&sl=auto&q={}".format(to_language, msg)).text
            result = str(translate).split('class="t0">')[1].split("</div>")[0]
            result = BeautifulSoup(result, "lxml").text
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name="Original", value=msg, inline=False)
            embed.add_field(name=language, value=result.replace("&amp;", "&"), inline=False)
            if result == msg:
                embed.add_field(name="Warning", value="This language may not be supported by Google Translate.")
            await ctx.send("", embed=embed)
        else:
            await ctx.send(self.bot.bot_prefix + "That's not a real language.")


def setup(bot):
    bot.add_cog(Translate(bot))
