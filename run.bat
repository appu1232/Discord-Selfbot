@echo off
echo Starting bot...
FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
python -m pip install -r requirements.txt > nul
python loopself.py