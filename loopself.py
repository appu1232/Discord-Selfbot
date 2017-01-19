import subprocess, traceback

while True:
    try:
        p = subprocess.call(['python3', 'appuselfbot.py'])
    except:
        traceback.print_exc()