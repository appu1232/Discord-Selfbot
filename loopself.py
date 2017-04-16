import subprocess
import os
import sys

while True:
    if os.path.isfile('quit.txt'):
        with open('quit.txt') as fp:
            kill = fp.read()
        os.remove('quit.txt')
        if kill == 'update':
            exit(15)
        break
    subprocess.call([sys.executable, 'appuselfbot.py'])
