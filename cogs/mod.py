import discord
import asyncio
from discord.ext import commands
from appuselfbot import bot_prefix
from cogs.utils.checks import *


'''Module for moderator commands.'''


class Mod:

    def __init__(self, bot):
        self.bot = bot

    def are_overwrites_empty(self, overwrites):
        """There is currently no cleaner way to check if a
        PermissionOverwrite object is empty"""
        original = [p for p in iter(overwrites)]
        empty = [p for p in iter(discord.PermissionOverwrite())]
        return original == empty

    @commands.command(pass_context=True)
    async def kick(self, ctx, *, user: str):
        """Kicks a user (if you have the permission)."""
        user = get_user(ctx.message, user)
        if user:
            try:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Kicked user: %s' % user.mention)
                await self.bot.kick(user)
            except discord.HTTPException:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Could not kick user. Not enough permissions.')
        else:
            return await self.bot.edit_message(ctx.message, bot_prefix + 'Could not find user.')

    @commands.command(pass_context=True)
    async def ban(self, ctx, *, user: str):
        """Bans a user (if you have the permission)."""
        user = get_user(ctx.message, user)
        if user:
            try:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Banned user: %s' % user.mention)
                await self.bot.ban(user)
            except discord.HTTPException:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Could not ban user. Not enough permissions.')
        else:
            return await self.bot.edit_message(ctx.message, bot_prefix + 'Could not find user.')

    @commands.command(aliases=['sban'], pass_context=True)
    async def softban(self, ctx, *, user: str):
        """Softbans a user (if you have the permission)."""
        user = get_user(ctx.message, user)
        if user:
            try:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Softbanned user: %s' % user.mention)
                await self.bot.ban(user)
                await self.bot.unban(ctx.message.server, user)
            except discord.HTTPException:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Could not softban user. Not enough permissions.')
        else:
            return await self.bot.edit_message(ctx.message, bot_prefix + 'Could not find user.')

    @commands.group(pass_context=True, no_pm=True)
    async def mute(self, ctx, *, user: str):
        """Chat mutes a user (if you have the permission)."""
        if ctx.invoked_subcommand is None:
            user = get_user(ctx.message, user)
            if user:
                for channel in ctx.message.server.channels:
                    if channel.type != discord.ChannelType.text:
                        continue
                    overwrites = channel.overwrites_for(user)
                    overwrites.send_messages = False
                    try:
                        await self.bot.edit_channel_permissions(channel, user, overwrites)
                    except discord.Forbidden:
                        return await self.bot.edit_message(ctx.message, bot_prefix + 'Unable to mute user. Not enough permissions.')
                await self.bot.edit_message(ctx.message, bot_prefix + 'Muted user: %s' % user.mention)
            else:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Could not find user.')

    @mute.command(pass_context=True, no_pm=True)
    async def channel(self, ctx, *, user: str):
        user = get_user(ctx.message, user)
        if user:
            overwrites = ctx.message.channel.overwrites_for(user)
            overwrites.send_messages = False
            try:
                await self.bot.edit_channel_permissions(ctx.message.channel, user, overwrites)
                await self.bot.edit_message(ctx.message, bot_prefix + 'Muted user in this channel: %s' % user.mention)
            except discord.Forbidden:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Unable to mute user. Not enough permissions.')
        else:
            await self.bot.edit_message(ctx.message, bot_prefix + 'Could not find user.')

    @commands.group(pass_context=True, no_pm=True)
    async def unmute(self, ctx, *, user: str):
        """Unmutes a user (if you have the permission)."""
        if ctx.invoked_subcommand is None:
            user = get_user(ctx.message, user)
            if user:
                for channel in ctx.message.server.channels:
                    if channel.type != discord.ChannelType.text:
                        continue
                    overwrites = channel.overwrites_for(user)
                    overwrites.send_messages = None
                    is_empty = self.are_overwrites_empty(overwrites)
                    try:
                        if not is_empty:
                            await self.bot.edit_channel_permissions(channel, user, overwrites)
                        else:
                            await self.bot.delete_channel_permissions(channel, user)
                        await self.bot.edit_channel_permissions(channel, user, overwrites)
                    except discord.Forbidden:
                        return await self.bot.edit_message(ctx.message, bot_prefix + 'Unable to unmute user. Not enough permissions.')
                await self.bot.edit_message(ctx.message, bot_prefix + 'Unmuted user: %s' % user.mention)
            else:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Could not find user.')

    @unmute.command(pass_context=True, no_pm=True)
    async def channel(self, ctx, *, user: str):
        user = get_user(ctx.message, user)
        if user:
            overwrites = ctx.message.channel.overwrites_for(user)
            is_empty = self.are_overwrites_empty(overwrites)
            try:
                if not is_empty:
                    await self.bot.edit_channel_permissions(ctx.message.channel, user, overwrites)
                else:
                    await self.bot.delete_channel_permissions(ctx.message.channel, user)
                await self.bot.edit_channel_permissions(ctx.message.channel, user, overwrites)
                await self.bot.edit_message(ctx.message, bot_prefix + 'Unmuted user in this channel: %s' % user.mention)
            except discord.Forbidden:
                await self.bot.edit_message(ctx.message, bot_prefix + 'Unable to unmute user. Not enough permissions.')
        else:
            await self.bot.edit_message(ctx.message, bot_prefix + 'Could not find user.')

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['p'], pass_context=True, no_pm=True)
    async def purge(self, ctx, msgs: int, *, txt=None):
        """Purge last n msgs or n msgs with a word. >help purge for more info.
        
        Ex:
        
        >purge 20 - deletes the last 20 messages in a channel sent by anyone.
        >purge 20 stuff - deletes any messages in the last 20 messages that contains the word 'stuff'."""
        await self.bot.delete_message(ctx.message)
        if msgs < 10000:
            async for message in self.bot.logs_from(ctx.message.channel, limit=msgs):
                try:
                    if txt:
                        if txt.lower() in message.content.lower():
                            await self.bot.delete_message(message)
                    else:
                        await self.bot.delete_message(message)
                except:
                    pass
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Too many messages to delete. Enter a number < 10000')


def setup(bot):
    bot.add_cog(Mod(bot))