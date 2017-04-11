import subprocess
import traceback
import os

while True:
    if os.path.isfile('quit.txt'):
        with open('quit.txt') as fp:
            kill = fp.read()
        os.remove('quit.txt')
        if kill == 'update':
            exit(15)
        break
    try:
        p = subprocess.call(['python3', 'appuselfbot.py'])
    except (SyntaxError, FileNotFoundError):
        p = subprocess.call(['python', 'appuselfbot.py'])
    except:
        traceback.print_exc()
