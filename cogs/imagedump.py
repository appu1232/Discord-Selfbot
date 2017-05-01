import datetime
import asyncio
import re
import sys
import subprocess
from datetime import datetime
from appuselfbot import bot_prefix
from discord.ext import commands
from cogs.utils.checks import *

'''Module for miscellaneous commands'''


class Imagedump:

    def __init__(self, bot):
        self.bot = bot

    def check_images(self, message, images, type_of_items):
        if message.attachments:
            for item in message.attachments:
                if item['url'] != '' and item['url'] not in images:
                    for i in type_of_items:
                        if item['url'].endswith(i.strip()):
                            return item['url']

        elif message.embeds:
            for data in message.embeds:
                try:
                    url = data['thumbnail']['url']
                    if (url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webm')) or data['type'] in {'jpg', 'jpeg', 'png', 'gif', 'gifv', 'webm', 'image'}) and url not in images:
                        for i in type_of_items:
                            if url.endswith(i.strip()):
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
                        for i in type_of_items:
                            if url.endswith(i.strip()):
                                return url

        return None

    @commands.group(pass_context=True)
    async def imagedump(self, ctx):
        if ctx.invoked_subcommand is None:
            error = 'Invalid syntax. ``>imagedump <n>`` where n is the number of messages to search in this channel. Ex: ``>imagedump 100``\n``>imagedump dir path/to/directory`` if you want to change where images are saved.'
            if ctx.message.content[11:].strip():
                if ctx.message.content[11] == 's':
                    silent = True
                    msg = ctx.message.content[13:].strip()
                else:
                    silent = False
                    msg = ctx.message.content[11:].strip()
                before = None
                after = None
                limit_images = None
                type_of_items = ['jpg', 'jpeg', 'png', 'gif', 'gifv', 'webm']
                x = y = dimx = dimy = 'None'
                fixed = 'no'

                before_msg = after_msg = limit_images_msg = type_of_items_msg = dimensions_msg = ratio_msg = channel_msg = ''

                simple = True
                channel = ctx.message.channel
                if ' | ' not in msg:
                    if msg.isdigit():
                        limit = int(msg) + 1
                    else:
                        return await self.bot.send_message(ctx.message.channel, bot_prefix + error)
                else:
                    simple = False
                    msg = msg.split(' | ')
                    if msg[0].strip().isdigit():
                        limit = int(msg[0].strip()) + 1
                    else:
                        return await self.bot.send_message(ctx.message.channel, bot_prefix + error)
                    for i in msg:
                        if i.strip().lower().startswith('items='):
                            limit_images = i.strip()[6:].strip()
                            if limit_images.isdigit():
                                limit_images_msg = 'Up to {} items. '.format(limit_images)
                                limit_images = int(limit_images)
                            else:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``items=`` should be the number of images. Ex: ``>imagedump 500 | items=10``')
                        if i.strip().lower().startswith('dim='):
                            dimensions = i.strip()[4:].strip()
                            if 'x' not in dimensions:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``dim=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim=1920x1080``')
                            x, y = dimensions.split('x')
                            if not x.strip().isdigit() or not y.strip().isdigit():
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``dim=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim=1920x1080``')
                            else:
                                x, y = x.strip(), y.strip()
                                fixed = 'yes'
                                dimensions_msg = 'Dimensions: {}. '.format(dimensions)

                        if i.strip().lower().startswith('dim>='):
                            dimensions = i.strip()[5:].strip()
                            if 'x' not in dimensions:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``dim>=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim>=1920x1080``')
                            x, y = dimensions.split('x')
                            if not x.strip().isdigit() or not y.strip().isdigit():
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``dim>=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim>=1920x1080``')
                            else:
                                x, y = x.strip(), y.strip()
                                fixed = 'more'
                                dimensions_msg = 'Dimensions: {} or larger. '.format(dimensions)

                        if i.strip().lower().startswith('dim<='):
                            dimensions = i.strip()[5:].strip()
                            if 'x' not in dimensions:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``dim<=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim<=1920x1080``')
                            x, y = dimensions.split('x')
                            if not x.strip().isdigit() or not y.strip().isdigit():
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``dim<=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim<=1920x1080``')
                            else:
                                x, y = x.strip(), y.strip()
                                fixed = 'less'
                                dimensions_msg = 'Dimensions: {} or smaller. '.format(dimensions)

                        if i.strip().lower().startswith('ratio='):
                            ratio = i.strip()[6:].strip()
                            if ':' not in ratio:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``ratio=`` should be the ratio of the image in the form w:h. Ex: ``>imagedump 500 | ratio=16:9``')
                            dimx, dimy = ratio.split(':')
                            if not dimx.strip().isdigit() or not dimy.strip().isdigit():
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``ratio=`` should be the ratio of the image in the form w:h. Ex: ``>imagedump 500 | ratio=16:9``')
                            else:
                                dimx, dimy = dimx.strip(), dimy.strip()
                                ratio_msg = 'Ratio: {}.'.format(ratio)

                        if i.strip().lower().startswith('before='):
                            try:
                                date = i.strip()[7:].strip()
                                before = datetime.strptime(date, '%Y-%m-%d')
                                before_msg = 'Before: {} '.format(date)
                            except:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``before=`` should be a date in the format YYYY-MM-DD. Ex: ``>imagedump 500 | before=2017-02-15``')

                        if i.strip().lower().startswith('after='):
                            try:
                                date = i.strip()[6:].strip()
                                after = datetime.strptime(date, '%Y-%m-%d')
                                after_msg = 'After: {} '.format(date)
                            except:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid Syntax. ``after=`` should be a date in the format YYYY-MM-DD. Ex: ``>imagedump 500 | after=2017-02-15``')

                        if i.strip().lower().startswith('type='):
                            type = i.strip()[5:].strip()
                            if ',' in type:
                                type_of_items = type.split(',')
                            else:
                                type_of_items = [type]
                            for i in type_of_items:
                                if 'png' in i or 'jpg' in i or 'gif' in i or 'webm' in i:
                                    pass
                                else:
                                    return await self.bot.send_message(ctx.message.channel,
                                                                       bot_prefix + 'Invalid Syntax. ``type=`` should be tye type(s) of items to download. Ex: ``>imagedump 500 | type=png`` or ``>imagedump 500 | type=png, gif``')
                            if 'jpg' in type_of_items or '.jpg' in type_of_items:
                                type_of_items.append('.jpeg')
                            type_of_items_msg = 'Types: ' + type

                        if i.strip().lower().startswith('channel='):
                            channel = i.strip()[8:].strip()
                            channel = self.bot.get_channel(channel)
                            if not channel:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Channel not found. Are you using the right syntax? ``channel=`` should be the channel id. '
                                                                                                     'Ex: ``>imagedump 500 | channel=299431230984683520``')
                            channel_msg = 'Channel: {}'.format(channel.name)

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
                    which_channel = 'in this channel...'
                    if ctx.message.channel != channel:
                        which_channel = 'in channel ``{}``'.format(channel.name)
                    if not simple:
                        params = 'Parameters: ``{}{}{}{}{}{}{}``'.format(limit_images_msg, before_msg, after_msg, dimensions_msg, ratio_msg, type_of_items_msg, channel_msg)
                    else:
                        params = ''
                    await self.bot.send_message(ctx.message.channel, bot_prefix + 'Downloading all images/gifs/webms from the last {} messages {}\nSaving to ``image_dump/{}`` Check console for progress.\n{}'.format(str(limit-1), which_channel, new_dump, params))
                start = time.time()
                images = []
                print('Fetching last %s messages...' % str(limit-1))
                async for message in self.bot.logs_from(channel, limit=limit, before=before, after=after):

                    url = self.check_images(message, images, type_of_items)

                    if url:
                        images.append(url)

                    if len(images) == limit_images:
                        break

                with open('cogs/utils/urls{}.txt'.format(new_dump), 'w') as fp:
                    for url in images:
                        fp.write(url + '\n')

                args = [sys.executable, 'cogs/utils/image_dump.py', path, new_dump, opt['image_dump_delay'], x, y, dimx, dimy, fixed]
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
    async def dir(self, ctx, *, msg: str = None):
        if msg:
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
        else:
            with open('settings/optional_config.json', 'r') as fp:
                opt = json.load(fp)
                if 'image_dump_location' not in opt:
                    path = os.path.abspath("settings")[:-8] + 'image_dump'
                else:
                    path = opt['image_dump_location'] + 'image_dump'
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Current imagedump download location: ``{}``'.format(path.replace('\\', '/')))

    @imagedump.command(pass_context=True, aliases=['stop'])
    async def cancel(self, ctx):
        for i in self.bot.imagedumps:
            i.kill()
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled all imagedump processes currently running.')
        print('Imagedump forcibily cancelled.')


def setup(bot):
    bot.add_cog(Imagedump(bot))
