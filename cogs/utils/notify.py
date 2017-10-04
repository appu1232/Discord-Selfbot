import discord
import json

description = '''Subreddit keyword notifier by appu1232'''

bot = discord.Client()
with open('settings/notify.json') as fp:
    notif = json.load(fp)


@bot.event
async def on_message(message):
    if notif['type'] == 'dm' and str(message.author.id) == notif['author'] and str(message.channel.id) == notif['channel']:
        if message.content:
            await message.author.send(message.content)
        else:
            await message.author.send(content=None, embed=message.embeds[0])

bot.run(notif["bot_token"])
