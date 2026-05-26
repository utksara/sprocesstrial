# =====================================================================
# Sentaurus Process (sprocess) - Advanced Topography & Etching Framework
# =====================================================================

# ---------------------------------------------------------------------
# 1. PARAMETRIC INITIAL GRID SPECIFICATION
# ---------------------------------------------------------------------
# Base coordinate grid lines
line x location = 0.00 spacing = 0.05 tag = LeftEdge
line x location = 1.00 spacing = 0.05 tag = RightEdge

line y location = 0.00 spacing = 0.02 tag = SubstrateTop
line y location = 3.00 spacing = 0.50 tag = SubstrateBottom

# Explicitly assign geometric domain to a designated material domain region
region Silicon xlo = LeftEdge xhi = RightEdge ylo = SubstrateTop yhi = SubstrateBottom

# ---------------------------------------------------------------------
# 2. DEVICE SUBSTRATE INITIALIZATION & BASE DOPING
# ---------------------------------------------------------------------
# Define initial crystalline characteristics and active carrier concentration 
init orientation = 100 concentration = 1.0e15 field = Boron

# ---------------------------------------------------------------------
# 3. ADVANCED ADAPTIVE REFINEBOX SYSTEM (CRITICAL FOR DRIE FRONT)
# ---------------------------------------------------------------------
# Dynamically adjusts elements near the interface to protect against mesh inversion
refinebox name = Etch_Refinement \
    min = { 0.0 0.0 } max = { 1.0 1.5 } \
    xrefine = { 0.01 } yrefine = { 0.01 } \
    materials = { Silicon }

# Activate the local grid refinement boundaries 
grid remesh

# ---------------------------------------------------------------------
# 4. HARD MASK DEPOSITION & PHOTOLITHOGRAPHY EMULATION
# ---------------------------------------------------------------------
# Deposit a solid sacrificial insulator layer (Oxide Mask)
deposit material = {Oxide} type = isotropic thickness = 0.25

# Define a photolithographic window opening segment (X bounds from 0.35 to 0.65)
mask name = Mask_Opening segments = { 0.35 0.65 }

# Cut an accurate trench profile opening directly out of the oxide layer 
etch material = {Oxide} type = anisotropic thickness = 0.30 mask = Mask_Opening

# ---------------------------------------------------------------------
# 5. MULTI-STEP ADVANCED GEOMETRIC SEMICONDUCTOR ETCH
# ---------------------------------------------------------------------
# Step A: Highly directional anisotropic drive down into the exposed Silicon
etch material = {Silicon} type = directional direction = {0 1} rate = 0.6 time = 1.0 mask = Mask_Opening

# Step B: Slight isotropic undercut expansion step to replicate real-world plasma profiles
etch material = {Silicon} type = isotropic thickness = 0.04 mask = Mask_Opening

# Re-evaluate the entire grid structure to smooth the newly deformed coordinates
grid remesh

# ---------------------------------------------------------------------
# 6. MASK STRIPPING & POST-PROCESSING CLEANUP
# ---------------------------------------------------------------------
# Completely remove the remaining sacrificial oxide layer
etch material = {Oxide} type = all

# Execute a final global smoothing pass 
grid remesh

# ---------------------------------------------------------------------
# 7. HIGH-FIDELITY SIMULATION DATA EXPORT
# ---------------------------------------------------------------------
struct tdr = advanced_etch_output.tdr

puts "Advanced process simulation cycle finished successfully."
exit