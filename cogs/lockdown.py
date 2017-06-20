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
        self.states = []

    @commands.has_permissions(manage_channels=True)
    @commands.command(pass_context=True, name="lockdown")
    async def lockdown(self, ctx):
       """Lock message sending in the channel. Staff only."""
       try:
            print(self.states)
            try:
                mod_strings = load_moderation()
                mod_role_strings = mod_strings[ctx.message.server.name]
                mod_roles = []
                for m in mod_role_strings:
                    mod_roles.append(discord.utils.get(ctx.message.server.roles, name=m))
            except:
                mod_roles = []
            server = ctx.message.server
            overwrites_everyone = ctx.message.channel.overwrites_for(server.default_role)
            overwrites_owner = ctx.message.channel.overwrites_for(server.role_hierarchy[0])
            if len(self.states) > 0:
                await self.bot.say("🔒 Channel is already locked down. Use `unlock` to unlock.")
                return
            for a in ctx.message.server.role_hierarchy:
                self.states.append([a, ctx.message.channel.overwrites_for(a).send_messages])
            print(self.states)
            overwrites_owner.send_messages = True
            overwrites_everyone.send_messages = False
            await self.bot.edit_channel_permissions(ctx.message.channel, server.default_role, overwrites_everyone)
            for modrole in mod_roles:
                await self.bot.edit_channel_permissions(ctx.message.channel, modrole, overwrites_owner)
            try:
                await self.bot.edit_channel_permissions(ctx.message.channel, server.get_member("135204578986557440"), overwrites_owner)
            except:
                print("If you have any issues with this feature, let 'thecommondude' know about it in Appu's Discord Server")
            await self.bot.say("🔒 Channel locked down. Only roles with permissions specified in `moderation.json` can speak.")
       except discord.errors.Forbidden:
            await self.bot.say("Missing Permissions.")

    @commands.has_permissions(manage_channels=True)
    @commands.command(pass_context=True, name="unlock")
    async def unlock(self, ctx):
       """Unlock message sending in the channel. Staff only."""
       try:
            server = ctx.message.server
            if self.states == []:
                await self.bot.say("🔓 Channel is already unlocked.")
                return
            for a in self.states:
                overwrites_a = ctx.message.channel.overwrites_for(a[0])
                overwrites_a.send_messages = a[1]
                await self.bot.edit_channel_permissions(ctx.message.channel, a[0], overwrites_a)
            self.states = []
            await self.bot.say("🔓 Channel unlocked.")
       except discord.errors.Forbidden:
            await self.bot.say("Missing Permissions.")

def setup(bot):
    bot.add_cog(Lockdown(bot))
