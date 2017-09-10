import discord
import requests
import os
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
        msg = msg.strip(':')
        if msg.startswith('<'):
            msg = msg[2:].split(':', 1)[0].strip()
        url = emoji = guild = None
        exact_match = False
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in str(emoji):
                    url = emoji.url
                    emote_name = emoji.name
                if msg.strip() == str(emoji).split(':')[1]:
                    url = emoji.url
                    emote_name = emoji.name
                    exact_match = True
                    break
            if exact_match:
                break
        response = requests.get(emoji.url, stream=True)
        name = emoji.url.split('/')[-1]
        with open(name, 'wb') as img:

            for block in response.iter_content(1024):
                if not block:
                    break

                img.write(block)

        if ctx.channel.permissions_for(ctx.author).attach_files and url:
            if get_guild:
                await ctx.send('**ID:** {}\n**Server:** {}'.format(str(emoji.id), guild.name))
            with open(name, 'rb') as fp:
                await ctx.send(file=discord.File(fp))
            os.remove(name)
        elif not ctx.channel.permissions_for(ctx.author).embed_links and url:
            await ctx.send(url)
        else:
            await ctx.send(self.bot.bot_prefix + 'Could not find emoji.')
            
    @emoji.command(pass_context=True, aliases=["steal"])
    @commands.has_permissions(manage_emojis=True)
    async def copy(self, ctx, *, msg):
        await ctx.message.delete()
        if msg.startswith('s '):
            msg = msg[2:]
            get_guild = True
        else:
            get_guild = False
        msg = msg.strip(':')
        if msg.startswith('<'):
            msg = msg[2:].split(':', 1)[0].strip()
        url = emoji = guild = None
        exact_match = False
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in str(emoji):
                    url = emoji.url
                    emote_name = emoji.name
                if msg.strip() == str(emoji).split(':')[1]:
                    url = emoji.url
                    emote_name = emoji.name
                    exact_match = True
                    break
            if exact_match:
                break
        if not url:
            return await ctx.send(self.bot.bot_prefix + 'Could not find emoji.')
        response = requests.get(emoji.url)
        emoji = await ctx.guild.create_custom_emoji(name=emoji.name, image=response.content)
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
