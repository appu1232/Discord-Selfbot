import discord
from appuselfbot import bot_prefix
from discord.ext import commands
from cogs.utils.checks import *

'''Module for the >info command.'''

class Userinfo:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def info(self, ctx):
        """Get user info. Ex: >info @user"""
        if ctx.invoked_subcommand is None:
            pre = cmd_prefix_len()
            name = ctx.message.content[4 + pre:].strip()
            if name:
                try:
                    user = ctx.message.mentions[0]
                except:
                    user = ctx.message.server.get_member_named(name)
                if not user:
                    user = ctx.message.server.get_member(name)
                if not user:
                    await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find user.')
                    return
            else:
                user = ctx.message.author

            # Thanks to IgneelDxD for help on this
            if user.avatar_url[60:].startswith('a_'):
                avi = 'https://images.discordapp.net/avatars/' + user.avatar_url[33:][:18] + user.avatar_url[59:-3] + 'gif'
            else:
                avi = user.avatar_url

            if embed_perms(ctx.message):
                em = discord.Embed(timestamp=ctx.message.timestamp, colour=0x708DD0)
                em.add_field(name='User ID', value=user.id, inline=True)
                em.add_field(name='Nick', value=user.nick, inline=True)
                em.add_field(name='Status', value=user.status, inline=True)
                em.add_field(name='In Voice', value=user.voice_channel, inline=True)
                em.add_field(name='Account Created', value=user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.add_field(name='Join Date', value=user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.set_thumbnail(url=avi)
                em.set_author(name=user, icon_url='https://i.imgur.com/RHagTDg.png')
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                msg = '**User Info:** ```User ID: %s\nNick: %s\nStatus: %s\nIn Voice: %s\nAccount Created: %s\nJoin Date: %s\nAvatar url:%s```' % (user.id, user.nick, user.status, user.voice_channel, user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), avi)
                await self.bot.send_message(ctx.message.channel, bot_prefix + msg)

            await self.bot.delete_message(ctx.message)

    @info.command(pass_context=True)
    async def avi(self, ctx, txt: str = None):
        """View bigger version of user's avatar. Ex: >info avi @user"""
        if txt:
            try:
                user = ctx.message.mentions[0]
            except:
                user = ctx.message.server.get_member_named(txt)
            if not user:
                user = ctx.message.server.get_member(txt)
            if not user:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find user.')
                return
        else:
            user = ctx.message.author

        # Thanks to IgneelDxD for help on this
        if user.avatar_url[60:].startswith('a_'):
            avi = 'https://images.discordapp.net/avatars/' + user.avatar_url[33:][:18] + user.avatar_url[59:-3] + 'gif'
        else:
            avi = user.avatar_url
        if embed_perms(ctx.message):
            em = discord.Embed(colour=0x708DD0)
            em.set_image(url=avi)
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + avi)
        await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(Userinfo(bot))
