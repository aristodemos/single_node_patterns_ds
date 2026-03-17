#!/bin/sh

REPO_URL="https://github.com/aristodemos/sidecar-file-share.git"
TARGET_DIR="/shared"

# 1. Clone if the directory is empty or not a git repo
if [ ! -d "$TARGET_DIR/.git" ]; then
    echo "Initializing: Cloning repository..."
    git clone "$REPO_URL" "$TARGET_DIR"
else
    echo "Repository exists. Skipping clone."
fi

# 2. Continuous Pull Loop
cd "$TARGET_DIR" || exit
while true; do
    echo "Syncing updates..."
    git pull origin main # Change 'main' to your branch name
    sleep 10
done