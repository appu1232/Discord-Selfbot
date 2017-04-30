import datetime
import asyncio
import strawpy
import random
import re
import sys
import subprocess
from datetime import datetime
from PythonGists import PythonGists
from appuselfbot import bot_prefix
from discord.ext import commands
from cogs.utils.checks import *

'''Module for miscellaneous commands'''


class Imagedump:

    def __init__(self, bot):
        self.bot = bot

    def check_images(self, message, images):
        if message.attachments:
            for item in message.attachments:
                if item['url'] != '' and item['url'] not in images:
                    return item['url']

        elif message.embeds:
            for data in message.embeds:
                try:
                    url = data['thumbnail']['url']
                    if (url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webm')) or data['type'] in {'jpg', 'jpeg', 'png', 'gif', 'gifv', 'webm', 'image'}) and url not in images:
                        return url
                except:
                    pass

        else:
            urls = []
            try:
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
            except:
                pass

            if urls is not []:
                for url in urls:
                    if url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webm')) and url not in images:
                        return url

        return None

    @commands.group(pass_context=True)
    async def imagedump(self, ctx):
        if ctx.invoked_subcommand is None:
            if ctx.message.content[11:].strip():
                if ctx.message.content[11] == 's':
                    silent = True
                    msg = ctx.message.content[13:].strip()
                else:
                    silent = False
                    msg = ctx.message.content[11:].strip()
                before = None
                after = None
                size = None
                images = None

                if msg.isdigit():
                    limit = int(msg)+1
                # elif 'before=' in msg or 'after=' in msg or 'images=' in msg:
                #     if 'before=' in msg:
                #         before = msg.split('before=')[1]
                #         if ' ' in before:
                #             before = before.split(' ')[0]
                #         before = datetime.strptime()
                #     pass

                else:
                    return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax. ``>imagedump <n>`` where n is the number of messages to search in this channel. '
                                                                                  'Ex: ``>imagedump 100``\n``>imagedump dir path/to/directory`` if you want to change where images are saved.')
                await self.bot.delete_message(ctx.message)
                with open('settings/optional_config.json', 'r+') as fp:
                    opt = json.load(fp)
                    if 'image_dump_delay' not in opt:
                        opt['image_dump_delay'] = "0"
                    fp.seek(0)
                    fp.truncate()
                    json.dump(opt, fp, indent=4)
                if 'image_dump_location' not in opt:
                    path = ''
                else:
                    path = opt['image_dump_location']
                if not os.path.exists('{}image_dump'.format(path)):
                    os.makedirs('{}image_dump'.format(path))
                try:
                    new_dump = time.strftime("%Y-%m-%dT%H_%M_%S_") + ctx.message.channel.name + '_' + ctx.message.server.name
                except:
                    new_dump = time.strftime("%Y-%m-%dT%H_%M_%S_")
                new_dump = "".join([x if x.isalnum() else "_" for x in new_dump])
                new_dump.replace('/', '_')
                os.makedirs('{}image_dump/{}'.format(path, new_dump))
                if not silent:
                    await self.bot.send_message(ctx.message.channel, bot_prefix + 'Downloading all images/gifs/webms from the last {} messages in this channel...\nSaving to ``image_dump/{}`` Check console for progress.'.format(msg, new_dump))
                start = time.time()
                images = []
                print('Fetching last %s messages...' % msg)
                async for message in self.bot.logs_from(ctx.message.channel, limit=limit):

                    url = self.check_images(message, images)

                    if url:
                        images.append(url)

                with open('cogs/utils/urls{}.txt'.format(new_dump), 'w') as fp:
                    for url in images:
                        fp.write(url + '\n')

                args = [sys.executable, 'cogs/utils/image_dump.py', path, new_dump, opt['image_dump_delay']]
                p = subprocess.Popen(args)
                self.bot.imagedumps.append(p)

                while p.poll() is None:
                    await asyncio.sleep(1)

                try:
                    with open('cogs/utils/finished{}.txt'.format(new_dump), 'r') as fp:
                        stop = float(fp.readline())
                        total = fp.readline()
                        failures = fp.readline()
                        size = fp.readline()
                except:
                    return print('Something went wrong when saving items and the download was stopped. Error posted above.')
                try:
                    os.remove('cogs/utils/finished{}.txt'.format(new_dump))
                except:
                    pass
                if int(failures) != 0:
                    if not silent:
                        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Done! ``{}`` items downloaded. ``{}`` However, ``{}`` items failed to download. Check your console for more info on which ones were missed. '
                                                                                      'Finished in: ``{} seconds.``'.format(str(total), size, str(failures), str(round(stop - start, 2))))
                    else:
                        print('{} items failed to download. See above for missed links. '
                              'Finished in: {} seconds.'.format(str(failures), str(round(stop - start, 2))))
                else:
                    if not silent:
                        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Done! ``{}`` items downloaded. ``{}`` Finished in: ``{} seconds.``'.format(str(total), size, str(round(stop-start, 2))))
                    else:
                        print('Finished in: {} seconds'.format(str(round(stop-start, 2))))
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid syntax. ``>imagedump <n>`` where n is the number of messages to search in this channel. '
                                                                              'Ex: ``>imagedump 100``\n``>imagedump dir path/to/directory`` if you want to change where images are saved.')

    @imagedump.command(pass_context=True)
    async def dir(self, ctx, *, msg):
        msg = msg.strip() if msg.strip().endswith('/') else msg.strip() + '/'
        if os.path.exists(msg):
            if not os.path.exists('{}image_dump'.format(msg)):
                os.makedirs('{}image_dump'.format(msg))
            with open('settings/optional_config.json', 'r+') as fp:
                opt = json.load(fp)
                opt['image_dump_location'] = msg
                fp.seek(0)
                fp.truncate()
                json.dump(opt, fp, indent=4)
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Successfully set path. Images will be saved to: ``{}image_dump/``'.format(msg))
        else:
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid path. Try again. Example: ``>imagedump dir C:/Users/Bill/Desktop``')

    @imagedump.command(pass_context=True, aliases=['stop'])
    async def cancel(self, ctx):
        for i in self.bot.imagedumps:
            i.kill()
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled all imagedump processes currently running.')
        print('Imagedump forcibily cancelled.')


def setup(bot):
    bot.add_cog(Imagedump(bot))
