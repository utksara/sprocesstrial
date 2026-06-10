##############################################################################
# Sentaurus Process (sprocess) Command Script
# Simulation: Deep Reactive Ion Etching (DRIE) - Bosch Process
#
# Description:
#   Simulates the cyclic Bosch DRIE process on a silicon substrate with
#   a patterned mask. Each Bosch cycle consists of:
#     Step 1 - SF6 plasma etch      (isotropic + ion-enhanced anisotropic)
#     Step 2 - C4F8 plasma deposit  (conformal passivation polymer)
#     Step 3 - Ion bombardment      (directional polymer removal from trench floor)
#
#   Plasma is modelled via the 'plasma' command, which characterises the
#   ion-angular distribution (IAD) and ion-energy distribution (IED) at
#   the wafer surface, feeding into the surface etch/deposition models.
#
# Units  : microns (um), seconds (s), degrees (deg), eV
# Tool   : Sentaurus Process (sprocess) + Sentaurus Topography 3D engine
##############################################################################


##############################################################################
# 1. GLOBAL SIMULATION SETTINGS
##############################################################################

# Use the level-set topography engine for surface evolution
pdbSet Topography Simulator  LevelSet

# Enable Monte Carlo ray tracing for flux calculation (needed for IAD)
pdbSet Topography MCIntegration 1

# Number of Monte Carlo rays for ion/neutral flux integration
pdbSet Topography NumberOfRays 5000

# Level-set grid resolution (um) - balance accuracy vs runtime
pdbSet Grid Resolution 0.01


##############################################################################
# 2. INITIAL SUBSTRATE DEFINITION
##############################################################################

# Define a silicon substrate: 4 um wide x 8 um deep (2D cross-section)
# Extend Z to 1 um for quasi-2D simulation
line x location= 0.0   spacing= 0.05  tag= top
line x location= 8.0   spacing= 0.1   tag= bottom
line y location= 0.0   spacing= 0.05  tag= left
line y location= 4.0   spacing= 0.05  tag= right

region silicon xlo= top xhi= bottom ylo= left yhi= right

# Initialise the structure (p-type silicon, 1e15 cm-3)
init concentration= 1e15  field= Boron  wafer.orient= {0 0 1}


##############################################################################
# 3. HARD MASK DEFINITION
# SiO2 hard mask with a 1 um opening centred at y = 1.5 to 2.5 um
##############################################################################

# Deposit a 0.5 um SiO2 hard mask over the full surface
deposit material= Oxide  type= isotropic  thickness= 0.5

# Pattern the mask: etch away the oxide in the trench opening window
# Mask opening: y = 1.5 um to y = 2.5 um  (1 um wide trench)
etch material= Oxide  type= anisotropic  thickness= 0.6 \
     coordinate= -0.5                                    \
     start.material= Oxide

# Alternatively, use a mask layer (comment block above and use below):
# photo mask= "trench_mask" thickness= 0.5
# etch  material= Oxide  type= anisotropic  thickness= 0.6
# strip photo


##############################################################################
# 4. PLASMA PARAMETER DEFINITIONS
#
#    The 'plasma' command in Sentaurus Process / Topography defines the
#    particle flux characteristics arriving at the wafer surface from
#    the plasma sheath. Key parameters:
#
#    -type        : ion | neutral
#    -distribution: cosine | gaussian | bimodal | uniform | custom
#    -energy      : mean ion energy at wafer surface (eV)
#    -sigma       : angular spread (FWHM in degrees) of the IAD
#    -flux        : normalised particle flux (relative units)
#
#    The IAD (Ion Angular Distribution) is critical for DRIE:
#      - Narrow IAD (small sigma) -> high anisotropy, vertical walls
#      - Broad  IAD (large sigma) -> lateral etching, bowing
##############################################################################

# ---- SF6 Etch Cycle Plasma (ICP-type, high-density) ----------------------
# Primary species: F* neutrals (chemical etch) + SF5+/SF3+ ions (physical)
# Pressure ~20 mTorr, ICP power ~800 W, Bias ~50 V

proc define_SF6_plasma {} {

    # SF5+ ions - directional, high energy, responsible for anisotropy
    plasma name= SF5ion                  \
           type= ion                     \
           energy= 80.0                  \
           distribution= gaussian        \
           sigma= 3.0                    \
           flux= 1.0                     \
           mass= 127.0                   \
           charge= 1

    # SF3+ ions - secondary ion species, slightly broader angular spread
    plasma name= SF3ion                  \
           type= ion                     \
           energy= 65.0                  \
           distribution= gaussian        \
           sigma= 4.5                    \
           flux= 0.3                     \
           mass= 89.0                    \
           charge= 1

    # F* neutrals - isotropic chemical etchant, cosine distribution
    plasma name= Fneutral                \
           type= neutral                 \
           energy= 0.04                  \
           distribution= cosine         \
           flux= 8.0                     \
           sticking= 0.1
}

# ---- C4F8 Deposition Cycle Plasma ----------------------------------------
# Primary species: CFx radicals -> deposit fluorocarbon passivation polymer
# Pressure ~50 mTorr, ICP power ~600 W, Bias ~0 V (no DC bias)

proc define_C4F8_plasma {} {

    # CFx radicals - nearly isotropic, low energy, conformal deposition
    plasma name= CFxradical              \
           type= neutral                 \
           energy= 0.04                  \
           distribution= cosine          \
           flux= 5.0                     \
           sticking= 0.8

    # C4F8+ ions - small ion flux, low energy (no external bias)
    plasma name= C4F8ion                 \
           type= ion                     \
           energy= 15.0                  \
           distribution= gaussian        \
           sigma= 8.0                    \
           flux= 0.15                    \
           mass= 200.0                   \
           charge= 1
}

# ---- Ion Bombardment / Polymer Clear Step --------------------------------
# Short SF6 or Ar step with high bias to clear polymer from trench floor
# High energy, narrow IAD -> strictly vertical bombardment

proc define_ionbomb_plasma {} {

    # Ar+ ions - purely physical sputtering to clear passivation from floor
    plasma name= Arion                   \
           type= ion                     \
           energy= 200.0                 \
           distribution= gaussian        \
           sigma= 1.5                    \
           flux= 1.0                     \
           mass= 40.0                    \
           charge= 1
}


##############################################################################
# 5. MATERIAL ETCH/DEPOSITION RATE MODELS
#
#    Rate models connect the plasma flux to surface reaction rates.
#    Sentaurus uses the 'etch' and 'deposit' commands with 'machine'
#    parameters that reference the plasma species defined above.
##############################################################################

# ---- SF6 Silicon Etch Rate Model -----------------------------------------
# Rate = (chemical rate from F*) + (ion-enhanced rate from SF5+/SF3+)
# Ion-enhanced etch: rate proportional to sqrt(ion energy) * ion flux

proc SF6_etch_model {} {
    # Chemical (isotropic) component - driven by F* neutral flux
    etch material= Silicon               \
         type= isotropic                 \
         rate= { <100> 0.15             \
                 <110> 0.17             \
                 <111> 0.10 }           \
         plasma.species= Fneutral        \
         sticking= 0.1

    # Ion-enhanced (anisotropic) component - driven by SF5+ ion flux
    etch material= Silicon               \
         type= ion_enhanced              \
         rate= 0.40                      \
         plasma.species= SF5ion          \
         threshold.energy= 20.0         \
         yield.factor= 0.85
}

# ---- C4F8 Polymer Deposition Model ---------------------------------------
proc C4F8_deposit_model {} {
    deposit material= Photoresist        \
            type= isotropic              \
            rate= 0.05                   \
            plasma.species= CFxradical   \
            sticking= 0.8
    # Note: 'Photoresist' is used here as a proxy for fluorocarbon polymer.
    # In a calibrated flow, define a custom material 'FCpolymer'.
}

# ---- Polymer Removal (Ion Bombardment) Model -----------------------------
proc polymer_clear_model {} {
    etch material= Photoresist           \
         type= ion_enhanced              \
         rate= 0.25                      \
         plasma.species= Arion           \
         threshold.energy= 30.0         \
         yield.factor= 1.2

    # Slight silicon etch during ion bombardment (physical sputtering)
    etch material= Silicon               \
         type= ion_enhanced              \
         rate= 0.03                      \
         plasma.species= Arion           \
         threshold.energy= 50.0         \
         yield.factor= 0.15
}


##############################################################################
# 6. BOSCH PROCESS CYCLE LOOP
#
#    Each cycle: [SF6 etch] -> [C4F8 deposit] -> [ion bombardment]
#    Typical cycle times at 20 mTorr / 800 W ICP:
#      SF6   etch  : 7 s  (etch ~400 nm/cycle)
#      C4F8  depo  : 5 s  (deposit ~50 nm polymer)
#      Ion bomb    : 2 s  (clear polymer from trench floor)
#
#    Target: ~10 cycles -> ~4 um trench depth
##############################################################################

set num_cycles 10

set sf6_etch_time   7.0    ;# seconds per SF6 etch sub-step
set c4f8_depo_time  5.0    ;# seconds per C4F8 deposition sub-step
set ionbomb_time    2.0    ;# seconds per ion bombardment sub-step

for { set cycle 1 } { $cycle <= $num_cycles } { incr cycle } {

    puts "--- Bosch Cycle $cycle / $num_cycles ---"

    ##########################################################################
    # SUB-STEP A: SF6 PLASMA ETCH
    ##########################################################################
    define_SF6_plasma

    # Ion-enhanced silicon etch (anisotropic, driven by SF5+ IAD)
    etch material= Silicon               \
         type= ion_enhanced              \
         time= $sf6_etch_time            \
         plasma= { SF5ion SF3ion Fneutral } \
         anisotropy= 0.85                \
         model= rie

    # Also etch any exposed hard-mask oxide at a slower rate (selectivity ~30:1)
    etch material= Oxide                 \
         type= ion_enhanced              \
         time= $sf6_etch_time            \
         rate= 0.005                     \
         plasma= { SF5ion }              \
         anisotropy= 0.90

    ##########################################################################
    # SUB-STEP B: C4F8 PLASMA DEPOSITION (Passivation)
    ##########################################################################
    define_C4F8_plasma

    # Conformal fluorocarbon polymer deposition on all surfaces
    deposit material= Photoresist        \
            type= conformal              \
            time= $c4f8_depo_time        \
            plasma= { CFxradical C4F8ion } \
            rate= 0.01                   \
            conformality= 0.95

    ##########################################################################
    # SUB-STEP C: ION BOMBARDMENT (Polymer Clear from Trench Floor)
    ##########################################################################
    define_ionbomb_plasma

    # Directional removal of polymer from horizontal surfaces only
    # Narrow IAD (sigma=1.5 deg) preserves sidewall polymer
    etch material= Photoresist           \
         type= ion_enhanced              \
         time= $ionbomb_time             \
         plasma= { Arion }               \
         anisotropy= 0.98                \
         model= sputter

    # Save intermediate profile every 2 cycles for visualisation
    if { [expr $cycle % 2] == 0 } {
        struct tdr= "DRIE_cycle_${cycle}"
    }
}


##############################################################################
# 7. POST-ETCH CLEANUP
# Strip residual polymer and save final structure
##############################################################################

# Ashing / wet strip of remaining fluorocarbon polymer
strip material= Photoresist

# Optional: brief O2 plasma clean (isotropic, no plasma command needed here)
etch material= Photoresist  type= isotropic  thickness= 0.02

# Save final etched structure
struct tdr= "DRIE_final_structure"

# Export to visualise in Sentaurus Visual (SVisual)
puts "DRIE Bosch simulation complete."
puts "Final structure saved: DRIE_final_structure.tdr"


##############################################################################
# 8. MEASUREMENT EXTRACTION
##############################################################################

# Extract trench depth (distance from top surface to deepest etch point)
set trench_depth [measure depth material= Silicon direction= x]
puts "Measured trench depth: $trench_depth um"

# Extract trench width at mid-depth (check for bowing)
set trench_width_mid [measure width material= Silicon \
                      at.depth= [expr $trench_depth / 2.0]]
puts "Trench width at mid-depth: $trench_width_mid um"

# Aspect ratio
set aspect_ratio [expr $trench_depth / $trench_width_mid]
puts "Aspect ratio: $aspect_ratio"


##############################################################################
# END OF SCRIPT
##############################################################################