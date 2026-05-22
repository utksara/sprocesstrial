# 1. Define a basic 2D grid layout (1 micron wide by 1 micron deep)
line x location=0.0 spacing=0.1
line x location=1.0 spacing=0.1

line y location=0.0 spacing=0.1
line y location=1.0 spacing=0.1

# 2. Initialize the grid space as a solid Silicon substrate
init silicon

# 3. Perform a simple geometric etch
# This etches a 0.4 micron deep trench exactly in the middle (from X=0.3 to X=0.7)
etch material=silicon type=anisotropic thickness=0.4 left=0.3 right=0.7

# 4. Save the resulting structure directly to a TDR file
struct tdr=simple_etch_out.tdr

exit