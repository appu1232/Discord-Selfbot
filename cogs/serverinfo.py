import prettytable
import discord
import os
import re
from urllib.parse import urlparse
from PythonGists import PythonGists
from discord.ext import commands
from cogs.utils.checks import embed_perms, cmd_prefix_len

'''Module for server commands.'''


class Server:

    def __init__(self, bot):
        self.bot = bot
        self.invites = ['discord.gg/', 'discordapp.com/invite/']
        self.invite_domains = ['discord.gg', 'discordapp.com']

    def find_server(self, msg):
        server = None
        if msg:
            try:
                float(msg)
                server = self.bot.get_guild(int(msg))
                if not server:
                    return self.bot.bot_prefix + 'Server not found.', False
            except:
                for i in self.bot.guilds:
                    if i.name.lower() == msg.lower().strip():
                        server = i
                        break
                if not server:
                    return self.bot.bot_prefix + 'Could not find server. Note: You must be a member of the server you are trying to search.', False

        return server, True

    # Stats about server
    @commands.group(aliases=['server', 'sinfo', 'si'], pass_context=True, invoke_without_command=True)
    async def serverinfo(self, ctx, *, msg=""):
        """Various info about the server. [p]help server for more info."""
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

    @serverinfo.command(pass_context=True)
    async def emojis(self, ctx, msg: str = None):
        """List all emojis in this server. Ex: [p]server emojis"""
        if msg:
            server, found = self.find_server(msg)
            if not found:
                return await ctx.send(server)
        else:
            server = ctx.message.guild
        emojis = [str(x) for x in server.emojis]
        await ctx.send("".join(emojis))
        await ctx.message.delete()

    @serverinfo.command(pass_context=True)
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

    @serverinfo.command(pass_context=True)
    async def role(self, ctx, *, msg):
        """Get more info about a specific role. Ex: [p]server role Admins"""
        for role in ctx.message.guild.roles:
            if msg.lower() == role.name.lower() or msg == role.id:
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
                elif len(role.members) >= 1:
                    em.add_field(name='All users', value=all_users, inline=False)
                else:
                    em.add_field(name='All users', value='There are no users in this role!', inline=False)
                em.add_field(name='Created at', value=role.created_at.__format__('%x at %X'))
                em.set_thumbnail(url='http://www.colorhexa.com/%s.png' % str(role.color).strip("#"))
                await ctx.message.delete()
                return await ctx.send(content=None, embed=em)
        await ctx.message.delete()
        await ctx.send(self.bot.bot_prefix + 'Could not find role ``%s``' % msg)

    @commands.command(aliases=['channel', 'cinfo', 'ci'], pass_context=True, no_pm=True)
    async def channelinfo(self, ctx, *, channel: int = None):
        """Shows channel information"""
        if not channel:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(channel)
        data = discord.Embed()
        if hasattr(channel, 'mention'):
            data.description = "**Information about Channel:** " + channel.mention
        if hasattr(channel, 'changed_roles'):
            if len(channel.changed_roles) > 0:
                data.color = discord.Colour.green() if channel.changed_roles[0].permissions.read_messages else discord.Colour.red()
        if isinstance(channel, discord.TextChannel): 
            _type = "Text"
        elif isinstance(channel, discord.VoiceChannel): 
            _type = "Voice"
        else: 
            _type = "Unknown"
        data.add_field(name="Type", value=_type)
        data.add_field(name="ID", value=channel.id, inline=False)
        if hasattr(channel, 'position'):
            data.add_field(name="Position", value=channel.position)
        if isinstance(channel, discord.VoiceChannel):
            if channel.user_limit != 0:
                data.add_field(name="User Number", value="{}/{}".format(len(channel.voice_members), channel.user_limit))
            else:
                data.add_field(name="User Number", value="{}".format(len(channel.voice_members)))
            userlist = [r.display_name for r in channel.members]
            if not userlist:
                userlist = "None"
            else:
                userlist = "\n".join(userlist)
            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)
        elif isinstance(channel, discord.TextChannel):
            try:
                pins = await channel.pins()
                data.add_field(name="Pins", value=len(pins), inline=True)
            except discord.Forbidden:
                pass
            data.add_field(name="Members", value="%s"%len(channel.members))
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)
            hidden = []
            allowed = []
            for role in channel.changed_roles:
                if role.permissions.read_messages is True:
                    if role.name != "@everyone":
                        allowed.append(role.mention)
                elif role.permissions.read_messages is False:
                    if role.name != "@everyone":
                        hidden.append(role.mention)
            if len(allowed) > 0: 
                data.add_field(name='Allowed Roles ({})'.format(len(allowed)), value=', '.join(allowed), inline=False)
            if len(hidden) > 0:
                data.add_field(name='Restricted Roles ({})'.format(len(hidden)), value=', '.join(hidden), inline=False)
        if channel.created_at:
            data.set_footer(text=("Created on {} ({} days ago)".format(channel.created_at.strftime("%d %b %Y %H:%M"), (ctx.message.created_at - channel.created_at).days)))
        await ctx.send(embed=data)

    @commands.command(aliases=['invitei', 'ii'], pass_context=True)
    async def inviteinfo(self, ctx, *, invite: str = None):
        """Shows invite information."""
        if invite:
            for url in re.findall(r'(https?://\S+)', invite):
                invite = await self.bot.get_invite(urlparse(url).path.replace('/', '').replace('<', '').replace('>', ''))
                break
        else:
            async for msg in ctx.message.channel.history():
                if any(x in msg.content for x in self.invites):
                    for url in re.findall(r'(https?://\S+)', msg.content):
                        url = urlparse(url)
                        if any(x in url for x in self.invite_domains):
                            print(url)
                            url = url.path.replace('/', '').replace('<', '').replace('>', '').replace('\'', '').replace(')', '')
                            print(url)
                            invite = await self.bot.get_invite(url)
                            break
        if not invite:
            await ctx.send(content="Could not find any invite in the last 100 messages. Please specify invite manually.")

        data = discord.Embed()
        content = None
        if invite.id is not None:
            content = self.bot.bot_prefix + "**Information about Invite:** %s" % invite.id
        if invite.revoked is not None:
            data.colour = discord.Colour.red() if invite.revoked else discord.Colour.green()
        if invite.created_at is not None:
            data.set_footer(text="Created on {} ({} days ago)".format(invite.created_at.strftime("%d %b %Y %H:%M"), (invite.created_at - invite.created_at).days))
        if invite.max_age is not None:
            if invite.max_age > 0:
                expires = '%s s' % invite.max_age
            else:
                expires = "Never"
            data.add_field(name="Expires in", value=expires)
        if invite.temporary is not None:
            data.add_field(name="Temp membership", value="Yes" if invite.temporary else "No")
        if invite.uses is not None:
            data.add_field(name="Uses", value="%s / %s" % (invite.uses, invite.max_uses))
        if invite.inviter.name is not None:
            data.set_author(name=invite.inviter.name + '#' + invite.inviter.discriminator + " (%s)" % invite.inviter.id, icon_url=invite.inviter.avatar_url)

        if invite.guild.name is not None:
            data.add_field(name="Guild", value="Name: " + invite.guild.name + "\nID: %s" % invite.guild.id, inline=False)
        if invite.guild.icon_url is not None:
            data.set_thumbnail(url=invite.guild.icon_url)

        if invite.channel.name is not None:
            channel = "%s\n#%s" % (invite.channel.mention, invite.channel.name) if isinstance(invite.channel, discord.TextChannel) else invite.channel.name
            data.add_field(name="Channel", value="Name: " + channel + "\nID: %s" % invite.channel.id, inline=False)

        try:
            await ctx.send(content=content, embed=data)
        except:
            await ctx.send(content="I need the `Embed links` permission to send this")


def setup(bot):
    bot.add_cog(Server(bot))
