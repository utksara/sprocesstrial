# =====================================================================
# Sentaurus Process (sprocess) - 3D Multi-Layer Domain Initialization
# =====================================================================

# 1. DEFINE THE 3D SPATIAL GRID BOUNDARIES
# X-Axis (Width: 0.0 to 1.0 microns)
line x location = 0.00 spacing = 0.10 tag = Left
line x location = 1.00 spacing = 0.10 tag = Right

# Z-Axis (Length/Depth-of-field: 0.0 to 1.0 microns)
line z location = 0.00 spacing = 0.10 tag = Front
line z location = 1.00 spacing = 0.10 tag = Back

# Y-Axis (Vertical Thickness: 0.0 down to 2.0 microns for base Silicon)
line y location = 0.00 spacing = 0.05 tag = SubTop
line y location = 2.00 spacing = 0.40 tag = SubBottom

# 2. BIND THE CORE 3D GEOMETRIC DOMAIN TO SILICON
region Silicon xlo = Left xhi = Right ylo = SubTop yhi = SubBottom zlo = Front zhi = Back

# 3. INITIALIZE THE BASE WAFER SUBSTRATE
# This generates the baseline 3D Silicon volume
init concentration = 1.0e15 field = Boron

# 4. DEPOSIT THE INSULATOR LAYER (SILICON OXIDE)
# Deposits a flat, uniform 0.20-micron thick layer on top of the Silicon
deposit material = {Oxide} type = isotropic thickness = 0.20

# 5. DEPOSIT THE SACRIFICIAL LAYER (PHOTORESIST)
# Deposits a flat, uniform 0.40-micron thick layer on top of the Oxide
deposit material = {Photoresist} type = isotropic thickness = 0.40

# 6. FORCE GLOBAL 3D MESH GENERATION
# This compiles the layers into a solid structural layout before any etching happens
grid remesh

# 7. EXPORT THE INITIALIZED 3D DATA STRUCTURE
struct tdr = initial_3d_domain.tdr

puts "3D multi-material surface framework constructed successfully."
exit