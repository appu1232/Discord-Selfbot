import collections

selflog = collections.deque(maxlen=200)
alllog = {}


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
        alllog[channel + ' ' + server] = collections.deque(maxlen=200)


def remove_alllog(channel, server):
    del alllog[channel + ' ' + server]

# def load_keywordslog():
#     return keywordlog
