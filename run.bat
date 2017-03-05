@echo off
echo Starting bot (this may take a minute or two)...
FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
python -m pip install -r requirements.txt
python loopself.py