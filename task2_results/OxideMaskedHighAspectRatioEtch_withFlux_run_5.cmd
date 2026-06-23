# =====================================================================
# Sentaurus Process - Calibrated Flux-Based Bosch Approximation
# =====================================================================

math dimension=2

# ---------------------------------------------------------------------
# Reactor Conditions (for documentation/calibration)
# ---------------------------------------------------------------------

set Pressure_mTorr 10
set ICPPower_W 500
set Bias_V 250

set SF6_Flux       8.0e17
set IonFlux        2.0e16
set IonEnergy_eV   120

set C4F8_Flux      1.5e17

# ---------------------------------------------------------------------
# Convert Physical Fluxes -> Effective Process Parameters
#
# These values would normally come from calibration,
# reactor simulation, or experiment.
# ---------------------------------------------------------------------

set PolymerDepRate 0.01
set SiliconEtchRate 0.5387

set DepTime 2.0
set EtchTime 8.0

set NumCycles 5

# ---------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------

line x location=0.0 spacing=0.1 tag=Left
line x location=1.0 spacing=0.1 tag=Right

line y location=0.0 spacing=0.1 tag=Top
line y location=5.0 spacing=0.1 tag=Bottom


# ---------------------------------------------------------------------
# Silicon Region
# ---------------------------------------------------------------------

region Silicon \
    xlo=Left xhi=Right \
    ylo=Top yhi=Bottom 

init

# ---------------------------------------------------------------------
# Hard Mask
# ---------------------------------------------------------------------

deposit material=Oxide \
    type=isotropic \
    thickness=0.20

mask name=via \
    left=0.45 right=0.55 

photo mask=via thickness=0.5

etch material=Oxide \
     type=anisotropic \
     thickness=0.25

strip PhotoResist

# ---------------------------------------------------------------------
# Bosch Loop
# ---------------------------------------------------------------------

for {set cycle 1} {$cycle <= $NumCycles} {incr cycle} {

    puts "Starting Bosch cycle $cycle"

    # Passivation
    deposit material=PhotoResist \
        type=isotropic \
        rate=$PolymerDepRate \
        time=$DepTime

    # Directional Silicon Etch
    etch material=Silicon \
         type=anisotropic \
         rate=$SiliconEtchRate \
         time=$EtchTime

    grid remesh

    puts "Completed Bosch cycle $cycle"
}

# ---------------------------------------------------------------------
# Save Final Geometry
# ---------------------------------------------------------------------

struct tdr=OxideMaskedHighAspectRatioEtch_withFlux_run_5