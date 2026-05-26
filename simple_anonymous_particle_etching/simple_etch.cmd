# =====================================================================
# Sentaurus Process - Working 3D Masking & Etch Benchmark
# =====================================================================

# 1. Initialize the 3D Math Environment
math dimension=3

# 2. Define a 3D grid box
line x location=0.0 spacing=0.05
line x location=1.0 spacing=0.05

line y location=0.0 spacing=0.05
line y location=2.0 spacing=0.05

line z location=0.0 spacing=0.05
line z location=1.0 spacing=0.05

# 3. Initialize solid Silicon substrate block
init silicon

# 4. Deposit a 0.2-micron thick Mask Layer (Oxide) on top
deposit material=oxide type=isotropic thickness=0.2

# 5. DEFINE THE 3D MASK LAYOUT
# We draw a literal 2D mask on the X-Z surface. 
# This defines a square blocking region from 0.0-0.3 and 0.7-1.0.
mask name=trench_window left=0.3 right=0.7 front=0.3 back=0.7 negative

# 6. APPLY PHOTOLITHOGRAPHY 
# This deposits photoresist everywhere EXCEPT where our 'trench_window' is open
photo thickness=0.5 mask=trench_window

# 7. ETCH THE OXIDE MASK WINDOW
# This removes the Oxide that is left unprotected by the photoresist
etch material=oxide type=anisotropic thickness=0.25

# 8. STRIP THE PHOTORESIST
# Cleans the remaining polymer off the wafer, leaving a perfect Oxide mask hole
strip photo

# 9. RUN THE DIRECTIONAL DRIE SILICON TRENCH ETCH
# This etches 0.4 microns straight down along the Y-axis inside the open hole
etch material=silicon type=directional direction = {0.1 1 0.1} rate = 0.4 time=1.0

# 10. Adaptively smooth and re-mesh the new 3D layout boundary
grid remesh

# 11. Save the final 3D structure mesh to a TDR file
struct tdr=simple_etch_3d_out.tdr

puts "3D Benchmark simulation finished successfully!"
exit