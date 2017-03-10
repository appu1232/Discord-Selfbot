import discord
import json

with open('cogs/utils/notify.json', 'r') as f:
    notif = json.load(f)
description = '''Subreddit keyword notifier by appu1232'''

bot = discord.Client()


@bot.event
async def on_message(message):
    with open('cogs/utils/notify.json', 'r') as f:
        notif = json.load(f)
    if notif['notify'] == 'on':
        if message.author.id == notif['author'] and message.channel.id == notif['channel']:
            if notif['type'] == 'ping':
                await bot.send_message(message.channel, message.author.mention)
            elif notif['type'] == 'dm':
                if message.content:
                    await bot.send_message(message.author, message.content)
                else:
                    em = discord.Embed()
                    em = em.from_data(message.embeds[0])
                    await bot.send_message(message.author, content=None, embed=em)
            else:
                try:
                    await bot.delete_message(message)
                except:
                    pass
                if message.content:
                    await bot.send_message(message.channel, message.content)
                else:
                    em = discord.Embed()
                    em = em.from_data(message.embeds[0])
                    await bot.send_message(message.channel, content=None, embed=em)


@bot.event
async def on_ready():
    pass

bot.run(notif["bot_token"])
