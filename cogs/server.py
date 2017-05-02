import prettytable
from PythonGists import PythonGists
from appuselfbot import bot_prefix
from discord.ext import commands
from cogs.utils.checks import *

'''Module for server commands.'''


class Server:

    def __init__(self, bot):
        self.bot = bot

    def find_server(self, msg):
        server = None
        if msg:
            try:
                float(msg)
                server = self.bot.get_server(msg)
                if not server:
                    return bot_prefix + 'Server not found.', False
            except:
                for i in self.bot.servers:
                    if i.name.lower() == msg.lower().strip():
                        server = i
                        break
                if not server:
                    return bot_prefix + 'Could not find server. Note: You must be a member of the server you are trying to search.', False

        return server, True

    # Stats about server
    @commands.group(pass_context=True)
    async def server(self, ctx):
        """Various info about the server. See the README for more info."""
        if ctx.invoked_subcommand is None:
            if ctx.message.content[7:]:
                server = None
                try:
                    float(ctx.message.content[7:].strip())
                    server = self.bot.get_server(ctx.message.content[7:].strip())
                    if not server:
                        return await self.bot.send_message(ctx.message.channel,
                                                           bot_prefix + 'Server not found.')
                except:
                    for i in self.bot.servers:
                        if i.name.lower() == ctx.message.content[7:].lower().strip():
                            server = i
                            break
                    if not server:
                        return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find server. Note: You must be a member of the server you are trying to search.')
            else:
                server = ctx.message.server

            online = 0
            for i in server.members:
                if str(i.status) == 'online':
                    online += 1
            all_users = []
            for user in server.members:
                all_users.append('{}#{}'.format(user.name, user.discriminator))
            all_users.sort()
            all = '\n'.join(all_users)
            if embed_perms(ctx.message):
                em = discord.Embed(color=0xea7938)
                em.add_field(name='Name', value=server.name)
                em.add_field(name='Owner', value=server.owner, inline=False)
                em.add_field(name='Members', value=server.member_count)
                em.add_field(name='Currently Online', value=online)
                em.add_field(name='Region', value=server.region)
                em.add_field(name='Verification Level', value=str(server.verification_level))
                em.add_field(name='Highest role', value=server.role_hierarchy[0])
                em.add_field(name='Default Channel', value=server.default_channel)
                url = PythonGists.Gist(description='All Users in: %s' % server.name, content=str(all), name='server.txt')
                gist_of_users = '[List of all {} users in this server]({})'.format(server.member_count, url)
                em.add_field(name='Users', value=gist_of_users)
                em.add_field(name='Created At', value=server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.set_thumbnail(url=server.icon_url)
                em.set_author(name='Server Info', icon_url='https://i.imgur.com/RHagTDg.png')
                em.set_footer(text='Selfbot made by appu1232#2569')
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                msg = '**Server Info:** ```Name: %s\nOwner: %s\nMembers: %s\nCurrently Online: %s\nRegion: %s\nVerification Level: %s\nHighest Role: %s\nDefault Channel: %s\nCreated At: %s\nServer avatar: : %s```' % (
                server.name, server.owner, server.member_count, online, server.region, str(server.verification_level), server.role_hierarchy[0], server.default_channel, server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), server.icon_url)
                await self.bot.send_message(ctx.message.channel, bot_prefix + msg)
            await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def emojis(self, ctx, msg: str = None):
        """List all emojis in this server. Ex: >server emojis"""
        if msg:
            server, found = self.find_server(msg)
        else:
            server = ctx.message.server
        emojis = ''
        for i in server.emojis:
            emojis += str(i)
        await self.bot.send_message(ctx.message.channel, emojis)
        await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def avi(self, ctx, msg: str = None):
        """Get server avatar image link."""
        if msg:
            server, found = self.find_server(msg)
        else:
            server = ctx.message.server
        if embed_perms(ctx.message):
            em = discord.Embed()
            em.set_image(url=server.icon_url)
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + server.icon_url)
        await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def role(self, ctx, *, msg):
        """Get more info about a specific role. Ex: >server role Admins"""
        for role in ctx.message.server.roles:
            if msg == role.name:
                role_count = 0
                all_users = []
                for user in ctx.message.server.members:
                    if role in user.roles:
                        all_users.append('{}#{}'.format(user.name, user.discriminator))
                        role_count += 1
                all_users.sort()
                all = ', '.join(all_users)
                em = discord.Embed(title='Role Info', color=role.color)
                em.add_field(name='Name', value=role.name)
                em.add_field(name='ID', value=role.id, inline=False)
                em.add_field(name='Users in this role', value=role_count)
                em.add_field(name='Role color hex value', value=str(role.color))
                em.add_field(name='Role color rgb value', value=role.color.to_tuple())
                em.add_field(name='Mentionable', value=role.mentionable)
                if len(all_users) > 10:
                    all = all.replace(', ', '\n')
                    url = PythonGists.Gist(description='Users in role: {} for server: {}'.format(role.name, ctx.message.server.name), content=str(all), name='role.txt')
                    em.add_field(name='All users', value='Long list, posted to Gist:\n %s' % url, inline=False)
                else:
                    em.add_field(name='All Users', value=all, inline=False)
                em.add_field(name='Created at', value=role.created_at.__format__('%x at %X'))
                em.set_thumbnail(url='http://www.colorhexa.com/%s.png' % str(role.color).strip("#"))
                return await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find role ``%s``' % msg)
        await self.bot.delete_message(ctx.message)

    @server.group(pass_context=True)
    async def members(self, ctx, msg: str = None):
        """List of members in the server."""
        if msg:
            server, found = self.find_server(msg)
        else:
            server = ctx.message.server
        msg = prettytable.PrettyTable(['User', 'Nickname', 'Join Date', 'Account Created', 'Color', 'Top Role', 'Is bot', 'Avatar url', 'All Roles'])
        for i in server.members:
            roles = ''
            for j in i.roles:
                if j.name != '@everyone':
                    roles += j.name + ', '
            if i.avatar_url[60:].startswith('a_'):
                avi = 'https://images.discordapp.net/avatars/' + i.avatar_url[33:][:18] + i.avatar_url[59:-3] + 'gif'
            else:
                avi = i.avatar_url
            try:
                join = i.joined_at.__format__('%x at %X')
            except:
                join = 'N/A'
            try:
                create = i.created_at.__format__('%x at %X')
            except:
                create = 'N/A'
            msg.add_row([str(i.name), i.nick, join, create, i.color, i.top_role, str(i.bot), avi, roles[:-2]])
        name = server.name
        keep_characters = (' ', '.', '_')
        name = ''.join(c for c in name if c.isalnum() or c in keep_characters).rstrip()
        name = name.replace(' ', '_')
        save_file = '%s_members.txt' % name
        try:
            msg = msg.get_string(sortby='User')
        except:
            pass
        with open(save_file, 'w') as file:
            file.write(str(str(msg).encode('ascii', 'ignore')))
        with open(save_file, 'rb') as file:
            await self.bot.send_file(ctx.message.channel, file)
        os.remove(save_file)
        await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(Server(bot))
