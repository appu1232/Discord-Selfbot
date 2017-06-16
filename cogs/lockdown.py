#Importing libraries
import discord
from discord.ext import commands
from cogs.utils.checks import *
from sys import argv

class Lockdown:
    """
    Channel lockdown commands.

    To give specific roles permissions to bypass lockdown, open `moderation.json` file in the settings folder 
    make an entry of the server name as the key
    make an entry of the list of role names as the value
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="lockdown")
    async def lockdown(self, ctx):
       """Lock message sending in the channel. Staff only."""
       try:
            mod_strings = load_moderation()
            mod_role_strings = mod_strings[ctx.message.server.name]
            mod_roles = []
            for m in mod_role_strings:
                mod_roles.append(discord.utils.get(ctx.message.server.roles, name=m))
            server = ctx.message.server
            overwrites_everyone = ctx.message.channel.overwrites_for(server.default_role)
            overwrites_owner = ctx.message.channel.overwrites_for(server.role_hierarchy[0])
            if overwrites_everyone.send_messages is False:
                await self.bot.say("🔒 Channel is already locked down. Use `unlock` to unlock.")
                return
            overwrites_owner.send_messages = True
            overwrites_everyone.send_messages = False
            await self.bot.edit_channel_permissions(ctx.message.channel, server.default_role, overwrites_everyone)
            for modrole in mod_roles:
                await self.bot.edit_channel_permissions(ctx.message.channel, modrole, overwrites_owner)
            await self.bot.say("🔒 Channel locked down. Only roles with permissions specified in `moderation.json` can speak.")
       except discord.errors.Forbidden:
            await self.bot.say("Missing Permissions.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unlock")
    async def unlock(self, ctx):
       """Unlock message sending in the channel. Staff only."""
       try:
            server = ctx.message.server
            overwrites_everyone = ctx.message.channel.overwrites_for(server.default_role)
            if overwrites_everyone.send_messages is None:
                await self.bot.say("🔓 Channel is already unlocked.")
                return
            overwrites_everyone.send_messages = None
            await self.bot.edit_channel_permissions(ctx.message.channel, server.default_role, overwrites_everyone)
            await self.bot.say("🔓 Channel unlocked.")
       except discord.errors.Forbidden:
            await self.bot.say("Missing Permissions.")

def setup(bot):
    bot.add_cog(Lockdown(bot))
