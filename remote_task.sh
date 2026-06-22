
#!/bin/bash

# --- CONFIGURATION ---
TARGET_FOLDER="./boschProcess"
COMMAND_TO_RUN="echo 'Running core tasks...'; timeout 120s sprocess OxideMaskedHighAspectRatioEtch.cmd" # Replace with your actual command
# ---------------------

# 1. cd to the certain folder
cd "$TARGET_FOLDER" || { echo "Directory not found"; exit 1; }

# 2. Run the command
eval "$COMMAND_TO_RUN"

# 3. Handle the log and tdr folders
# Ensure the logs and tdrs destination folders exist
mkdir -p logs
mkdir -p tdrs

# Delete all existing files inside the logs folder
rm -f logs/*

# Delete all existing files inside the tdrs folder
rm -f tdrs/*

# Transfer (move) all .log files in current directory to the logs folder
if ls *.log 1> /dev/null 2>&1; then
    mv *.log logs/
fi

# Transfer (move) all .tdr files in current directory to the tdrs folder
if ls *.tdr 1> /dev/null 2>&1; then
    mv *.tdr tdrs/
fi

echo "[Bash] Script tasks completed on remote host."