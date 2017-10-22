import asyncio
import tokage
import sys

list_of_ids = sys.argv[1:]

async def find_chars(all_ids):
    tok = tokage.Client()

    for id in all_ids:
        character = await tok.get_character(id)
        if character.name:
            print(character.name + ' | ' + str(character.favorites) + '\n')

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(find_chars(list_of_ids))
except:
    pass
loop.close()