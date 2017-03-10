import subprocess, traceback

while True:
    try:
        p = subprocess.call(['python3', 'appuselfbot.py'])
    except (SyntaxError, FileNotFoundError):
        p = subprocess.call(['python', 'appuselfbot.py'])
    except:
        traceback.print_exc()