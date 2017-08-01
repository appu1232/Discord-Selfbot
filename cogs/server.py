import prettytable
import discord
import os
from PythonGists import PythonGists
from discord.ext import commands
from cogs.utils.checks import embed_perms, cmd_prefix_len

'''Module for server commands.'''


class Server:

    def __init__(self, bot):
        self.bot = bot

    def find_server(self, msg):
        server = None
        if msg:
            try:
                float(msg)
                server = self.bot.get_server(int(msg))
                if not server:
                    return self.bot.bot_prefix + 'Server not found.', False
            except:
                for i in self.bot.servers:
                    if i.name.lower() == msg.lower().strip():
                        server = i
                        break
                if not server:
                    return self.bot.bot_prefix + 'Could not find server. Note: You must be a member of the server you are trying to search.', False

        return server, True

    # Stats about server
    @commands.group(pass_context=True, invoke_without_command=True)
    async def server(self, ctx, *, msg=""):
        """Various info about the server. >help server for more info."""
        if ctx.invoked_subcommand is None:
            if msg:
                server = None
                try:
                    float(msg)
                    server = self.bot.get_guild(int(msg))
                    if not server:
                        return await ctx.send(
                                              self.bot.bot_prefix + 'Server not found.')
                except:
                    for i in self.bot.guilds:
                        if i.name.lower() == msg.lower():
                            server = i
                            break
                    if not server:
                        return await ctx.send(self.bot.bot_prefix + 'Could not find server. Note: You must be a member of the server you are trying to search.')
            else:
                server = ctx.message.guild

            online = 0
            for i in server.members:
                if str(i.status) == 'online' or str(i.status) == 'idle' or str(i.status) == 'dnd':
                    online += 1
            all_users = []
            for user in server.members:
                all_users.append('{}#{}'.format(user.name, user.discriminator))
            all_users.sort()
            all = '\n'.join(all_users)

            channel_count = len([x for x in server.channels if type(x) == discord.channel.TextChannel])

            role_count = len(server.roles)
            emoji_count = len(server.emojis)

            if embed_perms(ctx.message):
                em = discord.Embed(color=0xea7938)
                em.add_field(name='Name', value=server.name)
                em.add_field(name='Owner', value=server.owner, inline=False)
                em.add_field(name='Members', value=server.member_count)
                em.add_field(name='Currently Online', value=online)
                em.add_field(name='Text Channels', value=str(channel_count))
                em.add_field(name='Region', value=server.region)
                em.add_field(name='Verification Level', value=str(server.verification_level))
                em.add_field(name='Highest role', value=server.role_hierarchy[0])
                em.add_field(name='Number of roles', value=str(role_count))
                em.add_field(name='Number of emotes', value=str(emoji_count))
                url = PythonGists.Gist(description='All Users in: %s' % server.name, content=str(all), name='server.txt')
                gist_of_users = '[List of all {} users in this server]({})'.format(server.member_count, url)
                em.add_field(name='Users', value=gist_of_users)
                em.add_field(name='Created At', value=server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.set_thumbnail(url=server.icon_url)
                em.set_author(name='Server Info', icon_url='https://i.imgur.com/RHagTDg.png')
                em.set_footer(text='Server ID: %s' % server.id)
                await ctx.send(embed=em)
            else:
                msg = '**Server Info:** ```Name: %s\nOwner: %s\nMembers: %s\nCurrently Online: %s\nRegion: %s\nVerification Level: %s\nHighest Role: %s\nDefault Channel: %s\nCreated At: %s\nServer avatar: : %s```' % (
                server.name, server.owner, server.member_count, online, server.region, str(server.verification_level), server.role_hierarchy[0], server.default_channel, server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), server.icon_url)
                await ctx.send(self.bot.bot_prefix + msg)
            await ctx.message.delete()

    @server.command(pass_context=True)
    async def emojis(self, ctx, msg: str = None):
        """List all emojis in this server. Ex: >server emojis"""
        if msg:
            server, found = self.find_server(msg)
            if not found:
                return await ctx.send(server)
        else:
            server = ctx.message.guild
        emojis = [str(x) for x in server.emojis]
        await ctx.send("".join(emojis))
        await ctx.message.delete()

    @server.command(pass_context=True)
    async def avi(self, ctx, msg: str = None):
        """Get server avatar image link."""
        if msg:
            server, found = self.find_server(msg)
            if not found:
                return await ctx.send(server)
        else:
            server = ctx.message.guild
        if embed_perms(ctx.message):
            em = discord.Embed()
            em.set_image(url=server.icon_url)
            await ctx.send(embed=em)
        else:
            await ctx.send(self.bot.bot_prefix + server.icon_url)
        await ctx.message.delete()

    @server.command(pass_context=True)
    async def role(self, ctx, *, msg):
        """Get more info about a specific role. Ex: >server role Admins"""
        for role in ctx.message.guild.roles:
            if msg == role.name or msg == role.id:
                all_users = [str(x) for x in role.members]
                all_users.sort()
                all_users = ', '.join(all_users)
                em = discord.Embed(title='Role Info', color=role.color)
                em.add_field(name='Name', value=role.name)
                em.add_field(name='ID', value=role.id, inline=False)
                em.add_field(name='Users in this role', value=str(len(role.members)))
                em.add_field(name='Role color hex value', value=str(role.color))
                em.add_field(name='Role color RGB value', value=role.color.to_rgb())
                em.add_field(name='Mentionable', value=role.mentionable)
                if len(role.members) > 10:
                    all_users = all_users.replace(', ', '\n')
                    url = PythonGists.Gist(description='Users in role: {} for server: {}'.format(role.name, ctx.message.guild.name), content=str(all_users), name='role.txt')
                    em.add_field(name='All users', value='{} users. [List of users posted to Gist.]({})'.format(len(role.members), url), inline=False)
                else:
                    em.add_field(name='All users', value=all_users, inline=False)
                em.add_field(name='Created at', value=role.created_at.__format__('%x at %X'))
                em.set_thumbnail(url='http://www.colorhexa.com/%s.png' % str(role.color).strip("#"))
                await ctx.message.delete()
                return await ctx.send(content=None, embed=em)
        await ctx.message.delete()
        await ctx.send(self.bot.bot_prefix + 'Could not find role ``%s``' % msg)


def setup(bot):
    bot.add_cog(Server(bot))
