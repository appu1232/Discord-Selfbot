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

    @commands.group(pass_context=True)
    async def mod(self, ctx):
        """Manage list of moderator roles for the >lockdown command. >help mod for more info.
        >mod - List your moderator roles that you have set.
        >mod add <server> <role> - Add a role to the list of moderators on a server.
        >mod remove <server> <role> - Remove a role from the list of moderators on a server.
        If a server or role name has spaces in it, you must enclose *both* of them in quotes, no matter which one is the one with spaces in it.
        """
        if ctx.invoked_subcommand is None:
            await self.bot.delete_message(ctx.message)
            mods = load_moderation()
            embed = discord.Embed(title="Moderator Roles", description="")
            for server in mods:
                embed.description += server + ":\n"
                for mod in mods["server"]:
                    embed.description += "    {}\n".format(mod)
            await self.bot.send_message(ctx.message.channel, "", embed=embed)

    @mod.command(pass_context=True)
    async def add(self, ctx, server, role):
        """Add a role to the list of moderators on a server.
        If a server or role name has spaces in it, you must enclose *both* of them in quotes, no matter which one is the one with spaces in it.
        """
        mods = load_moderation()
        valid_server = False
        valid_role = False
        for e in self.bot.servers:
            if e.name == server:
                valid_server = True
            for f in e.roles:
                if f.name == role:
                    valid_role = True
        if valid_server:
            if valid_role:
                try:
                    mods[server]
                except KeyError:
                    mods[server] = [role]
                else:
                    mods[server].append(role)
                with open("settings/moderation.json", "w+") as f:
                    json.dump(mods, f)
                await self.bot.send_message(ctx.message.channel, bot_prefix + "Successfully added {} to the list of mod roles on {}!".format(role, server))
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + "{} isn't a role on {}!".format(role, server))
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + "{} isn't a server!".format(server))

    @mod.command(pass_context=True)
    async def remove(self, ctx, server, role):
        """Remove a role from the list of moderators on a server.
        If a server or role name has spaces in it, you must enclose *both* of them in quotes, no matter which one is the one with spaces in it.
        """
        mods = load_moderation()
        try:
            mods[server].remove(role)
            with open("settings/moderation.json", "w+") as f:
                json.dump(mods, f)
            await self.bot.send_message(ctx.message.channel, bot_prefix + "Successfully removed {} from the list of mod roles on {}!".format(role, server))
        except (ValueError, KeyError):
            await self.bot.send_message(ctx.message.channel, bot_prefix + "You can't remove something that doesn't exist!")        

def setup(bot):
    bot.add_cog(Lockdown(bot))
