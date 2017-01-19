import discord
import datetime
import asyncio
from appuselfbot import isBot
from discord.ext import commands
import utils.settings


class Misc:

    def __init__(self, bot):
        self.bot = bot

    # Links to the Selfbot project on Github
    @commands.command(pass_context=True)
    async def about(self, ctx):
        em = discord.Embed(description='by appu1232#2569\n\nhttps://github.com/appu1232/Selfbot-for-Discord',
                           colour=0x593bd3)
        em.set_image(url='https://github.com/appu1232/Selfbot-for-Discord')
        em.set_author(name='Discord Selfbot', icon_url='http://i.imgur.com/mvyVEqw.jpg')
        await self.bot.send_message(ctx.message.channel, embed=em)

    # Get response time
    @commands.command(pass_context=True)
    async def ping(self, ctx):
        msgtime = ctx.message.timestamp.now()
        await self.bot.send_message(ctx.message.channel, isBot + ' pong')
        now = datetime.datetime.now()
        ping = now - msgtime
        pong = discord.Embed(title='Response Time:', description=str(ping), color=0x7A0000)
        pong.set_thumbnail(url='http://odysseedupixel.fr/wp-content/gallery/pong/pong.jpg')
        await self.bot.send_message(ctx.message.channel, content=None, embed=pong)

    # Simple calculator
    @commands.command(pass_context=True)
    async def calc(self, ctx, *, msg: str):
        equation = msg.strip()
        if '=' in equation:
            left = eval(equation.split('=')[0])
            right = eval(equation.split('=')[1])
            await self.bot.send_message(ctx.message.channel, isBot + str(left == right))
        else:
            await self.bot.send_message(ctx.message.channel, isBot + str(eval(equation)))

    # Sends a googleitfor.me link with the specified tags
    @commands.command(pass_context=True)
    async def l2g(self, ctx, *, msg: str):
        lmgtfy = 'http://googleitfor.me/?q='
        words = msg.lower().strip().split(' ')
        for word in words:
            lmgtfy += word + '+'
        await self.bot.send_message(ctx.message.channel, isBot + lmgtfy[:-1])

    # Deletes previous message immediately or after specified number of seconds (because why not)
    @commands.command(pass_context=True)
    async def d(self, ctx):

        # If number of seconds are specified
        if len(ctx.message.content.lower().strip()) > 2:
            if ctx.message.content[3] == '!':
                await self.bot.delete_message(utils.settings.remove_selflog())
                for i in range(int(ctx.message.content[4])):
                    await self.bot.delete_message(utils.settings.remove_selflog())
            else:
                killmsg = utils.settings.selflog[len(utils.settings.selflog) - 2]
                timer = int(ctx.message.content[2:].lower().strip())

                # Animated countdown because screw rate limit amirite
                destroy = await self.bot.edit_message(ctx.message, isBot + 'The above message will self-destruct in:')
                msg = await self.bot.send_message(ctx.message.channel, '``%s  |``' % timer)
                for i in range(0, timer, 4):
                    if timer - 1 - i == 0:
                        await self.bot.delete_message(destroy)
                        msg = await self.bot.edit_message(msg, '``0``')
                        break
                    else:
                        msg = await self.bot.edit_message(msg, '``%s  |``' % int(timer - 1 - i))
                        await asyncio.sleep(1)
                    if timer - 1 - i != 0:
                        if timer - 2 - i == 0:
                            await self.bot.delete_message(destroy)
                            msg = await self.bot.edit_message(msg, '``0``')
                            break
                        else:
                            msg = await self.bot.edit_message(msg, '``%s  /``' % int(timer - 2 - i))
                            await asyncio.sleep(1)
                    if timer - 2 - i != 0:
                        if timer - 3 - i == 0:
                            await self.bot.delete_message(destroy)
                            msg = await self.bot.edit_message(msg, '``0``')
                            break
                        else:
                            msg = await self.bot.edit_message(msg, '``%s  -``' % int(timer - 3 - i))
                            await asyncio.sleep(1)
                    if timer - 3 - i != 0:
                        if timer - 4 - i == 0:
                            await self.bot.delete_message(destroy)
                            msg = await self.bot.edit_message(msg, '``0``')
                            break
                        else:
                            msg = await self.bot.edit_message(msg, '``%s  \ ``' % int(timer - 4 - i))
                            await asyncio.sleep(1)
                await self.bot.edit_message(msg, ':bomb:')
                await asyncio.sleep(.5)
                await self.bot.edit_message(msg, ':fire:')
                await self.bot.edit_message(killmsg, ':fire:')
                await asyncio.sleep(.5)
                await self.bot.delete_message(msg)
                await self.bot.delete_message(killmsg)

        # If no number specified, delete message immediately
        else:
            await self.bot.delete_message(utils.settings.remove_selflog())
            await self.bot.delete_message(utils.settings.remove_selflog())


def setup(bot):
    bot.add_cog(Misc(bot))
