import collections
import time
import json

selflog = collections.deque(maxlen=200)
alllog = {}
oldtime = time.time()


def load_selflog():
    return selflog


def add_selflog(message):
    selflog.append(message)


def remove_selflog():
    return selflog.pop()


def load_alllog():
    return alllog


def add_alllog(channel, server, message):
    if channel + ' ' + server in alllog:
        alllog[channel + ' ' + server].append(message)
    else:
        with open('utils/log.json') as f:
            config = json.load(f)
            alllog[channel + ' ' + server] = collections.deque(maxlen=int(config['log_size']))
            alllog[channel + ' ' + server].append(message)


def remove_alllog(channel, server):
    del alllog[channel + ' ' + server]

# def load_keywordslog():
#     return keywordlog
