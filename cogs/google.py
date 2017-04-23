import discord
from discord.ext import commands
from cogs.utils.checks import *
import aiohttp
from urllib.parse import parse_qs
from lxml import etree

'''Module for google web and image search.'''


# Used Rapptz's implementation of google cards.
class Google:

    def __init__(self, bot):
        self.bot = bot

    def parse_google_card(self, node):
        if node is None:
            return None

        e = discord.Embed(colour=0x0057e7)

        # check if it's a calculator card:
        calculator = node.find(".//table/tr/td/span[@class='nobr']/h2[@class='r']")
        if calculator is not None:
            e.title = 'Calculator'
            e.description = ''.join(calculator.itertext())
            return e

        parent = node.getparent()

        # check for unit conversion card
        unit = parent.find(".//ol//div[@class='_Tsb']")
        if unit is not None:
            e.title = 'Unit Conversion'
            e.description = ''.join(''.join(n.itertext()) for n in unit)
            return e

        # check for currency conversion card
        currency = parent.find(".//ol/table[@class='std _tLi']/tr/td/h2")
        if currency is not None:
            e.title = 'Currency Conversion'
            e.description = ''.join(currency.itertext())
            return e

        # check for release date card
        release = parent.find(".//div[@id='_vBb']")
        if release is not None:
            try:
                e.description = ''.join(release[0].itertext()).strip()
                e.title = ''.join(release[1].itertext()).strip()
                return e
            except:
                return None

        # check for definition card
        words = parent.find(".//ol/div[@class='g']/div/h3[@class='r']/div")
        if words is not None:
            try:
                definition_info = words.getparent().getparent()[1]
            except:
                pass
            else:
                try:
                    e.title = words[0].text
                    e.description = words[1].text
                except:
                    return None
                for row in definition_info:
                    if len(row.attrib) != 0:
                        break
                    try:
                        data = row[0]
                        lexical_category = data[0].text
                        body = []
                        for index, definition in enumerate(data[1], 1):
                            body.append('%s. %s' % (index, definition.text))
                        e.add_field(name=lexical_category, value='\n'.join(body), inline=False)
                    except:
                        continue
                return e

        # check for translate card
        words = parent.find(".//ol/div[@class='g']/div/table/tr/td/h3[@class='r']")
        if words is not None:
            e.title = 'Google Translate'
            e.add_field(name='Input', value=words[0].text,  inline=True)
            e.add_field(name='Out', value=words[1].text,  inline=True)
            return e

        # check for "time in" card
        time_in = parent.find(".//ol//div[@class='_Tsb _HOb _Qeb']")
        if time_in is not None:
            try:
                time_place = ''.join(time_in.find("span[@class='_HOb _Qeb']").itertext()).strip()
                the_time = ''.join(time_in.find("div[@class='_rkc _Peb']").itertext()).strip()
                the_date = ''.join(time_in.find("div[@class='_HOb _Qeb']").itertext()).strip()
            except:
                return None
            else:
                e.title = time_place
                e.description = '%s\n%s' % (the_time, the_date)
                return e

        weather = parent.find(".//ol//div[@class='e']")
        if weather is None:
            return None

        location = weather.find('h3')
        if location is None:
            return None

        e.title = ''.join(location.itertext())

        table = weather.find('table')
        if table is None:
            return None

        try:
            tr = table[0]
            img = tr[0].find('img')
            category = img.get('alt')
            image = 'https:' + img.get('src')
            temperature = tr[1].xpath("./span[@class='wob_t']//text()")[0]
        except:
            return None
        else:
            e.set_thumbnail(url=image)
            e.description = '*%s*' % category
            e.add_field(name='Temperature', value=temperature)

        try:
            wind = ''.join(table[3].itertext()).replace('Wind: ', '')
        except:
            return None
        else:
            e.add_field(name='Wind', value=wind)

        try:
            humidity = ''.join(table[4][0].itertext()).replace('Humidity: ', '')
        except:
            return None
        else:
            e.add_field(name='Humidity', value=humidity)

        return e

    async def get_google_entries(self, query):
        params = {
            'q': query,
            'safe': 'off'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
        }
        entries = []
        card = None
        async with aiohttp.get('https://www.google.com/search', params=params, headers=headers) as resp:
            if resp.status != 200:
                config = load_optional_config()
                async with aiohttp.get("https://www.googleapis.com/customsearch/v1?q=" + query.replace(' ', '+') + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine']) as resp:
                    result = json.loads(await resp.text())
                return None, result['items'][0]['link']

            root = etree.fromstring(await resp.text(), etree.HTMLParser())
            card_node = root.find(".//div[@id='topstuff']")
            card = self.parse_google_card(card_node)
            search_nodes = root.findall(".//div[@class='g']")
            for node in search_nodes:
                url_node = node.find('.//h3/a')
                if url_node is None:
                    continue
                url = url_node.attrib['href']
                if not url.startswith('/url?'):
                    continue
                url = parse_qs(url[5:])['q'][0]
                entries.append(url)
        return card, entries

    @commands.command(pass_context=True)
    async def g(self, ctx, *, query):
        """Google web search. Ex: >g what is discordapp?"""
        if not embed_perms(ctx.message):
            config = load_optional_config()
            async with aiohttp.get("https://www.googleapis.com/customsearch/v1?q=" + query.replace(' ', '+') + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine']) as resp:
                result = json.loads(await resp.text())
            return await self.bot.send_message(ctx.message.channel, result['items'][0]['link'])
        try:
            card, entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await self.bot.send_message(ctx.message.channel, str(e))
        else:
            if card:
                value = '\n'.join(entries[:2])
                if value:
                    card.add_field(name='Search Results', value=value, inline=False)
                return await self.bot.send_message(ctx.message.channel, embed=card)
            if len(entries) == 0:
                return await self.bot.send_message(ctx.message.channel, 'No results.')
            next_two = entries[1:3]
            if next_two:
                formatted = '\n'.join(map(lambda x: '<%s>' % x, next_two))
                msg = '{}\n\n**See also:**\n{}'.format(entries[0], formatted)
            else:
                msg = entries[0]
            await self.bot.send_message(ctx.message.channel, msg)

    @commands.command(pass_context=True)
    async def i(self, ctx, *, query):
        """Google image search. >i Lillie pokemon sun and moon"""
        config = load_optional_config()
        if query[0].isdigit():
            item = int(query[0])
            query = query[1:]
        else:
            item = 0
        async with aiohttp.get("https://www.googleapis.com/customsearch/v1?q=" + query.replace(' ', '+') + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine'] + "&searchType=image") as resp:
            if resp.status != 200:
                await self.bot.send_message(ctx.message.channel, 'Google failed to respond.')
            result = json.loads(await resp.text())
            em = discord.Embed()
            if embed_perms(ctx.message):
                await self.bot.send_message(ctx.message.channel, content=None, embed=em.set_image(url=result['items'][item]['link']))
            else:
                await self.bot.send_message(ctx.message.channel, result['items'][item]['link'])
        await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(Google(bot))
