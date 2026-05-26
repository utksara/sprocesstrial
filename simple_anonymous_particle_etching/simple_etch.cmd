# =====================================================================
# Sentaurus Process (sprocess) - Advanced Topography & Etching Framework
# =====================================================================

# ---------------------------------------------------------------------
# 1. PARAMETRIC INITIAL GRID SPECIFICATION
# ---------------------------------------------------------------------
line x location = 0.00 spacing = 0.05 tag = LeftEdge
line x location = 1.00 spacing = 0.05 tag = RightEdge

line y location = 0.00 spacing = 0.02 tag = SubstrateTop
line y location = 3.00 spacing = 0.50 tag = SubstrateBottom

# Explicitly assign geometric domain to a designated material domain region
region Silicon xlo = LeftEdge xhi = RightEdge ylo = SubstrateTop yhi = SubstrateBottom

# ---------------------------------------------------------------------
# 2. DEVICE SUBSTRATE INITIALIZATION & BASE DOPING
# ---------------------------------------------------------------------
# Define the global crystal orientation of the wafer substrate first
slot orientation = 100

# Initialize the Domain and apply active background carrier concentration 
init concentration = 1.0e15 field = Boron

# ---------------------------------------------------------------------
# 3. ADVANCED ADAPTIVE REFINEBOX SYSTEM
# ---------------------------------------------------------------------
refinebox name = Etch_Refinement \
    min = { 0.0 0.0 } max = { 1.0 1.5 } \
    xrefine = { 0.01 } yrefine = { 0.01 } \
    materials = { Silicon }

grid remesh

# ---------------------------------------------------------------------
# 4. HARD MASK DEPOSITION & PHOTOLITHOGRAPHY EMULATION
# ---------------------------------------------------------------------
deposit material = {Oxide} type = isotropic thickness = 0.25

mask name = Mask_Opening segments = { 0.35 0.65 }

etch material = {Oxide} type = anisotropic thickness = 0.30 mask = Mask_Opening

# ---------------------------------------------------------------------
# 5. MULTI-STEP ADVANCED GEOMETRIC SEMICONDUCTOR ETCH
# ---------------------------------------------------------------------
etch material = {Silicon} type = directional direction = {0 1} rate = 0.6 time = 1.0 mask = Mask_Opening

etch material = {Silicon} type = isotropic thickness = 0.04 mask = Mask_Opening

grid remesh

# ---------------------------------------------------------------------
# 6. MASK STRIPPING & POST-PROCESSING CLEANUP
# ---------------------------------------------------------------------
etch material = {Oxide} type = all

grid remesh

# ---------------------------------------------------------------------
# 7. HIGH-FIDELITY SIMULATION DATA EXPORT
# ---------------------------------------------------------------------
struct tdr = advanced_etch_output.tdr

puts "Advanced process simulation cycle finished successfully."
exit