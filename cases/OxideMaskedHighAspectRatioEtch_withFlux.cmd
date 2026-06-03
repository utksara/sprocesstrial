# =====================================================================
# Sentaurus Process - Physical Flux-Based DRIE (Bosch) Simulation
# =====================================================================
math dimension=3

# [Standard Grid & Init Blocks go here - omitted for brevity]
# (Assume Silicon substrate with an Oxide mask window is already initialized)

# ---------------------------------------------------------------------
# STEP 1: DEFINE THE PHYSICAL PLASMA MACHINES
# ---------------------------------------------------------------------

# A. The Passivation Cycle Machine (C4F8 Plasma)
# We specify the actual neutral flux of polymer precursors and how they stick.
define_dep_machine name=C4F8_Flash \
    flux=1.5e17 \
    sticking=0.15 \
    angular_distribution=isotropic

# B. The Etching Cycle Machine (SF6 Plasma)
# We break this down into Ions (directional) and Neutrals (chemical/isotropic)
define_etch_machine name=SF6_Plasma \
    ion_flux=2.0e16 \
    neutral_flux=8.0e17 \
    ion_energy=120 \
    exponent=50 \
    neutral_distribution=isotropic

# ---------------------------------------------------------------------
# STEP 2: DEFINE SURFACE REACTION PHYSICS
# ---------------------------------------------------------------------
# Tell the simulator how Silicon reacts when hit by these specific fluxes
material_parameter material=Silicon \
    etch_yield={0.02 * ion_flux * (ion_energy^0.5)} \
    chemical_etch_rate={0.005 * neutral_flux}

# ---------------------------------------------------------------------
# STEP 3: EXECUTE THE ACTUAL BOSCH LOOP
# ---------------------------------------------------------------------
set total_cycles 5

for {set i 1} {$i <= $total_cycles} {incr i} {

    # Phase 1: Physical Polymer Deposition
    # The engine tracks neutral shadowing; less polymer deposits at the deep trench bottom.
    call_machine name=C4F8_Flash time=2.0

    # Phase 2: Directional Ion Breakthrough & Chemical Etch
    # High exponent means ions travel straight down, clearing the floor polymer 
    # while neutrals chemically etch the newly exposed silicon.
    call_machine name=SF6_Plasma time=5.0

    # Grid maintenance is mandatory every cycle because the physical profile 
    # will begin undulating (forming scallops) based on particle tracking.
    grid remesh
    
    puts "Completed Flux-Based Bosch Cycle: $i"
}

# ---------------------------------------------------------------------
# STEP 4: SAVE THE COMPOSITE LAYOUT
# ---------------------------------------------------------------------
struct tdr=flux_based_drie_out
exit