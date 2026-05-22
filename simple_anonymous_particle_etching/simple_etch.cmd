# 1. Define a basic 2D grid layout
line x location=0.0 spacing=0.1
line x location=1.0 spacing=0.1

line y location=0.0 spacing=0.1
line y location=1.0 spacing=0.1

# 2. Initialize the grid space as solid Silicon
init silicon

# 3. Define a clear masking window (Trench from X=0.3 to X=0.7)
mask name = trench_window segments = { 0.3 0.7 }

# 4. Perform the geometric etch using the mask
# This avoids inline coordinate math entirely
etch material = silicon type = anisotropic thickness = 0.4 mask = trench_window

# 5. Save the resulting structure directly to a TDR file
struct tdr = simple_etch_out.tdr

exit