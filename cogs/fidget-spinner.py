import discord
from discord.ext import commands
from .utils import checks
import time
from PIL import Image
import requests
from io import BytesIO


class FidgetSpinner:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=False, no_pm=True)
    async def spin(self, url=None):
        if url is not None:
            response = requests.get(url)
            im = Image.open(BytesIO(response.content))
            im = self.resize_and_binarize(im)
        else:
            im = Image.open("data/fidget-spinner/spinner.png")
        txt = self.pixelize(im)
        msg = await self.bot.say(txt)
        for deg in range(0, 720, 90):
            im = im.rotate(deg)
            txt = self.pixelize(im)
            t = time.time()
            await self.bot.edit_message(msg, txt)
            time.sleep(max(.5 - (time.time() - t), 0))  # wait remainder of .5 seconds

    @staticmethod
    def pixelize(im):
        msg = "```\n"
        size = im.size
        for rownum in range(size[1]):
            line = []
            for colnum in range(size[0]):
                if im.getpixel((colnum, rownum)):
                    line.append(' '),
                else:
                    line.append('#'),
            msg += ''.join(line) + '\n'
        msg += '```'
        return msg

    @staticmethod
    def resize_and_binarize(im: Image):
        im = im.convert('1')
        im = im.resize((25, 25))
        return im


def setup(bot):
    n = FidgetSpinner(bot)
    bot.add_cog(n)
