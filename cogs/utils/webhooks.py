# coding=utf-8
"""
discord.webhooks
~~~~~~~~~~~~~~~~~~~

Webhooks Extension to discord.py

:copyright: (c) 2017 AraHaan
:license: MIT, see LICENSE for more details.

"""
import discord
import asyncio
import aiohttp

__all__ = ['Webhook', 'WebHookRoute']


class WebHookRoute:
    """Resolves the route to webhook urls."""
    BASE = 'https://canary.discordapp.com/api/webhooks'

    def __init__(self, method, path):
        self.path = path
        self.method = method
        if self.BASE not in self.path:
            self.url = (self.BASE + self.path)
        else:
            self.url = self.path

    @property
    def bucket(self):
        # the bucket is just method + path w/ major parameters
        return '{0.method}:{0.path}'.format(self)


class Webhook:
    """Class for interacting with webhooks."""
    def __init__(self, bot):
        self.http = bot.http
        self.partialurl = None
        self.content = None
        self.username = None
        self.avatar_url = None
        self.tts = False
        self.file = None
        self.embeds = None
        self.payload = {}
        self.create_form_data = False
        self.form = None

    @asyncio.coroutine
    def request_webhook(self, partialurl, content=None, username=None,
                        avatar_url=None, tts=False, file=None, embeds=None,
                        filename=None):
        """Requests an webhook with the data provided to this function."""
        if self.create_form_data:
            self.create_form_data = False
        self.partialurl = partialurl
        self.content = content
        self.username = username
        self.avatar_url = avatar_url
        self.tts = tts
        self.file = file
        self.embeds = embeds
        if filename is None:
            filename = 'image.jpg'
        if self.partialurl is not None:
            if self.content is not None:
                self.payload['content'] = self.content
            if self.username is not None:
                self.payload['username'] = self.username
            if self.avatar_url is not None:
                self.payload['avatar_url'] = self.avatar_url
            if self.tts:
                self.payload['tts'] = self.tts
            if self.file is not None:
                self.create_form_data = True
            if self.embeds is not None:
                self.payload['embeds'] = self.embeds
            if self.create_form_data:
                self.form = aiohttp.FormData()
                self.form.add_field('payload_json', discord.utils.to_json(self.payload))
                self.form.add_field('file', self.file, filename=filename, content_type='multipart/form-data')
                yield from self.http.request(
                        WebHookRoute(
                            'POST',
                            self.partialurl),
                        data=self.form)
            else:
                yield from self.http.request(
                        WebHookRoute(
                            'POST',
                            self.partialurl),
                        json=self.payload)
