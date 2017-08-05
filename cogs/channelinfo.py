import discord
from discord.ext import commands
from random import randint, choice

class Channelinfo:
    """Shows Channel infos."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['channel', 'cinfo', 'ci'], pass_context=True, no_pm=True)
    async def channelinfo(self, ctx, *, channel: discord.channel=None):
        """Shows channel informations"""
        if not channel:
            channel = ctx.message.channel
        # else:
            # channel = ctx.message.guild.get_channel(int(chan))
            # if not channel: channel = self.bot.get_channel(int(chan))
        data = discord.Embed()
        content = None
        if hasattr(channel, 'mention'):
            content = self.bot.bot_prefix+"**Informations about Channel:** "+channel.mention
        if hasattr(channel, 'changed_roles'):
            if len(channel.changed_roles) > 0:
                if channel.changed_roles[0].permissions.read_messages:
                    data.color = discord.Colour.green()
                else: data.color = discord.Colour.red()
        if isinstance(channel, discord.TextChannel): _type = "Text"
        elif isinstance(channel, discord.VoiceChannel): _type = "Voice"
        else: _type = "Unknown"
        data.add_field(name="Type", value=_type)
        data.add_field(name="ID", value=channel.id)
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
            if channel.members:
                data.add_field(name="Members", value="%s"%len(channel.members))
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)
            _hidden = []; _allowed = []
            for role in channel.changed_roles:
                if role.permissions.read_messages: _allowed.append(role.mention)
                else: _hidden.append(role.mention)
            if len(_allowed) > 0: data.add_field(name='Allowed Roles (%s)'%len(_allowed), value=', '.join(_allowed), inline=False)
            if len(_hidden) > 0: data.add_field(name='Restricted Roles (%s)'%len(_hidden), value=', '.join(_hidden), inline=False)
        if channel.created_at:
            data.set_footer(text=("Created on {} ({} days ago)".format(channel.created_at.strftime("%d %b %Y %H:%M"), (ctx.message.created_at - channel.created_at).days)))
        # try:
            await ctx.send(content if content else None, embed=data)
        # except:
            # await ctx.send(self.bot.bot_prefix+"I need the `Embed links` permission to send this")


def setup(bot):
    bot.add_cog(Channelinfo(bot))
