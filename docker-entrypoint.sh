#!/bin/sh

# create our user and run the bot as that user
USER_ID=${UID:-1234}
GROUP_ID=${GID:-1234}

adduser -S -u $USER_ID -g $GROUP_ID selfbot
chown selfbot /app
chown selfbot /app/*

# move the original files back to the correct location as
# they have been mounted as volumes on the host filesystem
cp -rf /app/.sample/* /app/

# run bot as the selfbot user
su-exec selfbot "$@"

