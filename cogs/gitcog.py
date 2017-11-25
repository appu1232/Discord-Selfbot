import discord
from discord.ext import commands
import os
import json
import aiohttp
import traceback

class Git:
    '''Github Cog, facilitates viewing and creating issues'''
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
        async with self.session.get('https://api.github.com/user', headers={"Authorization": f"Bearer {self.githubtoken}"}) as resp: #get username 
            if 300 > resp.status >= 200:
                return (await resp.json())['login']
            if resp.status == 401: #invalid token!
                return None

    async def starred(self, repo):
        async with self.session.get('https://api.github.com/user/starred/' + repo, headers={"Authorization": f"Bearer {self.githubtoken}"}) as resp:
            if resp.status == 204:
                return True
            if resp.status == 404:
                return False
        
    async def __local_check(self, ctx):
        if self.githubtoken is None:
            await ctx.send('Github token not provided.', delete_after=10)
            return False
        return True

 
def setup(bot):
    bot.add_cog(Git(bot))
