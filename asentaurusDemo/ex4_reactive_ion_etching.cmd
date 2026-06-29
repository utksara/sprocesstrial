# Define a reactive ion etch machine and set
# its ion angular distribution exponent.
define_etch_machine model=rie exponent=100

# Multimaterial etch.
# Define materials and set the machine-dependent properties:
# rates and anisotropy.
add_material material=Aluminum rate=0.7 anisotropy=1.0
add_material material=Photoresist rate=0.5 anisotropy=1.0

# Load a structure from a file.
define_structure file=Structures/etch_input.tdr

# Start etch simulation process.
etch spacing={0.015 0.015 0.015} time=0.1

# Save the final structure to a file.
save