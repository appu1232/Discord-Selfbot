import subprocess
import traceback
import os

while True:
    if os.path.isfile('quit.txt'):
        os.remove('quit.txt')
        break
    try:
        p = subprocess.call(['python3', 'appuselfbot.py'])
    except (SyntaxError, FileNotFoundError):
        p = subprocess.call(['python', 'appuselfbot.py'])
    except:
        traceback.print_exc()
