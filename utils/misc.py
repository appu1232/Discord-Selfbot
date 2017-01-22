import discord
import datetime
import asyncio
from appuselfbot import isBot
from discord.ext import commands


class Misc:

    def __init__(self, bot):
        self.bot = bot

    # Links to the Selfbot project on Github
    @commands.command(pass_context=True)
    async def about(self, ctx):
        await self.bot.send_message(ctx.message.channel, 'https://github.com/appu1232/Selfbot-for-Discord')
        await asyncio.sleep(2)
        await self.bot.delete_message(ctx.message)

    # Bot stats, thanks IgneelDxD for the design
    @commands.command(pass_context=True)
    async def stats(self, ctx):
        em = discord.Embed(title='Bot Stats', color=0x32441c)
        uptime = (datetime.datetime.now() - self.bot.uptime)
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            time = '%s days, %s hours, %s minutes, and %s seconds' % (days, hours, minutes, seconds)
        else:
            time = '%s hours, %s minutes, and %s seconds' % (hours, minutes, seconds)
        em.add_field(name=':clock2: Uptime', value=time, inline=False)
        em.add_field(name=':outbox_tray: Messages sent', value=str(self.bot.icount))
        em.add_field(name=':inbox_tray: Messages recieved', value=':envelope_with_arrow: ' + str(self.bot.message_count))
        em.add_field(name=':exclamation: Mentions received', value=str(self.bot.mention_count))
        em.add_field(name=':crossed_swords: Servers', value=str(len(self.bot.servers)))
        em.add_field(name=':pencil2: Keywords logged', value=str(self.bot.keywords))
        await self.bot.send_message(ctx.message.channel, content=None, embed=em)
        await asyncio.sleep(2)
        await self.bot.delete_message(ctx.message)

    # # Stats about current server
    # @commands.command(pass_context=True)
    # async def server(self, ctx):
    #     em = discord.Embed(title='Bot Stats', color=0x32441c)


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
                await self.bot.delete_message(self.bot.self_log.pop())
                i = 0
                while i != int(ctx.message.content[4]):
                    try:
                        await self.bot.delete_message(self.bot.self_log.pop())
                        i += 1
                    except:
                        pass
            else:
                killmsg = self.bot.self_log[len(self.bot.self_log) - 2]
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
            await self.bot.delete_message(self.bot.self_log.pop())
            await self.bot.delete_message(self.bot.self_log.pop())


def setup(bot):
    bot.add_cog(Misc(bot))
