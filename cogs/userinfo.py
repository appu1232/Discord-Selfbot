import discord
from discord.ext import commands
from cogs.utils.checks import embed_perms, cmd_prefix_len

'''Module for the info command.'''


class Userinfo:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=['user', 'uinfo', 'info', 'ui'])
    async def userinfo(self, ctx, *, name=""):
        """Get user info. Ex: [p]info @user"""
        if ctx.invoked_subcommand is None:
            pre = cmd_prefix_len()
            if name:
                try:
                    user = ctx.message.mentions[0]
                except IndexError:
                    user = ctx.guild.get_member_named(name)
                if not user:
                    user = ctx.guild.get_member(int(name))
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

            role = user.top_role.name
            if role == "@everyone":
                role = "N/A"
            voice_state = None if not user.voice else user.voice.channel
            if embed_perms(ctx.message):
                em = discord.Embed(timestamp=ctx.message.created_at, colour=0x708DD0)
                em.add_field(name='User ID', value=user.id, inline=True)
                em.add_field(name='Nick', value=user.nick, inline=True)
                em.add_field(name='Status', value=user.status, inline=True)
                em.add_field(name='In Voice', value=voice_state, inline=True)
                em.add_field(name='Game', value=user.game, inline=True)
                em.add_field(name='Highest Role', value=role, inline=True)
                em.add_field(name='Account Created', value=user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.add_field(name='Join Date', value=user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.set_thumbnail(url=avi)
                em.set_author(name=user, icon_url='https://i.imgur.com/RHagTDg.png')
                await ctx.send(embed=em)
            else:
                msg = '**User Info:** ```User ID: %s\nNick: %s\nStatus: %s\nIn Voice: %s\nGame: %s\nHighest Role: %s\nAccount Created: %s\nJoin Date: %s\nAvatar url:%s```' % (user.id, user.nick, user.status, voice_state, user.game, role, user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), avi)
                await ctx.send(self.bot.bot_prefix + msg)

            await ctx.message.delete()

    @userinfo.command()
    async def avi(self, ctx, txt: str = None):
        """View bigger version of user's avatar. Ex: [p]info avi @user"""
        if txt:
            try:
                user = ctx.message.mentions[0]
            except IndexError:
                user = ctx.guild.get_member_named(txt)
            if not user:
                user = ctx.guild.get_member(int(txt))
            if not user:
                await ctx.send(self.bot.bot_prefix + 'Could not find user.')
                return
        else:
            user = ctx.message.author

        # Thanks to IgneelDxD for help on this
        if user.avatar_url_as(static_format='png')[54:].startswith('a_'):
            avi = 'https://images.discordapp.net/avatars/' + user.avatar_url[35:-10]
        else:
            avi = user.avatar_url_as(static_format='png')
        if embed_perms(ctx.message):
            em = discord.Embed(colour=0x708DD0)
            em.set_image(url=avi)
            await ctx.send(embed=em)
        else:
            await ctx.send(self.bot.bot_prefix + avi)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Userinfo(bot))
