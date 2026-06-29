# test_2d.cmd

math dimension=2

set Pressure_mTorr 10
set RFPower_W      500
set Bias_V         250
set SF6_sccm       80
set C4F8_sccm      100

set PolymerDepRate 0.01
set SiliconEtchRate 0.5387

set DepTime 2.0
set EtchTime 5.0
set NumCycles 2

line x location=0.0 spacing=0.1 tag=Left
line x location=1.0 spacing=0.1 tag=Right

line y location=0.0 spacing=0.1 tag=Top
line y location=5.0 spacing=0.1 tag=Bottom

region Silicon xlo=Left xhi=Right ylo=Top yhi=Bottom

init

deposit material=Oxide type=isotropic thickness=0.2

mask name=via left=0.45 right=0.55

photo mask=via thickness=0.5

etch material=Oxide type=anisotropic thickness=0.25

strip PhotoResist

for {set cycle 1} {$cycle <= $NumCycles} {incr cycle} {
    puts "Starting Bosch cycle $cycle"

    deposit material=PhotoResist type=isotropic rate=$PolymerDepRate time=$DepTime

    etch material=Silicon type=anisotropic rate=$SiliconEtchRate time=$EtchTime

    grid remesh

    puts "Completed Bosch cycle $cycle"
}

struct tdr=test_2d_out
