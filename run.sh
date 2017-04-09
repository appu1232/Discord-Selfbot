#!/bin/sh

echo "Warning: this script is still an alpha, expect bugs"
echo "Starting auto-update"
if hash git 2>/dev/null; then
	echo "Fetching origin"
	git fetch origin
	newcommits=$(git log HEAD..origin/master --oneline)
	if [[ "${newcommits}" != "" ]]; then
		echo "Installing update"
		echo "Stashing settings and custom modifications"
		git stash
		echo "Pulling new commits"
		git pull
		stashlist=$(git stash list)
		if [[ "${stashlist}" != "" ]]; then
			echo "Popping stash"
			if git stash pop; then
				echo "Changes restored"
			else
				echo "There are merge conflicts. Please resolve these manually" # Sort of abandoning the user her :/
				exit 255
			fi
		fi
		echo "Update succeeded"
	else
		echo "No updates"
	fi
else
	echo "You do not have git installed. Auto-update is not currently supported" # TODO HTTP update
	echo "Git is almost certainly available from your package manager"
	echo "However if you are, for instance, using Linux from Scratch, you likely do not need instruction"
fi

echo "Checking requirements"
if hash python3 2>/dev/null; then # TODO abstracify all this which mirrors above an also look up boolean operators in sh
	if hash pip3 2>/dev/null; then
		echo "Using global pip3 executable"
		if sudo pip3 install -r requirements.txt; then
			echo "Starting bot"
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
			if python3 -m pip install -r requirements.txt; then
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

else
	echo "You do not appear to have Python 3 installed"
	echo "Python 3 is almost certainly available from your package manager"
        echo "However if you are, for instance, using Linux from Scratch, you likely do not need instruction"
fi
