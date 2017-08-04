import discord
from discord.ext import commands
import json


class FriendCodes:

    def __init__(self, bot):
        self.bot = bot
        try:
            with open("settings/fc.json", encoding='utf-8') as fc:
                self.data = json.load(fc)
        except FileNotFoundError:
            self.data = {}

    async def simple_embed(self, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = text
        await self.bot.say("", embed=embed)

    @commands.group(pass_context=True)
    async def fc(self, ctx):
        """Do >help fc for more information. Lists all your friend codes that are saved in settings/fc.json."""
        if ctx.invoked_subcommand is None:
            await self.bot.delete_message(ctx.message)
            embed = discord.Embed(title="My Friend Codes", colour=16715760)
            if self.data["ds_fc"]:
                embed.add_field(name="3DS", value=self.data["ds_fc"], inline=False)
            if self.data["switch_fc"]:
                embed.add_field(name="Switch", value=self.data["switch_fc"], inline=False)
            if self.data["bnet_fc"]:
                embed.add_field(name="Battle.Net", value=self.data["bnet_fc"], inline=False)
            if self.data["steam_fc"]:
                embed.add_field(name="Steam", value=self.data["steam_fc"], inline=False)
            if self.data["psn_fc"]:
                embed.add_field(name="PSN", value=self.data["psn_fc"], inline=False)
            if self.data["xbox_fc"]:
                embed.add_field(name="Xbox Live", value=self.data["xbox_fc"], inline=False)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        
    @fc.command(pass_context=True)
    async def ds(self, ctx):
        """3ds Friend Code"""
        await self.bot.delete_message(ctx.message)
        if self.data["ds_fc"]:
            embed = discord.Embed(title="3DS Friend Code", colour=13506590)
            embed.description = self.data["ds_fc"]
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "You don't have a 3DS Friend Code registered!")
    
    @fc.command(pass_context=True)
    async def switch(self, ctx):
        """Switch Friend Code"""
        await self.bot.delete_message(ctx.message)
        if self.data["switch_fc"]:
            embed = discord.Embed(title="Switch Friend Code", colour=7631988)
            embed.description = self.data["switch_fc"]
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "You don't have a Switch Friend Code registered!")
    
    @fc.command(pass_context=True)
    async def bnet(self, ctx):
        """Battle.Net Address"""
        await self.bot.delete_message(ctx.message)
        if self.data["bnet_fc"]:
            embed = discord.Embed(title="Battle.Net Address", colour=4362438)
            embed.description = self.data["bnet_fc"]
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "You don't have a Battle.Net Address registered! ")
    
    @fc.command(pass_context=True)
    async def psn(self, ctx):
        """Playstation Network Account"""
        await self.bot.delete_message(ctx.message)
        if self.data["psn_fc"]:
            embed = discord.Embed(title="Playstation Network Account", colour=807811)
            embed.description = self.data["psn_fc"]
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "You don't have a Playstation Network Account registered!")
    
    @fc.command(pass_context=True)
    async def steam(self, ctx):
        """Steam Account"""
        await self.bot.delete_message(ctx.message)
        if self.data["steam_fc"]:
            embed = discord.Embed(title="Steam Account", colour=13553358)
            embed.description = self.data["steam_fc"]
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "You don't have a Steam Account registered!")
        
    @fc.command(pass_context=True)
    async def xbox(self, ctx):
        """Xbox Live Account"""
        await self.bot.delete_message(ctx.message)
        if self.data["xbox_fc"]:
            embed = discord.Embed(title="Xbox Live Account", colour=32811)
            embed.description = self.data["xbox_fc"]
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + "You don't have an Xbox Live Account registered!")
        
def setup(bot):
    bot.add_cog(FriendCodes(bot))