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

# ---------- mask ----------
mask name=Mask1 left=0.35 right=0.65
photo mask=Mask1 thickness=0.4

# ---------- oxide etch (ion-enhanced approximation) ----------
# replaces:
# machetch + plasma angular distribution model

etch material=Oxide type=anisotropic rate=1.0 time=1.2
strip PhotoResist

# ---------- output ----------
# === Task 3 Measurements (depth and CD) ===
set bottom_x 0.0
if { [catch {set bottom_x [interface Gas / Oxide y=0.5]} err] } {
    if { [catch {set bottom_x [interface Gas / Silicon y=0.5]} err2] } {
        set bottom_x 0.0
    }
}
set depth_calc [expr { $bottom_x - (-1.0) }]
if { $depth_calc < 0.0 } {
    set depth_calc 0.0
}
puts "DOE: Trench_Depth [format %.6f $depth_calc]"
set mid_x [expr { -1.0 + ($depth_calc / 2.0) }]
set bot_x [expr { $bottom_x - 0.05 }]
if { $bot_x < -0.95 } {
    set bot_x -0.95
}
puts "==LAYERS_TOP_CD=="
layers x=-0.95
puts "==LAYERS_MID_CD=="
layers x=$mid_x
puts "==LAYERS_BOT_CD=="
layers x=$bot_x
puts "==LAYERS_END=="
struct tdr=ion_enhanced_etch_run_7