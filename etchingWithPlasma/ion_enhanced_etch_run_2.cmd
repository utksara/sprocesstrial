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

etch material=Oxide type=anisotropic rate=0.7 time=1.7

# ---------- output ----------
struct tdr=ion_enhanced_etch_run_2