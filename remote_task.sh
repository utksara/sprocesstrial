#!/bin/bash

# --- CONFIGURATION ---
TARGET_FOLDER="./boschProcess"
# ---------------------

# 1. cd to the target folder
cd "$TARGET_FOLDER" || { echo "Directory not found"; exit 1; }

# Ensure the logs and tdrs destination folders exist
mkdir -p logs
mkdir -p tdrs

# Delete all existing files inside the logs and tdrs folders
rm -f logs/*
rm -f tdrs/*

# 2. Run all generated OxideMaskedHighAspectRatioEtch_withFlux_run_*.cmd files
echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_1.cmd..."
timeout 120s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_1.cmd
if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_1.log" ]; then
    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_1.log" logs/
fi
if ls OxideMaskedHighAspectRatioEtch_withFlux_run_1*.tdr 1> /dev/null 2>&1; then
    mv OxideMaskedHighAspectRatioEtch_withFlux_run_1*.tdr tdrs/
fi

echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_2.cmd..."
timeout 120s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_2.cmd
if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_2.log" ]; then
    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_2.log" logs/
fi
if ls OxideMaskedHighAspectRatioEtch_withFlux_run_2*.tdr 1> /dev/null 2>&1; then
    mv OxideMaskedHighAspectRatioEtch_withFlux_run_2*.tdr tdrs/
fi

echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_3.cmd..."
timeout 120s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_3.cmd
if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_3.log" ]; then
    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_3.log" logs/
fi
if ls OxideMaskedHighAspectRatioEtch_withFlux_run_3*.tdr 1> /dev/null 2>&1; then
    mv OxideMaskedHighAspectRatioEtch_withFlux_run_3*.tdr tdrs/
fi

echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_4.cmd..."
timeout 120s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_4.cmd
if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_4.log" ]; then
    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_4.log" logs/
fi
if ls OxideMaskedHighAspectRatioEtch_withFlux_run_4*.tdr 1> /dev/null 2>&1; then
    mv OxideMaskedHighAspectRatioEtch_withFlux_run_4*.tdr tdrs/
fi

echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_5.cmd..."
timeout 120s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_5.cmd
if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_5.log" ]; then
    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_5.log" logs/
fi
if ls OxideMaskedHighAspectRatioEtch_withFlux_run_5*.tdr 1> /dev/null 2>&1; then
    mv OxideMaskedHighAspectRatioEtch_withFlux_run_5*.tdr tdrs/
fi

echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_6.cmd..."
timeout 120s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_6.cmd
if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_6.log" ]; then
    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_6.log" logs/
fi
if ls OxideMaskedHighAspectRatioEtch_withFlux_run_6*.tdr 1> /dev/null 2>&1; then
    mv OxideMaskedHighAspectRatioEtch_withFlux_run_6*.tdr tdrs/
fi

echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_7.cmd..."
timeout 240s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_7.cmd
if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_7.log" ]; then
    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_7.log" logs/
fi
if ls OxideMaskedHighAspectRatioEtch_withFlux_run_7*.tdr 1> /dev/null 2>&1; then
    mv OxideMaskedHighAspectRatioEtch_withFlux_run_7*.tdr tdrs/
fi

echo "[Bash] All simulation runs completed on remote host."
