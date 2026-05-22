#!/bin/bash

# Scenario 1
echo "Running scenario 1..."
cd simple_anonymous_particle_etching
timeout 120s sprocess simple_etch.cmd
cd ..

# Git automation
# date_time=$(date +"%Y%m%d_%H%M%S")
# git add -A
# git commit -m "sentaurus_run_${date_time}"
# git push
