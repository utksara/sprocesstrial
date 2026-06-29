# Define a silicon unit cube as the initial bulk structure.
define_structure material=Silicon point_min={0 0 0} point_max={0.35 0.05 4.0}

# Fill the initial structure with aluminum with a thickness
# of 0.08 micrometers.
fill material=Aluminum thickness=0.08

# Fill again with Photoresist with a thickness of 0.18 micrometers.
fill material=Photoresist thickness=0.18

# Define a first cuboid shape that is used to etch a first trench
# out of the previously generated structure.
define_shape type=cube name=cuboid1 point_min={0.07 0.0 0.07} \
point_max={0.14 0.05 3.3}

# Define a second cuboid shape that is used to etch a second trench
# out of the previously generated structure.
define_shape type=cube name=cuboid2 point_min={0.21 0.0 0.07} \
point_max={0.28 0.05 3.3}

# Etch the two cuboids.
etch shape=cuboid1
etch shape=cuboid2

# Save the final structure to file.
save file=Structures/etch_input.tdr