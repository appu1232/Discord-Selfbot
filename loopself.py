import subprocess, traceback

while True:
    try:
        p = subprocess.call(['python', 'appuselfbot.py'])
    except:
        traceback.print_exc()