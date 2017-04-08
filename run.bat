@echo off
SETLOCAL EnableDelayedExpansion
type cogs\utils\credit.txt
echo[
echo[
git init . >nul || goto :git
git remote add origin https://github.com/appu1232/Discord-Selfbot.git >nul 2>&1
git remote show origin > tmp.txt
set findfile="tmp.txt"
set findtext="up"
findstr %findtext% %findfile% >nul 2>&1
if errorlevel 1 goto prompt
del tmp.txt
goto run


:prompt
	choice /t 10 /c yn /d n /m "There is an update for the bot. Download now?"
	if errorlevel 2 goto :run
	if errorlevel 1 goto :update
:update
	echo Starting update...
	if exist tmp del /F /Q tmp
	if exist cogs\afk.py (
		del cogs\afk.py
	)
	echo d | xcopy settings tmp /E >nul
	ren settings settings2
	del tmp.txt
	git reset --hard FETCH_HEAD
	git pull origin master > tmp.txt
	set findfile="tmp.txt"
	set findtext="Aborting"
	findstr %findtext% %findfile% >nul 2>&1
	if errorlevel 0 goto force
	rmdir /s /q settings
	ren settings2 settings
	echo Finished updating!
	pause
	goto run
:git
	TITLE Error!
	echo Git not found, Download here: https://git-scm.com/downloads
	echo Press any key to exit.
	pause >nul 2>&1
	CD /D "%root%"
	goto :EOF
:force
	git fetch --all
	git reset --hard origin/master
:run
	if exist settings2 (
		rmdir /s /q settings
		ren settings2 settings
	)
	if exist tmp.txt (
		del tmp.txt
	)
	FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
	echo Checking requirements...
	python -m pip install -r requirements.txt > nul
	echo Requirements satisifed.
	echo Starting the bot (this may take a minute or two)...
	python loopself.py