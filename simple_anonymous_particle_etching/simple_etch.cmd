# =====================================================================
# Sentaurus Process - Pure 3D Geometric Etch Benchmark
# =====================================================================
math dimension=3

# 1. Define a clean 3D grid spacing box
line x location=0.0 spacing=0.05
line x location=1.0 spacing=0.05

line y location=0.0 spacing=0.05
line y location=2.0 spacing=0.05

line z location=0.0 spacing=0.05
line z location=1.0 spacing=0.05

# 2. Initialize solid Silicon substrate block
init silicon

# 3. Deposit Mask Layer on top
deposit material=oxide type=isotropic thickness=0.2

# 4. FIX: Etch a 3D window into the Mask using 3D Coord Brackets
# Instead of left/right/front/back, we define a explicit bounding cube
etch material=oxide type=anisotropic thickness=0.25 \
     coord= {0.3 0.0 0.3} coord= {0.7 0.25 0.7}

# 5. Run a directional geometric etch into the 3D Silicon substrate
# This etches 0.4 microns straight down along the Y-axis
etch material=silicon type=directional direction={0 1 0} rate=0.4 time=1.0

# 6. Adaptively smooth and re-mesh the new 3D boundary
grid remesh

# 7. Save the final 3D structure mesh to a TDR file
struct tdr=simple_etch_3d_out.tdr

puts "3D Benchmark simulation finished successfully!"
exit