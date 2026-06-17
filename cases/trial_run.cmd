# Initialize wafer
init

# Oxide hard mask
deposit material=Oxide type=isotropic thickness=0.2

# Define trench opening
mask name=trench left=0.4 right=0.6

# Apply photoresist
photo mask=trench thickness=0.5

# Transfer pattern into oxide
etch material=Oxide type=anisotropic thickness=0.25

# Remove photoresist
strip PhotoResist

# Etch silicon vertically
# Depth ≈ rate * #time = 0.4 * 2 = 0.8
# Stop before reaching bottom
etch material=Silicon type=anisotropic rate=0.4 time=2

# Save structure
struct tdr=anisotropic_trench