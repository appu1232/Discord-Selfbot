#!/bin/bash

cd "$(dirname "$0")"
if [ $? -eq 0 ]; then
    echo "" 
else
    echo "Unable to set script's directory as the current working directory. You will need to make sure you run the script from it's directory."
fi

updater () {
	echo "Starting auto-update"
	if hash git 2>/dev/null; then
		echo "Fetching origin"
		git init >/dev/null 2>&1
		git remote add origin https://github.com/appu1232/Discord-Selfbot.git >/dev/null 2>&1
		git fetch origin master
		if [ -d "settings" ]; then
			cp -r settings settings_backup
		fi
		new=$(git remote show origin)
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
	else
		echo "You do not have git installed. Auto-update is not currently supported" # TODO HTTP update
		echo "Git is almost certainly available from your package manager. Install with:"
		echo "sudo apt-get install git-all"
	fi
}

min_updater() {
	if hash git 2>/dev/null; then
		if [ -d "settings" ]; then
			cp -r settings settings_backup
		fi
		git fetch origin master
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
		sleep 1
	else
		echo "You do not have git installed. Auto-update is not currently supported" # TODO HTTP update
		echo "Git is almost certainly available from your package manager. Install with:"
		echo "sudo apt-get install git-all"
	fi
}

run_bot() {
	echo "Checking requirements..."
	if hash python3 2>/dev/null; then # TODO abstracify all this which mirrors above an also look up boolean operators in sh
		if hash pip3 2>/dev/null; then
			echo "Using global pip3 executable"
			if pip3 install --user -r requirements.txt; then
				echo "Starting bot..."
				python3 loopself.py
				ret=$?
				if [ $ret == "15" ]; then
					min_updater
					run_bot
				else
					echo "Shutting down"
				fi
			else
				echo "Requirements installation failed"
				exit 254
			fi
		else
			echo "Using pip as a python3 module"
			echo "Upgrading pip"
			if python3 -m pip install --user --upgrade pip; then
				echo "Upgrading requirements"
				if python3 -m pip install --user --upgrade -r requirements.txt; then
					echo "Starting bot..."
					python3 loopself.py
					ret=$?
					if [ $ret == "15" ]; then
						min_updater
						run_bot
					else
						echo "Shutting down"
					fi
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
			if pip install --user -r requirements.txt; then
				echo "Starting bot..."
				python loopself.py
				ret=$?
				if [ $ret == "15" ]; then
					min_updater
					run_bot
				else
					echo "Shutting down"
				fi

			else
				echo "Requirements installation failed"
				exit 254
			fi
		else
			echo "Using pip as a python3 module"
			echo "Upgrading pip"
			if python -m pip install --user --upgrade pip; then
				echo "Upgrading requirements"
				if python -m pip install --user -r requirements.txt; then
					echo "Starting bot..."
					python loopself.py
					ret=$?
					if [ $ret == "15" ]; then
						min_updater
						run_bot
					else
						echo "Shutting down"
					fi
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

}

updater
run_bot
