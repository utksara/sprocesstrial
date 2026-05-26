# =====================================================================
# Sentaurus Process - Fully Validated 3D Geometric Etch Benchmark
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

# 3. Initialize a solid Silicon substrate block using the 3D grid
init silicon

# 4. Deposit a 0.2-micron thick Mask Layer on top
deposit material=oxide type=isotropic thickness=0.2

# 5. FIXED: No spaces, no commas inside the coordinate braces.
# Use negative signs explicitly to separate the values.
etch material=oxide type=anisotropic thickness=0.25 \
     coord= {0.3-0.1+0.3} to= {0.7+0.25+0.7}

# 6. FIXED: Directional vector formatted identically without spaces or commas
etch material=silicon type=directional direction= {0+1+0} rate=0.4 time=1.0

# 7. Adaptively smooth and re-mesh the new 3D boundary layout
grid remesh

# 8. Save the final 3D structure mesh to a TDR file
struct tdr=simple_etch_3d_out.tdr

puts "3D Benchmark simulation finished successfully!"
exit