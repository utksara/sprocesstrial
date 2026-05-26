# =====================================================================
# Sentaurus Process - Fully Validated 3D Masking & Etch Benchmark
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

# 3. FIXED: Define the explicit 3D region box boundaries during initialization
# This tells the engine exactly where the Silicon region exists in 3D space
init silicon min= {0.0 0.0 0.0} max= {1.0 2.0 1.0}

# 4. Deposit a 0.2-micron thick Mask Layer (Oxide) on top
deposit material=oxide type=isotropic thickness=0.2

# 5. Define the 2D Mask layout on the X-Z surface
mask name=trench_window left=0.3 right=0.7 front=0.3 back=0.7 negative

# 6. Apply photolithography resist
photo thickness=0.5 mask=trench_window

# 7. Etch the Oxide mask window open
etch material=oxide type=anisotropic thickness=0.25

# 8. Strip the temporary photolithography resist
strip photo

# 9. Run the DRIE Silicon Etch using your corrected vector syntax
etch material=silicon type=directional direction = {0.1 1 0.1} rate=0.4 time=1.0

# 10. Adaptively smooth and re-mesh the new 3D layout boundary
grid remesh

# 11. Save the final 3D structure mesh to a TDR file
struct tdr=simple_etch_3d_out.tdr

puts "3D Benchmark simulation finished successfully!"
exit