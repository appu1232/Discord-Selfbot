import discord
import asyncio
from appuselfbot import bot_prefix
from discord.ext import commands
from time import time
import redis
from datetime import datetime
from cogs.utils.checks import *

'''Shows number of Appu Selfbot users.'''

ONLINE_LAST_MINUTES = 10


# Credit to http://flask.pocoo.org/snippets/71/
class Online:
    def __init__(self, bot):
        self.bot = bot
        self.opt = load_optional_config()
        if 'online_stats' not in self.opt:
            with open('settings/optional_config.json', 'r+') as o:
                self.opt['online_stats'] = 'on'
                o.seek(0)
                o.truncate()
                json.dump(self.opt, o, indent=4)

    def mark_online(self, user_id):
        now = int(time.time())
        expires = now + (ONLINE_LAST_MINUTES * 60) + 10
        all_users_key = 'online-users/%d' % (now // 60)
        user_key = 'user-activity/%s' % user_id
        p = self.redis.pipeline()
        p.sadd(all_users_key, user_id)
        p.set(user_key, now)
        p.expireat(all_users_key, expires)
        p.expireat(user_key, expires)
        p.execute()

    def get_user_last_activity(self, user_id):
        last_active = self.redis.get('user-activity/%s' % user_id)
        if last_active is None:
            return None
        return datetime.utcfromtimestamp(int(last_active))

    def get_online_users(self):
        current = int(time.time()) // 60
        minutes = iter(range(ONLINE_LAST_MINUTES))
        return self.redis.sunion(['online-users/%d' % (current - x)
                             for x in minutes])

    @commands.command(pass_context=True)
    async def togglemystats(self, ctx):
        """Disable participation in global online count for the selfbot."""
        await self.bot.delete_message(ctx.message)
        with open('settings/optional_config.json', 'r+') as o:
            opt = json.load(o)
            if opt['online_stats'] == 'on':
                opt['online_stats'] = 'off'
                await self.bot.send_message(ctx.message.channel,
                                            bot_prefix + 'Turned off participation in global online count of selfbot users. Please consider re-enabling in order to provide accurate data. You would not be under any monitoring or security threats.')
            else:
                opt['online_stats'] = 'on'
                await self.bot.send_message(ctx.message.channel,
                                            bot_prefix + 'Turned on participation in global online count of selfbot users.')
            o.seek(0)
            o.truncate()
            json.dump(opt, o, indent=4)
        self.opt = load_optional_config()


    @commands.command(pass_context=True)
    async def online(self, ctx):
        """Show the number of users using this selfbot currently."""
        await self.bot.delete_message(ctx.message)
        opt = load_optional_config()
        if opt['online_stats'] == 'on':
            try:
                if embed_perms(ctx.message):
                    em = discord.Embed(timestamp=ctx.message.timestamp, color=0x0da504)
                    em.add_field(name='\ud83e\udd16 # of Appu Selfbots Online', value=str(len(self.get_online_users())))
                    await self.bot.send_message(ctx.message.channel, content=None, embed=em)
                else:
                    await self.bot.send_message(ctx.message.channel, bot_prefix + str(len(self.get_online_users())))
            except:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not fetch online user stats currently. Perhaps the server is down.')
        else:
            await self.bot.send_message(ctx.message.channel,
                                        bot_prefix + 'Online status of the selfbot must be enabled for tracking for yourself in order to view this. Enable with `togglemystats`.')

    async def set_online(self):
        await self.bot.wait_until_ready()
        await self.bot.wait_until_login()
        while self is self.bot.get_cog("Online"):

            # Pls don't judge me. WIP
            if self.opt.get('online_stats') == 'on':
                try:
                    pool = redis.ConnectionPool(host='162.243.35.169', port=6379, db=0)
                    pool.disconnect()
                except:
                    pass
                try:
                    pool = redis.ConnectionPool(host='162.243.35.169', port=6379, db=0)
                    self.redis = redis.Redis(connection_pool=pool)
                    self.mark_online(self.bot.user.id)
                    pool.disconnect()
                except:
                    raise
                await asyncio.sleep(500)


def setup(bot):
    o = Online(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(o.set_online())
    bot.add_cog(o)
