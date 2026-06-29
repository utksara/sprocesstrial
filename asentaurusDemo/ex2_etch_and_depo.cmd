# Number of etch cycles
set NumCycles 10

# Define an etchdepo machine and set the ion angular distribution exponent.
# Define the material that is redeposited and set the sticking coefficient
# and the redeposition rate.
define_etch_machine model=etchdepo exponent=100 \
    deposit_material=Anyinsulator sticking=0.035 rate=0.2

# Multimaterial etch.
# Define materials and set the machine-dependent properties:
# rates and sputtering coefficients.
add_material material=Oxide rate=2.0 s1=5.5 s2=-6
add_material material=Anyinsulator rate=0.1 s1=5.5 s2=-6

# Load a structure from a file.
define_structure file=Structures/etch_input.tdr

# Perform multiple etch cycles
for {set cycle 1} {$cycle <= $NumCycles} {incr cycle} {

    puts "Starting etch cycle $cycle"

    etch spacing={0.01 0.01 0.01} time=0.1

    puts "Completed etch cycle $cycle"
}

# Save the final structure
save file=etch_output.tdr