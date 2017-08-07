import discord
from discord.ext import commands
from cogs.utils.checks import embed_perms, cmd_prefix_len

'''Module for the >info command.'''


class Userinfo:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['user', 'uinfo', 'info', 'ui'])
    async def userinfo(self, ctx):
        """Get user info. Ex: >info @user"""
        if ctx.invoked_subcommand is None:
            pre = cmd_prefix_len()
            name = ctx.message.content[4 + pre:].strip()
            if name:
                try:
                    user = ctx.message.mentions[0]
                except:
                    user = ctx.guild.get_member_named(name)
                if not user:
                    try: user = ctx.guild.get_member(int(name))
                    except: pass
                if not user:
                    await ctx.send(self.bot.bot_prefix + 'Could not find user.')
                    return
            else:
                user = ctx.message.author

            if embed_perms(ctx.message):
                em = discord.Embed(timestamp=ctx.message.created_at, colour=0x708DD0)
                em.add_field(name='💳 User ID', value=user.id, inline=True)
                if user.nick: em.add_field(name='✏ Nick', value='`{}`'.format(user.nick), inline=True)
                if user.status == discord.Status.online: stat = '\uD83D\uDCD7'
                elif user.status == discord.Status.idle: stat = '\uD83D\uDCD9'
                elif user.status == discord.Status.dnd: stat = '\uD83D\uDCD5'
                elif user.status == discord.Status.invisible: stat = '\u2716'
                elif user.status == discord.Status.offline: stat = '\u274C'
                em.add_field(name='🌐 Status', value='\{} {}'.format(stat, user.status).title())
                if user.voice:
                    em.add_field(name='🔈 Voice Channel', value=user.voice.channel.name, inline=True)
                g = u'\U0001F3AE Game'
                game = user.game
                if game:
                    if '=' in game:
                        g = '\ud83c\udfa5 Stream'
                        game = user.game.split('=')
                        game = '[{}]({})'.format(game[0],game[1])
                    em.add_field(name=g, value=str(game), inline=True)
                profile = await self.bot.get_user_profile(user.id)
                if profile:
                    if profile.premium: em.add_field(name='Nitro', value='Since {} ({} days ago)'.format(profile.premium_since.__format__('%A, %d. %B %Y @ %H:%M:%S'), (ctx.message.created_at - profile.premium_since).days))
                    if profile.hypesquad: em.add_field(name='HypeSquad', value='Yes')
                    if profile.partner: em.add_field(name='Partner', value='Yes')
                    if profile.staff: em.add_field(name='Staff', value='Yes')
                em.add_field(name='🕙 Account Created', value='{} ({} days ago)'.format(user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), (ctx.message.created_at - user.created_at).days), inline=False)
                em.add_field(name='\U0001F4E5 Join Date', value='{} ({} days ago)'.format(user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), (ctx.message.created_at - user.joined_at).days), inline=False)
                em.add_field(name='Roles', value=', '.join([role.mention for role in user.roles]), inline=False)
                em.set_thumbnail(url=user.avatar_url)
                em.set_author(name=user, icon_url='https://i.imgur.com/RHagTDg.png')
                await ctx.send(embed=em)
            else:
                msg = '**User Info:** ```User ID: %s\nNick: %s\nStatus: %s\nIn Voice: %s\nGame: %s\nHighest Role: %s\nAccount Created: %s\nJoin Date: %s\nAvatar url:%s```' % (user.id, user.nick, user.status, voice_state, user.game, role, user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), avi)
                await ctx.send(self.bot.bot_prefix + msg)

            await ctx.message.delete()

    @userinfo.command()
    async def avi(self, ctx, txt: str = None):
        """View bigger version of user's avatar. Ex: >info avi @user"""
        if txt:
            try:
                user = ctx.message.mentions[0]
            except:
                user = ctx.guild.get_member_named(txt)
            if not user:
                user = ctx.guild.get_member(int(txt))
            if not user:
                await ctx.send(self.bot.bot_prefix + 'Could not find user.')
                return
        else:
            user = ctx.message.author

        # Thanks to IgneelDxD for help on this
        if user.avatar_url[54:].startswith('a_'):
            avi = 'https://images.discordapp.net/avatars/' + user.avatar_url[35:-10]
        else:
            avi = user.avatar_url
        if embed_perms(ctx.message):
            em = discord.Embed(colour=0x708DD0)
            em.set_image(url=avi)
            await ctx.send(embed=em)
        else:
            await ctx.send(self.bot.bot_prefix + avi)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Userinfo(bot))
