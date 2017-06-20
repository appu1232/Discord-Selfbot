import discord
import json
import os

with open('settings/notify.json', 'r') as f:
    notif = json.load(f)
description = '''Subreddit keyword notifier by appu1232'''

bot = discord.Client()


@bot.event
async def on_message(message):
    with open('settings/notify.json', 'r') as f:
        notif = json.load(f)
    if notif['type'] == 'dm':
        if message.author.id == notif['author'] and message.channel.id == notif['channel']:
            if notif['type'] == 'ping':
                if message.content:
                    desc, context = message.content.split('Context:', 1)
                    channel = context.split('User: ')[0].strip()
                    await bot.send_message(message.channel, desc + '\n' + channel[3:] + '\n' + message.author.mention)
                else:
                    em = discord.Embed()
                    em = em.from_data(message.embeds[0])
                    title = em.title
                    desc = em.description.split('Context:')[0]
                    await bot.send_message(message.channel, title + '\n' + desc.strip()[:-2] + message.author.mention)
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
