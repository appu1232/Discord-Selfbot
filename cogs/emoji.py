import discord
import requests
import io
import re
from discord.ext import commands

'''Tools relating to custom emoji manipulation and viewing.'''


class Emoji:

    def __init__(self, bot):
        self.bot = bot

    def find_emoji(self, msg):
        msg = re.sub("<:(.+):([0-9]+)>", "\\2", msg)
        color_modifiers = ["1f3fb", "1f3fc", "1f3fd", "1f44c", "1f3fe", "1f3ff"]  # These color modifiers aren't in Twemoji

        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in emoji.name:
                    url = emoji.url
                    emote_name = emoji.name
                if msg.strip() in (str(emoji.id), emoji.name):
                    name = "{}.png".format(emoji.name)
                    url = emoji.url
                    return name, url, emoji.id, guild.name

        # Here we check for a stock emoji before returning a failure
        codepoint_regex = re.compile('([\d#])?\\\\[xuU]0*([a-f\d]*)')
        unicode_raw = msg.encode('unicode-escape').decode('ascii')
        codepoints = codepoint_regex.findall(unicode_raw)
        if codepoints == []:
            return "", "", "", ""

        if len(codepoints) > 1 and codepoints[1][1] in color_modifiers:
            codepoints.pop(1)

        if codepoints[0][0] == '#':
            emoji_code = '23-20e3'
        elif codepoints[0][0] == '':
            codepoints = [x[1] for x in codepoints]
            emoji_code = '-'.join(codepoints)
        else:
            emoji_code = "3{}-{}".format(codepoints[0][0], codepoints[0][1])
        url = "https://raw.githubusercontent.com/astronautlevel2/twemoji/gh-pages/128x128/{}.png".format(emoji_code)
        name = "emoji.png"
        return name, url, "N/A", "Official"

    @commands.group(pass_context=True, aliases=['emote'], invoke_without_command=True)
    async def emoji(self, ctx, *, msg):
        """
        View, copy, add or remove emoji.
        Usage:
        1) [p]emoji <emoji> - View a large image of a given emoji. Use [p]emoji s for additional info.
        2) [p]emoji copy <emoji> - Copy a custom emoji on another server and add it to the current server if you have the permissions.
        3) [p]emoji add <url> - Add a new emoji to the current server if you have the permissions.
        4) [p]emoji remove <emoji> - Remove an emoji from the current server if you have the permissions
        """
        await ctx.message.delete()
        emojis = msg.split()
        if msg.startswith('s '):
            emojis = emojis[1:]
            get_guild = True
        else:
            get_guild = False

        if len(emojis) > 5:
            return await ctx.send(self.bot.bot_prefix + "Maximum of 5 emojis at a time.")

        images = []
        for emoji in emojis:
            name, url, id, guild = self.find_emoji(emoji)
            if url == "":
                await ctx.send(self.bot.bot_prefix + "Could not find {} emoji. Skipping.".format(emoji))
                continue
            response = requests.get(url, stream=True)
            if response.status_code == 404:
                await ctx.send(self.bot.bot_prefix + "Emoji {} not available. Open an issue on <https://github.com/astronautlevel2/twemoji> with the name of the missing emoji".format(emoji))
                continue

            img = io.BytesIO()
            for block in response.iter_content(1024):
                if not block:
                    break
                img.write(block)
            img.seek(0)
            images.append((guild, str(id), url, discord.File(img, name)))

        for (guild, id, url, file) in images:
            if ctx.channel.permissions_for(ctx.author).attach_files:
                if get_guild:
                    await ctx.send(content='**ID:** {}\n**Server:** {}'.format(id, guild), file=file)
                else:
                    await ctx.send(file=file)
            else:
                if get_guild:
                    await ctx.send('**ID:** {}\n**Server:** {}\n**URL: {}**'.format(id, guild, url))
                else:
                    await ctx.end(url)
            file.close()

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
