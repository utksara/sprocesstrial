# =====================================================================
# Sentaurus Process (sprocess) - True 3D Multi-Layer Solid Domain
# =====================================================================

# CRITICAL FIX: Force Sentaurus into full 3D structural mesh mode.
# Without this, it only calculates 1D/2D data curves.
math dimension=3

# 1. DEFINE THE 3D SPATIAL GRID BOUNDARIES (Finer spacing for 3D elements)
line x location = 0.00 spacing = 0.05 tag = Left
line x location = 1.00 spacing = 0.05 tag = Right

line z location = 0.00 spacing = 0.05 tag = Front
line z location = 1.00 spacing = 0.05 tag = Back

line y location = 0.00 spacing = 0.02 tag = SubTop
line y location = 2.00 spacing = 0.20 tag = SubBottom

# 2. BIND THE CORE 3D GEOMETRIC DOMAIN TO SILICON
region Silicon xlo = Left xhi = Right ylo = SubTop yhi = SubBottom zlo = Front zhi = Back

# 3. INITIALIZE THE BASE WAFER SUBSTRATE
init concentration = 1.0e15 field = Boron

# 4. DEPOSIT THE INSULATOR LAYER (SILICON OXIDE)
deposit material = {Oxide} type = isotropic thickness = 0.20

# 5. DEPOSIT THE SACRIFICIAL LAYER (PHOTORESIST)
deposit material = {Photoresist} type = isotropic thickness = 0.40

# 6. FORCE GLOBAL 3D MESH GENERATION
grid remesh

# 7. EXPORT THE INITIALIZED 3D DATA STRUCTURE
struct tdr = initial_3d_domain.tdr

puts "True 3D multi-material structure constructed successfully."
exit