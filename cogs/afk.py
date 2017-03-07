import json
from appuselfbot import isBot
from discord.ext import commands


class Afk:

    def __init__(self, bot):
        self.bot = bot

    # Set afk status on or off. If on, pinging will lead to an automated response.
    @commands.command(pass_context=True)
    async def setafk(self, ctx, *, msg: str):
        if msg.lower().strip() == 'on':
            with open('settings/config.json', 'r+') as conf:
                cf = json.load(conf)
                cf['set_afk'] = 'on'
                conf.seek(0)
                conf.truncate()
                json.dump(cf, conf, indent=4)
            await self.bot.send_message(ctx.message.channel, isBot + 'AFK on')
        elif msg.lower().strip() == 'off':
            with open('settings/config.json', 'r+') as conf:
                cf = json.load(conf)
                cf['set_afk'] = 'off'
                conf.seek(0)
                conf.truncate()
                json.dump(cf, conf, indent=4)
            await self.bot.send_message(ctx.message.channel, isBot + 'AFK off')
        else:
            await self.bot.send_message(ctx.message.channel, isBot + 'Invalid argument.')

    # Set afk message
    @commands.command(pass_context=True)
    async def setafkmsg(self, ctx, *, msg: str):
        with open('settings/config.json', 'r+') as conf:
            cf = json.load(conf)
            cf['afk_message'] = msg
            conf.seek(0)
            conf.truncate()
            json.dump(cf, conf, indent=4)
            await self.bot.send_message(ctx.message.channel, isBot + 'Set afk message to: %s' % cf['afk_message'])


def setup(bot):
    bot.add_cog(Afk(bot))
