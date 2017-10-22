import discord
from discord.ext import commands
from cogs.utils.checks import get_user


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
    async def kick(self, ctx, user, *, reason=""):
        """Kicks a user (if you have the permission)."""
        user = get_user(ctx.message, user)
        if user:
            try:
                await user.kick(reason=reason)
                return_msg = "Kicked user `{}`".format(user.mention)
                if reason:
                    return_msg += " for reason `{}`".format(reason)
                return_msg += "."
                await ctx.message.edit(content=self.bot.bot_prefix + return_msg)
            except discord.Forbidden:
                await ctx.message.edit(content=self.bot.bot_prefix + 'Could not kick user. Not enough permissions.')
        else:
            return await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user.')

    @commands.command(pass_context=True)
    async def ban(self, ctx, user, *, reason=""):
        """Bans a user (if you have the permission)."""
        user = get_user(ctx.message, user)
        if user:
            try:
                await user.ban(reason=reason)
                return_msg = "Banned user `{}`".format(user.mention)
                if reason:
                    return_msg += " for reason `{}`".format(reason)
                return_msg += "."
                await ctx.message.edit(content=self.bot.bot_prefix + return_msg)
            except discord.Forbidden:
                await ctx.message.edit(content=self.bot.bot_prefix + 'Could not ban user. Not enough permissions.')
        else:
            return await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user.')

    @commands.command(aliases=['sban'], pass_context=True)
    async def softban(self, ctx, user, *, reason=""):
        """Bans and unbans a user (if you have the permission)."""
        user = get_user(ctx.message, user)
        if user:
            try:
                await user.ban(reason=reason)
                await ctx.guild.unban(user)
                return_msg = "Banned and unbanned user `{}`".format(user.mention)
                if reason:
                    return_msg += " for reason `{}`".format(reason)
                return_msg += "."
                await ctx.message.edit(content=self.bot.bot_prefix + return_msg)
            except discord.Forbidden:
                await ctx.message.edit(content=self.bot.bot_prefix + 'Could not softban user. Not enough permissions.')
        else:
            return await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user.')

    @commands.group(pass_context=True, no_pm=True)
    async def mute(self, ctx, *, user: str):
        """Chat mutes a user (if you have the permission)."""
        if ctx.invoked_subcommand is None:
            user = get_user(ctx.message, user)
            if user and user != self.bot.user:
                failed = []
                channel_length = 0
                for channel in ctx.message.guild.channels:
                    if type(channel) != discord.channel.TextChannel:
                        continue
                    overwrites = channel.overwrites_for(user)
                    overwrites.send_messages = False
                    channel_length += 1
                    try:
                        await channel.set_permissions(user, overwrite=overwrites)
                    except discord.Forbidden:
                        failed.append(channel)
                if failed and len(failed) < channel_length:
                    await ctx.message.edit(content=self.bot.bot_prefix + "Muted user in {}/{} channels: {}".format(channel_length - len(failed), channel_length, user.mention))
                elif failed:
                    await ctx.message.edit(content=self.bot.bot_prefix + "Failed to mute user. Not enough permissions.")
                else:
                    await ctx.message.edit(content=self.bot.bot_prefix + 'Muted user: %s' % user.mention)
            else:
                await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user.')

    @mute.command(pass_context=True, no_pm=True)
    async def channel(self, ctx, *, user: str):
        user = get_user(ctx.message, user)
        if user:
            overwrites = ctx.message.channel.overwrites_for(user)
            overwrites.send_messages = False
            try:
                ctx.message.channel.set_permissions(user, overwrite=overwrites)
                await ctx.message.edit(content=self.bot.bot_prefix + 'Muted user in this channel: %s' % user.mention)
            except discord.Forbidden:
                await ctx.message.edit(content=self.bot.bot_prefix + 'Unable to mute user. Not enough permissions.')
        else:
            await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user.')

    @commands.group(pass_context=True, no_pm=True)
    async def unmute(self, ctx, *, user: str):
        """Unmutes a user (if you have the permission)."""
        if ctx.invoked_subcommand is None:
            user = get_user(ctx.message, user)
            if user:
                failed = []
                channel_length = 0
                for channel in ctx.message.guild.channels:
                    if type(channel) != discord.channel.TextChannel:
                        continue
                    overwrites = channel.overwrites_for(user)
                    overwrites.send_messages = None
                    channel_length += 1
                    is_empty = self.are_overwrites_empty(overwrites)
                    try:
                        if not is_empty:
                            await channel.set_permissions(user, overwrite=overwrites)
                        else:
                            await channel.set_permissions(user, overwrite=None)
                        await channel.set_permissions(user, overwrite=overwrites)
                    except discord.Forbidden:
                        failed.append(channel)
                if failed and len(failed) < channel_length:
                    await ctx.message.edit(content=self.bot.bot_prefix + "Unmuted user in {}/{} channels: {}".format(channel_length - len(failed), channel_length, user.mention))
                elif failed:
                    await ctx.message.edit(content=self.bot.bot_prefix + "Failed to unmute user. Not enough permissions.")
                else:
                    await ctx.message.edit(content=self.bot.bot_prefix + 'Unmuted user: %s' % user.mention)
            else:
                await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user.')

    @unmute.command(pass_context=True, no_pm=True)
    async def channel(self, ctx, *, user: str):
        user = get_user(ctx.message, user)
        if user:
            overwrites = ctx.message.channel.overwrites_for(user)
            is_empty = self.are_overwrites_empty(overwrites)
            try:
                if not is_empty:
                    ctx.message.channel.set_permissions(user, overwrite=overwrites)
                else:
                    await channel.set_permissions(user, overwrite=None)
                await channel.set_permissions(user, overwrite=overwrites)
                await ctx.message.edit(content=self.bot.bot_prefix + 'Unmuted user in this channel: %s' % user.mention)
            except discord.Forbidden:
                await ctx.message.edit(content=self.bot.bot_prefix + 'Unable to unmute user. Not enough permissions.')
        else:
            await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user.')

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['p'], pass_context=True, no_pm=True)
    async def purge(self, ctx, msgs: int, *, txt=None):
        """Purge last n msgs or n msgs with a word. [p]help purge for more info.
        
        Ex:
        
        [p]purge 20 - deletes the last 20 messages in a channel sent by anyone.
        [p]purge 20 stuff - deletes any messages in the last 20 messages that contains the word 'stuff'."""
        await ctx.message.delete()
        if msgs < 10000:
            async for message in ctx.message.channel.history(limit=msgs):
                try:
                    if txt:
                        if txt.lower() in message.content.lower():
                            await message.delete()
                    else:
                        await message.delete()
                except:
                    pass
        else:
            await ctx.send(self.bot.bot_prefix + 'Too many messages to delete. Enter a number < 10000')


def setup(bot):
    bot.add_cog(Mod(bot))
