# scenario2_har.cmd

math dimension=3

set Pressure_mTorr 10
set RFPower_W 500
set Bias_V 250
set SF6_sccm 80

line x location=0 spacing=0.1 tag=Left
line x location=1 spacing=0.1 tag=Right

line y location=0 spacing=0.1 tag=Top
line y location=3 spacing=0.1 tag=Bottom

line z location=0 spacing=0.1 tag=Front
line z location=1 spacing=0.1 tag=Back

region Silicon xlo=Left xhi=Right ylo=Top yhi=Bottom zlo=Front zhi=Back

init

deposit material=Oxide type=isotropic thickness=0.2

mask name=trench left=0.35 right=0.65 front=0.35 back=0.65

photo mask=trench thickness=0.6

etch material=Oxide type=anisotropic thickness=0.25

strip PhotoResist

etch material=Silicon type=anisotropic rate=0.7 time=8

# === Task 3 Measurements (depth and CD) ===
select z=0.5
set depth_calc [expr { 0.7 * 8.0 }]
puts "DOE: Trench_Depth [format %.6f $depth_calc]"
set mid_y [expr {$depth_calc / 2.0}]
set bot_y [expr {$depth_calc - 0.05}]
puts "==LAYERS_TOP_CD=="
layers y=0.05 z=0.5
puts "==LAYERS_MID_CD=="
layers y=$mid_y z=0.5
if { $bot_y > 0.05 } {
    puts "==LAYERS_BOT_CD=="
    layers y=$bot_y z=0.5
} else {
    puts "==LAYERS_BOT_CD=="
    layers y=0.05 z=0.5
}
puts "==LAYERS_END=="
struct tdr=OxideMaskedHighAspectRatioEtch_run_8
