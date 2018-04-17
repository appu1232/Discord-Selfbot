import re
import discord
import asyncio
from time import time as current_time
from cogs.utils.webhooks import Webhook
from discord.ext import commands
from cogs.utils.dataIO import dataIO

'''Todo list cog.'''


class Todo:

    def __init__(self, bot):
        self.bot = bot
        # load to-do list in from file
        todo_list = dataIO.load_json("settings/todo.json")
        for i in todo_list:
            if type(todo_list[i]) is str:
                todo_list[i] = [todo_list[i], i, 0, True, 0, 0]

        dataIO.save_json("settings/todo.json", todo_list)
        self.todo_list = todo_list

    def save_list(self):
        dataIO.save_json("settings/todo.json", self.todo_list)
        
    # don't like to do this but the one from appuselfbot.py is slightly different to my needs
    async def webhook(self, entry, send_type):
        temp = self.bot.log_conf['webhook_url'].split('/')
        channel = temp[len(temp) - 2]
        token = temp[len(temp) - 1]
        webhook_class = Webhook(self.bot)
        request_webhook = webhook_class.request_webhook
        em = discord.Embed(title='Timer Alert', color=0x4e42f4, description='Timer for item: **%s** just ran out.' % entry)
        if 'ping' in send_type:
            await request_webhook('/{}/{}'.format(channel, token), embeds=[em.to_dict()], content=self.bot.user.mention)
        else:
            await request_webhook('/{}/{}'.format(channel, token), content=None, embeds=[em.to_dict()])

    @commands.group(pass_context=True)
    async def todo(self, ctx):
        """Manage your to-do list. [p]help todo for more information.

        [p]todo - List all of the entries in your to-do list.

        [p]todo add <item> - Add an item to your to-do list. Example: [p]todo add buy bacon

        ---- ADD A TIMER ----
        [p]todo add <item> | <time> - Add an item to your to-do list with a timer. See below for more information.
          - When a timed to-do list item is completed, you will be notified via the webhook you set up for keyword logging.

          - Other possible parameters you can add when you set a timer:
            +  repeat=<n> - repeat timer <n> times. repeat=yes for indefinite.
            +  channel=<channel_id> - sends <item> (or text parameter if given) as a message to this channel when the timer runs out.
               -  Multiple channels are supported as well. Separate the ids with a comma.
               -  To get a channel's id: http://i.imgur.com/KMDS8cb.png then right click channel > copy id.
            +  text=<text> - sends this text (instead of the <item> field) to the channel specified.
            +  alert=off - add this if you don't want to get notified when the timer runs out.

        Example: [p]todo add Get Daily Tatsumaki Credits | 24h1m | text=t!daily | channel=299431230984683520 | repeat=yes | alert=off

        [p]todo remove <item> - Remove an item from your to-do list.
        [p]todo clear - Clear your entire to-do list.

        If you do not have keyword logging set up, go to https://github.com/appu1232/Discord-Selfbot/wiki/Keyword-Notifier---User-Following-Info-and-Setup

        ---------------------------------------------------


        """
        if ctx.invoked_subcommand is None:
            await ctx.message.delete()
            if not self.todo_list:
                await ctx.send(self.bot.bot_prefix + "Your to-do list is empty!")
            else:
                embed = discord.Embed(title="{}'s to-do list:".format(ctx.message.author.name), description="")
                sorted_items = sorted(self.todo_list.items(), key=lambda x: x[1][0] if type(x[1][0]) is float else 0)
                sorted_keys = [item[0] for item in sorted_items]

                description = ''
                all_entries = []

                for entry in sorted_keys:

                    if self.todo_list[entry][0] == "none":
                        embed.description += "\u2022 {}\n".format(entry)
                    elif self.todo_list[entry][0] == "done":
                        embed.description += "\u2022 {} - time's up!\n".format(entry)
                    else:
                        m, s = divmod(self.todo_list[entry][0]-current_time(), 60)
                        h, m = divmod(m, 60)
                        d, h = divmod(h, 24)
                        embed.description += "\u2022 {} - time left: {}\n".format(entry, "%02d:%02d:%02d:%02d" % (int(d), int(h), int(m), int(s)))
                        if entry[1] != 0:
                            if self.todo_list[entry][2] != 0:
                                channels = []
                                if type(self.todo_list[entry][2]) is str:
                                    channel = self.bot.get_channel(int(self.todo_list[entry][2]))
                                    channels.append(channel)
                                else:
                                    for channel in self.todo_list[entry][2]:
                                        chnl = self.bot.get_channel(int(channel.strip()))
                                        channels.append(chnl)
                                for channel in channels:
                                    if channel:
                                        embed.description += '    - Send to channel: #%s \n' % str(channel)
                                    else:
                                        embed.description += '    - Send to channel: Could not find channel. Message will not be sent.\n'
                            m, s = divmod(self.todo_list[entry][5], 60)
                            h, m = divmod(m, 60)
                            d, h = divmod(h, 24)
                            if self.todo_list[entry][4] == 'on':
                                repeat = 'every {}'.format('%02d:%02d:%02d:%02d \n' % (int(d), int(h), int(m), int(s)))
                                embed.description += '    - Repeat: %s' % repeat
                            elif self.todo_list[entry][4] != 0:
                                repeat = '{} more time(s) every {} \n'.format(self.todo_list[entry][4], "%02d:%02d:%02d:%02d" % (int(d), int(h), int(m), int(s)))
                                embed.description += '    - Repeat: %s' % repeat

                        else:
                            embed.description += "\u2022 {} - time left: {}\n".format(entry, "%02d:%02d:%02d:%02d" % (int(d), int(h), int(m), int(s)))

                    if len(embed.description + description) > 2000:
                        all_entries.append(embed)
                        embed = discord.Embed(title="{}'s to-do list:".format(ctx.message.author.name), description="")
                        embed.description = description

                all_entries.append(embed)
                for count, embed in enumerate(all_entries):
                    if len(all_entries) > 1:
                        embed.title = "{}'s to-do list ({}/{}):".format(ctx.message.author.name.format(), count+1, len(all_entries))
                    await ctx.send("", embed=embed)

    @todo.command(pass_context=True)
    async def add(self, ctx, *, msg):
        """Add to your to-do list."""
        await ctx.message.delete()
        seconds = time = "none"
        timer = text = channel = repeat = 0
        alert = True
        if " | " in msg:
            msg = msg.split(" | ")
            if len(msg) > 2:
                for i in msg[1:]:
                    if i.strip().startswith('timer='):
                        timer = i.strip()[6:].strip()
                    elif i.strip().startswith('text='):
                        text = i.strip()[5:].strip()
                    elif i.strip().startswith('channel='):
                        channel = i.strip()[8:].strip()
                    elif i.strip().startswith('alert='):
                        alert = i.strip()[6:].strip()
                    elif i.strip().startswith('repeat='):
                        if i.strip()[7:].strip() == 'on' or i.strip()[7:].strip() == 'yes':
                            repeat = 'on'
                        else:
                            try:
                                repeat = int(i.split('repeat=')[1])
                            except ValueError:
                                repeat = 0
                    else:
                        if timer == 0:
                            timer = i
            else:
                timer = msg[1]

            if ',' in str(channel):
                channel = channel.split(',')
            if timer != 0:
                # taken from kurisu
                units = {
                    "d": 86400,
                    "h": 3600,
                    "m": 60,
                    "s": 1
                }
                seconds = 0
                match = re.findall("([0-9]+[smhd])", timer)
                if match is None:
                    seconds = "none"
                else:
                    for item in match:
                        seconds += (int(item[:-1]) * units[item[-1]])
                    seconds += current_time()

                if text and channel == 0:
                    channel = str(ctx.message.channel.id)
                if channel and text == 0:
                    text = msg[0]
                if alert == 'off' or alert == 'false':
                    alert = False
                time = seconds-current_time()

            self.todo_list[msg[0]] = [seconds, text, channel, alert, repeat, time]
        else:
            self.todo_list[msg] = [seconds, text, channel, alert, repeat, time]
        self.save_list()
        await ctx.send(self.bot.bot_prefix + "Successfully added `{}` to your to-do list!".format(msg))

    @todo.command(pass_context=True)
    async def remove(self, ctx, *, msg):
        """Cross out entries from your to-do list."""
        await ctx.message.delete()
        if not self.todo_list:
            await ctx.send(self.bot.bot_prefix + "Your to-do list is empty!")
        else:
            found = self.todo_list.pop(msg, None)
            if found:
                self.save_list()
                await ctx.send(self.bot.bot_prefix + "Successfully removed `{}` from your to-do list!".format(msg))
            else:
                await ctx.send(self.bot.bot_prefix + "That entry doesn't exist!")

    @todo.command(pass_context=True)
    async def clear(self, ctx):
        """Clear your entire to-do list."""
        await ctx.message.delete()
        self.todo_list.clear()
        self.save_list()
        await ctx.send(self.bot.bot_prefix + "Successfully cleared your to-do list!")

    async def todo_timer(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Todo"):
            for entry in self.todo_list:
                if self.todo_list[entry][0] != "none" and self.todo_list[entry][0] != "done":
                    if self.todo_list[entry][0] < current_time():
                        self.todo_list[entry][0] = "done"

                        if self.todo_list[entry][4] == 'on':
                            self.todo_list[entry][0] = current_time() + self.todo_list[entry][5]
                        elif self.todo_list[entry][4] != 0:
                            self.todo_list[entry][0] = current_time() + self.todo_list[entry][5]
                            self.todo_list[entry][4] = self.todo_list[entry][4]-1
                        else:
                            self.todo_list[entry][0] = "done"
                        try:
                            if self.todo_list[entry][2] != 0:
                                if type(self.todo_list[entry][2]) is list:
                                    for channel in self.todo_list[entry][2]:
                                        chnl = self.bot.get_channel(int(channel.strip()))
                                        await chnl.send(self.todo_list[entry][1])
                                else:
                                    channel = self.bot.get_channel(int(self.todo_list[entry][2]))
                                    await channel.send(self.todo_list[entry][1])
                        except:
                            print('Unable to send message for todo list entry: %s' % entry)

                        self.save_list()

                        if self.todo_list[entry][3] is True:
                            if self.bot.notify['type'] == 'msg':
                                await self.webhook(entry, '')
                            elif self.bot.notify['type'] == 'ping':
                                await self.webhook(entry, 'ping')
                            else:
                                location = self.bot.log_conf['log_location'].split()
                                guild = self.bot.get_guild(int(location[1]))
                                em = discord.Embed(title='Timer Alert', color=0x4e42f4,
                                                   description='Timer for item: **%s** just ran out.' % entry)
                                await guild.get_channel(int(location[0])).send(content=None, embed=em)
            await asyncio.sleep(2)


def setup(bot):
    t = Todo(bot)
    bot.loop.create_task(t.todo_timer())
    bot.add_cog(t)
