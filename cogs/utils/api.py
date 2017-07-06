import requests
from cogs.utils.checks import get_user_token, get_bot_token

"""
'accept': '*/*',
'cache-control': 'no-cache',
'pragma': 'no-cache',
'origin': 'https://discordapp.com',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.297 Chrome/53.0.2785.143 Discord/1.4.12 Safari/537.36',
'authority': 'discordapp.com',
'accept-encoding': 'gzip, deflate',
'accept-language': 'en-US',
'x-super-properties': 'eyJvc9',
'$cookie': '',
'x-context-properties': 'asdas=',
'referer': 'https://discordapp.com/channels/0/0',
'content-length': '0',
"""

class api:

    def get(url, token=get_user_token()):
        head = {'authorization': token}
        return requests.get(url, headers=head)

    def put(url, data, token=get_user_token()):
        head = {
            'content-type': 'application/json',
            'authorization': token
        }
        return requests.put(url, data=data, headers=head)

    def delete(url, token=get_user_token()):
        head = {'authorization': token}
        return requests.delete(url, headers=head)

    def post(url, data, token=get_user_token()):
        head = {
            'content-type': 'application/json',
            'authorization': token
        }
        return requests.post(url, data=data, headers=head)

# Convinient Functions

def block_user(id):
    return api.put("https://discordapp.com/api/v6/users/@me/relationships/"+id, data='{"type":2}')

def unblock_user(id):
    return api.delete("https://discordapp.com/api/v6/users/@me/relationships/"+id)

def get_user_info(id):
    return api.get("https://discordapp.com/api/v6/users/"+id, token=get_bot_token())
