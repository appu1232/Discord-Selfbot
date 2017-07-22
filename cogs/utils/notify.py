import discord
import os
from cogs.utils.dataIO import dataIO

class Notify:

    def __init__(bot):
        self.bot = bot
        self.settings = dataIO.load_json('settings/notify.json')
        
async def on_message(message):
    if self.settings['type'] == 'dm':
        if message.author.id == self.settings['author'] and message.channel.id == self.settings['channel']:
            if self.settings['type'] == 'ping':
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
            elif self.settings['type'] == 'dm':
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
                    
def setup(bot):
    bot.add_cog(Notify(bot))


