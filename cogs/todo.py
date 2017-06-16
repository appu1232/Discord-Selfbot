import re
import json
import discord
from time import time as current_time
from appuselfbot import bot_prefix
from discord_webhooks import *
from discord.ext import commands
from cogs.utils.checks import *

'''Todo list cog.'''

# load to-do list in from file
try: 
    with open("settings/todo.json", "r+") as f:
        todo_list = json.load(f)
except IOError:
    todo_list = {}
    
notify = load_notify_config()
log = load_log_config()


  
class Todo:

    def __init__(self, bot):
        self.bot = bot
    
    def save_list(self):
        with open("settings/todo.json", "w") as f:
            json.dump(todo_list, f)
    
    # don't like to do this but the one from appuselfbot.py is slightly different to my needs
    async def webhook(self, keyword_content, send_type):
        temp = log['webhook_url'].split('/')
        channel = temp[len(temp) - 2]
        token = temp[len(temp) - 1]
        webhook_class = Webhook(self.bot)
        request_webhook = webhook_class.request_webhook
        if 'ping' in send_type:
            await request_webhook('/{}/{}'.format(channel, token), content=keyword_content + '\n' + self.bot.user.mention)
        else:
            await request_webhook('/{}/{}'.format(channel, token), content=keyword_content)
    
    @commands.group(pass_context=True)
    async def todo(self, ctx):
        """Manage your to-do list. >help todo for more information.
        >todo - List all of the entries in your to-do list.
        >todo add <item> - Add an item to your to-do list. Example: >todo add buy bacon
        >todo add <item> | <time> - Add an item to your to-do list with a timer. See below for more information. Example: >todo add buy bacon | 7h
        >todo remove <item> - Remove an item from your to-do list.
        >todo clear - Clear your entire to-do list.
        When a timed to-do list item is completed, you will be notified via the webhook you set up for keyword logging.
        If you do not have keyword logging set up, go to https://github.com/appu1232/Discord-Selfbot/wiki/Keyword-Notifier---User-Following-Info-and-Setup
        """
        if ctx.invoked_subcommand == None:
            await self.bot.delete_message(ctx.message)
            if not todo_list:
                await self.bot.send_message(ctx.message.channel, bot_prefix + "Your to-do list is empty!")
            else:
                embed = discord.Embed(title="{}'s to-do list:".format(ctx.message.author.name), description="")
                for entry in todo_list:
                    if todo_list[entry] == "none":
                        embed.description += "\u2022 {}\n".format(entry)
                    elif todo_list[entry] == "done":
                        embed.description += "\u2022 {} - time's up!\n".format(entry)
                    else:
                        m, s = divmod(todo_list[entry]-current_time(), 60)
                        h, m = divmod(m, 60)
                        d, h = divmod(h, 24)
                        embed.description += "\u2022 {} - remaining time {}\n".format(entry, "{}:{}:{}:{}".format(int(d), int(h), int(m), int(s)))
                await self.bot.send_message(ctx.message.channel, "", embed=embed)
            
    @todo.command(pass_context=True)
    async def add(self, ctx, *, msg):
        """Add to your to-do list."""
        await self.bot.delete_message(ctx.message)
        seconds = "none"
        if " | " in msg:
            msg, time = msg.split(" | ", 1)
            # taken from kurisu
            units = {
                "d": 86400,
                "h": 3600,
                "m": 60,
                "s": 1
            }
            seconds = 0
            match = re.findall("([0-9]+[smhd])", time)
            if match is None:
                seconds = "none"
            else:
                for item in match:
                    seconds += (int(item[:-1]) * units[item[-1]]) + current_time()
        todo_list[msg] = seconds
        self.save_list()
        await self.bot.send_message(ctx.message.channel, bot_prefix + "Successfully added `{}` to your to-do list!".format(msg))
            
    @todo.command(pass_context=True)
    async def remove(self, ctx, *, msg):
        """Cross out entries from your to-do list."""
        await self.bot.delete_message(ctx.message)
        if not todo_list:
            await self.bot.send_message(ctx.message.channel, bot_prefix + "Your to-do list is empty!")
        else:
            found = todo_list.pop(msg, None)
            if found:
                self.save_list()
                await self.bot.send_message(ctx.message.channel, bot_prefix + "Successfully removed `{}` from your to-do list!".format(msg)) 
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + "That entry doesn't exist!")
    
    @todo.command(pass_context=True)
    async def clear(self, ctx):
        """Clear your entire to-do list."""
        await self.bot.delete_message(ctx.message)
        todo_list.clear()
        self.save_list()
        await self.bot.send_message(ctx.message.channel, bot_prefix + "Successfully cleared your to-do list!")
    
    async def on_message(self, message):
        for entry in todo_list:
            if todo_list[entry] != "none" and todo_list[entry] != "done":
                if todo_list[entry] < current_time():
                    todo_list[entry] = "done"
                    self.save_list()
                    if notify['type'] == 'msg':
                        await self.webhook("Your timer for the to-do list entry '{}' just ran out!".format(entry), 'message')
                    elif notify['type'] == 'ping':
                        await self.webhook("Your timer for the to-do list entry '{}' just ran out!".format(entry), 'message ping')
                    else:
                        await self.bot.send_message(self.server.get_channel(location[0]), "Your timer for the to-do list entry '{}' just ran out!".format(entry))

def setup(bot):
    bot.add_cog(Todo(bot))