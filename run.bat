@echo off
SET root=%~dp0
CD /D %root%
SETLOCAL EnableDelayedExpansion
python -V >nul 2>&1 || goto :python
git init . >nul || goto :git
git remote add origin https://github.com/appu1232/Discord-Selfbot.git >nul 2>&1
get fetch origin master >nul 2>&1
if not exist appuselfbot.py (
    echo This seems to be your first run. The setup will now proceed to download all required files. They will be downloaded to the same location as where this run.bat file is.
    pause
    git fetch --all
	git reset --hard origin/master
)
git remote show origin > tmp.txt
set findfile="tmp.txt"
set findtext="up"
findstr %findtext% %findfile% >nul 2>&1		
if errorlevel 1 goto forward		
goto run		

:prompt
	choice /t 10 /c yn /d n /m "There is an update for the bot. Download now?"
	if errorlevel 2 goto :run
	if errorlevel 1 goto :update
:forward
	set findfile="tmp.txt"		
	set forwardable="fast-forwardable"		
	findstr %forwardable% %findfile% >nul 2>&1		
	if errorlevel 1 goto prompt
	goto run
:update
	echo Starting update...
	echo Backing up your settings...
	echo d | xcopy settings settings_backup /E >nul
	echo Latest update:
	git --no-pager log --pretty=oneline -n1 origin/master ^master
	git pull origin master
	if errorlevel 1 goto force
	echo Finished updating
	echo Starting up...
	goto run
:force
	git fetch --all
	git reset --hard origin/master
	echo Finished updating
	echo Starting up...
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
:run
	if exist tmp.txt del tmp.txt
	FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
	echo Checking/Installing requirements (takes some time on first install)...
	chcp 65001 >nul
	set PYTHONIOENCODING=utf-8
	python -m pip install --user --upgrade pip >nul
	python -m pip install --user -r requirements.txt
	if errorlevel 1 (
	    echo Requirements installation failed. Perhaps some dependency is missing or access was denied? Possible solutions:
	    echo - Run as administrator
	    echo - Google the error
	    echo - Visit the Discord server for help
	    echo Press any key to exit.
	    set /p input=
	    exit
	)
	ping 127.0.0.1 -n 2 > nul
	cls
	type cogs\utils\credit.txt
	echo[
	echo[
	echo Requirements satisfied.
	echo Starting the bot (this may take a minute or two)...
	python loopself.py
	if %ERRORLEVEL% == 15 goto update