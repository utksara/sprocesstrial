#!/bin/bash

# # Scenario 1
# echo "Running scenario 1..."
# cd simple_anonymous_particle_etching
# timeout 120s sprocess simple_etch.cmd
# cd ..


# Scenario 2
echo "Running scenario 1..."
cd cases
# timeout 120s sprocess OxideMaskedHighAspectRatioEtch.cmd
# timeout 120s sprocess SimpleRIESiliconTrench.cmd
# timeout 120s sprocess BoschDRIE.cmd
# timeout 120s sprocess DualLevelMEMSCavity.cmd
# timeout 120s sprocess MultiStepTSVProcess.cmd   
timeout 120s sprocess OxideMaskedHighAspectRatioEtch_withFlux.cmd
cd ..

# Git automation
# date_time=$(date +"%Y%m%d_%H%M%S")
# git add -A
# git commit -m "sentaurus_run_${date_time}"
# git push
