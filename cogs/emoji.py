import discord
import requests
import io
import os
import re
from discord.ext import commands

'''Tools relating to custom emoji manipulation and viewing.'''


class Emoji:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, aliases=['emote'], invoke_without_command=True)
    async def emoji(self, ctx, *, msg):
        """
        View, copy, add or remove emoji.
        Usage:
        1) >emoji <emoji> - View a large image of a given emoji. Use >emoji s for additional info.
        2) >emoji copy <emoji> - Copy a custom emoji on another server and add it to the current server if you have the permissions.
        3) >emoji add <url> - Add a new emoji to the current server if you have the permissions.
        4) >emoji remove <emoji> - Remove an emoji from the current server if you have the permissions
        """
        await ctx.message.delete()
        if msg.startswith('s '):
            msg = msg[2:]
            get_guild = True
        else:
            get_guild = False
        msg = re.sub("<:(.+):([0-9]+)>", "\\2", msg)

        match = None
        exact_match = False
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in emoji.name:
                    url = emoji.url
                    emote_name = emoji.name
                if msg.strip() in (str(emoji.id), emoji.name):
                    match = emoji
                    name = "{}.png".format(emoji.name)
                    url = emoji.url
                    exact_match = True
                    break
            if exact_match:
                break

        if not match:
            # Here we check for a stock emoji before returning a failure
            codepoint_regex = re.compile('(\d)?[xuU]0*([a-f\d]*)')
            unicode_raw = msg.encode('unicode-escape').decode('ascii').replace('\\', '')
            codepoints = codepoint_regex.findall(unicode_raw)
            if codepoints == []:
                return await ctx.send(self.bot.bot_prefix + 'Could not find emoji.')
            if codepoints[0][0] == '':
                codepoints = [x[1] for x in codepoints]
                emoji_code = '-'.join(codepoints)
            else:
                emoji_code = "3{}-{}".format(codepoints[0][0], codepoints[0][1])
            url = "https://raw.githubusercontent.com/astronautlevel2/twemoji/gh-pages/128x128/{}.png".format(emoji_code)
            name = "emoji.png"

        response = requests.get(url, stream=True)
        if response.status_code == 404:
            return await ctx.send(self.bot.bot_prefix + "Emoji not available. Open an issue on <https://github.com/astronautlevel2/twemoji> with the name of the missing emoji")

        img = io.BytesIO()
        for block in response.iter_content(1024):
            if not block:
                break
            img.write(block)
        img.seek(0)

        if ctx.channel.permissions_for(ctx.author).attach_files:
            if get_guild:
                await ctx.send('**ID:** {}\n**Server:** {}'.format(str(emoji.id), guild.name))
            await ctx.send(file=discord.File(img, name))
        elif ctx.channel.permissions_for(ctx.author).embed_links:
            await ctx.send(emoji.url)
        else:
            await ctx.send(self.bot.bot_prefix + "Cannot send emoji.")
        img.close()

    @emoji.command(pass_context=True, aliases=["steal"])
    @commands.has_permissions(manage_emojis=True)
    async def copy(self, ctx, *, msg):
        await ctx.message.delete()
        msg = re.sub("<:(.+):([0-9]+)>", "\\2", msg)

        match = None
        exact_match = False
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in str(emoji):
                    match = emoji
                if msg.strip() in (str(emoji.id), emoji.name):
                    match = emoji
                    exact_match = True
                    break
            if exact_match:
                break

        if not match:
            return await ctx.send(self.bot.bot_prefix + 'Could not find emoji.')

        response = requests.get(match.url)
        emoji = await ctx.guild.create_custom_emoji(name=match.name, image=response.content)
        await ctx.send(self.bot.bot_prefix + "Successfully added the emoji {0.name} <:{0.name}:{0.id}>!".format(emoji))

    @emoji.command(pass_context=True)
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, name, url):
        await ctx.message.delete()
        try:
            response = requests.get(url)
        except (requests.errors.MissingSchema, requests.errors.InvalidURL, requests.errors.InvalidSchema):
            return await ctx.send(self.bot.bot_prefix + "The URL you have provided is invalid.")
        if response.status_code == 404:
            return await ctx.send(self.bot.bot_prefix + "The URL you have provided leads to a 404.")
        elif url[-3:] not in ("png", "jpg") and url[-4:] != "jpeg":
            return await ctx.send(self.bot.bot_prefix + "Only PNG and JPEG format images work to add as emoji.")
        emoji = await ctx.guild.create_custom_emoji(name=name, image=response.content)
        await ctx.send(self.bot.bot_prefix + "Successfully added the emoji {0.name} <:{0.name}:{0.id}>!".format(emoji))

    @emoji.command(pass_context=True)
    @commands.has_permissions(manage_emojis=True)
    async def remove(self, ctx, name):
        await ctx.message.delete()
        emotes = [x for x in ctx.guild.emojis if x.name == name]
        emote_length = len(emotes)
        if not emotes:
            return await ctx.send(self.bot.bot_prefix + "No emotes with that name could be found on this server.")
        for emote in emotes:
            await emote.delete()
        if emote_length == 1:
            await ctx.send(self.bot.bot_prefix + "Successfully removed the {} emoji!".format(name))
        else:
            await ctx.send(self.bot.bot_prefix + "Successfully removed {} emoji with the name {}.".format(emote_length, name))


def setup(bot):
    bot.add_cog(Emoji(bot))
