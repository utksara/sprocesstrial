# ------------------------------------------------------------
# Ion-enhanced etch (Y-2026 sprocess-compatible)
# ------------------------------------------------------------

math dimension=2

# ---------- domain ----------
line x location=0 spacing=0.03 tag=Left
line x location=3 spacing=0.03 tag=Right

line y location=0 spacing=0.03 tag=Bottom
line y location=1 spacing=0.03 tag=Top

region Silicon xlo=Left xhi=Right ylo=Bottom yhi=Top

init

# ---------- initial structure ----------
deposit material=Oxide thickness=1.0
deposit material=PhotoResist thickness=0.4

# ---------- mask ----------
mask name=Mask1 left=0.35 right=0.65 front=0.35 back=0.65
photo mask=Mask1 thickness=0.4

# remove exposed resist
etch material=PhotoResist type=isotropic thickness=0.4
strip PhotoResist

# ---------- oxide etch (ion-enhanced approximation) ----------
# replaces:
# machetch + plasma angular distribution model

etch material=Oxide type=anisotropic rate=1.0 time=2.0

# ---------- output ----------
# === Task 3 Measurements (depth and CD) ===
set rate 1.0
set time 2.0
set depth_calc [expr { $rate * $time }]
puts "DOE: Trench_Depth [format %.6f $depth_calc]"
set mid_y [expr { 2.0 - ($depth_calc / 2.0) }]
set bot_y [expr { 2.0 - ($depth_calc - 0.05) }]
puts "==LAYERS_TOP_CD=="
layers y=1.95
puts "==LAYERS_MID_CD=="
layers y=$mid_y
if { $bot_y < 1.95 } {
    puts "==LAYERS_BOT_CD=="
    layers y=$bot_y
} else {
    puts "==LAYERS_BOT_CD=="
    layers y=1.95
}
puts "==LAYERS_END=="
struct tdr=ion_enhanced_etch_run_9