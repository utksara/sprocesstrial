# =====================================================================
# Sentaurus Process (sprocess) - Advanced Topography & Etching Framework
# =====================================================================

# 1. PARAMETRIC INITIAL GRID SPECIFICATION
line x location = 0.00 spacing = 0.05 tag = LeftEdge
line x location = 1.00 spacing = 0.05 tag = RightEdge

line y location = 0.00 spacing = 0.05 tag = SubstrateTop
line y location = 3.00 spacing = 0.50 tag = SubstrateBottom

# Explicitly assign geometric domain to a designated material domain region
region Silicon xlo = LeftEdge xhi = RightEdge ylo = SubstrateTop yhi = SubstrateBottom

# 2. DEVICE SUBSTRATE INITIALIZATION
init concentration = 1.0e15 field = Boron

# 3. ADVANCED ADAPTIVE REFINEBOX SYSTEM
refinebox name = Etch_Refinement \
    min = { 0.0 0.0 } max = { 1.0 3.0 } \
    xrefine = { 0.02 } yrefine = { 0.02 } \
    materials = { Silicon Oxide }

grid remesh

# 4. HARD MASK DEPOSITION & PHOTOLITHOGRAPHY EMULATION
deposit material = {Oxide} type = isotropic thickness = 0.25
grid remesh

mask name = Mask_Opening segments = { 0.35 0.65 }

# Cut the Oxide window
etch material = {Oxide} type = anisotropic thickness = 0.30 mask = Mask_Opening
grid remesh

# 5. MULTI-STEP ADVANCED GEOMETRIC SEMICONDUCTOR ETCH
# FIXED: Changed direction vector to explicit floating numbers {0.0 1.0} to satisfy the parser
etch material = {Silicon} type = directional direction = {0.01 1.0} rate = 0.6 time = 1.0 mask = Mask_Opening
grid remesh

# Optional: Slight isotropic undercut expansion step
etch material = {Silicon} type = isotropic thickness = 0.04 mask = Mask_Opening
grid remesh

# 6. MASK STRIPPING & POST-PROCESSING CLEANUP
etch material = {Oxide} type = all
grid remesh

# 7. HIGH-FIDELITY SIMULATION DATA EXPORT
struct tdr = advanced_etch_output.tdr

puts "Advanced process simulation cycle finished successfully."
exit