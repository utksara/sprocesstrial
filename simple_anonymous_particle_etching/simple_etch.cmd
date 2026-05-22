# 1. Define a basic 2D grid layout with boundary tags
line x location = 0.0 spacing = 0.1 tag = Left
line x location = 1.0 spacing = 0.1 tag = Right

line y location = 0.0 spacing = 0.1 tag = Top
line y location = 1.0 spacing = 0.1 tag = Bottom

# 2. Explicitly bind the grid coordinates to a named region
region Silicon xlo = Left xhi = Right ylo = Top yhi = Bottom

# 3. Initialize the simulation domain
init

# 4. Define a clear masking window (Trench from X=0.3 to X=0.7)
mask name = trench_window segments = { 0.3 0.7 }

# 5. Perform the geometric etch using the mask
etch material = silicon type = anisotropic thickness = 0.4 mask = trench_window

# 6. Save the resulting structure directly to a TDR file
struct tdr = simple_etch_out.tdr

exit