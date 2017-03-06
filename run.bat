@echo off
FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
python -m pip install -r requirements.txt
echo Starting bot (this may take a minute or two)...
python loopself.py