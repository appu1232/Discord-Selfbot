import discord
from discord.ext import commands
import os
import json
import aiohttp
import traceback

class Git:
    '''Github Cog, returns github token and username'''
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @property
    def githubtoken(self):
        '''
        Returns your token wherever it is

        This token can give any user complete access to the account.
        https://github.com/settings/tokens is where you make a token.
        '''
        
        return os.environ.get('GITHUBTOKEN')

    async def githubusername(self):
        '''Returns Github Username'''
        async with self.session.get('https://api.github.com/user', headers={"Authorization": "Bearer {}".format(self.githubtoken)}) as resp: #get username 
            if 300 > resp.status >= 200:
                return (await resp.json())['login']
            if resp.status == 401: #invalid token!
                return None
        
    async def __local_check(self, ctx):
        if self.githubtoken is None:
            await ctx.send('Github token not provided.', delete_after=10)
            return False
        return True

 
def setup(bot):
    bot.add_cog(Git(bot))
