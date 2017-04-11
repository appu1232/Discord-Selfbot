@echo off
SET root=%~dp0
CD /D %root%
SETLOCAL EnableDelayedExpansion
python -V >nul 2>&1 || goto :python
git init . >nul || goto :git
git remote add origin https://github.com/appu1232/Discord-Selfbot.git >nul 2>&1
git remote show origin > tmp.txt
set findfile="tmp.txt"
set findtext="up"
findstr %findtext% %findfile% >nul 2>&1
if errorlevel 1 goto forward
goto run

:forward
	set findfile="tmp.txt"
	set forwardable="fast-forwardable"
	findstr %forwardable% %findfile% >nul 2>&1
	if errorlevel 1 goto prompt
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
	echo Backing up your settings...
	echo d | xcopy settings tmp /E >nul
	ren settings settings2
	echo Latest update:
	git --no-pager log --pretty=oneline -n1 origin/master ^master
	git pull origin master
	if errorlevel 1 goto force
	echo Finished updating
	rmdir /s /q settings >nul 2>&1
	ren settings2 settings
	echo Starting up...
	ping 127.0.0.1 -n 4 >nul
	goto run
	
:git
	TITLE Error!
	echo Git not found, Download here: https://git-scm.com/downloads
	echo Press any key to exit.
	pause >nul
	CD /D "%root%"
	goto :EOF
:python
	TITLE Error!
	echo Python not added to PATH or not installed. Download Python 3.5.2 or above and make sure you add to PATH: https://i.imgur.com/KXgMcOK.png
	echo Press any key to exit.
	pause >nul
	CD /D "%root%"
	goto :EOF
:force
	git fetch --all
	git reset --hard origin/master
	echo Finished updating
	rmdir /s /q settings >nul 2>&1
	ren settings2 settings
	echo Starting up...
	ping 127.0.0.1 -n 4 >nul
	goto run
:run
	if exist tmp.txt del tmp.txt
	type cogs\utils\credit.txt
	echo[
	echo[
	FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
	echo Checking requirements...
	chcp 65001 >nul
	set PYTHONIOENCODING=utf-8
	python -m pip install --upgrade pip >nul
	python -m pip install -r requirements.txt >nul
	echo Requirements satisifed.
	echo Starting the bot (this may take a minute or two)...
	python loopself.py
	if %ERRORLEVEL% == 15 goto update