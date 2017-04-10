#!/bin/bash

echo "Warning: this script is still an alpha, expect bugs"
echo "Starting auto-update"
if hash git 2>/dev/null; then
	echo "Fetching origin"
	git init >/dev/null 2>&1
	git remote add origin https://github.com/appu1232/Discord-Selfbot.git >/dev/null 2>&1
	git fetch origin
	if [ -d "settings" ]; then
		cp -r settings tmp
		mv settings settings2
	fi
	news=$(git remote show origin)
	if [[ "${new}" =~ "up" ]] || [[ "${new}" =~ "fast-forwardable" ]] ; then
		echo "The bot is up to date."
		sleep 1
	else
		read -t 10 -n 1 -p "There is an update available. Download now? (y/n):" input
		if [[ "$input" =~ "y" ]] ; then
			echo ""
			echo "Installing update"
			echo "Updating to latest stable build."
			if git pull origin master ; then 
				echo "Update succeeded"
				sleep 2
			else
				echo "Pull failed, attempting to hard reset to origin master (settings are still saved)"
				git fetch --all
				git reset --hard origin/master
				echo "Update succeeded"
				sleep 2
			fi
		else
			echo ""
			echo "Cancelled update"
		fi
	fi
	sleep 1
	if [ -d "settings2" ]; then
			mv settings2 settings
	
	fi
else
	echo "You do not have git installed. Auto-update is not currently supported" # TODO HTTP update
	echo "Git is almost certainly available from your package manager. Install with:"
	echo "sudo apt-get install git-all"
fi

echo "Checking requirements..."
if hash python3 2>/dev/null; then # TODO abstracify all this which mirrors above an also look up boolean operators in sh
	if hash pip3 2>/dev/null; then
		echo "Using global pip3 executable"
		if sudo pip3 install -r requirements.txt >/dev/null; then
			echo "Starting bot..."
			python3 loopself.py
		else
			echo "Requirements installation failed"
			exit 254
		fi
	else
		echo "Using pip as a python3 module"
		echo "Upgrading pip"
		if python3 -m pip install --upgrade pip; then
			echo "Upgrading requirements"
			if python3 -m pip install -r requirements.txt >/dev/null; then
				python3 loopself.py
			else
				echo "Requirements installation failed"
				exit 254
			fi
		else
			echo "Pip could not be installed. Try using your package manager"
			exit 253
		fi
	fi
	
elif hash python 2>/dev/null; then # TODO abstracify all this which mirrors above an also look up boolean operators in sh
	case "$(python --version 2>&1)" in
		*" 3."*)
			echo ""
			;;
		*)
			echo "Wrong Python version!"
			echo "You need python 3.5.2 or up to use this bot!"
			exit
			;;
	esac
	if hash pip 2>/dev/null; then
		echo "Using global pip executable"
		if sudo pip install -r requirements.txt >/dev/null; then
			echo "Starting bot..."
			python loopself.py
		else
			echo "Requirements installation failed"
			exit 254
		fi
	else
		echo "Using pip as a python3 module"
		echo "Upgrading pip"
		if python -m pip install --upgrade pip; then
			echo "Upgrading requirements"
			if python -m pip install -r requirements.txt >/dev/null; then
				python loopself.py
			else
				echo "Requirements installation failed"
				exit 254
			fi
		else
			echo "Pip could not be installed. Try using your package manager"
			exit 253
		fi
	fi

else
	echo "You do not appear to have Python 3 installed"
	echo "Python 3 is almost certainly available from your package manager or just google how to get it"
    echo "However if you are, for instance, using Linux from Scratch, you likely do not need instruction"
fi
