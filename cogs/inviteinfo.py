import discord, re
from urllib.parse import urlparse
from discord.ext import commands

class InviteInfo:
    """Shows Invite infos."""
    invites = ['discord.gg/', 'discordapp.com/invite/']
    invite_domains = ['discord.gg', 'discordapp.com']
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['invitei', 'ii'], pass_context=True)
    async def inviteinfo(self, ctx, *, invite: str=None):
        """Shows invite informations."""
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
        if invite.id is not None:
            content = self.bot.bot_prefix+"**Informations about Invite:** %s"%invite.id
        if invite.revoked is not None:
            data.colour = discord.Colour.red() if invite.revoked else discord.Colour.green()
        if invite.created_at is not None:
            data.set_footer(text="Created on {} ({} days ago)".format(invite.created_at.strftime("%d %b %Y %H:%M"), (invite.created_at - invite.created_at).days))
        if invite.max_age is not None:
            if invite.max_age > 0: expires = '%s s'%invite.max_age
            else: expires = "Never"
            data.add_field(name="Expires in", value=expires)
        if invite.temporary is not None:
            data.add_field(name="Temp membership", value="Yes" if invite.temporary else "No")
        if invite.uses is not None:
            data.add_field(name="Uses", value="%s / %s"%(invite.uses, invite.max_uses))
        if invite.inviter.name is not None:
            data.set_author(name=invite.inviter.name+'#'+invite.inviter.discriminator+ " (%s)"%invite.inviter.id, icon_url=invite.inviter.avatar_url)

        if invite.guild.name is not None:
            data.add_field(name="Guild", value="Name: "+invite.guild.name+"\nID: %s"%invite.guild.id, inline=False)
        if invite.guild.icon_url is not None:
            data.set_thumbnail(url=invite.guild.icon_url)

        if invite.channel.name is not None:
            channel = "%s\n#%s"%(invite.channel.mention, invite.channel.name) if isinstance(invite.channel, discord.TextChannel) else invite.channel.name
            data.add_field(name="Channel", value="Name: "+channel+"\nID: %s"%invite.channel.id, inline=False)



        try:
            await ctx.send(content=content if content else None, embed=data)
        except:
            await ctx.send(content="I need the `Embed links` permission to send this")


def setup(bot):
    bot.add_cog(InviteInfo(bot))
