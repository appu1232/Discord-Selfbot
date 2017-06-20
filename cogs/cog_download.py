import discord
import os
import requests
from discord.ext import commands
from bs4 import BeautifulSoup
from appuselfbot import bot_prefix

"""Cog for cog downloading."""

class CogDownloading:
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(pass_context=True)
    async def cog(self, ctx):
        """Manage custom cogs. >help cog for more information.
        >cog install <cog> - Install a custom cog from the server.
        >cog uninstall <cog> - Uninstall one of your custom cogs.
        >cog list - List all cogs on the server.
        >cog view <cog> - View information about a cog.
        If you would like to add a custom cog to the server, see http://appucogs.tk
        """
        if ctx.invoked_subcommand is None:
            await self.bot.delete_message(ctx.message)
            await self.bot.send_message(ctx.message.channel, bot_prefix + "Invalid usage. >cog <install/uninstall> <cog>")
        
                
    @cog.command(pass_context=True)
    async def install(self, ctx, cog):
        """Install a custom cog from the server."""
        def check(msg):
            if msg:
                return msg.content.lower().strip() == 'y' or msg.content.lower().strip() == 'n'
            else:
                return False
                
        await self.bot.delete_message(ctx.message)
        response = requests.get("http://appucogs.tk/cogs/{}.json".format(cog))
        if response.status_code == 404:
            await self.bot.send_message(ctx.message.channel, bot_prefix + "That cog couldn't be found on the network. Check your spelling and try again.")
        else:
            cog = response.json()
            embed = discord.Embed(title=cog["title"], description=cog["description"])
            embed.set_author(name=cog["author"])
            await self.bot.send_message(ctx.message.channel, bot_prefix + "Are you sure you want to download this cog? (y/n)", embed=embed)
            reply = await self.bot.wait_for_message(author=ctx.message.author, check=check)
            if reply.content.lower() == "y":
                download = requests.get(cog["link"]).text
                filename = cog["link"].rsplit("/", 1)[1]
                with open("cogs/" + filename, "wb+") as f:
                    f.write(download.encode("utf-8"))
                await self.bot.send_message(ctx.message.channel, bot_prefix + "Successfully downloaded `{}` to your cogs folder. Run the `load cogs.{}` command to load in your cog.".format(cog["title"], filename.rsplit(".", 1)[0]))
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + "Didn't download `{}`: user cancelled.".format(cog["title"]))
    
    @cog.command(pass_context=True)
    async def uninstall(self, ctx, cog):
        """Uninstall one of your custom cogs."""
        def check(msg):
            if msg:
                return msg.content.lower().strip() == 'y' or msg.content.lower().strip() == 'n'
            else:
                return False
                
        await self.bot.delete_message(ctx.message)
        response = requests.get("http://appucogs.tk/cogs/{}.json".format(cog))
        if response.status_code == 404:
            await self.bot.send_message(ctx.message.channel, bot_prefix + "That's not a real cog!")
        else:
            found_cog = response.json()
            if os.path.isfile("cogs/" + cog + ".py"):
                embed = discord.Embed(title=found_cog["title"], description=found_cog["description"])
                embed.set_author(name=found_cog["author"])
                await self.bot.send_message(ctx.message.channel, bot_prefix + "Are you sure you want to delete this cog? (y/n)", embed=embed)
                reply = await self.bot.wait_for_message(author=ctx.message.author, check=check)
                if reply.content.lower() == "y":
                    os.remove("cogs/" + cog + ".py")
                    await self.bot.send_message(ctx.message.channel, bot_prefix + "Successfully deleted the `{}` cog.".format(found_cog["title"]))
                else:
                    await self.bot.send_message(ctx.message.channel, bot_prefix + "Didn't delete `{}`: user cancelled.".format(found_cog["title"]))
            else:
                await self.bot.send_message(ctx.message.channel, bot_prefix + "You don't have `{}` installed!".format(found_cog["title"]))
    
    @cog.command(pass_context=True)
    async def list(self, ctx):
        """List all cogs on the server."""
        await self.bot.delete_message(ctx.message)
        site = requests.get('https://github.com/LyricLy/Selfbot-Cogs/tree/master/cogs').text
        soup = BeautifulSoup(site, "lxml")
        data = soup.find_all(attrs={"class": "js-navigation-open"})
        list = []
        for a in data:
            list.append(a.get("title"))
        embed = discord.Embed(title="Cog list", description="")
        for entry in list[2:]:
            entry = entry.rsplit(".")[0]
            if os.path.isfile("cogs/" + entry + ".py"):
                embed.description += "• {} - installed\n".format(entry)
            else:
                embed.description += "• {} - not installed\n".format(entry)
        await self.bot.send_message(ctx.message.channel, "", embed=embed)
        
    @cog.command(pass_context=True)
    async def view(self, ctx, cog):
        """View information about a cog."""
        await self.bot.delete_message(ctx.message)
        response = requests.get("http://appucogs.tk/cogs/{}.json".format(cog))
        if response.status_code == 404:
            await self.bot.send_message(ctx.message.channel, bot_prefix + "That cog couldn't be found on the network. Check your spelling and try again.")
        else:
            cog = response.json()
            embed = discord.Embed(title=cog["title"], description=cog["description"])
            embed.set_author(name=cog["author"])
            await self.bot.send_message(ctx.message.channel, embed=embed)
            
    @cog.command(pass_context=True)
    async def update(self, ctx):
        """Update all of your installed cogs."""
        await self.bot.delete_message(ctx.message)
        msg = await self.bot.send_message(ctx.message.channel, bot_prefix + "Updating...")
        site = requests.get('https://github.com/LyricLy/Selfbot-Cogs/tree/master/cogs').text
        soup = BeautifulSoup(site, "lxml")
        data = soup.find_all(attrs={"class": "js-navigation-open"})
        list = []
        for a in data:
            list.append(a.get("title"))
        embed = discord.Embed(title="Cog list", description="")
        for entry in list[2:]:
            entry = entry.rsplit(".")[0]
            if os.path.isfile("cogs/" + entry + ".py"):
                link = requests.get("http://appucogs.tk/cogs/{}.json".format(entry)).json()["link"]
                download = requests.get(link).text
                filename = link.rsplit("/", 1)[1]
            with open("cogs/" + filename, "wb+") as f:
                f.write(download.encode("utf-8"))
        await self.bot.edit_message(msg, bot_prefix + "Updated all cogs.")
        
def setup(bot):
    bot.add_cog(CogDownloading(bot))