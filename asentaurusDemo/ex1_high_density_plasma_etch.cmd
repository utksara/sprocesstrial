# Define a high-density plasma etch machine and set
# its ion angular distribution exponent.
define_etch_machine model=hdp exponent=15

# Multimaterial etch.
# Define materials and set the machine-dependent properties:
# rates, anisotropy, and sputtering coefficients.
add_material material=Aluminum rate=1.13 anisotropy=0.04 s1=5.5 s2=-6
add_material material=Photoresist rate=0.663 anisotropy=0.95 s1=5.5 s2=-6

# Load a structure from a file.
define_structure file=Structures/etch_input.tdr

# Start etch simulation process.
etch spacing={0.015 0.015 0.015} time=0.1
# Save the final structure to a file.
save