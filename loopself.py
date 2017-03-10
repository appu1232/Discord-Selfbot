import subprocess, traceback

while True:
    try:
        p = subprocess.Popen(['python3', 'appuselfbot.py'])
    except (SyntaxError, FileNotFoundError):
        p = subprocess.Popen(['python', 'appuselfbot.py'])
    except:
        traceback.print_exc()