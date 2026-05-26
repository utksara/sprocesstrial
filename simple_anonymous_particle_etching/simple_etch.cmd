# =====================================================================
# Sentaurus Process - Pure 3D Geometric Etch Benchmark
# =====================================================================

# 1. Initialize the 3D Math Environment (Singular 'dimension')
math dimension=3

# 2. Define a clean 3D grid spacing box
# (1.0 micron wide [X], 2.0 microns deep [Y], 1.0 micron long [Z])
line x location=0.0 spacing=0.05
line x location=1.0 spacing=0.05

line y location=0.0 spacing=0.05
line y location=2.0 spacing=0.05

line z location=0.0 spacing=0.05
line z location=1.0 spacing=0.05

# 3. Initialize a solid Silicon substrate block using the 3D grid
init silicon

# 4. Deposit a 0.2-micron thick Mask Layer on top
deposit material=oxide type=isotropic thickness=0.2

# 5. Etch a 3D contact/trench window into the Mask
# Removes a window bound inside the center coordinates
etch material=oxide type=anisotropic thickness=0.25 \
     left=0.3 right=0.7 front=0.3 back=0.7

# 6. Run a directional geometric etch into the 3D Silicon substrate
# This etches 0.4 microns straight down along the Y-axis (direction {X Y Z})
etch material=silicon type=directional direction={0 1 0} rate=0.4 time=1.0

# 7. Adaptively smooth and re-mesh the new 3D layout boundary
grid remesh

# 8. Save the final 3D structure mesh to a TDR file
struct tdr=simple_etch_3d_out.tdr

puts "3D Benchmark simulation finished successfully!"
exit