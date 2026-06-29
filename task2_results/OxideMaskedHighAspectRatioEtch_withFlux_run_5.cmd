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

set SF6_Flux       8.0e+17
set IonFlux        2.0e+16
set IonEnergy_eV   250

set C4F8_Flux      1.5e+17

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

set NumCycles 2

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

# === Task 3 Measurements (depth and CD) ===
set depth_calc [expr { $NumCycles * $SiliconEtchRate * $EtchTime }]
puts "DOE: Trench_Depth [format %.6f $depth_calc]"
set mid_y [expr {$depth_calc / 2.0}]
set bot_y [expr {$depth_calc - 0.05}]
puts "==LAYERS_TOP_CD=="
layers y=0.05
puts "==LAYERS_MID_CD=="
layers y=$mid_y
if { $bot_y > 0.05 } {
    puts "==LAYERS_BOT_CD=="
    layers y=$bot_y
} else {
    puts "==LAYERS_BOT_CD=="
    layers y=0.05
}
puts "==LAYERS_END=="

struct tdr=OxideMaskedHighAspectRatioEtch_withFlux_run_5