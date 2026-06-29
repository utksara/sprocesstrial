# Define an ion-enhanced etch machine and set
# its ion angular distribution exponent.
define_etch_machine model=ion_enhanced exponent=10

# Multimaterial etch.
# Define materials and set the machine-dependent properties:
# rates, anisotropy, sputtering coefficients, and sticking coefficient.
add_material material=Aluminum rate=0.7 anisotropy=0.5 sticking=0.5 \
s1=5.5 s2=-6
add_material material=Photoresist rate=0.5 anisotropy=0.5 sticking=0.0 \
s1=5.5 s2=-6

# Load a structure from a file.
define_structure file=Structures/etch_input.tdr

# Start etch simulation process.
etch spacing={0.015 0.015 0.015} time=0.1

# Save the final structure to a file.
save