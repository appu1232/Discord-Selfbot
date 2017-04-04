from discord.ext import commands
from cogs.utils.checks import *
from discord_webhooks import *

class Webhooks:
    """webhook example cog class that contains an webhook example command."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def found_key(self, ctx):
        """
        sends whatever you typed into the command after the bot prefix + 'examplecommand' via webhook.
        """
        temp = self.bot.log_conf['webhook_url'].split('/')
        channel = temp[len(temp)-2]
        token = temp[len(temp)-1]
        self.webhook_class = Webhook(self.bot)
        self.request_webhook = self.webhook_class.request_webhook
        if self.bot.keyword_found[0].startswith('embed'):
            if 'msg' in self.bot.keyword_found[0]:
                await self.request_webhook('/{}/{}'.format(channel, token), embeds=[self.bot.keyword_found[1].to_dict()], content=ctx.message.author.mention)
            else:
                await self.request_webhook('/{}/{}'.format(channel, token), embeds=[self.bot.keyword_found[1].to_dict()], content=None)
        else:
            if 'msg' in self.bot.keyword_found[0]:
                await self.request_webhook('/{}/{}'.format(channel, token), content=self.bot.keyword_found[1] + '\n' + ctx.message.author.mention, embeds=None)
            else:
                await self.request_webhook('/{}/{}'.format(channel, token), content=self.bot.keyword_found[1], embeds=None)
        await self.bot.delete_message(ctx.message)


def setup(bot):
    """
    example webhook cog.
    """
    new_cog = Webhooks(bot)
    bot.add_cog(new_cog)
