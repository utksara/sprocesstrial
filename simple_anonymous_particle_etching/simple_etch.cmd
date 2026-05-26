# =====================================================================
# Sentaurus Process - Pure 3D Fixed Region Syntax
# =====================================================================

# 1. Initialize the 3D Math Environment
math dimension=3

# 2. Define a 3D grid box with explicit edge tags
line x location=0.0 spacing=0.05 tag=Left
line x location=1.0 spacing=0.05 tag=Right

line y location=0.0 spacing=0.05 tag=Top
line y location=2.0 spacing=0.05 tag=Bottom

line z location=0.0 spacing=0.05 tag=Front
line z location=1.0 spacing=0.05 tag=Back

# 3. FIXED: Define the 3D volume using explicit regions
# This bypasses all parameter bugs inside the 'init' engine entirely.
region material=silicon xlo=Left xhi=Right ylo=Top yhi=Bottom zlo=Front zhi=Back

# 4. Initialize the domain (Blank 'init' is completely legal here)
init

# 5. Deposit a 0.2-micron thick Mask Layer (Oxide) on top
deposit material=oxide type=isotropic thickness=0.2

# 6. Define the 2D Mask layout on the X-Z surface
mask name=trench_window left=0.3 right=0.7 front=0.3 back=0.7 negative

# 7. Apply photolithography resist
photo thickness=0.5 mask=trench_window

# 8. Etch the Oxide mask window open
etch material=oxide type=anisotropic thickness=0.25

# 9. Strip the temporary photolithography resist
strip photo

# 10. Run the DRIE Silicon Etch using your corrected vector syntax
etch material=silicon type=directional direction= {0.1 1 0.1} rate=0.4 time=1.0

# 11. Adaptively smooth and re-mesh the new 3D layout boundary
grid remesh

# 12. Save the final 3D structure mesh to a TDR file
struct tdr=simple_etch_3d_out.tdr

puts "3D Benchmark simulation finished successfully!"
exit